

# Import the required modules
import random

# Define the player's current location
player_location = 'entrance'

# Define the rooms in the cave
rooms = {
    'entrance': {
        'description': 'You are standing at the entrance of a dark and mysterious cave.',
        'exits': ['north'],
        'treasure': False,
        'sword_room': False
    },
    'north room': {
        'description': 'You find yourself in a small, dimly lit chamber.',
        'exits': ['east', 'south'],
        'treasure': True,
        'sword_room': False
    },
    'east room': {
        'description': 'You are now in a large, cavernous space filled with ancient relics.',
        'exits': ['west', 'north'],
        'treasure': True,
        'sword_room': False
    },
    'boss chamber': {
        'description': 'You have finally reached the heart of the cave: a vast, open chamber containing the legendary sword.',
        'exits': [],
        'treasure': True,
        'sword_room': True
    },
    'treacherous tunnel': {
        'description': 'This narrow, winding passage is fraught with danger. Be careful not to get trapped!',
        'exits': ['south'],
        'traps': [True]
    }
}

# Define the dragon boss
dragon = {
    'health': 100,
    'attack': 20
}

# Initialize the player's inventory and current location
player_inventory = []
player_location = 'entrance'

# Game loop
while True:
    # Print the current description of the room
    print(rooms[player_location]['description'])

    # Get user input for movement
    action = input('What do you want to do? (type "inventory" to see your inventory) ').lower()

    # Handle player's movement
    if action == 'north':
        if rooms[player_location]['exits'] == ['north']:
            print("You cannot go that way.")
        else:
            player_location = 'north room'
    elif action == 'east':
        if rooms[player_location]['exits'] == ['west']:
            player_location = 'east room'
        else:
            print("You cannot go that way.")
    elif action == 'south':
        if rooms[player_location]['exits'] == ['north']:
            player_location = 'entrance'
        else:
            print("You cannot go that way.")
    elif action == 'west':
        if rooms[player_location]['exits'] == ['east']:
            player_location = 'entrance'
        else:
            print("You cannot go that way.")

    # Check for treasure
    if action == 'inventory' or rooms[player_location].get('treasure', False):
        print(f"You found {'' if not rooms[player_location]['treasure'] else 'some'} treasure in the current room!")

    # Check for traps
    elif action == 'inventory' or rooms[player_location].get('traps', False) and random.choice([True, False]):
        print("You triggered a trap! You got hurt.")
        player_inventory.append('hurt')
    elif action == 'inventory' or rooms[player_location].get('traps', False):
        if not rooms[player_location]['traps']:
            print("The room is safe.")

    # Check for the sword
    elif action == 'inventory' and (rooms['north room']['treasure'] or rooms['east room']['treasure']):
        if not rooms[player_location]['sword_room']:
            player_location = 'boss chamber'
        else:
            print("You are in a room with the treasure, but it is guarded.")
    elif action == 'inventory':
        print(f"Your inventory: {', '.join(player_inventory)}")

    # Check for dragon battle
    if player_location == 'boss chamber' and rooms['boss chamber']['sword_room']:
        print("You have reached the heart of the cave. A fierce dragon awaits you!")
        while True:
            action = input('What do you want to do? (type "attack" to attack the dragon, or "run" to run away) ').lower()
            if action == 'attack':
                player_attack = random.randint(1, 10)
                print(f"You attacked the dragon for {player_attack} damage.")
                dragon['health'] -= player_attack
                if dragon['health'] <= 0:
                    print("You defeated the dragon! You found a treasure trove of gold and jewels!")
                    break
            elif action == 'run':
                print("You ran away from the battle. The dragon escapes, and you lose your chance to find the sword.")
                player_location = 'entrance'
                break

    # Print the current inventory
    if 'hurt' in player_inventory:
        print(f"You are hurt. You lost 5 health points.")
