import logging
import discord
import discord.ui
import asyncio
import random
import time
import sys

# todo
# double submission FIXED
# double votes OK
# self votes FIXED.
# too late votes
# start with configurations FIXED?
# Result of round 4 of 5 should list mine with 0 points.
# more compact score table
log = logging.getLogger(__name__)
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

client = discord.Client(intents=intents)

true = 1
false = 0

def_acro_time = 45
def_vote_time = 30
def_start_acro = 3
def_inc_acro = 0
def_rand_acro = 2
def_rounds = 7

#vote_time = 30
#start_acro = 3
#inc_acro = 1
#acro_time = 45
#rounds = 5

# acro_time = 20
# rounds = 2
# vote_time = 15
total_weight = 70
weight = [3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 2, 2, 1, 2, 2]
# A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']

allow_doubles = true  # Allow the same letter twice in a row
allow_triples = false  # Allow the same letter three times in a row

chanowner = "Kazak-"
botmaster = "Kazak-"
nick = "AcroBot"

help = [
    "How to play acro: At the start of each round I will give you an acro (for example: lmao). You then have to make up a phrase to fit that acro (for example: leather makes ankles oily).",
    "You enter your acro by typing /msg " + nick + " <your answer>",
    "After the alotted time has passed, I will display a numbered list of all the acros entered and a vote will then be held to determine the winner. You must then pick your favourite acro and vote for it.",
    "You submit your vote by typing ctrl+k and messaging " + nick + " <your vote> (note: you only have to type the number of your vote, for example /msg " + nick + " 5)",
    f"Usage: !start [submission_time_in_seconds [vote_time_in_seconds [number_of_rounds [start_acro_length [acro_increment_per_round [length_max_random_per_round]]]]] default is !start {def_acro_time} {def_vote_time} {def_rounds} {def_start_acro} {def_inc_acro} {def_rand_acro}"
]


# END CONFIGURATION


class MyModal(discord.ui.Modal, title="Solution"):
    answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.short)

    def __init__(self, acro):
        """

        :type acro: AcroBot
        """
        self.acro = acro
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        # interaction.response.defer()
        answer = self.answer.value
        userid = interaction.user.id
        username = interaction.user.name
        print(f"on_submit {username} {answer}")
        log.info(f"on_submit {username} {answer}")
        if acro.mode == "ACRO":

            if acro.confirm_acro(answer.split()) == false:
                response = f"Letters don't match the acro '{acro.acro}'. Try again."
                print(f"SENT {username} {response}")
                await interaction.response.send_message(response, ephemeral=True)
                return
            else:
                if username in acro.this_round_nicks:
                    response = "Can't send more than one acro in the same round."
                    print(f"SENT {username} {response}")
                    await interaction.response.send_message(response, ephemeral=True)
                    return
                elif answer not in acro.this_round_acros:
                    response = f"ACRO from {interaction.user.name} '{self.answer.value}' noted!"
                    print(f"SENT {username} {response}")
                    await interaction.response.send_message(response, ephemeral=True)
                    acro.this_round_ids.append(userid)
                    acro.this_round_nicks.append(username)
                    acro.this_round_acros.append(answer)
                    acro.this_round_scores.append(0)
                    return
                else:
                    response="That acro has already been entered. Please try again."
                    print(f"SENT {username} {response}")
                    await interaction.response.send_message(response, ephemeral=True)

                    return
        else:
            response = f"Too late mate. '{acro.acro}' '{interaction.user.name}' '{self.answer.value}'!"
            print(f"NOT SENT {username} {response}")
            response = f"{interaction.user.name}'s late solution: '{self.answer.value}'"
            print(f"SENT {username} {response}")
            await interaction.response.send_message(response)


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


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

    async def acro_mode(self, message):
        print('Acro mode start')
        await self.reset_round()
        self.gen_acro(self.start_acro + (self.which_round-1) * self.inc_acro + random.randint(0, self.rand_acro))
        self.mode = "ACRO"
        embed = discord.Embed(title=f"Round {self.which_round} of {self.rounds}", description=f"The new acro is",
                              color=0x800000)
        embed.add_field(name=self.acro, value=f"Round length {self.acro_time} seconds", inline=False)
        buttonview = discord.ui.View()
        btn = discord.ui.Button(label="I've got one!", custom_id="join", style=discord.ButtonStyle.blurple)

        async def my_callback_joinbutton(interaction):
            print(f"mycallbackbutton {message.author.name} {btn.custom_id}")
            log.info(f"mycallbackbutton {message.author.name} {btn.custom_id}")
            dialog = MyModal(self)
            dialog.title = f"Your solution to {self.acro}?"
            await interaction.response.send_modal(dialog)

        btn.callback = my_callback_joinbutton
        buttonview.add_item(btn)
        await message.channel.send(embed=embed, view=buttonview)
        print('Acro mode end')

        # self.which_round += 1
        # await message.channel.send(
        #    "Round " + str(self.which_round) + "/" + str(rounds) + "! The new acro is: " + self.acro)
        # await asyncio.sleep(acro_time)
        # await self.vote_mode(message)

    async def reset_round(self):
        self.this_round_nicks = []
        self.this_round_ids = []
        self.this_round_acros = []
        self.voted = []
        self.this_round_scores = []

    async def announce_aggregate_scores(self, message):
        #for nick in self.scores.keys():
        #    if self.scores[nick] > 0:
        #        await message.channel.send(nick + " with a score of " + str(self.scores[nick]) + "!")
        embed = discord.Embed(title=f"Aggregated after {self.which_round} of {self.rounds}",
                              description="",
                              color=0x000080)
        for nick in self.scores.keys():
            #if self.scores[nick] > 0:
            embed.add_field(name=nick, value=f"**{self.scores[nick]}** points", inline=False)
        await message.channel.send(embed=embed)

    async def announce_round_results(self, message):
        embed = discord.Embed(title=f"Result of round {self.which_round} of {self.rounds}",
                              description="",
                              color=0x000080)
        for n in range(len(self.this_round_nicks)):
            #if self.this_round_scores[n] > 0:
            embed.add_field(name=f'{self.this_round_nicks[n]} **+{self.this_round_scores[n]}**',
                            value=f"'{self.this_round_acros[n]}'", inline=False)
        await message.channel.send(embed=embed)

    async def accumulate_round_scores(self):
        for n in range(len(self.this_round_nicks)):
            if self.this_round_nicks[n] in self.scores:
                self.scores[self.this_round_nicks[n]] += self.this_round_scores[n]
            else:
                self.scores[self.this_round_nicks[n]] = self.this_round_scores[n]

    async def vote_mode(self, message):
        print('Vote mode start')
        self.mode = "VOTE"

        selview = discord.ui.View()

        embed = discord.Embed(title=f"Vote for round {self.which_round} of {self.rounds}", description=f"The acro was",
                              color=0x008000)
        sel = discord.ui.Select(custom_id='vote', placeholder="Pick the best!")
        if len(self.this_round_acros) == 0:
            embed.add_field(name=self.acro, value=f"No solutions submitted!", inline=False)
        else:
            embed.add_field(name=self.acro, value=f"Vote time is {self.vote_time} seconds", inline=False)
            for n in range(len(self.this_round_acros)):
                sel.add_option(label=self.this_round_acros[n], value=str(n))

        # btn = discord.ui.Button(label="I've got one!", custom_id="join", style=discord.ButtonStyle.blurple)

        async def my_callback_voteselect(interaction):
            print(f"my_callback_voteselect {message.author.name} {sel.values[0]}")
            log.info(f"my_callback_voteselect {message.author.name} {sel.values[0]}")
            vote = int(sel.values[0])
            votecount = len(self.this_round_nicks)
            print(f"self.this_round_nicks: '{self.this_round_nicks}'  vote: '{vote}'")
            print(f"interaction.user.name '{interaction.user.name}' == self.this_round_nicks[vote]: '{self.this_round_nicks[vote]}'  vote: '{vote}'")
            if vote < 0 or vote > votecount - 1:
                await interaction.response.send_message(
                    f"Invalid vote, pick one between 1 and {votecount}, but you can't vote for yourself.",
                    ephemeral=True)
            #elif interaction.user.id not in self.this_round_ids:
            #    await interaction.response.send_message("You can't vote if you don't participate.", ephemeral=True)
            elif interaction.user.name == self.this_round_nicks[vote]:
                await interaction.response.send_message("You can't vote for yourself. Try again.", ephemeral=True)
            elif interaction.user.id in self.voted:
                await interaction.response.send_message("You can only vote once.", ephemeral=True)
            else:
                self.this_round_scores[vote] += 1
                self.voted.append(interaction.user.id)
                await interaction.response.send_message("Your vote has been counted.", ephemeral=True)

        sel.callback = my_callback_voteselect
        selview.add_item(sel)
        if len(self.this_round_acros) == 0:
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(embed=embed, view=selview)

        # await message.channel.send("Acro time is up! Please vote now on the following choices:")
        # await message.channel.send(f'/msg {client.user.name} #votenumber in {acro_time} seconds to vote.')
        # for a in range(len(self.this_round_acros)):
        #    await message.channel.send("#" + str(a + 1) + ": " + self.this_round_acros[a])

        if len(self.this_round_acros) > 0:
            await asyncio.sleep(self.vote_time)
        self.mode = ""
        # await message.channel.send("Voting time is up!")
        await self.accumulate_round_scores()
        await self.announce_round_results(message)

    async def startgame(self, message):
        # Reset everything when starting a new game
        self.scores = {}
        self.this_round_ids = []
        self.this_round_nicks = []
        self.this_round_acros = []
        self.voted = []
        self.this_round_scores = []

        self.which_round = 1
        self.on = true
        self.mode = "ACRO"

        await message.channel.send('Starting a new game in 5-4-3-2-1! Get Ready!')
        await asyncio.sleep(5)
        # embed.set_footer(text=f"Round length {acro_time} seconds")
        # await message.channel.send(f'Round {self.which_round}!')
        # await message.channel.send('The new acro is: ' + self.acro)
        # await message.channel.send(f'/msg {client.user.name} [your answer] in {acro_time} seconds.')

        for self.which_round in range(1, self.rounds + 1):
            if self.which_round > 1:
                await self.announce_aggregate_scores(message)
            await self.acro_mode(message)
            await asyncio.sleep(self.acro_time)
            await self.vote_mode(message)
        await self.endgame(message)

    async def endgame(self, message):
        embed = discord.Embed(title=f"GAME OVER",
                              description="Final score",
                              color=0xA0A0A0)

        sortedlist = sorted(self.scores.items(), key=lambda item: item[1])
        for name, score in sortedlist:
            embed.add_field(name=f'{name}', value=f"{score} points", inline=False)
        await message.channel.send(embed=embed)

    # @asyncio.coroutine
    async def on_privmsg(self, channel, message):
        if message.author.id == client.user.id:
            return

        log.info(f"On privmsg {channel} {message.author} {message.content}")

        if message.content.startswith("!help"):
            await channel.send(help[0])
            await channel.send(help[1])
            await channel.send(help[2])
            await channel.send(help[3])
            await channel.send(help[4])
            await channel.send("Try !start")

        if message.content.startswith("!testselect"):
            log.info("!testselect")
            s = discord.ui.Select(custom_id="testselect", placeholder="Vote Now", options=[
                discord.SelectOption(label="SomethingSomething1", value="1"),
                discord.SelectOption(label="SomethingSomething2", value="2"),
                discord.SelectOption(label="SomethingSomething3", value="3"),
                discord.SelectOption(label="SomethingSomething4", value="4"),
            ])

            async def my_callback(interaction):
                log.info("mycallback")
                print("mycallback")
                await interaction.response.send_message(f"{interaction.user.name} chose {s.values[0]}")

            s.callback = my_callback
            v = discord.ui.View()
            v.add_item(s)
            await message.channel.send("Select Test", view=v)

        if message.content.startswith("!testinput"):
            log.info("!testinput")
            vtext = discord.ui.View()
            btn = discord.ui.Button(label="Yes, I want to submit a solution", custom_id="join")

            async def my_callback_button(interaction):
                print(f"mycallbackbutton {message.author.name} {btn.custom_id}")
                log.info(f"mycallbackbutton {message.author.name} {btn.custom_id}")
                await interaction.response.send_modal(MyModal(self))

            btn.callback = my_callback_button
            vtext.add_item(btn)
            await message.channel.send("Wanna join this round?", view=vtext)

        elif message.content.startswith("!start"):
            s = message.content.split()
            self.vote_time = def_vote_time
            self.acro_time = def_acro_time
            self.rounds = def_rounds
            self.start_acro = def_start_acro
            self.inc_acro = def_inc_acro
            self.rand_acro = def_rand_acro


            print(f"Start command: {message.content} = {s}")
            if len(s) > 1 and check_int(s[1]) and int(s[1]) >= 10 and int(s[1]) < 86400:
                self.acro_time = int(s[1])
            if len(s) > 2 and check_int(s[2]) and int(s[2]) >= 10 and int(s[2]) < 86400:
                self.vote_time = int(s[2])
            if len(s) > 3 and check_int(s[3]) and int(s[3]) > 0 and int(s[3]) < 100:
                self.rounds = int(s[3])
            if len(s) > 4 and check_int(s[4]) and int(s[4]) > 1 and int(s[4]) < 100:
                self.start_acro = int(s[4])
            if len(s) > 5 and check_int(s[5]) and int(s[5]) >= 0 and int(s[5]) < 5:
                self.inc_acro = int(s[5])
            if len(s) > 6 and check_int(s[6]) and int(s[6]) >= 0 and int(s[6]) < 5:
                self.rand_acro = int(s[6])
            await message.channel.send(f"Starting game with acro_time={self.acro_time} vote_time={self.vote_time} rounds={self.rounds} start_acro={self.start_acro} inc_acro={self.inc_acro} rand_acro={self.rand_acro}")
            await self.startgame(message)
        elif message.content.startswith("!stop"):
            await self.endgame(message)
        elif message.content.startswith("!shutdown"):
            await channel.send("Have fun, bye!")
            self.disconnect()
        # elif self.mode == "ACRO":
        #    return await self.acrosubmission(message)
        # elif self.mode == "VOTE":
        #    await self.votesubmission(message)

    async def votesubmission(self, message):
        try:
            if message.content.startswith("#"):
                vote = int(message.content[1:])
            else:
                vote = int(message.content)
            votecount = len(self.this_round_nicks)
            if vote < 1 or vote > votecount:
                await message.channel.send(
                    f"Invalid vote, pick one between 1 and {votecount}, but you can't vote for yourself.")
            elif message.author.id not in self.this_round_nicks:
                await message.channel.send("You can't vote if you don't participate.")
            elif message.author.id == self.this_round_nicks[vote - 1]:
                await message.channel.send("You can't vote for yourself. Try again.")
            elif message.author.id in self.voted:
                await message.channel.send("You can only vote once.")
            else:
                self.this_round_scores[vote - 1] += 1
                self.voted.append(message.author.id)
                await message.channel.send("Your vote has been counted.")
        except ValueError:
            pass

    async def acrosubmission(self, message):
        if self.confirm_acro(message.content.split()) == false:
            await message.channel.send("Letters don't match the acro. Try again.")
            return
        else:
            if message.author.id in self.this_round_nicks:
                await message.channel.send("Can't send more than one acro.")
                return
            elif message.content not in self.this_round_acros:
                await message.channel.send("Accepted acro.")
                self.this_round_ids.append(message.author.id)
                self.this_round_nicks.append(message.author.name)
                self.this_round_acros.append(message.content)
                self.this_round_scores.append(0)
                return
            else:
                await message.channel.send("That acro has already been entered. Please try again.")
                return

    def confirm_acro(self, input):
        return True
        # For Essex

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
async def on_ready():
    # await client.change_status(game=discord.Game(name="Acro, motherfucker!"))
    print('Logged in as', client.user.name, client.user.id)


@client.event
async def on_message(message):
    await acro.on_privmsg(message.channel, message)


import config
acro.run(config.TOKEN)
