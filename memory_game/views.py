from django.shortcuts import render
from django.http import JsonResponse
from app import get_cards
import redis
import json

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
    """API endpoint to list active game rooms from Redis"""
    try:
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        
        # Get all game keys from Redis
        game_keys = r.keys('game:*')
        rooms = []
        
        for key in game_keys:
            room_name = key.replace('game:', '')
            game_data_str = r.get(key)
            if game_data_str:
                game_data = json.loads(game_data_str)
                player_count = len(game_data.get('players', {}))
                rooms.append({
                    'name': room_name,
                    'players': player_count,
                    'started': game_data.get('started', False),
                    'theme': game_data.get('theme', 'emoji')
                })
        
        return JsonResponse({'rooms': rooms})
    except Exception as e:
        return JsonResponse({'rooms': [], 'error': str(e)})

def new_game(request):
    theme = request.GET.get('theme', 'emoji')
    cards = get_cards(theme)
    return JsonResponse({'cards': cards, 'theme': theme})
