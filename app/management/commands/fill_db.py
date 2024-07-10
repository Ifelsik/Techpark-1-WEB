from django.core.management.base import BaseCommand, CommandError
from app.models import Profile, Tag, Question, QuestionLike, Answer, AnswerLike, User

from random import randint
from django.contrib.auth.hashers import make_password

USERS = ["VladOS", "Vova", "Lev", "Tigr", "Aboba", "Voin228", "KillerQueen", "Borz06", "Arslan21"]
TAGS = ["Python", "Django", "Web", "Java", "JS", "TensorFlow", "NumPy", "PHP", "SQL"]
TITLES = ["What?", "How", "Vor", "auf", "stop", "сложна", "Vk", "Yandex"]
TEXTS = ["Amogus", "How to generate", "why so hard", "Aghhh...", "Comment :D", "Lolol", "You can just...",
         "писят два!!!",
         "Кто я?"]

DEFAULT_PASSWORD = "123"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('total', type=int)

    @staticmethod
    def create_profiles(count):
        users = [
            User(
                username=f"{USERS[i % len(USERS)]}{i}",
                password=make_password(DEFAULT_PASSWORD)
            ) for i in range(count)
        ]
        User.objects.bulk_create(users)

        profiles = [Profile(user=users[i]) for i in range(count)]
        Profile.objects.bulk_create(profiles)

    @staticmethod
    def create_tags(count):
        Tag.objects.bulk_create([Tag(name=f"{TAGS[i % len(TAGS)]} {i}") for i in range(count)])

    # @staticmethod
    # def create_likes(count):
    #     Like.objects.bulk_create([Like(count=randint(-20, 20)) for i in range(count)])

    @staticmethod
    def create_answer_likes(ratio):
        AnswerLike.objects.bulk_create(
            [
                AnswerLike(user_id=i % ratio + 1, answer_id=i % (100 * ratio) + 1, value=2 * (i % 2) - 1)
                for i in range(100 * ratio)
            ]
        )

    @staticmethod
    def create_question_likes(ratio):
        QuestionLike.objects.bulk_create(
            [
                QuestionLike(user_id=i % ratio + 1, question_id=i % (10 * ratio) + 1, value=2 * (i % 2) - 1)
                for i in range(10 * ratio)
            ]
        )

    def handle(self, *args, **options):
        ratio = int(options["total"])
        self.create_profiles(ratio)
        self.create_tags(ratio)
        # self.create_likes(200 * ratio)

        range_start = randint(0, ratio // 3)
        offset = 5 if ratio > 5 else ratio
        random_tags = Tag.objects.filter(id__gte=range_start).all()[:offset]

        for j in range(10):
            questions = Question.objects.bulk_create([
                Question(
                    author_id=(j * i) % ratio + 1,
                    title=TITLES[(j * i) % len(TITLES)],
                    text=TEXTS[(j * i) % len(TEXTS)],
                ) for i in range(ratio)
            ])

            through_model_instances = [
                Question.tag.through(question=question, tag=tag)
                for question, tag in zip(questions, random_tags)
            ]

            Question.tag.through.objects.bulk_create(through_model_instances)

        for j in range(100):
            Answer.objects.bulk_create([
                Answer(
                    question_id=((i + 1) * j) % (10 * ratio) + 1,
                    author_id=(j * i) % ratio + 1,
                    text=TEXTS[(j * i) % len(TEXTS)]
                ) for i in range(ratio)
            ])

        self.create_question_likes(ratio)
        self.create_answer_likes(ratio)

        print("OK!")
