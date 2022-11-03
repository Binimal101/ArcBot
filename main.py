#Main Imports
import discord, os, asyncio
from ratelimit import limits, sleep_and_retry #So that the bot doesn't get ratelimited and die
#File Imports
from commands import * #terrible practice, but much needed due to the amount of imports needed
from helper import commands
from shop import get_shop_items

TOKEN = os.environ.get('TOKEN') #.env variable since the project is public and the key has to be secret for security
intents = discord.Intents.default()
intents = intents.all()

activity = discord.Activity(type=discord.ActivityType.listening, name="the typing of a hasty dev") #Gives bot a custom status
permissions = discord.Permissions(administrator=True)
client = discord.Client(intents=intents,activity=activity,permissions=permissions) #Creates bot cli with intents; just means the bot has special permissions

@client.event #this just means that this function is passed into discords client object as a wrapper for the event superclass
async def on_ready():
	os.system('clear') #clears terminal for aesthetics
	print('Bot is now running')

@client.event 
async def on_message(message): #message object is given to this function
	if message.author.bot or message.author.id == client.user.id or isinstance(message.channel, discord.channel.DMChannel): #just checks to see if the bot is talking to itself or if it's talking in a dm
		return #just so the thread doesn't sit idly
	
	connection = message.channel #this var has a instance function called send that sends messages and embeds to the channel of the message instance
	guild = connection.guild

	if message.channel.id != 844572963264135178 and 'arc ' in message.content.lower():
		allowed = client.get_channel(844572963264135178)
		await message.delete()
		
		warning = await message.channel.send(f'Sorry, I can\'t talk here, try going to "bot_testing"')
		
		await asyncio.sleep(3) #sleep for 3 seconds

		await warning.delete() #delete the warning

	
 	# each command is called when all of the aliases (string arguements in commands.command) are called in a message in addition to the bot name,
    # there is also the option to run when any of the aliases are in the message, which will be checked off when or_aliases is set to true
 	
	elif commands.command(message, 'hey', 'hi', 'howdy', 'hello', 'heya', or_aliases=True):
		await Fun.greet(message)
	
	elif commands.command(message, 'update'):
		await database.log_user(client, message.author)
	
	elif commands.command(message, 'work'):
		reciept = await database.commands.work(client, message.author, 5)
		await message.channel.send(reciept)
	
	elif commands.command(message, 'buy'):
		func_output = commands.parse_for_item(message)
		if len(func_output) == 2:
			item_name, amount = func_output
		else:
			item_name, amount = func_output

		item = get_shop_items(find=item_name)
		
		if item == None:
			await message.channel.send(f"Sorry! But the item, {item_name} does not exist, make sure you have it spelt correctly")
		else:
			order_reciept = await database.commands.buy(client, message.author, item, amount=amount)
			await message.channel.send(order_reciept)
	
	elif commands.command(message, 'sell'):
		func_output = commands.parse_for_item(message)
		if len(func_output) == 2:
			item_name, amount = func_output
		else:
			item_name, amount = func_output

		item = get_shop_items(find=item_name)
		
		if item == None:
			await message.channel.send(f"Sorry! But the item, {item_name} does not exist, make sure you have it spelt correctly")
		else:
			order_reciept = await database.commands.sell(client, message.author, item, amount=amount)
			await message.channel.send(order_reciept)
	
	elif commands.command(message, 'bal', 'balance', 'bank', 'wallet', 'money', or_aliases=True):
		await message.channel.send(await database.commands.balance(message.author))
	
	elif commands.command(message, 'shop', 'store', or_aliases=True):
		await database.commands.shop(client, message.author)
	
	elif commands.command(message, 'inv', 'inventory', or_aliases=True):
		embed = await database.commands.inventory(client, message.author)
		await message.channel.send(embed=embed)

client.run(TOKEN)