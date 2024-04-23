from django.db import models
from django.contrib.auth.models import User


class ProfileManager(models.Manager):
    def get_avatar(self):
        pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatar")

    objects = ProfileManager()


class Like(models.Model):
    count = models.IntegerField()


class Tag(models.Model):
    name = models.CharField(max_length=256)


class QuestionManager(models.Manager):
    def get_author(self, id):
        return self.get(pk=id)


class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like = models.ForeignKey(Like, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    title = models.CharField(max_length=256)
    text = models.TextField()

    objects = QuestionManager()

    def __str__(self):
        return self.title


class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "question"]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like = models.ManyToManyField(Like)
    text = models.TextField()


class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "answer"]
