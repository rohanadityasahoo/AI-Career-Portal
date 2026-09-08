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

    if (!answerField || !wordCount || !guidance) {
        return;
    }

    const updateAnswerGuidance = () => {
        const words = answerField.value.trim()
            ? answerField.value.trim().split(/\s+/).length
            : 0;

        wordCount.textContent = `${words} word${words === 1 ? "" : "s"}`;

        if (words >= 50) {
            wordCount.className = "small text-success fw-semibold";
            guidance.textContent = "Great detail. Add a concrete result or example to make the answer memorable.";
        } else {
            wordCount.className = "small text-muted";
            guidance.textContent = "Tip: aim for at least 50 words when explaining a skill, decision, or experience.";
        }
    };

    answerField.addEventListener("input", updateAnswerGuidance);
    updateAnswerGuidance();
});
