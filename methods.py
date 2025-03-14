import random
from cards_and_messages import *
from aiogram import types

# Handlers Methods


class HandlerM:

    @staticmethod
    def add_to_lobby_with_id(lobby, member_id, username):
        lobby[username] = member_id

    @staticmethod
    def player_in_lobby(username, lobby):
        return username in lobby

    @staticmethod
    def player_is_admin(username, admin):
        return username == admin

    @staticmethod
    async def send_round_panel(bot, id, message):
        round_markup = HandlerM.create_round_keyboard()
        await bot.send_message(id, message, reply_markup=round_markup)

    @staticmethod
    def create_round_keyboard():
        round_markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("1", callback_data="1")
        button2 = types.InlineKeyboardButton("2", callback_data="2")
        button3 = types.InlineKeyboardButton("3", callback_data="3")
        button4 = types.InlineKeyboardButton("4", callback_data="4")
        button5 = types.InlineKeyboardButton("5", callback_data="5")
        end_button = types.InlineKeyboardButton("Конец игры!", callback_data="0")
        round_markup.add(button1, button2, button3, button4, button5)
        round_markup.row(end_button)
        return round_markup



# path Methods
def get_catastrophe_path():
    return "JPG/Катастрофа/" + random.choice(catastrophe)


# just chill method, don't touch him pls
def get_key_of_max_in_dict(input_dict):
    max_value = max(input_dict.values())
    for key, value in input_dict.items():
        if value == max_value:
            return key


# sending methods
async def send_messages_for_players(bot, message, lobby):
    for player in lobby:
        id_ = lobby[player]
        await bot.send_message(id_, message)

async def send_messages_for_all_with_players(bot, message, lobby, markup):
    for player in lobby:
        id_ = lobby[player]
        await bot.send_message(id_, message, reply_markup=markup)


# MEGA SUPER DUPER CLASSES FOR GAME
class VotingM:
    def __init__(self, bot, this_round, players, dp):
        self.bot = bot
        self.this_round = this_round
        self.players = players
        self.dp = dp
        self.count_of_members = len(players)
        self.kicked_players = []

    async def first_voting(self, zero_voting_message):
        for player in self.players:
            id = self.players[player]
            await self.bot.send_message(id, zero_voting_message)

    def get_list_of_voting(self):
        count_of_staying = self.count_of_members // 2
        count_of_banned = self.count_of_members - count_of_staying

        list_of_voting = [0, 0, 0, 0, 0]
        for i in [4, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1]:
            if count_of_banned != 0:
                list_of_voting[i] += 1

                count_of_banned -= 1

        return list_of_voting

    def get_count_of_voting(self):

        list_of_voting = self.get_list_of_voting()
        # пример для 4х игроков [0, 0, 0, 1, 1]

        return list_of_voting[self.this_round - 1]

    def create_voting_keyboard(self):

        markup = types.InlineKeyboardMarkup()
        for player in self.players:
            button = types.InlineKeyboardButton(text=player, callback_data=player)
            markup.add(button)

        return markup

    async def send_voting(self):
        voting_markup = self.create_voting_keyboard()
        await send_messages_for_all_with_players(self.bot, "Голосование", self.players, voting_markup)

    def create_vote_dict(self):
        number_of_votes = {}
        for player in self.players:
            number_of_votes[player] = 0

        return number_of_votes

    def get_number_of_votes(self, number_of_votes, callback):
        for member in self.players:
            if callback.data == member:
                number_of_votes[member] += 1
        return number_of_votes

    def get_result_message(self, number_of_votes):

        results_message = get_results_message(number_of_votes)
        kicked_player = get_key_of_max_in_dict(number_of_votes)

        if self.without_loosers(number_of_votes):
            return f"Результаты голосования:\n{results_message}\n\n" + without_loosers_message
        else:
            return f"Результаты голосования:\n{results_message}\n\n\n" + get_with_looser_message(kicked_player)

    def everyone_voted(self, players, voted):
        return voted == len(players)

    @staticmethod
    def without_loosers(votes):
        if not votes:
            return False

        max_votes = max(votes.values())
        count = 0
        for vote in votes.values():
            if vote == max_votes:
                count += 1
        return count >= 2

    def kick_looser(self, number_of_votes):
        kicked_player = get_key_of_max_in_dict(number_of_votes)
        self.kicked_players.append(self.players[kicked_player])
        del self.players[kicked_player]

        print(f"{kicked_player} был изгнан)")

    @staticmethod
    def without_vote(count_of_votings):
        return count_of_votings == 0

    async def send_to_kicked(self, message):
        for player in self.kicked_players:
            await self.bot.send_message(player, message)

    @staticmethod
    def player_already_vote(username, already_vote):
        already_vote.append(username)
        return already_vote

    @staticmethod
    def player_didnt_vote(player, already_vote):

        return player not in already_vote



class GameM:
    def __init__(self, lobby):
        self.lobby = lobby

    def right_number_of_players(self):
        count_of_players = len(self.lobby)
        return count_of_players <= 16  # and count_of_players >= 4 #Стоит здесь временно ибо как мне в соло тестить то

    @staticmethod
    def find_player_random_cards():
        cards = {
            "special": random.choice(special),
            "baggage": random.choice(baggage),
            "biology": random.choice(biology),
            "health": random.choice(health),
            "job": random.choice(job),
            "fact": random.choice(facts),
            "hobby": random.choice(hobby)
        }
        return cards

    @staticmethod
    def create_cards_group(player_random_cards):
        cards_photo_group = types.MediaGroup()
        for card in player_random_cards:
            card_path = GameM.open_card_photo(card, player_random_cards)
            cards_photo_group.attach_photo(card_path)
        return cards_photo_group

    @staticmethod
    def game_ends(current_round):
        return current_round == 0

    @staticmethod
    def open_card_photo(card, member_random_cards):
        file_name = "JPG/" + str(card) + "/" + member_random_cards[card]
        return open(file_name, "rb")

    @staticmethod
    def get_list_of_cards_about_bunker():
        bunker_cards = []
        for i in range(5):
            card = random.choice(bunkers)
            file_name = "JPG/bunkers/" + str(card)
            bunker_cards.append(file_name)
        return bunker_cards







