import discord
from dotenv import load_dotenv
load_dotenv()
import os

client = discord.Client()
prefix = '!'
connection = ''
dispatcher = ''


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

async def switch_voice (message, command):
    global connection, dispatcher
    argument = command.split()[0]
    if argument == str(prefix + "join"):
        if message.author.voice:
            voice_channel = message.author.voice.channel
            connection = await voice_channel.connect()
            await message.channel.send("Je rejoins votre salon vocal.")
        else:
            await message.channel.send("Vous devez être dans un salon vocal pour que je vous rejoigne.")
    elif argument == str(prefix + "leave"):
        if connection != '':
            await connection.disconnect()
            await message.channel.send("Je viens de quitter le salon vocal.")
        else:
            await message.channel.send("Je ne suis dans aucun salon vocal.")
    elif argument == str(prefix + "play"):
        voice = await client.join_voice_channel(message.author.voice.channel)
        
        # voice_channel = message.author.voice.channel
        url = command.split()[1]
        print(url)
        if connection == '':
            connection = await voice_channel.connect()
            await message.channel.send("Je rejoins votre salon vocal pour pouvoir jouer de la musique.")
        # dispatcher = await connection.create_ytdl_player(url)
        # dispatcher.start()
        player = await voice.create_ytdl_player(url)
        player.start()
        await message.channel.send("Je lance le titre.")

def get_available_commands(message):
    commandArray = []
    toExecute = []
    file = open('available_commands', 'r')
    for line in file:
      commandArray.append("".join(list(line)[:-1]))
    file.close()
    file = open('commands_to_execute', 'r')
    for line in file:
      toExecute.append("".join(list(line)[:-1]).format(message.author.nick))
    file.close()
    return (commandArray, toExecute)

async def switch_message(message, command):
    commandArray, toExecute = get_available_commands(message)
    
    argument = "".join(list(command)[1:]).split(' ')[0]
    if argument in commandArray:
        await message.channel.send(toExecute[commandArray.index(argument)])

def add_available_commands(argument, task):
    file = open('available_commands', 'a')
    file.write(argument+'\n')
    file.close()
    file = open('commands_to_execute', 'a')
    file.write(" ".join(task)+'\n')
    file.close()

def remove_available_commands(args):
    commandArray = []
    toExecute = []
    file = open('available_commands', 'r')
    for line in file:
      commandArray.append("".join(list(line)[:-1]))
    file.close()
    file = open('commands_to_execute', 'r')

    for line in file:
      toExecute.append("".join(list(line)[:-1]))
    file.close()
    for item in args:
        if item in commandArray:
            toExecute.pop(commandArray.index(item))
            commandArray.remove(item)

    file = open('available_commands', 'w')
    for item in commandArray:
        file.write(item+'\n')
    file.close()
    file = open('commands_to_execute', 'w')
    for item in toExecute:
        file.write(item+'\n')
    file.close()

async def show_available_commands(message):
    commandArray, toExecute = get_available_commands(message)
    toDisp = '```'
    for i in range(len(commandArray)):
        toDisp += str(prefix + commandArray[i] + ' ==> ' + toExecute[commandArray.index(commandArray[i])] + '\n')
    await message.channel.send(toDisp + '```')
        
async def show_help(message):
    await message.channel.send("""
    ```
Tu as demandé de l'aide frerot ?
        
    !help show this message
    !disp ==> get available commands
    !add + args ===> add a personnal message
    !remove + args ===> remove a personnal message
    !join ===> join a voice channels
    !leave ==> leave a voice channel
    !play + args ===> play a music
    ```
    """)

async def switch_edit_command(message, command):
    argument = command.split()
    if argument[0] == str(prefix + "add") and len(argument) >= 3:
        add_available_commands(argument[1], argument[2:])
        await message.channel.send("Commande ajoutée")
    elif argument[0] == str(prefix + "remove") and len(argument) >= 2:
        remove_available_commands(argument[1:])
        await message.channel.send("Commande(s) supprimée(s)")
    elif argument[0] == str(prefix + "disp"):
        await show_available_commands(message)
    elif argument[0] == str(prefix + "help"):
        await show_help(message)

async def switch_cases(message):
    await switch_message(message, message.content.lower())
    await switch_edit_command(message, message.content.lower())
    await switch_voice(message, message.content)

@client.event
async def on_message(message):
    if f"{message.author}" != "GoddiBot#3052" and list(message.content.lower())[0] == prefix:
        # print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
        await switch_cases(message)
    
client.run(os.getenv("TOKEN"))