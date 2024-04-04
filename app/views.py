from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
QUESTIONS = [
    {
        "id": i,
        "title": f"Question {i}",
        "image": "zoomer.png",
        "text": f"This is question number {i}",
        "tags": ["tag1", "tag2", "tag3", "tag4"],
    } for i in range(22)
]

POPULAR = {
    "tags": [f"tag{i+1}" for i in range(5)],
    "users": [f"user{i+1}" for i in range(5)]
}


def index(request):
    page = paginator(QUESTIONS, request)
    return render(request, "index.html", {"current": "New Questions",
                                          "other": "Hot Questions",
                                          "questions": page,
                                          "popular": POPULAR})


def hot(request):
    page = paginator(QUESTIONS[::-1], request)
    return render(request, "index.html", {"current": "Hot Questions",
                                          "other": "New Questions",
                                          "questions": page,
                                          "popular": POPULAR})


def tag(request, tag_name):
    page = paginator(QUESTIONS, request)
    return render(request, "tag.html", {"content_title": f"Tag: {tag_name}",
                                        "questions": page,
                                        "popular": POPULAR})


def question(request, question_id):
    return render(request, "question.html", {"content_title": "Question",
                                             "question": QUESTIONS[question_id],
                                             "popular": POPULAR})


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


def paginator(objects_list, request, per_page=5):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)
    return paginator.page(page_num)
