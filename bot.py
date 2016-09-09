import discord
import asyncio

import random
import threading
import time
import sys

client = discord.Client()

true = 1
false = 0

acro_time = 90
vote_time = 45
start_acro = 3
rounds = 5
total_weight = 70
weight = [3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 2, 2, 1, 2, 2]
		# A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

allow_doubles	= true 	# Allow the same letter twice in a row
allow_triples	= false # Allow the same letter three times in a row


class AcroBot():
	def __init__(self, token):
		print("AcroBot online!")

		self.rnd = random.Random(time.time())
		self.mode_switcher = threading.Timer(acro_time, self.switch_mode)
		self.vote_time = threading.Timer(vote_time, self.round)

		self.on = false
		self.scores = {}
		self.this_round_nicks = []
		self.this_round_acros = []
		self.voted = []
		self.this_round_scores = []
		self.which_round = 0
		self.acro = ""
		self.mode = ""
		self.channel = ''

		client.run(token)

	def disconnect(self):
		print("Disconnecting...")
		sys.exit()

	def round(self):
		for n in range(len(self.this_round_nicks)):
			if self.this_round_nicks[n] in self.scores:
				self.scores[self.this_round_nicks[n]] += self.this_round_scores[n]
			else:
				self.scores[self.this_round_nicks[n]] = self.this_round_scores[n]

		yield from client.send_message(message.channel, 'Hye, you called?')

		self.connection.privmsg(self.chan, "\x02\x0304Voting time is up!")
		for n in range(len(self.this_round_nicks)):
			if self.this_round_scores[n] > 0:
				self.connection.privmsg(self.chan,
				                        "\x1F\x0313" + self.this_round_nicks[
					                        n] + "'s\x0F \x02\x0312reponse was \x0F\x0306'" +
				                        self.this_round_acros[
					                        n] + "'\x0F\x02\x0312 and got \x0F\x02\x1F\x0313" + str(
					                        self.this_round_scores[
						                        n]) + "\x0F\x02\x0312 votes!")

		if self.which_round == rounds:
			self.endgame()
			return

		self.connection.privmsg(self.chan, "\x02\x0312The score stands at:")
		for nick in self.scores.keys():
			if self.scores[nick] > 0:
				self.connection.privmsg(self.chan,
				                        "\x02\x0313" + nick + "\x0312 with a score of \x0313" + str(
					                        self.scores[nick]) + "\x0312!")

		self.this_round_nicks = []
		self.this_round_acros = []
		self.voted = []
		self.this_round_scores = []

		self.which_round += 1
		self.gen_acro(start_acro + self.which_round - 1)
		self.mode = "ACRO"
		self.connection.privmsg(self.chan, "\x0304\x1FRound " + str(
			self.which_round) + "!\x0F \x0304The new acro is: \x02\x0303" + self.acro)
		threading.Timer(acro_time, self.switch_mode).start()

	def switch_mode(self):
		self.mode = "VOTE"
		self.connection.privmsg(self.chan,
		                        "\x02\x0304Acro time is up! Please vote now on the following choices:")
		for a in range(len(self.this_round_acros)):
			self.connection.privmsg(self.chan, "\x0306\x1F#" + str(
				a) + "\x0F: \x02\x0312" + self.this_round_acros[a])
		threading.Timer(vote_time, self.round).start()

	def startgame(self, message):
		# The following (hopefully) fixes a bug that carries
		# acros and scores across games
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

		threading.Timer(acro_time, self.switch_mode).start()

	def endgame(self):
		msg = self.connection.privmsg
		msg(self.chan, "\x02\x0304The game is over!")
		msg(self.chan, "\x02\x0304Ending scores:")
		for nick in self.scores.keys():
			msg(self.chan,
			    "\x0313\x1F" + nick + "\x0F\x02\x0312 with a score of \x0F\x1F\x0313" + str(
				    self.scores[nick]) + "\x0F\x02\x0312!")

	def on_welcome(self, c, e):
		c.join(self.chan)
		c.privmsg(self.chan,
		          "Hello! Try '/msg " + nick + " !help' for more info. Have fun! :) ")

	def on_privmsg(self, c, e):
		if string.split(e.arguments()[0])[0] == "!help":
			c.privmsg(irclib.nm_to_n(e.source()), help_intro)
			c.privmsg(irclib.nm_to_n(e.source()), help_main01)
			c.privmsg(irclib.nm_to_n(e.source()), help_main02)
			c.privmsg(irclib.nm_to_n(e.source()), help_main03)
			c.privmsg(irclib.nm_to_n(e.source()), help_main04)
			c.privmsg(irclib.nm_to_n(e.source()), help_main05)
		elif string.split(e.arguments()[0])[0] == "!start":
			self.startgame()
		elif string.split(e.arguments()[0])[0] == "!rehash":
			c.privmsg(self.chan, "Restarting...")
			self.start()
		elif string.split(e.arguments()[0])[0] == "!shutdown":
			c.privmsg(self.chan, "Have fun, bye!")
			self.disconnect()
		elif self.on == false:
			c.privmsg(e.source(),
			          "Sorry, no game is currently running. Try '!help'.")
		elif self.mode == "ACRO":
			if self.confirm_acro(string.split(e.arguments()[0])) == false:
				c.notice(irclib.nm_to_n(e.source()),
				         "That does not match the acro. Try again.")
				return
			else:
				if irclib.nm_to_n(e.source()) in self.this_round_nicks:
					c.notice(irclib.nm_to_n(e.source()),
					         "You may not enter more than once.")
					return
				elif e.arguments()[0] not in self.this_round_acros:
					c.notice(irclib.nm_to_n(e.source()),
					         "You've been entered in this round.")
					self.this_round_nicks.append(irclib.nm_to_n(e.source()))
					self.this_round_acros.append(e.arguments()[0])
					self.this_round_scores.append(0)
					return
				else:
					c.notice(irclib.nm_to_n(e.source()),
					         "That acro has already been entered. Please try again.")
					return
		elif self.mode == "VOTE":
			try:
				vote = int(string.split(e.arguments()[0])[0])
				if irclib.nm_to_n(e.source()) not in self.this_round_nicks:
					c.notice(irclib.nm_to_n(e.source()),
					         "You can't vote if you don't participate.")
					return
				if irclib.nm_to_n(e.source()) == self.this_round_nicks[vote]:
					c.notice(irclib.nm_to_n(e.source()),
					         "You can't vote for yourself. Try again.")
					return
				if irclib.nm_to_n(e.source()) not in self.voted:
					self.this_round_scores[vote] += 1
					self.voted.append(irclib.nm_to_n(e.source()))
					c.notice(irclib.nm_to_n(e.source()),
					         "Your vote has been counted.")
					return
			except ValueError:
				pass

	def confirm_acro(self, input):
		if len(input) != len(self.acro):
			return false
		for i in range(len(self.acro)):
			if string.capitalize(input[i])[0] != self.acro[i]:
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


@client.event
@asyncio.coroutine
def on_ready():
	print('Logged in as', client.user.name, client.user.id)


@client.event
@asyncio.coroutine
def on_message(message):
	if message.content.startswith('!acro'):
		yield from client.send_message(message.channel, 'Hye, you called?')

AcroBot('MjIzNjI1MzU2ODAyOTE2MzU0.CrOq7Q.FBqjuX16eUTz214axIpBt_gYduI')