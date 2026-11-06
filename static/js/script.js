console.log("CareerPilot AI Loaded Successfully");

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("select[data-selected-value]").forEach((select) => {
        if (select.dataset.selectedValue) {
            select.value = select.dataset.selectedValue;
        }
    });

    const answerField = document.querySelector("[data-interview-answer]");
    const wordCount = document.querySelector("#answer-word-count");
    const guidance = document.querySelector("#answer-guidance");
    const characterCount = document.querySelector("#answer-character-count");
    const interviewForm = document.querySelector("[data-interview-form]");
    const submitButton = document.querySelector("[data-interview-submit]");

    if (!answerField || !wordCount || !guidance) {
        return;
    }

    const maxCharacters = Number(answerField.dataset.answerMax) || 5000;
    const updateAnswerGuidance = () => {
        const value = answerField.value.trim();
        const words = value
            ? value.split(/\s+/).length
            : 0;

        wordCount.textContent = `${words} word${words === 1 ? "" : "s"}`;
        if (characterCount) {
            characterCount.textContent = `${answerField.value.length.toLocaleString()}/${maxCharacters.toLocaleString()}`;
        }

        if (words >= 75) {
            wordCount.className = "small text-success fw-semibold";
            guidance.textContent = "Well developed. Check that every detail answers the question and ends with a concrete result or lesson.";
        } else if (words >= 35) {
            wordCount.className = "small text-primary fw-semibold";
            guidance.textContent = "Good start. Add one specific action, example, or result to make the answer convincing.";
        } else {
            wordCount.className = "small text-muted";
            guidance.textContent = "Build the answer: make your main point, explain your reasoning, then add truthful evidence.";
        }
    };

    answerField.addEventListener("input", updateAnswerGuidance);
    updateAnswerGuidance();

    if (interviewForm && submitButton) {
        interviewForm.addEventListener("submit", () => {
            if (!interviewForm.checkValidity()) {
                return;
            }
            submitButton.disabled = true;
            submitButton.textContent = "Reviewing answer…";
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const resumeInput = document.querySelector("[data-resume-file]");
    const resumeForm = document.querySelector("[data-resume-form]");
    const fileName = document.querySelector("#resume-file-name");
    const submitButton = document.querySelector("[data-resume-submit]");

    if (resumeInput && fileName) {
        resumeInput.addEventListener("change", () => {
            const selectedFile = resumeInput.files && resumeInput.files[0];
            const dropzone = resumeInput.previousElementSibling;

            if (!selectedFile) {
                fileName.textContent = "PDF only · maximum 16 MB · selectable text recommended";
                dropzone?.classList.remove("is-file-selected");
                return;
            }

            fileName.textContent = selectedFile.name;
            dropzone?.classList.add("is-file-selected");
        });
    }

    if (resumeForm && submitButton) {
        resumeForm.addEventListener("submit", () => {
            if (!resumeForm.checkValidity()) {
                return;
            }
            submitButton.disabled = true;
            submitButton.querySelector("span").textContent = "Analyzing your resume…";
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const roadmapForm = document.querySelector("[data-roadmap-form]");
    const roadmapSubmit = document.querySelector("[data-roadmap-submit]");

    if (!roadmapForm || !roadmapSubmit) {
        return;
    }

    roadmapForm.addEventListener("submit", () => {
        if (!roadmapForm.checkValidity()) {
            return;
        }
        roadmapSubmit.disabled = true;
        const buttonText = roadmapSubmit.querySelector("span");
        if (buttonText) {
            buttonText.textContent = "Creating roadmap…";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const coach = document.querySelector("[data-dashboard-coach]");
    const refreshButton = document.querySelector("[data-dashboard-refresh]");

    if (!coach || !refreshButton || !coach.dataset.aiUrl) {
        return;
    }

    const setList = (selector, items) => {
        const list = coach.querySelector(selector);
        if (!list) {
            return;
        }
        list.replaceChildren();
        (items || []).forEach((item) => {
            const entry = document.createElement("li");
            entry.textContent = item;
            list.append(entry);
        });
    };

    const setAction = (action) => {
        const title = coach.querySelector("[data-dashboard-action-title]");
        const body = coach.querySelector("[data-dashboard-action-body]");
        const link = coach.querySelector("[data-dashboard-action-link]");
        if (title) title.textContent = action.title || "Choose your next step";
        if (body) body.textContent = action.body || "Use one CareerPilot tool to keep preparing.";
        if (link) {
            link.href = action.url || "/dashboard";
            link.textContent = action.label || "Open CareerPilot";
        }
    };

    const setPlan = (items) => {
        const plan = coach.closest(".career-dashboard-page")
            ?.querySelector("[data-dashboard-plan]");
        if (!plan) {
            return;
        }
        plan.replaceChildren();
        (items || []).forEach((item, index) => {
            const entry = document.createElement("li");
            const number = document.createElement("span");
            const content = document.createElement("div");
            const title = document.createElement("h3");
            const detail = document.createElement("p");
            const link = document.createElement("a");

            number.className = "dashboard-plan-index";
            number.textContent = String(index + 1);
            title.className = "h6 mb-1";
            title.textContent = item.title || "Next step";
            detail.className = "mb-2";
            detail.textContent = item.detail || "Continue with a focused preparation activity.";
            link.href = item.url || "/dashboard";
            link.textContent = item.label || "Open CareerPilot";
            content.append(title, detail, link);
            entry.append(number, content);
            plan.append(entry);
        });
    };

    const showGuidance = (guidance) => {
        const headline = coach.querySelector("[data-dashboard-headline]");
        const summary = coach.querySelector("[data-dashboard-summary]");
        const badge = coach.querySelector("[data-dashboard-ai-badge]");

        if (headline) headline.textContent = guidance.headline || "Your next best career step";
        if (summary) summary.textContent = guidance.summary || "Use one focused action to keep your preparation moving.";
        if (badge) {
            badge.textContent = guidance.ai_assisted ? "AI personalised" : "Progress-based";
            badge.classList.toggle("dashboard-ai-badge-local", !guidance.ai_assisted);
        }
        setAction(guidance.next_action || {});
        setList("[data-dashboard-strengths]", guidance.strengths);
        setList("[data-dashboard-focus]", guidance.focus_areas);
        setPlan(guidance.weekly_plan);
    };

    refreshButton.addEventListener("click", async () => {
        const buttonText = refreshButton.querySelector("span");
        refreshButton.disabled = true;
        if (buttonText) buttonText.textContent = "Creating coaching…";

        try {
            const response = await fetch(coach.dataset.aiUrl, {
                method: "POST",
                headers: { "Accept": "application/json" },
            });
            if (!response.ok) {
                throw new Error("Dashboard coaching request failed");
            }
            const payload = await response.json();
            if (!payload.guidance) {
                throw new Error("Dashboard coaching response was incomplete");
            }
            showGuidance(payload.guidance);
        } catch (_error) {
            // Preserve the existing useful progress-based advice on a network error.
            if (buttonText) buttonText.textContent = "Try AI coaching again";
            refreshButton.disabled = false;
            return;
        }

        if (buttonText) buttonText.textContent = "Refresh AI coaching";
        refreshButton.disabled = false;
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.querySelector("[data-chat-form]");
    const chatInput = document.querySelector("[data-chat-input]");
    const chatSubmit = document.querySelector("[data-chat-submit]");
    const characterCount = document.querySelector("#chat-character-count");

    if (!chatForm || !chatInput) {
        return;
    }

    const updateCharacterCount = () => {
        if (characterCount) {
            characterCount.textContent = `${chatInput.value.length.toLocaleString()}/800`;
        }
    };

    document.querySelectorAll("[data-chat-prompt]").forEach((prompt) => {
        prompt.addEventListener("click", () => {
            chatInput.value = prompt.dataset.chatPrompt || "";
            updateCharacterCount();
            chatInput.focus();
        });
    });

    chatInput.addEventListener("input", updateCharacterCount);
    updateCharacterCount();

    chatForm.addEventListener("submit", () => {
        if (!chatForm.checkValidity() || !chatSubmit) {
            return;
        }
        chatSubmit.disabled = true;
        const label = chatSubmit.querySelector("span");
        if (label) {
            label.textContent = "Building your guidance…";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("[data-login-form]");
    const passwordToggle = loginForm?.querySelector("[data-password-toggle]");
    const passwordField = passwordToggle
        ? document.getElementById(passwordToggle.getAttribute("aria-controls"))
        : loginForm?.querySelector('input[type="password"]');
    const loginSubmit = loginForm?.querySelector("[data-login-submit]");

    if (!loginForm || !passwordField) {
        return;
    }

    if (passwordToggle) {
        passwordToggle.addEventListener("click", () => {
            const isHidden = passwordField.type === "password";
            passwordField.type = isHidden ? "text" : "password";
            passwordToggle.textContent = isHidden ? "Hide" : "Show";
            passwordToggle.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
        });
    }

    loginForm.addEventListener("submit", () => {
        if (!loginForm.checkValidity() || !loginSubmit) {
            return;
        }
        loginSubmit.disabled = true;
        const label = loginSubmit.querySelector("span");
        if (label) {
            label.textContent = "Signing you in…";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.querySelector("[data-register-form]");
    const passwordField = document.querySelector("[data-register-password]");
    const passwordConfirmation = document.querySelector("[data-register-password-confirm]");
    const passwordGuidance = document.querySelector("[data-password-guidance]");
    const passwordMatch = document.querySelector("[data-password-match]");
    const registerSubmit = document.querySelector("[data-register-submit]");

    if (!registerForm || !passwordField || !passwordConfirmation) {
        return;
    }

    const updatePasswordFeedback = () => {
        const password = passwordField.value;
        const confirmation = passwordConfirmation.value;
        const score = [
            password.length >= 4,
            /[a-z]/.test(password) && /[A-Z]/.test(password),
            /\d/.test(password),
            /[^A-Za-z0-9]/.test(password),
        ].filter(Boolean).length;
        const meter = registerForm.querySelector(".auth-password-meter");

        if (meter) {
            meter.dataset.strength = String(score);
        }
        if (passwordGuidance) {
            passwordGuidance.textContent = password.length === 0
                ? "Use 4+ characters with a mix of letters, numbers, and symbols."
                : score <= 1
                    ? "Add uppercase letters, numbers, or symbols to strengthen your password."
                    : score <= 3
                        ? "Good start. Add another character type for a stronger password."
                        : "Strong password pattern.";
        }

        const hasConfirmation = confirmation.length > 0;
        const matches = password === confirmation;
        passwordConfirmation.setCustomValidity(hasConfirmation && !matches ? "Passwords do not match." : "");
        if (passwordMatch) {
            passwordMatch.textContent = hasConfirmation
                ? matches ? "Passwords match." : "Passwords do not match."
                : "";
            passwordMatch.classList.toggle("is-match", hasConfirmation && matches);
            passwordMatch.classList.toggle("is-mismatch", hasConfirmation && !matches);
        }
    };

    document.querySelectorAll("[data-register-password-toggle]").forEach((toggle) => {
        toggle.addEventListener("click", () => {
            const target = document.querySelector(`#${toggle.dataset.passwordTarget}`);
            if (!target) {
                return;
            }
            const isHidden = target.type === "password";
            target.type = isHidden ? "text" : "password";
            toggle.textContent = isHidden ? "Hide" : "Show";
            toggle.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
        });
    });

    passwordField.addEventListener("input", updatePasswordFeedback);
    passwordConfirmation.addEventListener("input", updatePasswordFeedback);
    updatePasswordFeedback();

    registerForm.addEventListener("submit", () => {
        updatePasswordFeedback();
        if (!registerForm.checkValidity() || !registerSubmit) {
            return;
        }
        registerSubmit.disabled = true;
        const label = registerSubmit.querySelector("span");
        if (label) {
            label.textContent = "Creating your account…";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const profileForm = document.querySelector("[data-profile-form]");
    const photoInput = document.querySelector("[data-profile-photo-input]");
    const photoStatus = document.querySelector("#profile-photo-file-name");
    const profileSubmit = document.querySelector("[data-profile-submit]");

    if (!profileForm) {
        return;
    }

    let preview = document.querySelector("[data-profile-photo-preview]");
    let previewUrl = null;

    if (photoInput) {
        photoInput.addEventListener("change", () => {
            const selectedFile = photoInput.files && photoInput.files[0];
            photoInput.setCustomValidity("");

            if (!selectedFile) {
                if (photoStatus) {
                    photoStatus.textContent = "No new file selected";
                    photoStatus.classList.remove("is-error");
                }
                return;
            }

            const validTypes = ["image/jpeg", "image/png"];
            const isSupportedType = validTypes.includes(selectedFile.type);
            const isWithinLimit = selectedFile.size <= 5 * 1024 * 1024;
            if (!isSupportedType || !isWithinLimit) {
                const message = !isSupportedType
                    ? "Choose a JPG or PNG image."
                    : "Choose an image smaller than 5 MB.";
                photoInput.setCustomValidity(message);
                if (photoStatus) {
                    photoStatus.textContent = message;
                    photoStatus.classList.add("is-error");
                }
                return;
            }

            if (photoStatus) {
                photoStatus.textContent = `${selectedFile.name} selected`;
                photoStatus.classList.remove("is-error");
            }

            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
            previewUrl = URL.createObjectURL(selectedFile);
            const imagePreview = document.createElement("img");
            imagePreview.src = previewUrl;
            imagePreview.alt = "Selected profile photo preview";
            imagePreview.className = "profile-avatar";
            imagePreview.dataset.profilePhotoPreview = "";

            if (preview) {
                preview.replaceWith(imagePreview);
            }
            preview = imagePreview;
        });
    }

    profileForm.addEventListener("submit", () => {
        if (!profileForm.checkValidity() || !profileSubmit) {
            return;
        }
        profileSubmit.disabled = true;
        const label = profileSubmit.querySelector("span");
        if (label) {
            label.textContent = "Saving profile…";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    let resumePhotoData = "";
    const photoInput = document.querySelector("[data-resume-photo-input]");
    const photoPreview = document.querySelector("[data-resume-photo-preview]");
    const photoPreviewWrap = document.querySelector("[data-resume-photo-preview-wrap]");
    const photoRemoveButton = document.querySelector("[data-remove-resume-photo]");
    const photoStatus = document.querySelector("[data-resume-photo-status]");

    photoInput?.addEventListener("change", () => {
        const file = photoInput.files?.[0];
        if (!file) {
            return;
        }
        if (!["image/jpeg", "image/png"].includes(file.type)) {
            photoInput.value = "";
            if (photoStatus) photoStatus.textContent = "Choose a JPG or PNG image.";
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            photoInput.value = "";
            if (photoStatus) photoStatus.textContent = "Choose an image smaller than 5 MB.";
            return;
        }

        const reader = new FileReader();
        reader.addEventListener("load", () => {
            const image = new Image();
            image.addEventListener("load", () => {
                const size = 480;
                const scale = Math.max(size / image.naturalWidth, size / image.naturalHeight);
                const canvas = document.createElement("canvas");
                canvas.width = size;
                canvas.height = size;
                const context = canvas.getContext("2d");
                const width = image.naturalWidth * scale;
                const height = image.naturalHeight * scale;
                context.drawImage(image, (size - width) / 2, (size - height) / 2, width, height);
                resumePhotoData = canvas.toDataURL("image/jpeg", 0.88);
                if (photoPreview) photoPreview.src = resumePhotoData;
                if (photoPreviewWrap) photoPreviewWrap.hidden = false;
                if (photoRemoveButton) photoRemoveButton.hidden = false;
                if (photoStatus) photoStatus.textContent = "Photo added to the resume header.";
            });
            image.addEventListener("error", () => {
                photoInput.value = "";
                if (photoStatus) photoStatus.textContent = "The selected image could not be read.";
            });
            image.src = reader.result;
        });
        reader.readAsDataURL(file);
    });

    photoRemoveButton?.addEventListener("click", () => {
        resumePhotoData = "";
        if (photoInput) photoInput.value = "";
        if (photoPreview) photoPreview.src = "";
        if (photoPreviewWrap) photoPreviewWrap.hidden = true;
        photoRemoveButton.hidden = true;
        if (photoStatus) photoStatus.textContent = "Photo removed from the resume.";
    });

    document.querySelectorAll("[data-copy-target]").forEach((button) => {
        button.addEventListener("click", async () => {
            const target = document.getElementById(button.dataset.copyTarget);
            if (!target) {
                return;
            }

            const text = "value" in target ? target.value : target.textContent;
            try {
                await navigator.clipboard.writeText(text);
            } catch (error) {
                target.focus();
                target.select?.();
                document.execCommand("copy");
            }

            const originalLabel = button.textContent;
            button.textContent = "Copied";
            window.setTimeout(() => {
                button.textContent = originalLabel;
            }, 1400);
        });
    });

    document.querySelectorAll("[data-remove-target]").forEach((button) => {
        button.addEventListener("click", () => {
            const card = document.getElementById(button.dataset.removeTarget);
            const preview = document.querySelector(
                `[data-resume-preview-section="${button.dataset.removePreview}"]`,
            );
            card?.remove();
            preview?.remove();
        });
    });

    document.querySelectorAll("[data-download-resume]").forEach((button) => {
        button.addEventListener("click", async () => {
            const status = document.querySelector("[data-resume-download-status]");
            const draft = {};
            document.querySelectorAll("[data-resume-field]").forEach((field) => {
                draft[field.dataset.resumeField] = field.value;
            });
            const template = document.querySelector("[data-resume-template]:checked")?.value || "modern";

            const originalLabel = button.textContent;
            button.disabled = true;
            button.textContent = "Generating...";
            if (status) {
                status.textContent = "Preparing your edited resume...";
                status.classList.remove("is-error");
            }

            try {
                const response = await fetch(button.dataset.downloadUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ draft, template, photo: resumePhotoData || null }),
                });
                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.error || "The resume file could not be generated.");
                }

                const blob = await response.blob();
                const downloadUrl = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = downloadUrl;
                link.download = button.dataset.downloadResume === "pdf"
                    ? "CareerPilot_Resume.pdf"
                    : "CareerPilot_Resume.docx";
                document.body.appendChild(link);
                link.click();
                link.remove();
                URL.revokeObjectURL(downloadUrl);
                if (status) {
                    status.textContent = "Your file is ready and downloading.";
                }
            } catch (error) {
                if (status) {
                    status.textContent = error.message;
                    status.classList.add("is-error");
                }
            } finally {
                button.disabled = false;
                button.textContent = originalLabel;
            }
        });
    });

});
