from django.shortcuts import render
from django.http import JsonResponse
from app import get_cards

def lobby(request):
    return render(request, 'lobby.html', {
        'base_path': '/copilot/memory-game/'
    })

def game_room(request, room_name):
    return render(request, 'game.html', {
        'room_name': room_name,
        'base_path': '/copilot/memory-game/',
        'ws_base_path': '/copilot/memory-game'
    })

def new_game(request):
    theme = request.GET.get('theme', 'emoji')
    cards = get_cards(theme)
    return JsonResponse({'cards': cards, 'theme': theme})
