rooms = {
        'Mines of Moria': {'West': 'West Wing', 'East': 'East Wing', 'North': 'North Hall', 'South': 'South Hall', 'item': 'Seeing Stone'},
        'West Wing': {'East': 'Mines of Moria', 'item': 'Lothlorian Bow'},
        'North Hall': {'South': 'Mines of Moria', 'East': 'North Bunker', 'item': 'Staff of Gandalf'},
        'North Bunker': {'West': 'North Hall', 'item': 'Mythril Armor'},
        'South Hall': {'North': 'Mines of Moria', 'East': 'South Bunker', 'item': 'Light of Galadriel'},
        'South Bunker': {'West': 'South Hall', 'item': 'Helmet of Eowyn'},
        'East Wing': {'West': 'Mines of Moria', 'North': 'Dungeon', 'item': 'Sword of Gondor'},
        'Dungeon': {'item': 'Balrog'},

}

current_room = 'Mines of Moria'
inventory = []
def get_new_room(current_room, direction):
        new_room = current_room
        for i in rooms:
                if i == current_room:
                        if direction in rooms[i]:
                                new_room = rooms[i][direction]
        return new_room

def get_item(current_room):
    if 'item' in rooms[current_room]:
        return rooms[current_room]['item']
    else:
        return 'This room has no item.'

print()
print('********** The Fellowship & The Balrog **********')
print('You and The Fellowship have fallen into the Mines of Moria...')
print('A great beast lies at the end of these mines...')
print('Prepare to protect The Fellowship by collecting all items in each of the rooms.')
print('Navigate between the rooms using the inputs of "North, South, East or West"')
print("To gather an item, type 'get [item name]'")
print('...and remember to keep it secret, keep it safe!')
print('*************************************************')
print()

inventory = []
while(current_room):
        print('You find yourself in the', current_room)
        print('Inventory:', inventory)
        item = get_item(current_room)
        if item == 'Balrog':
                print ("IT'S THE BALROG!")
        else:
                print('You come upon a unique item. It is the', item)
        print('*************************************************')
        if current_room == 'Dungeon':
                if len(inventory)==7:
                        print('You have brought honor to The Fellowship and gather all the items to defeat the Balrog.\n')
                        print('The Fellowship is safe and escaped the Mines of Moria!!')
                else:
                        if len(inventory)<7:
                                print('You did not collect all the items and therefore The Fellowship fell to defeat by the Balrog! Better luck next time...')
                break
        direction = input('Enter a direction or pickup an item >') 
        direction = direction.capitalize()
        if (direction == 'Exit'):
           exit(0)
        if (direction == 'East' or direction == 'West' or direction == 'North' or direction == 'South'):
                new_room = get_new_room(current_room, direction)
                if new_room == current_room:
                        print('No path to follow...')
                else:
                        current_room = new_room
        elif direction == str('get '+item).capitalize():
                if 'item' in inventory:
                        print('You have collected this item. Seek out a new room...')
                else:
                        inventory.append(item)

        else:
                print('Invalid direction. Choose another path...')
