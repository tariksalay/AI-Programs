import numpy as np
import pygame
import sys 
import random
import math 
from mcts import mcts

BLUE = (0,0,255) #rgb values
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)


ROW_COUNT = 6 #since this is given as variable you can choose the board's size 
COLUMN_COUNT = 7 #and the algorithm below would be fine with it

PLAYER = 0
AI = 1

PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4
EMPTY = 0

def create_board(): #to create the board 7x6
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece #to fill the board with Players's move such as 1 and 2

def is_valid_location(board, col): #to see if there is an empty spot on the top row
	return board[ROW_COUNT-1][col] == 0 #then we can drop a piece there

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0: #if the current row is empty 
			return r

def print_board(board): #for gravity
	print(np.flip(board, 0))

def winning_move(board, piece):
	#check horizontal 
	for c in range(COLUMN_COUNT-3): #horizontally, it can't start after col_count-3 and have 4 connections
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True
	#check vertical
	for c in range(COLUMN_COUNT): #vertically, it can't start below of column_count-3 and have 4 connections
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True	
	#check positive sloped diagonal
	for c in range(COLUMN_COUNT-3): 
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True	
 	#check negative sloped diagonal
	for c in range(COLUMN_COUNT-3): 
		for r in range(3, ROW_COUNT): #3rd row until the end. cannot start before 3rd row
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True	

def evaluate_window(window, piece):
	score = 0;
	opp_piece = PLAYER_PIECE #opponent piece
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) ==3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2							

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4 #if opponent has 3 in a row, for preference, block him

	return score 

def score_position(board, piece):
	score = 0 #as an initial value

	#having the center pieces are important because it allows more opportunity
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])] #//2 to have middle 
	center_count = center_array.count(piece)
	score += center_count * 3

	#horizontal scoring
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])] #":" isused to go over every column 
		for c in range (COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window,piece)

	#vertical scoring
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]		
			score += evaluate_window(window,piece)


	#scoring positively sloped diagonal
	for r in range(ROW_COUNT-3): #cut off at the top
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)] #going diagonal
			score += evaluate_window(window,piece)

	#scoring for negative sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window,piece)

	return score

def is_terminal_node(board): #if one of the players won, or board is full
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minmax(board, depth, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal: #None since we do not know which column produces those
			if winning_move(board, AI_PIECE):
				return (None, 999999)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -999999)
			else: #full board
				return (None, 0)
		else: #depth == 0
			return (None, score_position(board, AI_PIECE))

	if maximizingPlayer:
		value = -math.inf #negative infinity
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy() #we would want to copy the location to prevent errors while calling this recursively
			drop_piece(b_copy, row, col, AI_PIECE) 
			new_score = minmax(b_copy, depth-1, False)[1] #calling recursively 
			if new_score > value: #we want to get max points for AI
				value = new_score
				column = col
		return column, value

	else:
		value = math.inf #positive infinity
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy() 
			drop_piece(b_copy, row, col, PLAYER_PIECE) 
			new_score = minmax(b_copy, depth-1, True)[1] 		 	
			if new_score < value: #we want to reach min points for Player
				value = new_score
				column = col
		return column, value

def get_valid_locations(board): #to keep track of the valid locations in a list
	valid_locations = []
	for col in range (COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):
	valid_locations = get_valid_locations(board)
	best_score = -10000 #to not make AI confused
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy() #in order to memory location correction
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE)) #with width = 0, and extra SQUARESIZE added since we want an extra line
			pygame.draw.circle(screen, WHITE, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
			
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			if board[r][c] == PLAYER_PIECE: #red starts first
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] ==AI_PIECE:
			 	pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()			

board = create_board()
print_board(board)
game_over = False #false as initial state


pygame.init()

SQUARESIZE = 100 #pixels

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE #to have an extra place to see the ball

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()
turn = random.randint(PLAYER, AI) #better UI to start randomly between real player and AI

#main
while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION: #to keep track of the mouse motion on the top
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0] #center of the circle
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			#print(event.pos) #to see where I clicked on the screen
			pygame.draw.rect(screen, WHITE, (0,0, width, SQUARESIZE))	
			#Ask for the first player's input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE)) #Divide the X position by 100 or whatever squaresize to pick which column we are dropping a piece

				if is_valid_location(board,col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					if winning_move(board, PLAYER_PIECE):
						print("Player 1 Wins!")
						game_over = True

					turn += 1
					turn = turn % 2	

					print_board(board)
					draw_board(board)
						
	#Ask for the second player's input
	if turn == AI and not game_over:

		#col = random.randint(0, COLUMN_COUNT-1) #0 to 6 in our example
		#col = pick_best_move(board, AI_PIECE)
		col, minmax_score = minmax(board, 3, True) #whatever depth is given, in other words how further should my AI look, 7^n


		if is_valid_location(board,col):
			pygame.time.wait(750) #to give a little break for better User Interface
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)

			if winning_move(board, AI_PIECE):
				print("Player 2 Wins!")
				game_over = True


			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2 #to take reminder

	if game_over:
		pygame.time.wait(2222) #exiting in 3 seconds
