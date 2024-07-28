import json

import django.core.paginator
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from app.forms import LoginForm, RegisterForm, EditProfileForm, QuestionForm, AnswerForm

# Create your views here.

POPULAR = {
    "tags": [f"tag{i + 1}" for i in range(5)],
    "users": [f"user{i + 1}" for i in range(5)]
}


def index(request):
    if request.user.is_authenticated:
        questions = Question.objects.get_new(user=request.user).all()
    else:
        questions = Question.objects.get_new().all()

    page_obj = paginator(request, questions)
    context = {
        "content_title": "New Questions",
        "questions": page_obj,
        "popular":
            {
                "tags": Tag.objects.get_popular(),
                "users": POPULAR['users']
            }
    }
    return render(request, "index.html", context)


def hot(request):
    questions = Question.objects.get_hot().all()
    page_obj = paginator(request, questions)
    context = {
        "content_title": "Hot Questions",
        "questions": page_obj,
        "popular": POPULAR
    }
    return render(request, "hot.html", context)


def tag(request, tag_name):
    questions = Question.objects.get_by_tag(tag_name).all()
    page_obj = paginator(request, questions)
    context = {
        "content_title": f"Tag: {tag_name}",
        "questions": page_obj,
        "popular": POPULAR
    }
    return render(request, "tag.html", context)


def question(request, question_id):
    post = Question.objects.get_by_id(question_id)

    if post is None:
        return HttpResponseNotFound('<h1>404 Not found...</h1>')

    answers = Answer.objects.get_by_question(post)

    if request.method == 'POST':
        form = AnswerForm(request.POST, question=post, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('question', question_id=post.id)
    else:
        form = AnswerForm()

    context = {
        "content_title": "Question",
        "question": post,
        "answers": paginator(request, answers),
        "form": form,
        "popular": POPULAR
    }
    return render(request, "question.html", context)


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            return redirect('question', question_id=question.id)
    else:
        form = QuestionForm()

    return render(request, "ask.html", {"content_title": "Ask", "form": form, "popular": POPULAR})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))  # нужен ли reverse?
    else:
        form = RegisterForm()

    return render(request, "register.html", {"content_title": "Registration", "form": form, "popular": POPULAR})


def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('index')
            else:
                form.add_error(None, "Wrong login or password!")
    else:
        form = LoginForm()  # создаем пустую форму чтобы сбросить поля формы, либо по дефолту в обход if

    context = {
        "content_title": "Login",
        "form": form,
        "popular": POPULAR
    }
    return render(request, 'login.html', context)


def logout(request):
    next_page = request.META.get('HTTP_REFERER', None)
    auth.logout(request)

    if next_page:
        return redirect(next_page)

    return redirect(reverse('index'))


@login_required
def settings(request):
    if request.method == "POST":
        form = EditProfileForm(data=request.POST, current_session_user=request.user)  # править
        if form.is_valid():
            form.save()
    else:
        form = EditProfileForm(current_session_user=request.user)

    context = {
        "content_title": "Settings",
        "form": form,
        "popular": POPULAR
    }
    return render(request, 'settings.html', context)


@require_http_methods(['POST'])
@login_required(login_url="login")
def async_like(request):  # fat controller?
    body = json.loads(request.body)  # Got a json request from JS

    profile = Profile.objects.get(user=request.user)

    id = int(body['id'])  # may cause error, if id is not integer

    match body['type']:
        case "question":
            thing = Question.objects.get(pk=id)
            like, like_created = QuestionLike.objects.get_or_create(user=profile, question=thing)
            LIKE = QuestionLike.Mark.LIKE
            DISLIKE = QuestionLike.Mark.DISLIKE
        case "answer":
            thing = Answer.objects.get(pk=id)
            like, like_created = AnswerLike.objects.get_or_create(user=profile, answer=thing)
            LIKE = AnswerLike.Mark.LIKE
            DISLIKE = AnswerLike.Mark.DISLIKE
        case _:
            raise ValueError(f"Unknown value for 'type': should be 'question' or 'answer', got '{body['type']}'")

    match body['activity']:
        case "like":
            if like.value == LIKE:
                like.delete()
                body['status'] = 0
            else:  # like.value == DISLIKE or like_created
                like.value = LIKE
                like.save()
                body['status'] = 1
        case "dislike":
            if like.value == DISLIKE:
                like.delete()
                body['status'] = 0
            else:  # like.value == LIKE or like_created
                like.value = DISLIKE
                like.save()
                body['status'] = 1
        case _:
            raise ValueError(f"Unknown value for 'activity': should be 'like' or 'dislike', got '{body['activity']}'")

    body['like_count'] = thing.get_likes_count()

    return JsonResponse(body)


def paginator(request, objects_list, per_page_obj=5):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page_obj)
    try:
        page = paginator.page(page_num)
    except django.core.paginator.PageNotAnInteger:  # If not GET contains Integer
        page = paginator.page(1)
    except django.core.paginator.EmptyPage:  # If num of page not in a range
        page = paginator.page(paginator.num_pages)
    return page
