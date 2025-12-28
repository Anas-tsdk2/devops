class Question:
    def __init__(self, id: int = None, title: str = "", text: str = "", image: str = "", position: int = None, answers=None):
        self.id = id
        self.title = title
        self.text = text
        self.image = image
        self.position = position
        self.answers = answers if answers is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "image": self.image,
            "position": self.position,
            "possibleAnswers": [a.to_dict() for a in self.answers]
        }

    @staticmethod
    def from_dict(data: dict):
        answers = []
        if "possibleAnswers" in data:
            for ans_data in data["possibleAnswers"]:
                answers.append(Reponse.from_dict(ans_data))
        return Question(
            title=data.get("title"),
            text=data.get("text"),
            image=data.get("image"),
            position=data.get("position"),
            answers=answers
        )

class Reponse:
    def __init__(self, id: int = None, question_id: int = None, text: str = "", isCorrect: bool = False, answer_index: int = None):
        self.id = id
        self.question_id = question_id
        self.text = text
        self.isCorrect = isCorrect
        self.answer_index = answer_index

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "index": self.answer_index,
            "isCorrect": bool(self.isCorrect)
        }

    @staticmethod
    def from_dict(data: dict, question_id: int = None):
        return Reponse(
            question_id=question_id,
            text=data.get("text"),
            isCorrect=data.get("isCorrect", False)
        )
