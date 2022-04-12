import random, discord
from helper import *

class Fun():	
	def greetings(username):
		#this is a cool trick I learned where you can create a whole lot of f-strings
		#based on a parameter and return the a new list of strings instead of having  
		#to create the strings manually
		greeting = (
			f'Hey {username}! Whats up',
			f'Howdee partner',
			f'Is that you {username}? Great seeing you here!',
			f'Heya {username}',
			f'Hi {username}',
		)
		return greeting
		
	async def greet(message):
		greeting = random.choice(Fun.greetings(message.author.name))
		await message.channel.send(greeting) 

class database():
	#Some static variables
	global PATH
	PATH = 'Users/'

	async def log_user(client, user):
		await json_helpers.update(client, user)

	async def add_money(client, user, amount):
		await json_helpers.update(client, user, functions={
			'add_money' : amount,
		})

	async def subtract_money(client, user, amount):
		await json_helpers.update(client, user, functions={
			'subtract_money' : amount,
		})
	
	def get_money(user):
		return int(json_helpers.read_json(json_helpers.get_full_path(PATH, user.id))['money'])
	
	def get_items(user):
		return json_helpers.read_json(json_helpers.get_full_path(PATH, user.id))['items']

	def get_item_count(item):
		return item['count']

	def get_name(user):
		return json_helpers.read_json(json_helpers.get_full_path(PATH, user.id))['name']
	
	def affordable(user, total=None):
		if total is None:
			return
		else:
			user_cash = database.get_money(user)
			return user_cash >= int(total)
	
	def get_price(item, stock_bought):
		return int(item['price_per']) * int(item['count'] * int(stock_bought))

	def get_change(user, total=None):
		if total is None:
			return
		else:
			user_cash = database.get_money(user)
			return int(user_cash - int(total))

	def set_money(user, amount):
		json_helpers.replace_json(json_helpers.get_full_path(PATH, user.id), {'money' : amount})
	
	def add_item_to_inventory(user, item):
		new_inv = json_helpers.read_json(json_helpers.get_full_path(PATH, user.id))['items']
		if item['name'] in new_inv:
			#print(new_inv)
			new_inv[item['name']]['count'] = new_inv[item['name']]['count'] + 1
		else:
			new_inv[item['name']] = item
		json_helpers.replace_json(json_helpers.get_full_path(PATH, user.id), {'items' : new_inv})

	def remove_item_from_inventory(user, item):
		new_inv = json_helpers.read_json(json_helpers.get_full_path(PATH, user.id))['items']
		if type(item) == str:
			new_inv[item]['count'] = new_inv[item]['count'] - 1
			if new_inv[item]['count'] == 0:
				del new_inv[item]
				
		else:
			if item['name'] in new_inv: 
				new_inv[item['name']]['count'] = new_inv[item['name']]['count'] - 1
				if new_inv[item['name']]['count'] == 0:
					del new_inv[item['name']]
			else:
				return False
		json_helpers.replace_json(json_helpers.get_full_path(PATH, user.id), {'items' : new_inv})

	async def get_inventory(user):
		embed=discord.Embed(title=f"{user.name}'s inventory",description='** **')
		inv = database.get_items(user)
		for item in inv:
			embed.add_field(name=f"{inv[item]['name']}",value=f"Amount: {inv[item]['count']}", inline=False)
		return embed

	async def shop_interface():
		embed=discord.Embed(title="Arcade Shop", description="Buy some items, Stay a while", color=0xff0000)
	
		embed.add_field(name="cookie(consumable)", value="Who doesn't like a good cookie", inline=True)
		embed.add_field(name="| 2 dollars", value="| Batch of 3", inline=True)

		embed.add_field(name="\u200b", value="_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_", inline=False)

		embed.add_field(name="nickname(consumable)", value="Want a server nickname? I got you", inline=True)
		embed.add_field(name="| 50 dollars", value="| Batch of 1", inline=True)

		embed.add_field(name="\u200b", value="_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_", inline=False)

		embed.add_field(name="speak(consumable)", value="I'll say what you want me to say", inline=True)
		embed.add_field(name="| 20 dollars", value="| Batch of 1", inline=True)

		embed.add_field(name="** **", value="_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_", inline=False)

		embed.add_field(name="gold-star", value="For the prestigious", inline=True)
		embed.add_field(name="| 200 dollars", value="| Batch of 1", inline=True)

		embed.set_footer(text="Arc buy {item_name} {count}")
		return embed
	
	class commands():
		async def work(client, user, base_paycheck, mult=1, variation=(2,8)):
			paycheck = base_paycheck + random.choice(range(variation[0],variation[1]))
			final_pay = paycheck * mult
			await database.add_money(client, user, final_pay)
			return f"You come back from work with {final_pay} dollars and you now have {database.get_money(user)} total dollars"

		async def buy(client, user, item, amount=1):
			total = database.get_price(item, amount)
			
			if database.affordable(user, total=total):
				new_amount = database.get_change(user, total=total)
				for _ in range(int(amount)):
					for _ in range(int(item['count'])):
						database.add_item_to_inventory(user, item)

				database.set_money(user, new_amount)
				return f"You have bought {amount * item['count']} {item['name']}, You now have {database.get_items(user)[item['name']]['count']}\nNew Balance: {new_amount}"
			else:
				return f"Sorry! This transaction costs {total}, and you only have {database.get_money(user)} dollars"
			return 
		
		async def sell(client, user, item, amount=1):
			new_amount = database.get_money(user) + (int(item['price_per']*0.5*int(amount)))

			if not database.get_item_count(item) < 0:
				for _ in range(int(amount)):
					database.remove_item_from_inventory(user, item)
				database.set_money(user, new_amount)
				#TODO make it to where it checks if the item still exists after the sell command, also make sure the user actually
				#has enough items to sell
				return f"You have sold {amount} {item['name']}s, You now have {database.get_items(user)[item['name']]['count']} left\nNew Balance: {new_amount}"
			else:
				return f"Sorry! This transaction needs {amount} {item['name']}, and you only have {item['count']}"

		async def balance(user):
			return f"Your balance: {database.get_money(user)}"
		
		async def shop(client, user):
			embed = await database.shop_interface()
			await commands.dm_user(client, embed=embed, id=user.id)

		async def inventory(client, user):
			return await database.get_inventory(user)
