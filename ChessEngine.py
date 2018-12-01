import chess

import numpy as np

# —————————————————————————————————————————————————————————————————
# In charge of the artificial intelligence of the ai
# —————————————————————————————————————————————————————————————————
class ChessEngine():

    def __init__(self):
        self.board = chess.Board()
        self.board_size = 8

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
                    print(str(piece_map[piece_index]) + ' ', end='')
                else:
                    print(u"\u25A1 ", end='')
            print("|", row + 1 , " ")
        print("")

    def GetMove(self, depth):

        alpha = float('-inf')
        beta = float('inf')
        best_value = float('-inf')
        best_move = None
        # Find the best move
        for move in self.board.legal_moves:
            self.board.push(move)
            # The best move is based on future moves of the player and enemy
            score = - self.Negamax(depth - 1, -beta, -alpha)
            self.board.pop()

            if score > best_value:
                best_value = score
                best_move = move
                if score > alpha:
                    alpha = score
        print(best_value, self.Evaluate())
        return best_move

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
        return alpha

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

    def Evaluate(self):
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

        # Negate the score if it is black's turn
        return total_value if self.board.turn else -total_value

    def PrintMoves(self):
        for move in self.board.legal_moves:
            print(" From:", chess.SQUARE_NAMES[move.from_square], " To:", chess.SQUARE_NAMES[move.to_square])

# —————————————————————————————————————————————————————————————————
# Manages the chess game
# —————————————————————————————————————————————————————————————————
class ChessManager():

    def __init__(self):
        self.chess_engine = ChessEngine()
        self.square_dict = {chess.SQUARE_NAMES[i]: i for i in range(64)}

    # Get a random availible move
    def GetRandomMove(self):
        if self.chess_engine.board.legal_moves.count() == 0:
            return None
        else:
            return np.random.choice(list(self.chess_engine.board.legal_moves))

    # Get input from the player to move
    def GetPlayerMove(self):
        move = None
        while(not move in self.chess_engine.board.legal_moves):
            print("Enter from square:")
            from_square = str(input())
            print("Enter to square:")
            to_square = str(input())
            if from_square in self.square_dict and to_square in self.square_dict:
                move = chess.Move(self.square_dict[from_square], self.square_dict[to_square])

        return move

    # Push the move onto the board
    def Move(self, move):
        self.chess_engine.board.push(move)

    # Plays the game
    def StartGame(self):
        for i in range(20):
            #self.chess_engine.PrintMoves()
            self.chess_engine.PrintBoard()
            self.Move(self.GetRandomMove())
            self.chess_engine.PrintBoard()
            self.Move(self.chess_engine.GetMove(4))

chess_manager = ChessManager()
chess_manager.StartGame()