import chess
import numpy as np
import time

# —————————————————————————————————————————————————————————————————
# In charge of the artificial intelligence of the ai
# —————————————————————————————————————————————————————————————————
class ChessAgent():

    def __init__(self, board):
        self.board = board

    # Used iterative deepening to calcuate the best move
    def GetMove(self, time_limit):

        timeout = time.time() + time_limit
        depth = 1 # Start out with a depth of 1
        best_move = None

        while(True):
            alpha = float('-inf')
            beta = float('inf')
            best_value_depth = float('-inf')
            best_move_depth = None
            # Find the best move
            for move in self.board.legal_moves:

                # Timeout: return the best value of the last depth iteration
                if(time.time() > timeout):
                    print("Depth: ", depth, " Moves: ", self.board.legal_moves.count())
                    return best_move

                self.board.push(move)
                # The best move is based on future moves of the player and enemy
                score = - self.Negamax(depth - 1, -beta, -alpha)
                self.board.pop()

                if score > best_value_depth:
                    best_value_depth = score
                    best_move_depth = move
                    if score > alpha:
                        alpha = score

            # The search at this depth completed: update the value
            best_move = best_move_depth
            depth += 1

    # Algorithm based on pseudocode from https://www.chessprogramming.org/Alpha-Beta
    # This is a 'soft fail' alpha beta that allows scores outside the alpha beta bounds
    # Further reading: https://www.chessprogramming.org/Fail-Soft
    def Negamax(self, depth, alpha, beta):
        # Reach the end of the tree
        if depth == 0:
            return self.QuiescenceSearch(alpha, beta)

        best_value = float('-inf')
        # Find the best move
        for move in self.board.legal_moves:
            self.board.push(move)
            # The best move is based on future moves of the player and enemy
            score = - self.Negamax(depth - 1, -beta, -alpha)
            self.board.pop()
            if score >= beta:
                return score

            if score > best_value:
                best_value = score
                if score > alpha:
                    alpha = score
        return best_value

    # Evaluates the final move to see if it is a 'quiet' move, which
    # prevents the algorithm from choosing moves stupidly because it dosesn't
    # take into account the next move. It helps avoid the 'horizon effect'
    # Further reading: https://www.chessprogramming.org/Quiescence_Search
    # Pseudo code based on chessprogramming.org
    def QuiescenceSearch(self, alpha, beta):

        # Initial evaluation when there are no captures
        initial = self.Evaluate();

        if initial >= beta:
            return beta

        if alpha < initial:
            alpha = initial

        for move in self.board.legal_moves:
            if self.board.is_capture(move):
                self.board.push(move)
                score = -self.QuiescenceSearch(-beta, -alpha)
                self.board.pop()

                if score >= beta:
                    return beta
                
                if score > alpha:
                    alpha = score

        return alpha

    # Get the piece values by summing up all pieces
    # Note, white is positive
    def BoardPiecesValue(self):
        piece_map = self.board.piece_map()
        total_value = 0
        for _, piece in piece_map.items():

            # Map from piece_type to a value
            piece_to_value = {
                1: 100,
                2: 300,
                3: 300,
                4: 500,
                5: 900,
                6: 2000
            }
            # Add white scores and subtract black scores
            if piece.color:
                total_value += piece_to_value.get(piece.piece_type, "nan")
            else:
                total_value -= piece_to_value.get(piece.piece_type, "nan")
        return total_value

    # Gets the mobility of the players at the current board
    def GetMobility(self):
        # Get the mobility of the current player and their opponent
        total_value = self.board.legal_moves.count()

        self.board.push(chess.Move.null())
        total_value -= self.board.legal_moves.count()
        self.board.pop()

        # If the current player was white, then the legal moves is positive
        if self.board.turn:
            return total_value
        else:
            return -total_value

    # Reduces the current state of the board into a heuristic value for the agent to make decision from
    def Evaluate(self):
        total_value = self.BoardPiecesValue() + self.GetMobility()

        total_value += self.board.legal_moves.count() if self.board.turn else self.board.legal_moves.count()

        # Negate the score if it is black's turn
        return total_value if self.board.turn else -total_value

# —————————————————————————————————————————————————————————————————
# Manages the chess game
# —————————————————————————————————————————————————————————————————
class ChessManager():

    def __init__(self):
        self.board = chess.Board()
        self.board_size = 8
        self.square_dict = {chess.SQUARE_NAMES[i]: i for i in range(64)}
        self.game_end = False

    def PrintBoard(self):
        piece_map = self.board.piece_map()
        print("a b c d e f g h")
        print("———————————————")
        for row in range(self.board_size):
            for col in range(self.board_size):

                # Piece index calculates the pieces based on row and column, from 0 to 63
                piece_index = row * self.board_size + col

                # If there is a piece, print it, otherwise print an empty square
                if piece_index in piece_map:
                    print(self.PieceToUnicode(piece_map[piece_index]) + ' ', end='')
                else:
                    print(u"\u25A1 ", end='')
            print("|", row + 1 , " ")
        print("")

    # Print all possible moves: eg From: h8 To: h6
    def PrintMoves(self):
        for move in self.board.legal_moves:
            print(" From:", chess.SQUARE_NAMES[move.from_square], " To:", chess.SQUARE_NAMES[move.to_square])

    # Converts a piece to the unicode character to make it look nice
    def PieceToUnicode(self, piece):
        piece_to_unicode = {
            "P": u"\u2659",
            "N": u"\u2658",
            "B": u"\u2657",
            "R": u"\u2656",
            "Q": u"\u2655",
            "K": u"\u2654",
            "p": u"\u265f",
            "n": u"\u265e",
            "b": u"\u265d",
            "r": u"\u265c",
            "q": u"\u265b",
            "k": u"\u265a"
        }
        return piece_to_unicode.get(piece.symbol(), "ERROR")

    # Get a random availible move
    def GetRandomMove(self):
        if self.board.legal_moves.count() == 0:
            return None
        else:
            return np.random.choice(list(self.board.legal_moves))

    # Get input from the player to move
    def GetPlayerMove(self):
        move = None
        while(not move in self.board.legal_moves):
            print("Enter from square:")
            from_square = str(input())
            print("Enter to square:")
            to_square = str(input())
            if from_square in self.square_dict and to_square in self.square_dict:
                move = chess.Move(self.square_dict[from_square], self.square_dict[to_square])

        return move

    # Push the move onto the board, or if there is none, handle game end
    def Move(self, move):
        if move == None:
            if self.board.turn:
                print("Black Wins!")
            else:
                print("White Wins!")
            game_end = True
        else:
            self.board.push(move)

    # Plays the game
    def StartGame(self):
        chess_agent = ChessAgent(self.board)
        while(not self.game_end):
            #self.chess_engine.PrintMoves()
            self.PrintBoard()
            self.Move(chess_agent.GetMove(3))

chess_manager = ChessManager()
chess_manager.StartGame()