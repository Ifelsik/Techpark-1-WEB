from django.db import models
from django.contrib.auth.models import User
from datetime import date

AVATAR_PATH = "uploads/avatar" # settings.py

class ProfileManager(models.Manager):
    def create_user(self):
        pass

    def get_avatar(self):
        pass



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(blank=True, upload_to=AVATAR_PATH)

    objects = ProfileManager()

    def __str__(self):
        return self.user.__str__()


class Like(models.Model):
    count = models.IntegerField()

    def __str__(self):
        return f"{self.count} (id: {self.id})"


# class TagManager(models.Manager):
#     def get_questions(self, tag):
#         return self.filter(name=tag).all()


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=256)

    # objects = TagManager()
    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def get_new(self):
        return self.order_by('-created')

    def get_hot(self):
        return self.order_by('-like__count')

    def get_by_tag(self, tag_name):
        return self.filter(tag__name=tag_name)

    def get_by_id(self, question_id):
        try:
            return self.get(pk=question_id)
        except Question.DoesNotExist:
            return None


class Question(models.Model):
    author = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    like = models.ForeignKey(Like, on_delete=models.CASCADE)
    answer_count = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField(Tag)
    title = models.CharField(max_length=256)
    text = models.TextField()

    objects = QuestionManager()

    def __str__(self):
        return self.title


class QuestionLike(models.Model):
    class Mark(models.IntegerChoices):
        LIKE = 1
        NONE = 0
        DISLIKE = -1

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.IntegerField(choices=Mark)

    class Meta:
        unique_together = ["user", "question"]


class AnswerManager(models.Manager):
    def get_by_question(self, question):
        answers = self.filter(question=question)
        answers.order_by("-created")
        return answers


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like = models.ForeignKey(Like, on_delete=models.CASCADE)
    # like_count = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    objects = AnswerManager()

    def __str__(self):
       return self.text[:20]


class AnswerLike(models.Model):
    # class Mark(models.IntegerChoices):
    #     LIKE = 1
    #     NONE = 0
    #     DISLIKE = -1

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)

    class Meta:
        unique_together = ["user", "answer"]
