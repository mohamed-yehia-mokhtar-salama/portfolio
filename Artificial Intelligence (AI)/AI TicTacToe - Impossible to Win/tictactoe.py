"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Counting occurrences of X and O in the board
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return X if x_count <= o_count else O  # Returning X if it's X's turn and O otherwise

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] == EMPTY}  # Creating set comprehension for empty cells

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    Raises an exception for invalid moves (out-of-bounds or non-empty cells).
    """
    i, j = action
    # Raising exception if move is out of bounds
    if i < 0 or i >= 3 or j < 0 or j >= 3:
        raise IndexError("Move out of bounds")

    # Raising exception if cell is already occupied
    if board[i][j] is not EMPTY:
        raise ValueError("Cell already occupied")

    new_board = [row[:] for row in board]  # Creating a deep copy of the board
    new_board[i][j] = player(board)  # Placing the current player's symbol in the chosen cell
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        # Checking rows and columns for a winning condition
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][0] 
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i] 
    
    # Checking diagonals for a winning condition
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None or all(EMPTY not in row for row in board):  # Checking if there's a winner or if the board is full
        return True 
    return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)  # Determining the winner of the board
    if win == X:
        return 1 
    elif win == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):  # Checking if the game is over
        return None 

    current_player = player(board)

    if current_player == X:
        value, move = max_value(board)  # Using max_value to find the optimal move
    else:
        value, move = min_value(board)  # Using min_value to find the optimal move

    return move  # Returning the optimal move

def max_value(board):
    # Returning the utility value and no move if the game is over
    if terminal(board):
        return utility(board), None
    
    v = -math.inf 
    best_action = None 
    for action in actions(board):
        min_v, _ = min_value(result(board, action))  # Calculating the minimum value for the result of each action
        if min_v > v:
            v = min_v  # Updating v with the minimum value
            best_action = action  # Updating the best action with the current action
    return v, best_action

def min_value(board):
    # Returning the utility value and no move if the game is over
    if terminal(board):
        return utility(board), None
    
    v = math.inf
    best_action = None
    for action in actions(board): 
        max_v, _ = max_value(result(board, action))  # Calculating the maximum value for the result of each action
        if max_v < v:
            v = max_v  # Updating v with the maximum value
            best_action = action  # Updating the best action with the current action
    return v, best_action