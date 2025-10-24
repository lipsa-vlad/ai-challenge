#!/usr/bin/env python3
"""
Test multiplayer functionality by simulating two players
"""
import asyncio
import websockets
import json
import sys

async def player_client(player_name, room_name, delay=0):
    """Simulate a player connecting to a game room"""
    url = f"wss://www.pipeline-dev-k8s.com/copilot/memory-game/ws/game/{room_name}/"
    print(f"{player_name}: Connecting to {url}")
    
    try:
        await asyncio.sleep(delay)
        async with websockets.connect(url, ssl=True) as websocket:
            print(f"{player_name}: ✅ Connected!")
            
            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                print(f"{player_name}: Received {data['type']}")
                
                if data['type'] == 'game_update':
                    game = data['game']
                    players = game.get('players', [])
                    print(f"{player_name}: Game has {len(players)} players:")
                    for p in players:
                        you_marker = " (YOU)" if p.get('is_you') else ""
                        turn_marker = " 🎯" if p.get('is_current') else ""
                        print(f"  - {p['name']}{you_marker}{turn_marker}")
                    
                    # If this is player 1 and game not started, start it
                    if player_name == "Player 1" and not game['started'] and len(players) >= 2:
                        print(f"{player_name}: Starting game!")
                        await websocket.send(json.dumps({
                            'action': 'start_game',
                            'theme': 'emoji'
                        }))
                
                # Keep connection alive for a bit
                await asyncio.sleep(0.1)
                
    except websockets.exceptions.WebSocketException as e:
        print(f"{player_name}: ❌ WebSocket error: {e}")
    except Exception as e:
        print(f"{player_name}: ❌ Error: {e}")

async def test_multiplayer():
    """Test with two players joining the same room"""
    room_name = "test-room-" + str(int(asyncio.get_event_loop().time()))
    
    print(f"\n🎮 Testing multiplayer in room: {room_name}\n")
    
    # Start two players with slight delay
    tasks = [
        asyncio.create_task(player_client("Player 1", room_name, delay=0)),
        asyncio.create_task(player_client("Player 2", room_name, delay=1))
    ]
    
    # Run for 10 seconds
    try:
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=10)
    except asyncio.TimeoutError:
        print("\n⏱️  Test completed (10s timeout)")
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()

if __name__ == "__main__":
    print("=" * 60)
    print("  MULTIPLAYER WEBSOCKET TEST")
    print("=" * 60)
    
    try:
        asyncio.run(test_multiplayer())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    print("\n" + "=" * 60)
