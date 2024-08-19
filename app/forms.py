from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import CharField

from app.models import Profile, User, Question, Tag, Answer
from django.contrib.auth.hashers import make_password


class LoginForm(forms.Form):
    # добавить CSS класс для label, если возможно и отредачить шаблон
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login'}))
    password = forms.CharField(max_length=100,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class RegisterForm(forms.ModelForm):
    password_confirm = forms.CharField(max_length=100, label="Подтверждение пароля",
                                       widget=forms.PasswordInput(
                                           attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    avatar = forms.ImageField(required=False, label="Аватар",
                              widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            "username": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login'}),
            "email": forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            "password": forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }
        labels = {
            "username": "Логин",
            "email": "Эл. почта",
            "password": "Пароль",
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        username.strip()
        has_user = User.objects.filter(username=username).exists()
        if has_user:
            raise ValidationError("User with such username already exists!")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        email.strip()
        has_user = User.objects.filter(email=email).exists()
        if has_user:
            raise ValidationError("This email already used!")
        return email

    def clean_password_confirm(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            self.add_error("password_confirm", "Passwords doesn't match!")

    def save(self, commit=True):  # Возможно стоит убрать параметр по умолчанию
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
        # возможно надо не использовать ModelManager для избежание потенциальных ошибок
        print(f"avatar: {self.cleaned_data['avatar']}")
        Profile.objects.create(user=user, avatar=self.cleaned_data['avatar'])

        return user


class EditProfileForm(RegisterForm):
    old_password = forms.CharField(max_length=100, label="Текущий пароль (подтверждение действий)",
                                   widget=forms.PasswordInput(
                                       attrs={'class': 'form-control', 'placeholder': 'Current password'}))

    def __init__(self, current_session_user, *args, **kwargs):
        self.current_session_user = current_session_user
        super(EditProfileForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        username.strip()

        print(username == self.current_session_user.username)
        if username != self.current_session_user.username:
            username = super().clean_username()

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        email.strip()

        if email != self.current_session_user.email:
            email = super().clean_email()

        return email

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']

        if not self.current_session_user.check_password(old_password):
            raise ValidationError("Incorrect password!")

        return old_password

    def save(self, commit=True):
        user = User.objects.get(pk=self.current_session_user.id)
        new_username = self.cleaned_data['username']
        if new_username != user.username:
            print("!= in save new_username")
            user.username = new_username

        new_email = self.cleaned_data['email']
        if new_email != "" and new_email != user.email:
            user.email = new_email

        if self.cleaned_data['old_password'] != self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])

        new_avatar = self.cleaned_data['avatar']
        if new_avatar != "" and new_avatar != user.profile.avatar:
            user.profile.avatar = new_avatar

        if commit:
            user.save()

        return user


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(required=False, max_length=128,
                           widget=forms.TextInput(attrs={'class': 'form-control col'}), label='Теги')

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control col'}),
            'text': forms.Textarea(attrs={'class': 'form-control col', 'rows': 5})
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def __get_or_create_tags(self):
        tags_list = self.cleaned_data['tags'].split()
        tags = []

        for tag in tags_list:
            tag_object, created = Tag.objects.get_or_create(name=tag)  # возврващает кортеж (объект, создан_ли)
            tags.append(tag_object)

        return tags

    def clean_title(self):
        return self.cleaned_data['title'].strip()

    def clean_text(self):
        return self.cleaned_data['text'].strip()

    def save(self, commit=True):
        question = super().save(commit=False)

        question.author = self.user.profile
        question.answer_count = 0
        question.title = self.cleaned_data['title']
        question.text = self.cleaned_data['text']

        if commit:
            tags = self.__get_or_create_tags()
            question.save()
            question.tag.set(tags)

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control col',
                'rows': 3,
                'placeholder': 'Enter your comment here'})
        }

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_text(self):
        return self.cleaned_data['text'].strip()

    def save(self, commit=True):
        answer = super().save(commit=False)

        answer.question = self.question
        answer.author = self.user.profile
        answer.text = self.cleaned_data['text']

        if commit:
            answer.save()

        return answer
