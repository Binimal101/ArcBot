import json, os, datetime
from ratelimit import sleep_and_retry, limits

class json_helpers():

	class User():
		def __init__(self, name, money=0, items={}):
			self.name = name
			self.money = money
			self.items = items
		
		#Setter Methods
		def addItem(self, item):
			self.items[item.name] = item
		def removeItem(self, item):
			self.items.remove(item)
		def setName(self, name):
			self.name = name
		def setMoney(self, amount):
			self.money = amount
		def addMoney(self, amount):
			self.money += amount
		def subtractMoney(self, amount):
			self.money -= amount
		#Getter Methods
		def affordable(self, comparison):
			return self.money >= comparison
		def getMoney(self):
			return self.money
		def getName(self):
			return self.name
		def getItems(self):
			return self.items
		def getChange(self, amount):
			return self.money - amount
		def getUserAttributes(self):
			attributes = {
				'money' : self.money,
				'name' : self.name,
				'items' : self.items
			}
			return attributes

	def is_stable(FULL_PATH):
		look_for = ('name', 'money', 'items')
		info = json_helpers.read_json(FULL_PATH)
		for key in look_for:
			if not key in info:
				return False #will return true if this if-block never runs
		return True

	def replace_json(FULL_PATH, injection): #takes injection as dictionary 
		with open(FULL_PATH,'r') as file:
			info = json.load(file)

			for key in injection:
				info[key] = injection[key] #replaces values from injection into info; adds new key-value pairs if not any already existing

		with open(FULL_PATH,'w') as file:
			json.dump(info, file) #deposits information into the user instances file
		with open(FULL_PATH,'r') as file:
			return json.load(file) #returns the info deposited so I can check for error in the injections


	def read_json(FULL_PATH):
		with open(FULL_PATH, 'r') as file:
			return json.load(file)

	def get_full_path(PATH, uid):
		return f'{PATH}/{uid}'


	@sleep_and_retry
	@limits(calls=20, period=60)
	async def update(client, USER, injection=None, functions=None):
		uid = str(USER.id)
		PATH = 'Users'
		FULL_PATH = f'{PATH}/{uid}'
		logged_users = os.listdir(PATH)
		if uid in logged_users:	#user is in /Users
			try:
				json_helpers.is_stable(FULL_PATH)
				unstable = False
			except json.decoder.JSONDecodeError:
				unstable = True

			if not unstable and json_helpers.is_stable(FULL_PATH):
				info = json_helpers.read_json(FULL_PATH)
				money, name, items = info['money'], info['name'], info['items']
				
				if injection is not None:
					user = json_helpers.User(name, money=money, items=items)
					json_helpers.replace_json(FULL_PATH, injection)

				if functions is not None:
					info = json_helpers.read_json(FULL_PATH)
					money, name, items = info['money'], info['name'], info['items']
					user = json_helpers.User(name, money=money)

					if 'add_money' in functions:
						user.addMoney(int(functions["add_money"]))
					if 'subtract_money' in functions:
						user.subtractMoney(int(functions["subtract_money"]))
					
					json_helpers.replace_json(FULL_PATH, user.getUserAttributes())

				elif name != USER.name:
					with open(FULL_PATH,'w') as file:
						user = json_helpers.User(USER.name, money=money)
						json.dump(user.getUserAttributes(), file) #User comes with name and *money* amount of dollars
			else:	#Account is unstable/Missing JSON params
				try:	
					await commands.dm_user(client, message='Your ARC account has been corrupted, I have messaged the admins.\nSorry for the inconvenience',id=str(uid))
				except:
					pass
				finally:
					try:
						await commands.dm_user(client, message=f'USER: {uid}\'s account has been corrupted and reset to default', id='765972771418275841')
					except:
						pass

				os.remove(FULL_PATH) #deletion of path 
				user = json_helpers.User(USER.name)
				with open(FULL_PATH,'w') as file:
					json.dump(user.getUserAttributes(), file) #User comes with a name and $0

		else: #user isn't already in /Users
			user = json_helpers.User(USER.name)
			with open(FULL_PATH,'w') as file:
				json.dump(user.getUserAttributes(), file) #User comes with a name and $0
		
		user_info_object = json_helpers.read_json(FULL_PATH)
		return user_info_object

			
	
class FunHelpers():
	def get_timestamp():
		obj = datetime.datetime.now()
		year, month, day = str(obj.year), str(obj.month), str(obj.day)
		timestamp = f"{year}-{month}-{day}"
		return timestamp
	
class commands():
	def parse_for_item(message):
		content = message.content
		if 'arc ' in content:
			content = content.replace('arc ', '')
		if 'arcbot ' in content:
			content = content.replace('arcbot ', '')
		if '849310753588903986' in content:
			content = content.replace('849310753588903986 ', '')
		content = content.split()
		amount, item = [x for x in content if x.isdigit()], [x for x in content if not x.isdigit() and not (x.lower() == 'buy' or x.lower() == 'sell')]
		
		try:
			amount = amount[0]
		except IndexError:
			return item[0], 1
		else:
			return item[0], amount

	def bot_name(content):
		aliases = ['arc','arcbot','849310753588903986']
		for alias in aliases:
			if alias in content:
				return True
		return False #If none of the above identifiers are in content
	
	def is_admin(message):
		return message.channel.permissions_for(message.author).administrator

	def in_channel(allowed_channel, message):
		if allowed_channel == message.channel or allowed_channel == message.channel.id:
			return True

	def command(message,*aliases,or_aliases=False,and_alaises=False,prefix=None,allowed_channel=None, admin=None):
		content = message.content.lower()

		#Checks for admin perms
		if admin is not None:	
			if admin == True and not commands.is_admin(message):
				return
		#Checks if its in the right channel
		if allowed_channel is not None:
			if commands.in_channel(allowed_channel,message):
				return
		
		if prefix is not None:
			for alias in aliases:
				if content.startswith(prefix + alias):
					return True
		else:
			if and_alaises: #if all aliases in content
				for command_name in aliases:
					if command_name in content and commands.bot_name(content):
						continue
					else:
						return False
				return True

			elif or_aliases: #if one or more aliases in content
				for command_name in aliases:
					if command_name in content and commands.bot_name(content): #only needs one of the alaises
						return True
			else:
				for command_name in aliases:
					if command_name in content and commands.bot_name(content): #only needs one of the alaises
						return True
		
	@sleep_and_retry #So function will still run with the same arguements
	@limits(calls=15, period=20) # Will sleep the function if it tries to call more than 10 dm's in 30 seconds; helps to prevent rate limiting
	async def dm_user(client,message=None,embed=None,id=None):
		try:
			if id is not None:
				id = str(id)
				if message is not None and embed is None:
					recipient = await client.fetch_user(id)
					await recipient.send(message)

				elif message is None and embed is not None:
					recipient = await client.fetch_user(id)
					await recipient.send(embed=embed)

				elif message is not None and embed is not None:
					recipient = await client.fetch_user(id)
					await recipient.send(message, embed=embed)
				else:
					return
			else:
				return
		except:
			print("User does not have dm's open to the bot")