# description
DEADFACE has written another challenge to test the skills of new recruits. White to move. (Please use Short Algebraic Notation)

`grandmaster.deadface.io:5000`

The flag will be in the format. `flag{.*}`.

# problems
when we connect to the host we're sent an ASCII chess board and asked to find the move that forces mate in 2 like so :
```text
Which move forces mate in 2?
. . R . R . . .
K p . k . . . .
. . p p p p . .
p r . . . r . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. Q . . . . . B
\n
```

let's break up the problem into smaller problems, we're going to use python to solve this challenge
## problem 1: receiving data
the data is being sent over to us in the form of bytes, and we only need the ASCII chess board so we need to remove the text string and the whitespace surrounding the board
but first let's set up a connection to the socket, we're going to use `pwntools` library
```python
from pwntools import *
# establish connection
HOST = "grandmaster.deadface.io"
PORT = 5000

r = remote(HOST, PORT)
```
now let's reveive and sanitize the board (removing text and whitespace)
```python
BOARD = r.recvrepeatS(timeout=0.9)

# sanitize board
BOARD = BOARD[28:].strip().split("\n")
```
the `recvrepeatS()` function receives data untill the specified timeout or an EOF, here i set the timeout to 0.9 which is enough to receive the board, the function then decodes the received bytes to string type, so now we have the board as a list of strings
```python
['. . . . . . B .', '. . . K . . p N', '. . . . N . . .', '. R p . . k . p', '. . Q . . . b r', '. . . . . p . .', '. r . b . . . .', 'B . n . . . R .']
```

## problem 2: board representation
of course the board is useless to us in that form, and finding a best move is very difficult, luckily there's a library that aids with chess related stuff !
let's import `chess` library
```python
import chess
```
`chess` has a `Board` class that we can use to initialize a chess board from any position we want, **BUT**, it only accepts the [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) notation of the board position, which introduces a new problem

## problem 3: converting ASCII board to FEN
by reading the wikipedia page you should learn how to use the FEN notation, now we'll write a function that does the job for us.
BUT first, we can transform the board to a new structure that's easier to deal with, so instead of a list of strings let's make the board a list of lists, 
each list represents a row and contains characters, where each character represents a square on the board
```python
def prepare_board(ascii_board):

	"""
	
	returns a list of lists
	
	each list represents a row
	
	each item in each list is a chess square
	
	  
	
	"""
	
	for i in range(len(ascii_board)):
	
		ascii_board[i] = ascii_board[i].split(' ')
	
	return ascii_board
```
```python

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
```

and putting it all together
```python
board = chess.Board(ascii_to_fen(BOARD))
```
now that we have a board ready we arrive at the final major problem

## problem 4: finding the best move
writing logic to find the best move is a lengthy process and would produce multiple solutions that might not be accepted by the bot
so it's easier that we summon an engine and let it find the best move for us !

luckily stockfish is an open source chess engine that's just right for the job

> i won't go into the steps of installing stockfish on the system, as it's beyond the scope of this writeup

`chess` library provides a module that serves as an interface to communicate with engines
```python
import chess.engine
```
now let's initialize stockfish 
```python
engine = chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")
```
by reading through the docs we can find a method `analysis` that takes a `Board` instance and starts analyzing the position, we give it a timeout because we need to be quick before the bot rejects our solution and we call the `wait()` method which returns a `BestMove` object.
we can take the `move` attribure from that object and we have our best move !
```python
best_move = engine.analysis(board, chess.engine.Limit(time=0.1)).wait().move
```
we still need to provide it in Short Algebraic Notation, so we call `board.san()` on it
```python
best_move = board.san(best_move)
```

all that's left is to send the best move as a byte string with `r.send()`, receive the flag with `r.recv()`, quit the engine and close connection
```python
r.send(best_move.encode())
# recieve flag and close connection
flag = r.recv()
log.success(flag.decode())

engine.quit()

r.close()
```

# putting it all together
the final script resulting
```python
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
```

i hope you like my writeup, i welcome any feedback so i can improve my writeup process