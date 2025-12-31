import psycopg2
import psycopg2.extras
from question import Question, Reponse
import time
import os
import json

# Connection parameters
DB_HOST = os.environ.get("POSTGRES_HOST", "database")
DB_NAME = os.environ.get("POSTGRES_DB", "quiz")
DB_USER = os.environ.get("POSTGRES_USER", "quiz-user")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "quiz-password")

def get_connection_with_retry(retries=10, delay=2):
    for _ in range(retries):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            return conn
        except psycopg2.OperationalError as e:
            print(f"Waiting for DB... {e}")
            time.sleep(delay)
    raise Exception("Could not connect to database")

# ---------- Helpers BD ----------
def rebuild_db():
    conn = get_connection_with_retry()
    cur = conn.cursor()
    # drop if exist
    cur.execute("DROP TABLE IF EXISTS Reponse;")
    cur.execute("DROP TABLE IF EXISTS Question CASCADE;")
    cur.execute("DROP TABLE IF EXISTS Participation;")
    
    # recreate
    cur.execute("""
    CREATE TABLE Question (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        image TEXT,
        position INTEGER NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE Reponse (
        id SERIAL PRIMARY KEY,
        question_id INTEGER NOT NULL,
        answer_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        isCorrect BOOLEAN NOT NULL,
        FOREIGN KEY (question_id) REFERENCES Question(id) ON DELETE CASCADE,
        UNIQUE (question_id, answer_index)
    );
    """)

    cur.execute("""
    CREATE TABLE Participation (
        id SERIAL PRIMARY KEY,
        playerName TEXT NOT NULL,
        score INTEGER NOT NULL,
        answers TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def ensure_db():
    conn = get_connection_with_retry()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM Question LIMIT 1;")
    except psycopg2.Error:
        conn.rollback()
        rebuild_db()
    finally:
        conn.close()

# ---------- Count ----------
def count_questions() -> int:
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as cnt FROM Question")
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0

# ---------- Insertion avec position ----------
def shift_positions_on_insert(position: int):
    conn = get_connection_with_retry()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Question SET position = position + 1 WHERE position >= %s", (position,))
    conn.commit()
    conn.close()

def insert_question(question: Question) -> int:
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        if question.position is None:
            cur.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 as next_pos FROM Question")
            question.position = cur.fetchone()["next_pos"]
        else:
            cur.execute(
                "UPDATE Question SET position = position + 1 WHERE position >= %s", (question.position,))
        
        cur.execute("""
            INSERT INTO Question (title, text, image, position)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (question.title, question.text, question.image, question.position))
        qid = cur.fetchone()['id']
        conn.commit()
        return qid
    except psycopg2.Error:
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_answer(answer: Reponse) -> int:
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        INSERT INTO Reponse (question_id, answer_index, text, isCorrect)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (answer.question_id, answer.answer_index, answer.text, bool(answer.isCorrect)))
    aid = cur.fetchone()['id']
    conn.commit()
    conn.close()
    return aid

# ---------- Get by id / position ----------
def get_question_by_id(question_id: int) -> Question:
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM Question WHERE id = %s", (question_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    q = Question(
        id=row["id"], title=row["title"], text=row["text"],
        image=row["image"], position=row["position"]
    )
    cur.execute("SELECT * FROM Reponse WHERE question_id = %s", (q.id,))
    answers = []
    for a in cur.fetchall():
        answers.append(Reponse(
            id=a["id"],
            question_id=a["question_id"],
            text=a["text"],
            isCorrect=bool(a["iscorrect"]), # Postgres lowercases column names in dict cursor usually? No, depends on creation.
            answer_index=a["answer_index"]
        ))
    q.answers = answers
    conn.close()
    return q

def get_question_by_position(position: int) -> Question:
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM Question WHERE position = %s", (position,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    q = Question(
        id=row["id"], title=row["title"], text=row["text"],
        image=row["image"], position=row["position"]
    )
    cur.execute("SELECT * FROM Reponse WHERE question_id = %s", (q.id,))
    answers = []
    for a in cur.fetchall():
        # Postgres lowercase sensitivity check: created as "isCorrect" but unquoted identifier -> lowercase "iscorrect"
        answers.append(Reponse(
            id=a["id"],
            question_id=a["question_id"],
            text=a["text"],
            isCorrect=bool(a["iscorrect"]), 
            answer_index=a["answer_index"]
        ))
    q.answers = answers
    conn.close()
    return q

def get_all_questions():
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM Question ORDER BY position ASC")
    questions = cur.fetchall()
    result = []
    for q in questions:
        q_id = q["id"]
        cur.execute("SELECT * FROM Reponse WHERE question_id = %s", (q_id,))
        reponses = cur.fetchall()
        question_data = {
            "id": q_id,
            "title": q["title"],
            "text": q["text"],
            "image": q["image"],
            "position": q["position"],
            "reponses": [dict(r) for r in reponses]
        }
        result.append(question_data)
    conn.close()
    return result

# ---------- Update fields & move logic ----------
def replace_answers_for_question(question_id: int, new_answers: list):
    conn = get_connection_with_retry()
    cur = conn.cursor()
    cur.execute("DELETE FROM Reponse WHERE question_id = %s", (question_id,))
    for idx, ans in enumerate(new_answers, start=1):
        cur.execute("""
                INSERT INTO Reponse (question_id, answer_index, text, isCorrect)
                VALUES (%s, %s, %s, %s)
                """, (question_id, idx, ans.text, bool(ans.isCorrect)))
    conn.commit()
    conn.close()

def update_question_fields(question: Question):
    conn = get_connection_with_retry()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Question
        SET title = %s, text = %s, image = %s, position = %s
        WHERE id = %s
    """, (question.title, question.text, question.image, question.position, question.id))
    conn.commit()
    conn.close()

def get_position_by_id(question_id: int):
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT position FROM Question WHERE id = %s", (question_id,))
    row = cur.fetchone()
    conn.close()
    return row["position"] if row else None

def move_question_by_id(question_id: int, new_position: int):
    old_position = get_position_by_id(question_id)
    if old_position is None:
        return
    move_question(question_id, new_position)

def move_question_by_position(old_position: int, new_position: int):
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id FROM Question WHERE position = %s", (old_position,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return
    question_id = row["id"]
    move_logic(old_position, new_position, question_id)

def move_logic(old_pos, new_pos, qid):
    conn = get_connection_with_retry()
    cur = conn.cursor()
    cur.execute("UPDATE Question SET position = -1 WHERE id = %s", (qid,))
    if new_pos < old_pos:
        cur.execute("""
            UPDATE Question
            SET position = position + 1
            WHERE position >= %s AND position < %s
        """, (new_pos, old_pos))
    else:
        cur.execute("""
            UPDATE Question
            SET position = position - 1
            WHERE position > %s AND position <= %s
        """, (old_pos, new_pos))
    cur.execute("UPDATE Question SET position = %s WHERE id = %s", (new_pos, qid))
    conn.commit()
    conn.close()
    
def move_question(question_id: int, new_position: int):
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT position FROM Question WHERE id = %s", (question_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Question id {question_id} not found")
    old_position = row["position"]
    cur.execute("SELECT COUNT(*) as count FROM Question")
    total = cur.fetchone()["count"]
    
    if new_position < 1:
        new_position = 1
    elif new_position > total:
        new_position = total
        
    if new_position == old_position:
        conn.close()
        return

    cur.execute("UPDATE Question SET position = 0 WHERE id = %s", (question_id,))

    if new_position < old_position:
        cur.execute("""
            UPDATE Question
            SET position = position + 1
            WHERE position >= %s AND position < %s
        """, (new_position, old_position))
    else:
        cur.execute("""
            UPDATE Question
            SET position = position - 1
            WHERE position <= %s AND position > %s
        """, (new_position, old_position))

    cur.execute("UPDATE Question SET position = %s WHERE id = %s",
            (new_position, question_id))

    conn.commit()
    conn.close()

# ---------- Delete logic ----------

def delete_question_and_shift(question_id: int):
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT position FROM Question WHERE id = %s", (question_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    pos = row["position"]
    cur.execute("DELETE FROM Question WHERE id = %s", (question_id,))
    cur.execute(
        "UPDATE Question SET position = position - 1 WHERE position > %s", (pos,))
    conn.commit()
    conn.close()

def delete_all_questions():
    conn = get_connection_with_retry()
    cur = conn.cursor()
    cur.execute("DELETE FROM Reponse")
    cur.execute("DELETE FROM Question")
    conn.commit()
    conn.close()

# ---------- Helpers ----------

def question_already_exist(id) -> bool:
    conn = get_connection_with_retry()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Question WHERE id = %s", (id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

# ---------- Update question ----------

def update_question(question: Question):
    update_question_fields(question)
    return question.id

# ---------- Verification answers ----------

def is_answer_correct(question_id: int, answer_index: int) -> bool:
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT isCorrect FROM Reponse
        WHERE question_id = %s AND answer_index = %s
    """, (question_id, answer_index))
    row = cur.fetchone()
    conn.close()
    # Postgres returns boolean natively
    return bool(row and row["iscorrect"])

# ---------- Participations ----------

def insert_participation(playerName: str, score: int, answers: list) -> int:
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("INSERT INTO Participation (playerName, score, answers) VALUES (%s, %s, %s) RETURNING id",
                (playerName, int(score), json.dumps(answers)))
    pid = cur.fetchone()['id']
    conn.commit()
    conn.close()
    return pid

def get_all_participations_sorted():
    conn = get_connection_with_retry()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT playerName, score FROM Participation ORDER BY score DESC, id ASC")
    rows = cur.fetchall()
    result = [{"playerName": r["playername"], "score": r["score"]}
                for r in rows]
    conn.close()
    return result

def delete_all_participations():
    conn = get_connection_with_retry()
    cur = conn.cursor()
    cur.execute("DELETE FROM Participation")
    conn.commit()
    conn.close()
