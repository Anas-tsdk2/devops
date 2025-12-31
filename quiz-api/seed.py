import question_dao
from question import Question, Reponse

print("Checking database...")
# Initialisation des tables si nécessaire
question_dao.ensure_db()

if question_dao.count_questions() > 0:
    print("Database already contains questions. Skipping seed.")
    exit(0)

print("Seeding database with 1 test question...")
# Si on veut forcer le reset, on pourrait appeler rebuild_db() ici
# question_dao.rebuild_db()

q = Question(
    title="Question de test",
    text="Est-ce que l'image Docker contient cette question ?",
    image="https://www.docker.com/wp-content/uploads/2022/03/vertical-logo-monochromatic.png",
    position=1
)
q_id = question_dao.insert_question(q)

answers = [
    {"text": "Oui", "isCorrect": True},
    {"text": "Non", "isCorrect": False},
    {"text": "Peut-être", "isCorrect": False},
    {"text": "Je ne sais pas", "isCorrect": False}
]

for i, ans_data in enumerate(answers, 1):
    ans = Reponse(
        question_id=q_id,
        answer_index=i,
        text=ans_data["text"],
        isCorrect=ans_data["isCorrect"]
    )
    question_dao.insert_answer(ans)

print("Database seeded successfully.")
