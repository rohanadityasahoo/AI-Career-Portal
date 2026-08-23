def predict_placement(ats_score, skill_score, interview_score):

    final_score = (
        ats_score * 0.4 +
        skill_score * 0.3 +
        interview_score * 0.3
    )

    if final_score >= 80:
        return "High Chance", final_score

    elif final_score >= 60:
        return "Moderate Chance", final_score

    else:
        return "Low Chance", final_score