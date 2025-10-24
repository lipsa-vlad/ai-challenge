from django.shortcuts import render
from django.http import JsonResponse
from app import get_cards
from memory_game.consumers import GameConsumer

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

def list_rooms(request):
    """API endpoint to list active game rooms"""
    rooms = []
    for room_name, game_data in GameConsumer.games.items():
        player_count = len([p for p in game_data['players'].values() if p['connected']])
        rooms.append({
            'name': room_name,
            'players': player_count,
            'started': game_data['started'],
            'theme': game_data['theme']
        })
    return JsonResponse({'rooms': rooms})

def new_game(request):
    theme = request.GET.get('theme', 'emoji')
    cards = get_cards(theme)
    return JsonResponse({'cards': cards, 'theme': theme})
