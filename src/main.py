import re
import requests
from enum import Enum


class ChessTrieNode():
	def __init__(self, label):
		self.children = {}
		self.frequency = 0
		self.label = label

	def add_move(self, move):
		self.frequency += 1
		if move not in self.children:
			self.children[move] = ChessTrieNode(move) 			

		return self.children[move]


class ChessTrie():
	def __init__(self):
		self.root = ChessTrieNode('*')

	def add_game(self, moves):
		curr = self.root
		for move in moves:
			curr = curr.add_move(move)
		curr.frequency += 1

	def display(self, curr = None, dep = 0):
		if curr is None:
			curr = self.root

		print('{}{} -> {}'.format('.' * dep, curr.label, curr.frequency))
		for child in sorted(curr.children.values(), key=lambda x: x.frequency, reverse=True):
			self.display(child, dep + 2)


class ColorFilter(Enum):
	WHITE = 'white'
	BLACK = 'black'


class UserDataFetcher():
	ARCHIVE_URL = 'https://api.chess.com/pub/player/{0}/games/archives'

	def get_pgns(self, username, color_filter = None):
		archive_urls = requests.get(self.ARCHIVE_URL.format(username)).json()['archives']

		data = []
		for archive_url in archive_urls:
			data.extend(requests.get(archive_url).json()['games'])

		data.sort(key=lambda x: x['end_time'], reverse=True)

		if color_filter is not None:

			data = list(filter(lambda x: x[color_filter.value]['username'] == username, data))
		pgns = list(map(self.__extract_pgn_from_game_json , data))

		return list(filter(None, pgns)) 

	def __extract_pgn_from_game_json(self, game_json):
		raw_pgn = game_json['pgn']
		maybe_pgn = re.search('(1\. .*$)', raw_pgn)
		result = []
		if not maybe_pgn:
			return result

		pgn_with_timestamps = maybe_pgn.group(1)
		pgn_string = re.sub('{.*?}', '', pgn_with_timestamps)
		moves = re.findall('([a-zA-Z]+[\d]?[#\+]?)', pgn_string)

		if len(moves) % 2 == 1:
			moves.append('NAN')

		for i in range(len(moves) // 2):
			result.append('{}. {} {}'.format(i + 1, moves[2 * i], moves[2 * i + 1]))
		return result


fetcher = UserDataFetcher()
pgns = fetcher.get_pgns('pranetverma', ColorFilter.WHITE)

trie = ChessTrie()

for pgn in pgns[0:50]:
	trie.add_game(pgn[0:3])

trie.display()



