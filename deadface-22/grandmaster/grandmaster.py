import chess
import chess.engine
from pwn import *

# prepare board
def prepare_board(ascii_board):
    """ 
    returns a list of lists
    each list represents a row
    each item in each list is a chess square

    """
    for i in range(len(ascii_board)):
        ascii_board[i] = ascii_board[i].split(' ')
    return ascii_board

# convert board to fen notation
def ascii_to_fen(ascii_board):

    """
    returns a fen notation board
    """
    ascii_board = prepare_board(ascii_board)
    board = ""
    for row in ascii_board:
        fen_row = ""
        empty = 0

        for i in range(len(row)):
            # print("square is", row[i])
            if row[i] == '.' and i==len(row)-1:
                empty+=1
                fen_row+=str(empty)
                break

            if row[i] == '.':
                empty+=1
                continue
            else :
                if empty > 0 :
                    fen_row+=str(empty)
                    
                fen_row += row[i]
                empty = 0

                
                
           
        fen_row+="/"
        board+=fen_row
    return board[:-1]


# establish connection
HOST = "grandmaster.deadface.io"
PORT = 5000
r = remote(ADDRESS, PORT)


BOARD = r.recvrepeatS(timeout=0.9)

# sanitize board
BOARD = BOARD[28:].strip().split("\n")


# initialize stockfish
engine = chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")

# initialize board
board = chess.Board(ascii_to_fen(BOARD))

# find best move in SAN notation
best_move = engine.analysis(board, chess.engine.Limit(time=0.1)).wait().move
best_move = board.san(best_move)
log.success(f"Best Move {best_move}")

# send best move
r.send(best_move.encode())

# recieve flag and close connection
flag = r.recv()
log.success(flag.decode())

engine.quit()
r.close()
