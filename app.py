import json
from dataclasses import dataclass
from pathlib import Path
from random import randint

from flask import Flask, render_template

app = Flask(__name__)


@dataclass
class Question:
    text: str
    answers: tuple[str, str, str, str]
    correct_answer_id: int


def json_to_questions(path: Path) -> list[Question]:
    print(path)
    questions_files = path.glob("questions/**/questions.json")
    ret: list[Question] = []
    for questions_file in questions_files:
        with open(questions_file) as f:
            questions = json.load(f)
            for question in questions:
                ret.append(
                    Question(
                        questions_file.parent.joinpath(
                            question["text_file"]
                        ).read_text(),
                        tuple(question["answers"]),
                        question["correct_answer_id"],
                    )
                )

    return ret


QUESTIONS = json_to_questions(Path("."))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/question/<int:id>")
def get_question(id: int):
    if id >= len(QUESTIONS):
        return f"<p>question {id} not found</p>"

    question = QUESTIONS[id]

    return render_template(
        "question.html", question=question, enumerate=enumerate, id=id
    )


@app.get("/question/random")
def get_question_random():
    id = randint(0, len(QUESTIONS) - 1)

    question = QUESTIONS[id]

    return render_template(
        "question.html", question=question, enumerate=enumerate, id=id
    )


@app.get("/question/<int:question_id>/answer/<int:answer_id>")
def check_answer(question_id: int, answer_id: int):
    question = QUESTIONS[question_id]
    correct_answer_id = question.correct_answer_id
    is_correct = False

    if answer_id == correct_answer_id:
        is_correct = True

    return render_template(
        "light_up_answer.html",
        question=question,
        is_correct=is_correct,
        correct_answer_id=correct_answer_id,
        answer_id=answer_id,
        enumerate=enumerate,
    )
