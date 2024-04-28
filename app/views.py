import django.core.paginator
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.shortcuts import render

from app.models import Profile, Like, Tag, Question, Answer

# Create your views here.

POPULAR = {
    "tags": [f"tag{i + 1}" for i in range(5)],
    "users": [f"user{i + 1}" for i in range(5)]
}


def index(request):
    questions = Question.objects.get_new().all()
    page_obj = paginator(request, questions)
    context = {
        "content_title": "New Questions",
        "questions": page_obj,
        "popular": POPULAR
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

    context = {
        "content_title": "Question",
        "question": post,
        "answers": paginator(request, answers),
        "popular": POPULAR
    }
    return render(request, "question.html", context)


def ask(request):
    return render(request, "ask.html", {"content_title": "Ask", "popular": POPULAR})


def register(request):
    return render(request, "register.html", {"content_title": "Registration", "popular": POPULAR})


def login(request):
    return render(request, 'login.html', {"content_title": "Login", "popular": POPULAR})


def settings(request):
    context = {
        "content_title": "Settings",
        "settings": {
            "current_login": "Dr. Pepper",
            "current_email": "example@mail.com"
        },
        "popular": POPULAR
    }
    return render(request, 'settings.html', context)


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
