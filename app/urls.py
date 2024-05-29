from django.urls import path
from app import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
    path('question/<int:question_id>', views.question, name='question'),
    path('ask', views.ask, name='ask'),
    path('signup', views.register, name='register'),
    path('login', views.log_in, name='login'),
    path('profile/edit', views.settings, name='settings'),
    path('logout', views.logout, name='logout')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
