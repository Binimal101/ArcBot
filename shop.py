import random
from commands import database

def bot_speak(client, user):
	pass

async def nickname(client, user, name=None):
	if name is None:
		name = random.choice(('Peepy','NoName','Nerdatron','LilKeybored','SoggySocks','PristeneFruitPunch'))
		await user.edit(nick=name)
	return f"Your new nickname is {name}"

async def eat_cookie(channel, user):
	database.remove_item_from_inventory(user, 'cookie') #may cause a problem because I think this function compares the cookie obj and not the name
	
def get_shop_items(find=None):
	items = {
		'speak' : {'name' : 'speak', 'count' : 1, 'usable' : 'bot_speak', 'price_per' : 20},
		'nickname' : {'name' : 'nickname', 'count' : 1, 'usable' : 'nickname', 'price_per' : 50},
		'cookie' : {'name' : 'cookie', 'count' : 3, 'usable' : 'eat_cookie', 'price_per' : 2},
		'gold-star' : {'name' : 'gold_star', 'count' : 1, 'usable' : False, 'price_per' : 200},
	}
	
	if find is not None and find not in items:
		return None

	elif find is not None:
		return items[find]	
	
	else:
		return items