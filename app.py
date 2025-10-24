import random
import requests

THEMES = {
    'emoji': ['💩', '🤡', '🦄', '🍕', '🦖', '🧙', '👽', '🤖'],
    'animals': ['🦙', '🦥', '🦦', '🦨', '🦡', '🦘', '🦒', '🦔'],
    'food': ['🌮', '🍔', '🍟', '🍕', '🌭', '🧇', '🥓', '🍩'],
    'faces': ['🤪', '🥴', '😵', '🤯', '🥳', '🤠', '🤑', '😎'],
    'starwars': [],
    'pokemon': [],
    'chuck': []
}

CHUCK_JOKES_CACHE = []

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

def fetch_chuck_jokes():
    """Fetch Chuck Norris jokes from API"""
    global CHUCK_JOKES_CACHE
    try:
        jokes = []
        for _ in range(8):
            response = requests.get('https://api.chucknorris.io/jokes/random', timeout=3)
            if response.status_code == 200:
                joke = response.json()['value']
                jokes.append(joke[:80] + '...' if len(joke) > 80 else joke)
        if len(jokes) == 8:
            CHUCK_JOKES_CACHE = jokes
            return jokes
    except:
        pass
    
    # Fallback jokes if API fails
    return [
        "Chuck Norris counted to infinity. Twice.",
        "Chuck Norris can divide by zero.",
        "Chuck Norris can slam a revolving door.",
        "Chuck Norris can kill two stones with one bird.",
        "Chuck Norris can unscramble an egg.",
        "Chuck Norris can hear sign language.",
        "Chuck Norris can speak braille.",
        "Chuck Norris threw a grenade and killed 50 people. Then it exploded."
    ]

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
    elif theme == 'chuck':
        if not THEMES['chuck']:
            THEMES['chuck'] = fetch_chuck_jokes()
        items = THEMES['chuck']
    elif theme in THEMES:
        items = THEMES[theme]
    else:
        items = THEMES['emoji']
    
    cards = items * 2
    random.shuffle(cards)
    return cards
