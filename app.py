import random
import requests

THEMES = {
    'emoji': ['💩', '🤡', '🦄', '🍕', '🦖', '🧙', '👽', '🤖'],
    'animals': ['🦙', '🦥', '🦦', '🦨', '🦡', '🦘', '🦒', '🦔'],
    'food': ['🌮', '🍔', '🍟', '🍕', '🌭', '🧇', '🥓', '🍩'],
    'faces': ['🤪', '🥴', '😵', '🤯', '🥳', '🤠', '🤑', '😎'],
    'starwars': [],
    'pokemon': []
}

def fetch_starwars_characters():
    """Fetch character names from SWAPI"""
    try:
        response = requests.get('https://swapi.dev/api/people/?page=1', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [char['name'] for char in data['results'][:8]]
    except:
        pass
    return ['Luke', 'Vader', 'Leia', 'Han', 'Yoda', 'Obi-Wan', 'R2-D2', 'C-3PO']

def fetch_pokemon():
    """Fetch Pokemon names from PokeAPI"""
    try:
        pokemon_ids = random.sample(range(1, 151), 8)
        names = []
        for pid in pokemon_ids:
            response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pid}', timeout=2)
            if response.status_code == 200:
                names.append(response.json()['name'].capitalize())
        return names if len(names) == 8 else None
    except:
        pass
    return ['Pikachu', 'Charizard', 'Bulbasaur', 'Squirtle', 'Jigglypuff', 'Meowth', 'Psyduck', 'Snorlax']

def get_cards(theme):
    """Get cards for the specified theme"""
    if theme == 'starwars':
        if not THEMES['starwars']:
            THEMES['starwars'] = fetch_starwars_characters()
        items = THEMES['starwars']
    elif theme == 'pokemon':
        if not THEMES['pokemon']:
            THEMES['pokemon'] = fetch_pokemon()
        items = THEMES['pokemon']
    elif theme in THEMES:
        items = THEMES[theme]
    else:
        items = THEMES['emoji']
    
    cards = items * 2
    random.shuffle(cards)
    return cards
