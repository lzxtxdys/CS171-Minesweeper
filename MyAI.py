# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import random

# 0 ： covered cell
# 1-8: number of mines around the cell
# 9: mine

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.rowDimension = rowDimension
		self.colDimension = colDimension
		self.totalMines = totalMines
		self.startX = startX
		self.startY = startY
		self.visited_position = []
		self.board = [[-1 for _ in range(self.rowDimension)] for _ in range(self.colDimension)]
		self.currentX = -1
		self.currentY = -1
		# queue for safe cells
		self.safeCells = []
		# queue for mines
		self.mineCells = []
		self.zeros = []
		self.detected_mines = 0
		self.last_is_not_mine = True
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################


	def getAction(self, number: int) -> "Action Object":
		if self.last_is_not_mine:
			# update the last moved cell
			if self.currentX == -1 and self.currentY == -1:
				self.board[self.startX][self.startY] = number
				self.currentX = self.startX
				self.currentY = self.startY
			else:
				self.board[self.currentX][self.currentY] = number

			# different action based on the number
			if number == 0:
				if (self.currentX, self.currentY) not in self.zeros:
					self.zeros.append((self.currentX, self.currentY))

		self.last_is_not_mine = True

		# clear the zeros
		while self.zeros:
			x, y = self.zeros.pop(0)
			around = self.getAround(x, y)
			for i, j in around:
				if self.board[i][j] == -1:
					# if the cell is al in safe cells or mine cells don't add it
					if (i, j) not in self.safeCells and self.board[i][j] == -1:
						self.safeCells.append((i, j))

		# iterate all visited cells, check surrounding cells
		for x, y in self.visited_position:
			# check 8 surrounding cells
			surronding = self.checkSurronding(x, y)
			if surronding == 1:
				around = self.getAround(x, y)
				for i, j in around:
					if self.board[i][j] == -1:
						if (i, j) not in self.safeCells and self.board[i][j] == -1:
							self.safeCells.append((i, j))
			elif surronding == 2:
				around = self.getAround(x, y)
				for i, j in around:
					if self.board[i][j] == -1:
						self.board[i][j] = 9
						if (i, j) not in self.mineCells:
							self.mineCells.append((i, j))

			# substraction
			for i in range(2):
				x2 = x + i
				y2 = y + 1 - i
				if not self.RangeCheck(x2, y2):
					continue
				if (x2, y2) not in self.visited_position:
					continue
				res = self.checkTwoUncoveredCell(x, y, x2, y2)
				if res:
					around1, around2 = res
					for a, b in around1:
						if (a, b) not in self.safeCells and self.board[a][b] == -1:
							self.safeCells.append((a, b))
					for a, b in around2:
						if (a, b) not in self.mineCells:
							self.board[a][b] = 9
							self.mineCells.append((a, b))

		# clear the safe cells and mine cells
		if self.detected_mines == self.totalMines:
			return Action(AI.Action.LEAVE)
		if self.safeCells:
			x, y = self.safeCells.pop(0)
			self.visited_position.append((x, y))
			self.currentX = x
			self.currentY = y
			return Action(AI.Action.UNCOVER, x, y)
		if self.mineCells:
			x, y = self.mineCells.pop(0)
			self.currentX = x
			self.currentY = y
			self.last_is_not_mine = False
			self.detected_mines += 1
			return Action(AI.Action.FLAG, x, y)

		# if no safe cells or mine cells, guess a cell
		# get a random cell
		x, y = self.getRandomMove()
		self.visited_position.append((x, y))
		self.currentX = x
		self.currentY = y
		return Action(AI.Action.UNCOVER, x, y)



	# 0: Unknown
	# 1: Surrounding cells are all safe
	# 2: Surrounding cells are all mines
	def checkSurronding(self, x, y):
		if not self.RangeCheck(x, y):
			return 0
		playerValue = self.board[x][y]

		if self.board[x][y] > 8:
			return 0

		uncovered = 0
		flagged = 0
		around = self.getAround(x, y)

		for i, j in around:
			boradValue = self.board[i][j]
			if boradValue == -1:
				uncovered += 1
			elif boradValue == 9:
				flagged += 1
		if uncovered == 0:
			return 0
		if playerValue - flagged == uncovered:
			return 2
		if playerValue == flagged:
			return 1
		return 0



	def RangeCheck(self, x, y):
		# check if the cell is within the range of the board
		if x < 0 or y < 0 or x >= self.colDimension or y >= self.rowDimension:
			return False
		return True

	def getAround(self, x, y):
		# get all the cells around the current cell
		around = []
		for i in range(-1, 2):
			for j in range(-1, 2):
				if self.RangeCheck(x + i, y + j):
					around.append((x + i, y + j))
		return around

	def getRandomMove(self):
		# get a random cell to move
		# here can build a priority queue to have a better performance
		for x, y in self.visited_position:
			around = self.getAround(x, y)
			for i, j in around:
				if self.board[i][j] == -1:
					return i, j
		return 0, 0

	def checkTwoUncoveredCell(self, x1, y1, x2, y2):
		num1 = self.board[x1][y1]
		num2 = self.board[x2][y2]
		diffX = x2 - x1
		diffY = y2 - y1
		if abs(diffX) + abs(diffY) != 1:
			return None
		around1 = []
		around2 = []

		for i in range(-1, 2):
			xx1 = x1 - diffX + diffY * i
			yy1 = y1 - diffY + diffX * i
			if self.RangeCheck(xx1, yy1):
				pp1 = self.board[xx1][yy1]
				if pp1 == 9:
					num1 -= 1
				elif pp1 == -1:
					around1.append((xx1, yy1))

			xx2 = x2 + diffX + diffY * i
			yy2 = y2 + diffY + diffX * i
			if self.RangeCheck(xx2, yy2):
				pp2 = self.board[xx2][yy2]
				if pp2 == 9:
					num2 -= 1
				elif pp2 == -1:
					around2.append((xx2, yy2))
		res = None
		if num2 - num1 - len(around2) == 0:
			res = (around1, around2)
		elif num1 - num2 - len(around1) == 0:
			res = (around2, around1)
		return res

