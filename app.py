import json
import shutil
from atexit import register
from dataclasses import dataclass
from pathlib import Path
from random import randint
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from flask import Flask, render_template

if TYPE_CHECKING:
    from os import PathLike

type StrPath = str | PathLike[str]

app = Flask(__name__)


@dataclass
class Question:
    text: str
    answers: tuple[str, str, str, str]
    correct_answer_id: int


def prefix_image_src(html: str, relative_path: Path, dir: Path) -> str:
    if "<img" not in html:
        return html

    soup = BeautifulSoup(html, "lxml")

    for img in soup("img"):
        shutil.copy(f"{relative_path}/{img["src"]}", dir)
        final_path = f"/static/{str(dir.name)}/{Path(img["src"]).name}"

        img["src"] = final_path

    return soup.prettify()


def json_to_questions(path: StrPath, dir: Path) -> list[Question]:
    path = Path(path)
    questions_files = path.glob("**/questions.json")
    ret: list[Question] = []
    for questions_file in questions_files:
        with open(questions_file) as f:
            questions = json.load(f)
            for question in questions:
                ret.append(
                    Question(
                        prefix_image_src(
                            questions_file.parent.joinpath(
                                question["text_file"]
                            ).read_text(),
                            questions_file.parent,
                            dir,
                        ),
                        tuple(question["answers"]),
                        question["correct_answer_id"],
                    )
                )

    return ret


with TemporaryDirectory(dir="static", delete=False) as tmpdir:
    questions = json_to_questions("questions", Path(tmpdir))
    register(lambda: shutil.rmtree(tmpdir))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/question/<int:id>")
def get_question(id: int):
    if id >= len(questions):
        return f"<p>question {id} not found</p>"

    question = questions[id]

    return render_template(
        "question.html", question=question, enumerate=enumerate, id=id
    )


@app.get("/question/random")
def get_question_random():
    id = randint(0, len(questions) - 1)

    question = questions[id]

    return render_template(
        "question.html", question=question, enumerate=enumerate, id=id
    )


@app.get("/question/<int:question_id>/answer/<int:answer_id>")
def check_answer(question_id: int, answer_id: int):
    question = questions[question_id]
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
