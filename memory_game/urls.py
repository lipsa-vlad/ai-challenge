from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from . import views

urlpatterns = [
    path('', views.lobby, name='lobby'),
    path('game/<str:room_name>/', views.game_room, name='game_room'),
    path('api/rooms', views.list_rooms, name='list_rooms'),
    path('api/new-game', views.new_game, name='new_game'),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),
]
