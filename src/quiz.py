import re
import os
from utils import write_settings
from chatgpt import ask


def update_settings(settings, key, value):
    try:
        value = int(value)
    except ValueError:
        return "The value is not an integer"
    if key == "time":
        if not (5 <= value <= 60):
            return "Time setting must be between 5 and 60 seconds."

    elif key == "difficulty":
        if not (1 <= value <= 10):
            return "Difficulty setting must be between 1 and 10."

    elif key == "choices":
        if not (2 <= value <= 7):
            return "Invalid choices setting. Must be between 2 and 7."

    else:
        return "Invalid setting. Use 'time', 'difficulty', or 'choices'."

    settings[key] = value
    write_settings(settings)
    return f"Settings have been updated. Set {key} to {value}."


def generate_quiz(settings, subject):
    subject = " ".join(subject)
    # im not sure if these are actually needed

    if (
        not (1 <= settings["difficulty"] <= 10)
        or not (5 <= settings["time"] <= 60)
        or not (2 <= settings["choices"] <= 7)
    ):
        return "Invalid settings."

    prompt = (
        f"A quiz consists of 3 sections: Question:, Choices:, and "
        f"Answer:. Each section should be separated by a new line. "
        f"The format of a quiz must be as follows: Question: What "
        f"is 2 + 2? Choices: A) 3 B) 4 C) 5 D) 6 Answer: B "
        f"Generate a quiz question on the subject of {subject} "
        f"with a difficulty level of {settings['difficulty']} on a scale of "
        f"1-10 where 1 is the easiest and 10 is the most difficult. "
        f"Provide {settings['choices']} answer choices."
    )

    api_key = os.getenv("API_KEY")
    response = ask(api_key, prompt)

    try:
        match = re.search(
            r"Question:\s*(.*?)\nChoices:\s*(.*?)\nAnswer:\s*(.*)",
            response,
            re.DOTALL,
        )
        if not match:
            return "Failed to generate a quiz question. Please try again."

        question = match.group(1).strip()
        answer_choices_text = match.group(2).replace("\n", " ").strip()
        correct_answer = match.group(3).strip()
        answer_choices = re.split(r" (?=[A-Z]\))", answer_choices_text)

    except Exception:
        return "Failed to generate a quiz question. Please try again."

    return {"question": question, "choices": answer_choices,
            "answer": correct_answer.split(") ")[0]}
