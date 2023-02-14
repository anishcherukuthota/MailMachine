import discord
import ezgmail
import re

# parameter(s): 'user' is a discord.Member object
# functionality: searches through the email-list.txt file and identifies the email associated with the given user
# return: the email associated with the user if they exist in the text file, None otherwise
def get_email(user):
  email_list = open("FILE PATH", 'r') # "FILE PATH" represents the path of the text file storing user id's and their corresponding emails
  for line in email_list:
    user_info = line.strip().split(',')
    if (user_info[0] == str(user.id)):
      return user_info[1]
  return None

# parameter(s): 'message' is a discord.Message object
# functionality: validates that the given message contains an email and appends it to the list of emails
# return: none
def add_email(message):
  if (re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", message.content)):
    email_list = open("FILE PATH", 'a+') # "FILE PATH" represents path of text file storing user id's and their corresponding emails
    if (get_email(message.author) == None):
      print("user does not exist")
      email_list.write(str(message.author.id) + "," + message.content + "\n")
    email_list.close()

# parameter(s): 'attributes' is a list that contains the [subject, body, sender, recipients] of the email in that order
# functionality: uses the ezgmail API to send an email with the provided subject; sent to sender and bcc'd to recipients
# return: none
def send_email(attributes):
  print(attributes[3])
  recipients = ','.join(attributes[3])
  print (attributes[1])
  # ezgmail.send(attributes[2], attributes[0], attributes[1], bcc=recipients)
  print("sent")

# parameter(s): 'message' is a discord.Message object
# functionality: checks if the message's content contains the send-mail command keyword '\mail'
# return: True or False
def command_triggered(message):
  ind = message.content.find("\mail[")
  if (ind != -1):
    if (message.content.find(']', ind+5) != -1):
      return True
  return False

# parameter(s): 'message' is a discord.Message object
# functionality: identifies all unique members pinged in the provided message and compiles them in a list
# return: list of all pinged members within the message
def pinged(message):
  mentions = message.mentions
  roles = message.role_mentions
  for role in roles:
    for member in role.members:
      if (mentions.count(member) == 0):
        mentions.append(member)
  if ("@everyone" in message.content):
    for member in message.guild.members:
      if (mentions.count(member) == 0):
        mentions.append(member)
  if ("@here" in message.content):
    for member in message.channel.members:
      if (mentions.count(member) == 0):
        mentions.append(member)
  emails = []
  for user in mentions:
    email = get_email(user)
    if (email != None):
      emails.append(email)
  return emails
  
# parameter(s): 'message' is a discord.Message object
# functionality: breaks down message into subject, body, and list of pinged users
# return: list containing the [subject, body, sender, recipients] of the email in that order
def decompose(message):
  ind = message.content.find("\mail")
  start = ind+6
  end = message.content.find(']', start)
  subject = message.content[start:end]
  body = message.content[0:ind] + message.content[end+1:]
  roles = message.role_mentions
  for role in roles:
    ind = body.find(str(role.id))
    body = body[0:ind-2] + body[ind+len(str(role.id))+1]
  mentions = message.mentions
  for mention in mentions:
    ind = body.find(str(mention.id))
    body = body[0:ind-2] + body[ind+len(str(mention.id))+1:]
  ind = body.find("@everyone")
  if (ind != -1):
    body = body[0:ind] + body[ind+9:]
  ind = body.find("@here")
  if (ind != -1):
    body = body[0:ind] + body[ind+5:]
  return [subject, body, get_email(message.author), pinged(message)]
  
# setting up discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# setting up gmail client
ezgmail.init() 

# triggers on bot log in
@client.event
async def on_ready():
  print("Logged in as a bot {0.user}".format(client))

# triggers on every message that is sent in the server
@client.event
async def on_message(message):
  print(message.content)
  if (message.channel.name == "email-list"):
    add_email(message)
  if (command_triggered(message)):
    send_email(decompose(message))

# launches bot
client.run("TOKEN") # "TOKEN" represents the discord bot token used to authenticate the bot
