import sqlite3
import json
from question import Question, Reponse
import time
import os

DB_PATH = os.environ.get("DATABASE_PATH", "instance/database.db")

# ---------- Connection ----------
def get_connection_with_retry(retries=5, delay=0.1):
    for _ in range(retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                time.sleep(delay)
            else:
                raise
    raise sqlite3.OperationalError("Database is locked after multiple retries")

# ---------- Helpers BD ----------
def rebuild_db():
    conn = get_connection_with_retry()
    c = conn.cursor()
    # drop if exist
    c.executescript("""
    DROP TABLE IF EXISTS Reponse;
    DROP TABLE IF EXISTS Participation;
    DROP TABLE IF EXISTS Question;
    """)
    # recreate
    c.executescript("""
    CREATE TABLE Question (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        image TEXT,
        position INTEGER NOT NULL
    );

    CREATE TABLE Reponse (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        answer_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        isCorrect BOOLEAN NOT NULL CHECK (isCorrect IN (0, 1)),
        FOREIGN KEY (question_id) REFERENCES Question(id) ON DELETE CASCADE
        UNIQUE (question_id, answer_index)
    );


    CREATE TABLE Participation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playerName TEXT NOT NULL,
        score INTEGER NOT NULL,
        answers TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def ensure_db():
    try:
        conn = get_connection_with_retry()
        conn.execute("SELECT 1 FROM Question LIMIT 1;")
        conn.close()
    except Exception:
        rebuild_db()

# ---------- Count ----------
def count_questions() -> int:
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM Question")
    row = c.fetchone()
    conn.close()
    return row["cnt"] if row else 0

# ---------- Insertion avec position ----------
def shift_positions_on_insert(position: int):
    conn = get_connection_with_retry()
    c = conn.cursor()
    # increment positions >= position
    c.execute(
        "UPDATE Question SET position = position + 1 WHERE position >= ?", (position,))
    conn.commit()
    conn.close()

def insert_question(question: Question) -> int:
    conn = get_connection_with_retry()
    c = conn.cursor()
    try:
        c.execute("BEGIN IMMEDIATE TRANSACTION")

        if question.position is None:
            c.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 as next_pos FROM Question")
            question.position = c.fetchone()["next_pos"]
        else:
            c.execute(
                "UPDATE Question SET position = position + 1 WHERE position >= ?", (question.position,))
        c.execute("""
            INSERT INTO Question (title, text, image, position)
            VALUES (?, ?, ?, ?)
        """, (question.title, question.text, question.image, question.position))
        qid = c.lastrowid
        conn.commit()
        return qid
    except sqlite3.IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_answer(answer: Reponse) -> int:
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("""
        INSERT INTO Reponse (question_id, answer_index, text, isCorrect)
        VALUES (?, ?, ?, ?)
    """, (answer.question_id, answer.answer_index, answer.text, int(bool(answer.isCorrect))))
    aid = c.lastrowid
    conn.commit()
    conn.close()
    return aid

# ---------- Get by id / position ----------
def get_question_by_id(question_id: int) -> Question:
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT * FROM Question WHERE id = ?", (question_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    q = Question(
        id=row["id"], title=row["title"], text=row["text"],
        image=row["image"], position=row["position"]
    )
    c.execute("SELECT * FROM Reponse WHERE question_id = ?", (q.id,))
    answers = []
    for a in c.fetchall():
        answers.append(Reponse(
            id=a["id"],
            question_id=a["question_id"],
            text=a["text"],
            isCorrect=bool(a["isCorrect"]),
            answer_index=a["answer_index"]
        ))
    q.answers = answers
    conn.close()
    return q

def get_question_by_position(position: int) -> Question:
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT * FROM Question WHERE position = ?", (position,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    q = Question(
        id=row["id"], title=row["title"], text=row["text"],
        image=row["image"], position=row["position"]
    )
    c.execute("SELECT * FROM Reponse WHERE question_id = ?", (q.id,))
    answers = []
    for a in c.fetchall():
        answers.append(Reponse(
            id=a["id"],
            question_id=a["question_id"],
            text=a["text"],
            isCorrect=bool(a["isCorrect"]),
            answer_index=a["answer_index"]
        ))
    q.answers = answers
    conn.close()
    return q

def get_all_questions():
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT * FROM Question ORDER BY position ASC")
    questions = c.fetchall()
    result = []
    for q in questions:
        q_id = q["id"]
        c.execute("SELECT * FROM Reponse WHERE question_id = ?", (q_id,))
        reponses = c.fetchall()
        question_data = {
            "id": q_id,
            "title": q["title"],
            "text": q["text"],
            "image": q["image"],
            "position": q["position"],
            "reponses": [dict(r) for r in reponses]
        }
        result.append(question_data)
        print("\n=== Questions et Réponses ===")
    for q in questions:
        print(f"Question {q['position']} - {q['title']}")
        c.execute("SELECT * FROM Reponse WHERE question_id = ? ORDER BY answer_index ASC", (q["id"],))
        reponses = c.fetchall()
        for r in reponses:
            print(f"  [{r['answer_index']}] {r['text']}  |  Correct: {bool(r['isCorrect'])}")
    print("=============================\n")
    conn.close()
    return result

# ---------- Update fields & move logic ----------
def replace_answers_for_question(question_id: int, new_answers: list):
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("DELETE FROM Reponse WHERE question_id = ?", (question_id,))
    for idx, ans in enumerate(new_answers, start=1):
        c.execute("""
                INSERT INTO Reponse (question_id, answer_index, text, isCorrect)
                VALUES (?, ?, ?, ?)
                """, (question_id, idx, ans.text, int(bool(ans.isCorrect))))
    conn.commit()
    conn.close()

def update_question_fields(question: Question):
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("""
        UPDATE Question
        SET title = ?, text = ?, image = ?, position = ?
        WHERE id = ?
    """, (question.title, question.text, question.image, question.position, question.id))
    conn.commit()
    conn.close()

def get_position_by_id(question_id: int):
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT position FROM Question WHERE id = ?", (question_id,))
    row = c.fetchone()
    conn.close()
    return row["position"] if row else None

def move_question_by_id(question_id: int, new_position: int):
    old_position = get_position_by_id(question_id)
    if old_position is None:
        return
    move_question(question_id, new_position)

def move_question_by_position(old_position: int, new_position: int):
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT id FROM Question WHERE position = ?", (old_position,))
    row = c.fetchone()
    conn.close()
    if not row:
        return
    question_id = row["id"]
    move_logic(old_position, new_position, question_id)

def move_logic(old_pos, new_pos, qid):
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("UPDATE Question SET position = -1 WHERE id = ?", (qid,))
    if new_pos < old_pos:
        c.execute("""
            UPDATE Question
            SET position = position + 1
            WHERE position >= ? AND position < ?
        """, (new_pos, old_pos))
    else:
        c.execute("""
            UPDATE Question
            SET position = position - 1
            WHERE position > ? AND position <= ?
        """, (old_pos, new_pos))
    c.execute("UPDATE Question SET position = ? WHERE id = ?", (new_pos, qid))
    conn.commit()
    conn.close()
    
def move_question(question_id: int, new_position: int):
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT position FROM Question WHERE id = ?", (question_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Question id {question_id} not found")
    old_position = row["position"]
    c.execute("SELECT COUNT(*) as count FROM Question")
    total = c.fetchone()["count"]
    
    if new_position < 1:
        new_position = 1
    elif new_position > total:
        new_position = total
        
    if new_position == old_position:
        conn.close()
        return

    c.execute("UPDATE Question SET position = 0 WHERE id = ?", (question_id,))

    if new_position < old_position:
        c.execute("""
            UPDATE Question
            SET position = position + 1
            WHERE position >= ? AND position < ?
        """, (new_position, old_position))
    else:
        c.execute("""
            UPDATE Question
            SET position = position - 1
            WHERE position <= ? AND position > ?
        """, (new_position, old_position))

    c.execute("UPDATE Question SET position = ? WHERE id = ?",
            (new_position, question_id))

    conn.commit()
    conn.close()

# ---------- Delete logic ----------

def delete_question_and_shift(question_id: int):
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT position FROM Question WHERE id = ?", (question_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    pos = row["position"]
    c.execute("DELETE FROM Question WHERE id = ?", (question_id,))
    c.execute(
        "UPDATE Question SET position = position - 1 WHERE position > ?", (pos,))
    conn.commit()
    conn.close()

def delete_all_questions():
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("DELETE FROM Reponse")
    c.execute("DELETE FROM Question")
    conn.commit()
    conn.close()

# ---------- Helpers ----------

def question_already_exist(id) -> bool:
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("SELECT 1 FROM Question WHERE id = ?", (id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# ---------- Update question ----------

def update_question(question: Question):
    update_question_fields(question)
    return question.id

# ---------- Verification answers ----------

def is_answer_correct(question_id: int, answer_index: int) -> bool:
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("""
        SELECT isCorrect FROM Reponse
        WHERE question_id = ? AND answer_index = ?
    """, (question_id, answer_index))
    row = c.fetchone()
    conn.close()
    return bool(row and row["isCorrect"])

# ---------- Participations ----------

def insert_participation(playerName: str, score: int, answers: list) -> int:
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("INSERT INTO Participation (playerName, score, answers) VALUES (?, ?, ?)",
                (playerName, int(score), json.dumps(answers)))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_all_participations_sorted():
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute(
        "SELECT playerName, score FROM Participation ORDER BY score DESC, id ASC")
    rows = c.fetchall()
    result = [{"playerName": r["playerName"], "score": r["score"]}
                for r in rows]
    conn.close()
    return result

def delete_all_participations():
    conn = get_connection_with_retry()
    c = conn.cursor()
    c.execute("DELETE FROM Participation")
    conn.commit()
    conn.close()