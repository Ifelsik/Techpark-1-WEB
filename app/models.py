from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="/avatar")


class Like(models.Model):
    count = models.IntegerField()


class Tag(models.Model):
    name = models.CharField(max_length=256)


class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like = models.ForeignKey(Like, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    title = models.CharField(max_length=256)
    text = models.CharField(max_length=10240)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like = models.ManyToManyField(Like)
    text = models.CharField(max_length=10240)

class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        pass
