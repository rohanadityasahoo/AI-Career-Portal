"""Generate downloadable resume documents from the editable resume draft."""

import base64
from io import BytesIO
import re
import textwrap
import unicodedata
from zipfile import ZIP_DEFLATED, ZipFile

RESUME_FIELDS = (
    "name",
    "contact",
    "headline",
    "summary",
    "skills",
    "education",
    "projects",
    "experience",
    "certifications",
    "achievements",
)

SECTION_LABELS = {
    "summary": "Professional Summary",
    "experience": "Experience",
    "projects": "Projects",
    "skills": "Skills",
    "education": "Education",
    "certifications": "Certifications",
    "achievements": "Achievements",
}

PDF_PAGE_WIDTH = 612
PDF_PAGE_HEIGHT = 792
PDF_LEFT = 54
PDF_RIGHT = 54
PDF_BOTTOM = 48
PDF_BODY_WIDTH = PDF_PAGE_WIDTH - PDF_LEFT - PDF_RIGHT
PDF_NAVY = "102A56"
PDF_BLUE = "2563EB"
PDF_SLATE = "334155"
PDF_MUTED = "64748B"
PDF_LIGHT = "E2E8F0"
PDF_WHITE = "FFFFFF"
PDF_PALE_BLUE = "DBEAFE"

RESUME_TEMPLATES = {
  "modern": {
    "label": "Modern Navy",
    "description": "Bold header with crisp blue accents.",
    "header": "102A56",
    "header_text": "102A56",
    "primary": "2563EB",
    "title": "DBEAFE",
    "body": "334155",
    "muted": "64748B",
    "light": "E2E8F0",
    "soft": "DBEAFE",
    "header_mode": "band",
  },
  "minimal": {
    "label": "Minimal Teal",
    "description": "Clean white layout with subtle teal details.",
    "header": "FFFFFF",
    "header_text": "0F172A",
    "primary": "0F766E",
    "title": "0F766E",
    "body": "334155",
    "muted": "64748B",
    "light": "CBD5E1",
    "soft": "CCFBF1",
    "header_mode": "minimal",
  },
  "classic": {
    "label": "Classic Charcoal",
    "description": "Traditional structure with warm gold accents.",
    "header": "263238",
    "header_text": "263238",
    "primary": "B7791F",
    "title": "FDE68A",
    "body": "374151",
    "muted": "6B7280",
    "light": "E5E7EB",
    "soft": "FDE68A",
    "header_mode": "band",
  },
}


def normalize_resume_template(value):
  """Return a supported template key and default safely for old clients."""
  key = str(value or "modern").strip().lower()
  return key if key in RESUME_TEMPLATES else "modern"


def normalize_resume_photo(value):
  """Validate and standardize a browser-uploaded profile photo as JPEG bytes."""
  if not value:
    return None
  if not isinstance(value, str) or "," not in value:
    raise ValueError("Upload a JPG or PNG profile photo.")

  header, encoded = value.split(",", 1)
  if header.lower() not in {
      "data:image/jpeg;base64",
      "data:image/jpg;base64",
      "data:image/png;base64",
  }:
    raise ValueError("Only JPG and PNG profile photos are supported.")

  try:
    photo_bytes = base64.b64decode(encoded, validate=True)
  except (ValueError, TypeError):
    raise ValueError("The profile photo could not be read.") from None
  if not photo_bytes or len(photo_bytes) > 5 * 1024 * 1024:
    raise ValueError("Profile photos must be smaller than 5 MB.")

  try:
    from PIL import Image, ImageOps

    with Image.open(BytesIO(photo_bytes)) as image:
      if image.width * image.height > 20_000_000:
        raise ValueError("The profile photo is too large to process.")
      image.verify()

    with Image.open(BytesIO(photo_bytes)) as image:
      image = ImageOps.exif_transpose(image).convert("RGB")
      image = ImageOps.fit(
          image,
          (320, 320),
          method=Image.Resampling.LANCZOS,
      )
      output = BytesIO()
      image.save(output, format="JPEG", quality=88, optimize=True)
      return output.getvalue()
  except ValueError:
    raise
  except Exception:
    raise ValueError("The profile photo is not a valid JPG or PNG image.") from None


def normalize_resume_draft(payload):
  """Keep download input limited to the fields and sizes used by the draft."""
  draft = {}
  for field in RESUME_FIELDS:
    value = payload.get(field, "") if isinstance(payload, dict) else ""
    draft[field] = str(value or "").strip()[:12000]
  return draft


def _plain_text(value):
  """Convert authored text to predictable PDF-safe ASCII."""
  normalized = unicodedata.normalize("NFKD", str(value or ""))
  ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
  ascii_text = (
      ascii_text.replace("\u2022", "-")
      .replace("\u2013", "-")
      .replace("\u2014", "-")
      .replace("\u2018", "'")
      .replace("\u2019", "'")
      .replace("\u201c", '"')
      .replace("\u201d", '"')
  )
  return re.sub(r"[ \t]+", " ", ascii_text).strip()


def _clean_lines(value):
  lines = []
  for raw_line in str(value or "").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
    line = _plain_text(raw_line)
    if line:
      lines.append(line)
    elif lines and lines[-1] != "":
      lines.append("")
  while lines and lines[-1] == "":
    lines.pop()
  return lines


def _blocks(value):
  blocks = []
  current = []
  for line in _clean_lines(value):
    if not line:
      if current:
        blocks.append(current)
        current = []
      continue
    current.append(line)
  if current:
    blocks.append(current)
  return blocks


def _strip_bullet(value):
  text = str(value or "").strip()
  if text.startswith(("- ", "* ", "+ ")):
    return True, text[2:].strip()
  return False, text


def _sentence_parts(lines):
  joined = " ".join(line.strip() for line in lines if line.strip())
  if not joined:
    return []
  parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", joined)
  return [part.strip() for part in parts if part.strip()]


def _bullet_groups(lines):
  groups = []
  current = []
  for line in lines:
    is_bullet, cleaned = _strip_bullet(line)
    if is_bullet:
      if current:
        groups.append(" ".join(current).strip())
      current = [cleaned]
    elif current:
      current.append(cleaned)
    else:
      current = [cleaned]
  if current:
    groups.append(" ".join(current).strip())
  return groups


def _content_items(field, value):
  """Return semantic content items so authored lines become readable bullets."""
  blocks = _blocks(value)
  items = []
  if field == "summary":
    for block in blocks:
      items.append(("paragraph", " ".join(block)))
    return items

  if field in {"experience", "projects"}:
    for block in blocks:
      if not block:
        continue
      bullet_index = next(
          (index for index, line in enumerate(block) if _strip_bullet(line)[0]),
          None,
      )
      if bullet_index is not None:
        if bullet_index > 0:
          items.append(("entry", block[0]))
          for group in _bullet_groups(block[bullet_index:]):
            items.append(("bullet", group))
        else:
          for group in _bullet_groups(block):
            items.append(("bullet", group))
        continue

      if len(block) > 1:
        items.append(("entry", block[0]))
        for sentence in _sentence_parts(block[1:]):
          items.append(("bullet", sentence))
      else:
        items.append(("paragraph", block[0]))
    return items

  if field in {"certifications", "achievements"}:
    for block in blocks:
      for line in block:
        is_bullet, cleaned = _strip_bullet(line)
        items.append(("bullet" if is_bullet or len(block) > 1 else "paragraph", cleaned))
    return items

  for block in blocks:
    for line in block:
      is_bullet, cleaned = _strip_bullet(line)
      items.append(("bullet" if is_bullet else "paragraph", cleaned))
  return items
def _wrap(value, width):
  text = _plain_text(value)
  if not text:
    return []
  return textwrap.wrap(
      text,
      width=width,
      break_long_words=True,
      break_on_hyphens=False,
  ) or [text]


def _color(value):
  value = value.lstrip("#")
  return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))


def _pdf_color(value):
  red, green, blue = _color(value)
  return f"{red:.3f} {green:.3f} {blue:.3f}"


def _pdf_escape(value):
  return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_text(font, size, x, y, value, color=PDF_SLATE):
  return (
      f"BT /{font} {size} Tf {_pdf_color(color)} rg 1 0 0 1 {x:.2f} {y:.2f} Tm "
      f"({_pdf_escape(_plain_text(value))}) Tj ET"
  )


def _pdf_rect(x, y, width, height, color):
  return f"q {_pdf_color(color)} rg {x:.2f} {y:.2f} {width:.2f} {height:.2f} re f Q"


def _pdf_line(x1, y1, x2, y2, color, width=0.8):
  return f"q {_pdf_color(color)} RG {width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S Q"


def _pdf_circle(x, y, radius, color):
  control = radius * 0.5523
  return (
      f"q {_pdf_color(color)} rg {x + radius:.2f} {y:.2f} m "
      f"{x + radius:.2f} {y + control:.2f} {x + control:.2f} {y + radius:.2f} {x:.2f} {y + radius:.2f} c "
      f"{x - control:.2f} {y + radius:.2f} {x - radius:.2f} {y + control:.2f} {x - radius:.2f} {y:.2f} c "
      f"{x - radius:.2f} {y - control:.2f} {x - control:.2f} {y - radius:.2f} {x:.2f} {y - radius:.2f} c "
      f"{x + control:.2f} {y - radius:.2f} {x + radius:.2f} {y - control:.2f} {x + radius:.2f} {y:.2f} c f Q"
  )


def _pdf_image(name, x, y, width, height):
  return f"q {width:.2f} 0 0 {height:.2f} {x:.2f} {y:.2f} cm /{name} Do Q"


def _draw_pdf_header(commands, draft, first_page, template, photo_bytes=None):
  name = _plain_text(draft.get("name")) or "Resume"
  headline = _plain_text(draft.get("headline"))
  contact = _plain_text(draft.get("contact"))
  if first_page:
    text_width = 60 if photo_bytes else 92
    if template["header_mode"] == "band":
      commands.append(_pdf_rect(0, 650, PDF_PAGE_WIDTH, 142, template["header"]))
      commands.append(_pdf_rect(0, 650, PDF_PAGE_WIDTH, 5, template["primary"]))
      name_color = PDF_WHITE
      title_color = template["title"]
      contact_color = PDF_WHITE
      line_color = template["soft"]
    else:
      name_color = template["header_text"]
      title_color = template["primary"]
      contact_color = template["muted"]
      line_color = template["primary"]

    commands.append(_pdf_text("F2", 25, PDF_LEFT, 736, name, name_color))
    if headline:
      headline_lines = _wrap(headline, text_width)
      for index, line in enumerate(headline_lines[:2]):
        commands.append(_pdf_text("F1", 11.5, PDF_LEFT, 705 - (index * 13), line, title_color))
    contact_lines = _wrap(contact, text_width)
    for index, line in enumerate(contact_lines[:2]):
      contact_y = 681 - (index * 12) if not headline or len(headline_lines) < 2 else 668 - (index * 12)
      commands.append(_pdf_text("F1", 8.5, PDF_LEFT, contact_y, line, contact_color))
    if photo_bytes:
      commands.append(_pdf_image("Im1", PDF_PAGE_WIDTH - PDF_RIGHT - 86, 687, 86, 86))
    commands.append(_pdf_line(PDF_LEFT, 651 if template["header_mode"] == "band" else 665, PDF_PAGE_WIDTH - PDF_RIGHT, 651 if template["header_mode"] == "band" else 665, line_color, 0.7))
    return 620 if template["header_mode"] == "band" else 634

  commands.append(_pdf_text("F2", 11, PDF_LEFT, 758, name, template["header_text"]))
  if headline:
    commands.append(_pdf_text("F1", 8.5, PDF_LEFT + 180, 759, headline, template["muted"]))
  commands.append(_pdf_line(PDF_LEFT, 742, PDF_PAGE_WIDTH - PDF_RIGHT, 742, template["light"], 0.8))
  return 718


def _section_estimate(field, value):
  heading = 26
  total = heading
  for item_type, text in _content_items(field, value):
    if item_type == "entry":
      total += max(1, len(_wrap(text, 86))) * 13 + 4
    elif item_type == "bullet":
      total += max(1, len(_wrap(text, 84))) * 12 + 2
    else:
      total += max(1, len(_wrap(text, 94))) * 12 + 3
  return total + 8


def build_resume_pdf(draft, template_key="modern", photo_bytes=None):
  """Build a polished, ATS-safe single-column PDF with deliberate hierarchy."""
  template = RESUME_TEMPLATES[normalize_resume_template(template_key)]
  pages = []
  commands = []
  y = _draw_pdf_header(commands, draft, True, template, photo_bytes)
  pages.append(commands)

  def new_page():
    nonlocal commands, y
    commands = []
    y = _draw_pdf_header(commands, draft, False, template)
    pages.append(commands)

  def ensure_space(height):
    nonlocal y
    if y - height < PDF_BOTTOM:
      new_page()

  for field in ("summary", "experience", "projects", "skills", "education", "certifications", "achievements"):
    value = str(draft.get(field, "") or "").strip()
    if not value:
      continue

    estimate = _section_estimate(field, value)
    available = y - PDF_BOTTOM
    if y < 620 and estimate < 620 and estimate > available:
      new_page()

    label = SECTION_LABELS[field].upper()
    ensure_space(28)
    commands.append(_pdf_text("F2", 9.4, PDF_LEFT, y, label, template["primary"]))
    label_width = min(170, max(96, len(label) * 5.1 + 14))
    commands.append(_pdf_line(PDF_LEFT + label_width, y + 3, PDF_PAGE_WIDTH - PDF_RIGHT, y + 3, template["light"], 1.0))
    y -= 18

    for item_type, text in _content_items(field, value):
      if not text:
        continue
      if item_type == "entry":
        lines = _wrap(text, 86)
        ensure_space(max(1, len(lines)) * 13 + 5)
        for line in lines:
          commands.append(_pdf_text("F2", 9.7, PDF_LEFT, y, line, template["header_text"]))
          y -= 13
        y -= 3
        continue

      if item_type == "bullet":
        lines = _wrap(text, 84)
        ensure_space(max(1, len(lines)) * 12 + 2)
        for line_index, line in enumerate(lines):
          if line_index == 0:
            commands.append(_pdf_circle(PDF_LEFT + 2.5, y + 3, 1.7, template["primary"]))
          commands.append(_pdf_text("F1", 9.1, PDF_LEFT + 11, y, line, template["body"]))
          y -= 12
        y -= 2
        continue

      lines = _wrap(text, 94)
      ensure_space(max(1, len(lines)) * 12 + 3)
      for line in lines:
        commands.append(_pdf_text("F1", 9.1, PDF_LEFT, y, line, template["body"]))
        y -= 12
      y -= 3

    y -= 5

  for page_number, page_commands in enumerate(pages, start=1):
    page_commands.append(_pdf_line(PDF_LEFT, 34, PDF_PAGE_WIDTH - PDF_RIGHT, 34, template["light"], 0.6))
    page_commands.append(_pdf_text("F1", 7.5, PDF_LEFT, 22, "CareerPilot Resume", template["muted"]))
    page_commands.append(_pdf_text("F1", 7.5, PDF_PAGE_WIDTH - PDF_RIGHT - 35, 22, f"{page_number}", template["muted"]))

  objects = [
      "<< /Type /Catalog /Pages 2 0 R >>",
      "",
      "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
      "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
  ]
  image_object_number = None
  if photo_bytes:
    image_object_number = len(objects) + 1
    objects.append(
        b"<< /Type /XObject /Subtype /Image /Width 320 /Height 320 "
        b"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
        + f"/Length {len(photo_bytes)} >>\nstream\n".encode("ascii")
        + photo_bytes
        + b"\nendstream"
    )
  page_numbers = []
  for page_commands in pages:
    stream = "\n".join(page_commands) + "\n"
    content_number = len(objects) + 1
    objects.append(f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}endstream")
    page_number = len(objects) + 1
    resources = "/Font << /F1 3 0 R /F2 4 0 R >>"
    if image_object_number:
      resources += f" /XObject << /Im1 {image_object_number} 0 R >>"
    objects.append(
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        f"/Resources << {resources} >> /Contents {content_number} 0 R >>"
    )
    page_numbers.append(page_number)

  kids = " ".join(f"{number} 0 R" for number in page_numbers)
  objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_numbers)} >>"

  output = bytearray(b"%PDF-1.4\n")
  offsets = [0]
  for number, obj in enumerate(objects, start=1):
    offsets.append(len(output))
    output.extend(f"{number} 0 obj\n".encode("ascii"))
    output.extend(obj if isinstance(obj, bytes) else obj.encode("latin-1"))
    output.extend(b"\nendobj\n")
  xref_offset = len(output)
  output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
  output.extend(b"0000000000 65535 f \n")
  for offset in offsets[1:]:
    output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
  output.extend(
      f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
      f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
  )
  return bytes(output)


def _xml_text(value):
  return (
      str(value or "")
      .replace("&", "&amp;")
      .replace("<", "&lt;")
      .replace(">", "&gt;")
      .replace('"', "&quot;")
      .replace("'", "&apos;")
  )


def _word_run(text, *, bold=False, size=20, color="334155", font="Aptos"):
  properties = (
      f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}"/>'
      f'<w:sz w:val="{size}"/><w:color w:val="{color}"/>'
      + ("<w:b/>" if bold else "")
  )
  return f'<w:r><w:rPr>{properties}</w:rPr><w:t xml:space="preserve">{_xml_text(text)}</w:t></w:r>'


def _word_paragraph(
    text="",
    *,
    bold=False,
    size=20,
    color="334155",
    align=None,
    style=None,
    before=0,
    after=90,
    keep_next=False,
    left_indent=None,
    hanging=None,
    num_id=None,
):
  paragraph_properties = []
  if align:
    paragraph_properties.append(f'<w:jc w:val="{align}"/>')
  if style:
    paragraph_properties.append(f'<w:pStyle w:val="{style}"/>')
  if before or after:
    paragraph_properties.append(f'<w:spacing w:before="{before}" w:after="{after}" w:line="270" w:lineRule="auto"/>')
  if keep_next:
    paragraph_properties.append("<w:keepNext/>")
  if left_indent is not None:
    indent = f'<w:ind w:left="{left_indent}"'
    if hanging is not None:
      indent += f' w:hanging="{hanging}"'
    paragraph_properties.append(indent + "/>" )
  if num_id is not None:
    paragraph_properties.append(f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr>')
  properties = f"<w:pPr>{''.join(paragraph_properties)}</w:pPr>"
  return f"<w:p>{properties}{_word_run(text, bold=bold, size=size, color=color)}</w:p>"


def _word_drawing(relation_id, size=960120):
  return (
      '<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
      f'<wp:extent cx="{size}" cy="{size}"/>'
      '<wp:docPr id="1" name="Profile photo"/>'
      '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
      '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
      '<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="Profile photo"/><pic:cNvPicPr/></pic:nvPicPr>'
      f'<pic:blipFill><a:blip r:embed="{relation_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
      f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{size}" cy="{size}"/></a:xfrm>'
      '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
      '</a:graphicData></a:graphic></wp:inline></w:drawing>'
  )


def _word_header(draft, template, photo_bytes=None):
  name = _plain_text(draft.get("name")) or "Resume"
  headline = _plain_text(draft.get("headline"))
  contact = _plain_text(draft.get("contact"))
  is_band = template["header_mode"] == "band"
  name_color = PDF_WHITE if is_band else template["header_text"]
  title_color = template["title"] if is_band else template["primary"]
  contact_color = PDF_WHITE if is_band else template["muted"]
  body = [
      _word_paragraph(name, bold=True, size=34, color=name_color, style="ResumeName", before=0, after=30, keep_next=True),
  ]
  if headline:
    body.append(_word_paragraph(headline, size=21, color=title_color, style="ResumeTitle", before=0, after=25, keep_next=True))
  if contact:
    body.append(_word_paragraph(contact, size=16, color=contact_color, before=0, after=20))
  cell_borders = (
      f'<w:tcBorders><w:bottom w:val="single" w:sz="12" w:space="0" w:color="{template["primary"]}"/></w:tcBorders>'
      if not is_band
      else ""
  )
  cell_properties = (
      f'<w:tcPr><w:shd w:fill="{template["header"]}"/>{cell_borders}<w:tcMar>'
      '<w:top w:w="220" w:type="dxa"/><w:left w:w="260" w:type="dxa"/>'
      '<w:bottom w:w="220" w:type="dxa"/><w:right w:w="260" w:type="dxa"/>'
      '</w:tcMar></w:tcPr>'
  )
  text_cell = f'<w:tc>{cell_properties}{"".join(body)}</w:tc>'
  table_properties = (
      '<w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblLayout w:type="fixed"/><w:tblBorders>'
      '<w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>'
      '<w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders></w:tblPr>'
  )
  if not photo_bytes:
    return f'<w:tbl>{table_properties}<w:tr>{text_cell}</w:tr></w:tbl>'

  photo_cell_properties = (
      f'<w:tcPr><w:tcW w:w="1700" w:type="dxa"/><w:shd w:fill="{template["header"]}"/>'
      '<w:vAlign w:val="center"/><w:tcMar>'
      '<w:top w:w="180" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
      '<w:bottom w:w="180" w:type="dxa"/><w:right w:w="260" w:type="dxa"/>'
      '</w:tcMar></w:tcPr>'
  )
  photo_cell = (
      f'<w:tc>{photo_cell_properties}<w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
      f'{_word_drawing("rId3")}</w:p></w:tc>'
  )
  grid = '<w:tblGrid><w:gridCol w:w="8740"/><w:gridCol w:w="1700"/></w:tblGrid>'
  return f'<w:tbl>{table_properties}{grid}<w:tr>{text_cell}{photo_cell}</w:tr></w:tbl>'


def _word_body_item(item_type, text, template):
  if item_type == "entry":
    return _word_paragraph(text, bold=True, size=20, color=template["header_text"], before=55, after=35, keep_next=True)
  if item_type == "bullet":
    return _word_paragraph(text, size=19, color=template["body"], style="ResumeBullet", before=0, after=45, left_indent=420, hanging=220, num_id=1)
  return _word_paragraph(text, size=19, color=template["body"], before=0, after=55)


def _word_styles(template):
  return (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
      f'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="{template["body"]}"/><w:sz w:val="19"/></w:rPr></w:rPrDefault></w:docDefaults>'
      f'<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:color w:val="{template["body"]}"/><w:sz w:val="19"/></w:rPr><w:pPr><w:spacing w:after="55" w:line="270"/></w:pPr></w:style>'
      f'<w:style w:type="paragraph" w:styleId="ResumeName"><w:name w:val="Resume Name"/><w:rPr><w:b/><w:color w:val="{PDF_WHITE if template["header_mode"] == "band" else template["header_text"]}"/><w:sz w:val="34"/></w:rPr></w:style>'
      f'<w:style w:type="paragraph" w:styleId="ResumeTitle"><w:name w:val="Resume Title"/><w:rPr><w:color w:val="{template["title"] if template["header_mode"] == "band" else template["primary"]}"/><w:sz w:val="21"/></w:rPr></w:style>'
      f'<w:style w:type="paragraph" w:styleId="ResumeHeading"><w:name w:val="Resume Heading"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:caps/><w:color w:val="{template["primary"]}"/><w:sz w:val="20"/></w:rPr><w:pPr><w:spacing w:before="190" w:after="75"/><w:keepNext/><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="4" w:color="{template["light"]}"/></w:pBdr></w:pPr></w:style>'
      '<w:style w:type="paragraph" w:styleId="ResumeBullet"><w:name w:val="Resume Bullet"/><w:basedOn w:val="Normal"/></w:style>'
      '</w:styles>'
  )


def _word_numbering():
  return (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
      '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="-"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="420" w:hanging="220"/></w:pPr></w:lvl></w:abstractNum>'
      '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
      '</w:numbering>'
  )


def build_resume_docx(draft, template_key="modern", photo_bytes=None):
  """Build a clean Word resume with a modern header and consistent hierarchy."""
  template = RESUME_TEMPLATES[normalize_resume_template(template_key)]
  body = [_word_header(draft, template, photo_bytes)]
  body.append(_word_paragraph("", size=10, after=20))

  for field in ("summary", "experience", "projects", "skills", "education", "certifications", "achievements"):
    value = str(draft.get(field, "") or "").strip()
    if not value:
      continue
    body.append(_word_paragraph(SECTION_LABELS[field].upper(), bold=True, size=20, color=template["primary"], style="ResumeHeading", before=170, after=75, keep_next=True))
    for item_type, text in _content_items(field, value):
      if text:
        body.append(_word_body_item(item_type, text, template))

  document_xml = (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
      '<w:body>'
      + "".join(body)
      + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="720" w:right="900" w:bottom="720" w:left="900"/></w:sectPr>'
      '</w:body></w:document>'
  )
  image_content_type = (
      '<Default Extension="jpg" ContentType="image/jpeg"/>'
      if photo_bytes
      else ""
  )
  content_types = (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      + image_content_type
      + '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      + '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
      + '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
      '</Types>'
  )
  package_rels = (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
      '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
      '</Relationships>'
  )
  document_rels = (
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
      '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
      '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
      + (
          '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/profile-photo.jpg"/>'
          if photo_bytes
          else ""
      )
      + '</Relationships>'
  )

  output = BytesIO()
  with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    archive.writestr("[Content_Types].xml", content_types)
    archive.writestr("_rels/.rels", package_rels)
    archive.writestr("word/document.xml", document_xml)
    archive.writestr("word/styles.xml", _word_styles(template))
    archive.writestr("word/numbering.xml", _word_numbering())
    archive.writestr("word/_rels/document.xml.rels", document_rels)
    if photo_bytes:
      archive.writestr("word/media/profile-photo.jpg", photo_bytes)
  return output.getvalue()
