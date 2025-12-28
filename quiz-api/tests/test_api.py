import sys
import os
import pytest
import json

# Ajouter le dossier parent au PYTHONPATH AVANT l'import de app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

# ---------------- FIXTURES ----------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_header(mocker):
    # mock decode_token pour simuler un admin connecté
    mocker.patch("app.decode_token", return_value=True)
    return {"Authorization": "Bearer fake-token"}


# ---------------- ROUTES GENERALES ----------------

def test_hello_world(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.data.decode() == "Hello, world"


def test_login_success(client, mocker):
    mocker.patch("app.expected_hash", "5f4dcc3b5aa765d61d8327deb882cf99")  # md5("password")
    res = client.post("/login", json={"password": "password"})
    assert res.status_code == 200
    assert "token" in res.json


def test_login_fail(client):
    res = client.post("/login", json={"password": "wrong"})
    assert res.status_code == 401


def test_rebuild_db_unauthorized(client):
    res = client.post("/rebuild-db")
    assert res.status_code == 401


def test_rebuild_db_authorized(client, auth_header, mocker):
    mocker.patch("question_dao.rebuild_db")
    res = client.post("/rebuild-db", headers=auth_header)
    assert res.status_code == 200


# ---------------- QUIZ INFO ----------------

def test_quiz_info(client, mocker):
    mocker.patch("question_dao.count_questions", return_value=2)
    mocker.patch(
        "question_dao.get_all_participations_sorted",
        return_value=[{"playerName": "Alice", "score": 2}],
    )

    res = client.get("/quiz-info")
    assert res.status_code == 200
    assert res.json["size"] == 2
    assert res.json["scores"][0]["playerName"] == "Alice"


# ---------------- QUESTIONS ----------------

def test_get_all_questions(client, mocker):
    mocker.patch("question_dao.get_all_questions", return_value=[])
    res = client.get("/questions")
    assert res.status_code == 204


def test_get_question_by_position_not_found(client, mocker):
    mocker.patch("question_dao.get_question_by_position", return_value=None)
    res = client.get("/questions?position=1")
    assert res.status_code == 404


def test_post_question_unauthorized(client):
    res = client.post("/questions", json={})
    assert res.status_code == 401


def test_post_question_authorized(client, auth_header, mocker):
    mocker.patch("question_dao.insert_question", return_value=1)
    mocker.patch("question_dao.insert_answer", return_value=1)

    payload = {
        "title": "Question test",
        "position": 1,
        "possibleAnswers": [
            {"text": "A", "isCorrect": True},
            {"text": "B", "isCorrect": False},
        ],
    }

    res = client.post("/questions", json=payload, headers=auth_header)
    assert res.status_code == 200
    assert res.json["title"] == "Question test"


def test_delete_all_questions_unauthorized(client):
    res = client.delete("/questions/all")
    assert res.status_code == 401


def test_delete_all_questions_authorized(client, auth_header, mocker):
    mocker.patch("question_dao.delete_all_questions")
    res = client.delete("/questions/all", headers=auth_header)
    assert res.status_code == 204


def test_get_question_by_id_not_found(client, mocker):
    mocker.patch("question_dao.get_question_by_id", return_value=None)
    res = client.get("/questions/1")
    assert res.status_code == 404


# ---------------- PARTICIPATIONS ----------------

def test_post_participation_missing_fields(client):
    res = client.post("/participations", json={})
    assert res.status_code == 400


def test_post_participation_bad_answers_type(client):
    res = client.post(
        "/participations",
        json={"playerName": "Bob", "answers": "not-a-list"},
    )
    assert res.status_code == 400


def test_post_participation_success(client, mocker):
    mocker.patch(
        "question_dao.get_all_questions",
        return_value=[{"id": 1}, {"id": 2}],
    )
    mocker.patch("question_dao.is_answer_correct", side_effect=[True, False])
    mocker.patch("question_dao.insert_participation", return_value=1)

    payload = {
        "playerName": "Bob",
        "answers": [1, 2],
    }

    res = client.post("/participations", json=payload)
    assert res.status_code == 200
    assert res.json["score"] == 1


def test_delete_participations_unauthorized(client):
    res = client.delete("/participations/all")
    assert res.status_code == 401


def test_delete_participations_authorized(client, auth_header, mocker):
    mocker.patch("question_dao.delete_all_participations")
    res = client.delete("/participations/all", headers=auth_header)
    assert res.status_code == 204
