import chess
import chess.uci
import numpy as np
import time

# Michael Yoshimura

# —————————————————————————————————————————————————————————————————
# In charge of the artificial intelligence of the ai
# —————————————————————————————————————————————————————————————————
class ChessAgent():

    def __init__(self, board):
        self.board = board

    # Use iterative deepening to calcuate the best move
    def GetMove(self, time_limit):
        ordered_moves = [move for move in self.board.legal_moves] # Initially, we have unordered moves
        # If we have no moves, return (end of game)
        if len(ordered_moves) == 0:
            return None

        timeout = time.time() + time_limit
        depth = 1 # Start out with a depth of 1
        best_move = ordered_moves[0]
        best_score = float('-inf')

        while(True):
            aspiration_width = 10
            alpha = float('-inf') if best_score == float('-inf') else best_score - aspiration_width
            beta = float('inf') if best_score == float('-inf') else best_score + aspiration_width

            # Represents the best scores of a certain depth
            best_score_depth = float('-inf')
            best_move_depth = best_move
            move_scores = [] # Helps to order the moves from best to worst

            # Find the best move
            for move in ordered_moves:
                # Timeout: return the best value of the last depth iteration
                if(time.time() > timeout):
                    if depth == 1: # If the comuter needs more time to do a base calulation, then allocate more time
                        timeout += 1
                    else:
                        print("Depth: ", depth, " Moves: ", self.board.legal_moves.count(), "A Score: ", best_score)
                        return best_move

                # The best move is based on future moves of the player and enemy
                self.board.push(move)
                score = - self.Negamax(depth - 1, -beta, -alpha)

                # A catch for if the aspiration windows fail initially
                if(score >= beta):
                    beta = float('inf')
                    score = - self.Negamax(depth - 1, -beta, -alpha)
                if(score <= alpha):
                    alpha = float('-inf')
                    score = - self.Negamax(depth - 1, -beta, -alpha)

                self.board.pop()

                move_scores.append((move, score))

                if score > best_score_depth:
                    best_score_depth = score
                    best_move_depth = move
                    alpha = max(score, alpha)

            # For the next deepening, sort the moves based on the best in this deepening in order to make the alpha beta algorithm process faster
            ordered_moves = [move for (move, score) in sorted(move_scores, reverse=True, key=lambda x: x[1])]

            # The search at this depth completed: update the value
            best_move = best_move_depth
            best_score = best_score_depth
            depth += 1

    # Calculates the best move to a certain depth
    def GetMoveDepth(self, depth):
        start_time = time.time()
        # If we have no moves, return (end of game)
        if self.board.legal_moves.count() == 0:
            return None

        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        # Find the best move
        for move in self.board.legal_moves:
                    
            # The best move is based on future moves of the player and enemy
            self.board.push(move)
            score = - self.Negamax(depth - 1, -beta, -alpha)
            self.board.pop()
            if score > best_score:
                best_score = score
                best_move = move
                alpha = max(score, alpha)

        print("Time: ", time.time() - start_time, " Moves: ", self.board.legal_moves.count(), "Score: ", best_score)
        return best_move

    # Algorithm based on pseudocode from https://www.chessprogramming.org/Alpha-Beta
    # This is a 'soft fail' alpha beta that allows scores outside the alpha beta bounds
    # Further reading: https://www.chessprogramming.org/Fail-Soft
    def Negamax(self, depth, alpha, beta):
        # Reach the end of the tree
        if depth == 0:
            return self.DepthLimitedQuiescenceSearch(alpha, beta, 3)

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
                alpha = max(score, alpha)

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

        alpha = max(alpha, initial)

        for move in self.board.legal_moves:
            if self.board.is_capture(move):
                self.board.push(move)
                score = -self.QuiescenceSearch(-beta, -alpha)
                self.board.pop()

                if score >= beta:
                    return beta
                
                alpha = max(score, alpha)

        return alpha

    # Same as QuiescenceSearc, except if a capture goes too long, avoid it entirely
    def DepthLimitedQuiescenceSearch(self, alpha, beta, depth):
        if depth <= 0:
            return float('-inf')

        # Initial evaluation when there are no captures
        initial = self.Evaluate();

        if initial >= beta:
            return beta

        alpha = max(alpha, initial)

        for move in self.board.legal_moves:
            if self.board.is_capture(move):
                self.board.push(move)
                score = -self.DepthLimitedQuiescenceSearch(-beta, -alpha, depth)
                self.board.pop()

                if score >= beta:
                    return beta
                
                alpha = max(score, alpha)

        return alpha

    # Get the piece values by summing up all pieces
    # Note, white is positive
    def BoardPiecesValue(self):
        piece_map = self.board.piece_map()
        total_value = 0
        # Map from piece_type to a value
        piece_to_value = {
            1: 100,
            2: 300,
            3: 300,
            4: 500,
            5: 900,
            6: 2000
        }

        for _, piece in piece_map.items():

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
        total_value = self.BoardPiecesValue() + 10 * self.GetMobility()

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

        # Initialize the stockfish engine (see https://stockfishchess.org/)
        self.stockfish_engine = chess.uci.popen_engine("Stockfish/stockfish/Windows/stockfish_10_x64_popcnt.exe")
        self.stockfish_engine.uci()

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
            "p": u"\u2659",
            "n": u"\u2658",
            "b": u"\u2657",
            "r": u"\u2656",
            "q": u"\u2655",
            "k": u"\u2654",
            "P": u"\u265f",
            "N": u"\u265e",
            "B": u"\u265d",
            "R": u"\u265c",
            "Q": u"\u265b",
            "K": u"\u265a"
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
        if self.board.legal_moves.count() == 0: # You lost!
            return move

        while(not move in self.board.legal_moves):
            print("Enter the 'from' square:")
            from_square = str(input())
            print("Enter the 'to' square:")
            to_square = str(input())
            if from_square in self.square_dict and to_square in self.square_dict:
                move = chess.Move(self.square_dict[from_square], self.square_dict[to_square])
            if not move in self.board.legal_moves:
                print("That was not a valid move! make sure you are entering a valid square, for example : g4")

        return move

    # Push the move onto the board, or if there is none, handle game end
    def Move(self, move):
        if move == None:
            if self.board.turn:
                print("Black Wins!")
            else:
                print("White Wins!")
            self.PrintBoard()
            raise SystemExit
        else:
            self.board.push(move)

    # Get a move from the stockfish engine
    def GetStockfishMove(self):
        self.stockfish_engine.position(self.board)
        return self.stockfish_engine.go(movetime=2000)[0]

    # Plays the game
    def StartGame(self):
        chess_agent = ChessAgent(self.board)

        # Plays the game until there are no moves left (no moves means checkmate)
        while(True):
            self.PrintBoard()
            self.Move(self.GetStockfishMove())
            self.PrintBoard()
            self.Move(chess_agent.GetMove(5))

chess_manager = ChessManager()
chess_manager.StartGame()