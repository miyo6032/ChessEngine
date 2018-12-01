import chess

class ChessEngine():

    def __init__(self):
        self.board = chess.Board()
        self.board_size = 8

    def PrintBoard(self):
        piece_map = self.board.piece_map()
        for row in range(self.board_size):
            for col in range(self.board_size):

                # Piece index calculates the pieces based on row and column, from 0 to 63
                piece_index = row * self.board_size + col

                # If there is a piece, print it, otherwise print an empty square
                if piece_index in piece_map:
                    print(str(piece_map[piece_index]) + ' ', end='')
                else:
                    print(u"\u25A1 ", end='')
            # Print a newline
            print("")
        print("")

    def Move(self, move):
        self.board.push(move)

    def GetMove(self, depth):
        max_score = float('-inf')
        best_move = None

        # Find the best move
        for move in self.board.legal_moves:
            self.board.push(move)
            # The best move is based on future moves of the player and enemy
            score = - self.Negamax(depth - 1)
            if score > max_score:
                max_score = score
                best_move = move
            self.board.pop()
        return best_move

    def Negamax(self, depth):
        # Reach the end of the tree
        if depth == 0:
            return self.Evaluate()
        max_score = float('-inf')

        # Find the best move
        for move in self.board.legal_moves:
            self.board.push(move)
            # The best move is based on future moves of the player and enemy
            score = - self.Negamax(depth - 1)
            if score > max_score:
                max_score = score
            self.board.pop()
        return max_score

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

chess_engine = ChessEngine()
chess_engine.PrintBoard()
for i in range(50):
    chess_engine.Move(chess_engine.GetMove(2))
    chess_engine.PrintBoard()