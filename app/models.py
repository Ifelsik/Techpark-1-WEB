from django.db import models
from django.contrib.auth.models import User
from datetime import date

from django.db.models import Sum, Count, Prefetch
from django.db.models.functions import Coalesce

AVATAR_PATH = "avatar/"  # MEDIA_ROOT/avatar


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(blank=True, upload_to=AVATAR_PATH)

    def __str__(self):
        return self.user.__str__()


class TagManager(models.Manager):
    def get_popular(self, count=5):
        return self.annotate(count=Count('question__tag')).order_by('-count')[:count]


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=256)

    objects = TagManager()

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def _form_vote_field(self, user):
        qs = self
        if user is not None and user.is_authenticated:
            qs = qs.prefetch_related(
                Prefetch(
                    'questionlike_set',
                    queryset=QuestionLike.objects.filter(user=user.profile),  # rename to author
                    to_attr='vote',
                )
            )
        return qs

    def get_new(self, user=None):
        """User parameter isn't necessary.
        If there is a user you will get field with current user's vote for every post"""

        return self._form_vote_field(user).order_by('-created')

    def get_hot(self, user=None):  # а что если > 1 млн записей?
        return self._form_vote_field(user).annotate(likes=Coalesce(Sum('questionlike__value'), 0)).order_by('-likes')

    def get_by_tag(self, tag_name, user=None):
        return self._form_vote_field(user).filter(tag__name=tag_name).order_by('-created')

    def get_by_id(self, question_id, user=None):
        try:
            return self._form_vote_field(user).get(pk=question_id)
        except Question.DoesNotExist:
            return None


class Question(models.Model):
    author = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField(Tag)
    title = models.CharField(max_length=256)
    text = models.TextField()

    objects = QuestionManager()

    def get_likes_count(self):
        # result of aggregate is a dict
        likes = QuestionLike.objects.filter(question=self).aggregate(Sum("value"))["value__sum"]
        return 0 if likes is None else likes

    def get_answers_count(self):
        return Answer.objects.filter(question=self).count()

    def get_short_text(self, max_length=256):
        if len(self.text) > max_length:
            return self.text[:max_length] + "..."
        return self.text

    def __str__(self):
        return f"(id: {self.id})-{self.title}"


class QuestionLike(models.Model):
    class Mark(models.IntegerChoices):
        LIKE = 1
        DISLIKE = -1

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Probably better change name user to author/profile
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=0, choices=Mark.choices)

    class Meta:
        unique_together = ["user", "question"]


class AnswerManager(models.Manager):
    def get_by_question(self, question, user=None):
        qs = self
        if user is not None and user.is_authenticated:
            qs = qs.prefetch_related(
                Prefetch(
                    'answerlike_set',
                    queryset=AnswerLike.objects.filter(user=user.profile),  # rename user to author/profile
                    to_attr='vote'
                )
            )
        return qs.filter(question=question).order_by("-created")


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    is_correct = models.BooleanField(null=True)

    objects = AnswerManager()

    def get_likes_count(self):
        # result of aggregate is a dict
        likes = AnswerLike.objects.filter(answer=self).aggregate(Sum("value"))["value__sum"]
        return 0 if likes is None else likes

    def get_correct_status(self):
        if self.is_correct is None or not self.is_correct:
            return False
        return True

    def __str__(self):
        return f"(id: {self.id})-{self.text[20:]}"


class AnswerLike(models.Model):
    class Mark(models.IntegerChoices):
        LIKE = 1
        DISLIKE = -1

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Probably better change name user to author/profile
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=0, choices=Mark.choices)

    class Meta:
        unique_together = ["user", "answer"]
