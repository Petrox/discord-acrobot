import discord
import asyncio

import random
import threading
import time
import sys

client = discord.Client()

true = 1
false = 0

acro_time = 45
vote_time = 30
start_acro = 3
rounds = 5
total_weight = 70
weight = [3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 2, 2, 1, 2, 2]
	# A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

allow_doubles	= true 	# Allow the same letter twice in a row
allow_triples	= false # Allow the same letter three times in a row

chanowner="lipho"
botmaster="alexa"
nick="AcroBot"

help = [
"How to play acro: At the start of each round I will give you an acro (for example: lmao). You then have to make up a phrase to fit that acro (for example: leather makes ankles oily).",
"You enter your acro by typing /msg " + nick + " <your answer>",
"After the alotted time has passed, I will display a numbered list of all the acros entered and a vote will then be held to determine the winner. You must then pick your favourite acro and vote for it.",
"You submit your vote by typing ctrl+k and messaging " + nick + " <your vote> (note: you only have to type the number of your vote, for example /msg " + nick + " 5)",
"For more information, please ask " + chanowner + ", " + botmaster + " or one of the ops for help."
]
# END CONFIGURATION

class AcroBot():
	def __init__(self):
		print("AcroBot online!")

		self.rnd = random.Random(time.time())

		self.on = false
		self.scores = {}
		self.this_round_nicks = []
		self.this_round_acros = []
		self.voted = []
		self.this_round_scores = []
		self.which_round = 0
		self.acro = ""
		self.mode = ""

	def run(self, token):
		client.run(token)

	def disconnect(self):
		print("Disconnecting...")
		sys.exit()

	def round(self, message):
		for n in range(len(self.this_round_nicks)):
			if self.this_round_nicks[n] in self.scores:
				self.scores[self.this_round_nicks[n]] += self.this_round_scores[n]
			else:
				self.scores[self.this_round_nicks[n]] = self.this_round_scores[n]

		yield from client.send_message(message.channel, "Voting time is up!")
		for n in range(len(self.this_round_nicks)):
			if self.this_round_scores[n] > 0:
				yield from client.send_message(message.channel, self.this_round_nicks[n] + "'s response was '" + self.this_round_acros[n] + "'and got " + str(self.this_round_scores[n]) + " votes!")

		if self.which_round == rounds:
			yield from self.endgame(message)
			return

		yield from client.send_message(message.channel, "The score stands at:")
		for nick in self.scores.keys():
			if self.scores[nick] > 0:
				yield from client.send_message(message.channel, nick + " with a score of " + str(self.scores[nick]) + "!")

		self.this_round_nicks = []
		self.this_round_acros = []
		self.voted = []
		self.this_round_scores = []

		self.which_round += 1
		self.gen_acro(start_acro + self.which_round - 1)
		self.mode = "ACRO"
		yield from client.send_message(message.channel, "Round " + str(self.which_round) + "! The new acro is: " + self.acro)

		yield from asyncio.sleep(acro_time)
		yield from self.switch_mode(message)

	def switch_mode(self, message):

		self.mode = "VOTE"
		yield from client.send_message(message.channel, "Acro time is up! Please vote now on the following choices:")
		for a in range(len(self.this_round_acros)):
			yield from client.send_message(message.channel, "#" + str(a) + ": " + self.this_round_acros[a])

		yield from asyncio.sleep(vote_time)
		yield from self.round(message)

	def test(self):
		yield from client.send_message(message.channel, "TEST")

	def startgame(self, message):
		# Reset everything when starting a new game
		self.scores = {}
		self.this_round_nicks = []
		self.this_round_acros = []
		self.voted = []
		self.this_round_scores = []

		self.which_round = 1
		self.on = true
		self.gen_acro(start_acro)
		self.mode = "ACRO"

		yield from client.send_message(message.channel, 'Starting a new game! Get Ready!')
		yield from client.send_message(message.channel, 'Round ' + str(self.which_round) + '!')
		yield from client.send_message(message.channel, 'The new acro is: ' + self.acro)

		yield from asyncio.sleep(acro_time)
		yield from self.switch_mode(message)

	def endgame(self, message):
		yield from client.send_message(message.channel, "\x02\x0304The game is over!")
		yield from client.send_message(message.channel, "\x02\x0304Ending scores:")
		for nick in self.scores.keys():
			yield from client.send_message(message.channel, nick + " with a score of " + str(self.scores[nick]) + "!")

	@asyncio.coroutine
	def on_privmsg(self, channel, message):
		if message.author.id == client.user.id:
			return

		print("On privmsg")

		if message.content.startswith("!help"):
			yield from client.send_message(channel, help_main01)
			yield from client.send_message(channel, help_main02)
			yield from client.send_message(channel, help_main03)
			yield from client.send_message(channel, help_main04)
			yield from client.send_message(channel, help_main05)

		elif message.content.startswith("!start"):
			yield from self.startgame(message)
		elif message.content.startswith("!stop"):
			yield from self.endgame(message)
		elif message.content.startswith("!shutdown"):
			yield from client.send_message(channel, "Have fun, bye!")
			self.disconnect()
		elif self.mode == "ACRO" and message.channel.is_private:
			if self.confirm_acro(message.content.split()) == false:
				yield from client.send_message(message.channel, "That does not match the acro. Try again.")
				return
			else:
				if message.author.id in self.this_round_nicks:
					yield from client.send_message(message.channel, "You may not enter more than once.")
					return
				elif message.content not in self.this_round_acros:
					yield from client.send_message(message.channel, "You've been entered in this round.")
					self.this_round_nicks.append(message.author.id)
					self.this_round_acros.append(message.content)
					self.this_round_scores.append(0)
					return
				else:
					yield from client.send_message(message.channel, "That acro has already been entered. Please try again.")
					return
		elif self.mode == "VOTE" and message.channel.is_private:
			try:
				vote = int(message.content)
				if vote not in self.this_round_nicks:
					yield from client.send_message(message.channel)
					return
				elif message.author.id not in self.this_round_nicks:
					yield from client.send_message(message.channel, "You can't vote if you don't participate.")
					return
				elif message.author.id == self.this_round_nicks[vote]:
					yield from client.send_message(message.channel, "You can't vote for yourself. Try again.")
					return
				elif message.author.id not in self.voted:
					self.this_round_scores[vote] += 1
					self.voted.append(message.author.id)
					yield from client.send_message(message.channel, "Your vote has been counted.")
					return
			except ValueError:
				pass

	def confirm_acro(self, input):
		if len(input) != len(self.acro):
			return false
		for i in range(len(self.acro)):
			if input[i][0].capitalize() != self.acro[i]:
				return false
		return true

	def gen_acro(self, length):
		self.acro = self.random_letter()
		letter = self.random_letter()
		if allow_doubles == false and self.acro[0] == letter:
			while self.acro[0] == letter:
				letter = self.random_letter()
		self.acro += letter

		for i in range(2, length):
			letter = self.random_letter()
			if allow_doubles == false and self.acro[i - 1] == letter:
				while self.acro[i - 1] == letter:
					letter = self.random_letter()
			if allow_triples == false and self.acro[i - 1] == letter and \
					self.acro[i - 2] == letter:
				while self.acro[i - 1] == letter:
					letter = self.random_letter()
			self.acro += letter

	def random_letter(self):
		n = self.rnd.randrange(0, total_weight - 1)
		for l in range(len(alphabet)):
			if n < weight[l]:
				return alphabet[l]
			else:
				n -= weight[l]
		return alphabet[-1]



acro = AcroBot()

@client.event
@asyncio.coroutine
def on_ready():
	yield from client.change_status(game=discord.Game(name="Acro, motherfucker!"))
	print('Logged in as', client.user.name, client.user.id)


@client.event
@asyncio.coroutine
def on_message(message):
	yield from acro.on_privmsg(message.channel, message)

acro.run('MjIzNjI1MzU2ODAyOTE2MzU0.CrOq7Q.FBqjuX16eUTz214axIpBt_gYduI')
