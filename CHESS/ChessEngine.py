"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state.
It will also keep a move log.
"""

class GameState():
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.moveFunctions = {'p': self.getPawnMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
                               'R': self.getRookMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []

        # For simplicity, we're tracking position of both Kings all the time.
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False

    """
    Takes a move as a parameter and executes it.
    The functioning of Castling, Pawn Promotion and En-Passant is not available in this.
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # Log the move that occurred in game. It is also used to undo move.
        self.whiteToMove = not self.whiteToMove  # Make next Turn
        # Update Kings' Location if they moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
    """
    Undo the last move in the Move Log.
    """
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Update Kings' Location is they moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

    """
    ALl moves considering checks.
    """
    def getValidMoves(self):
        # Naive Solution:
        # 1. Generate all the possible moves
        moves = self.getAllPossiblesMoves()
        # 2. For each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            # 3. Generate all the opponent's moves
            # 4. For each of those moves, see if they attack your King
            if self.inCheck():
                # 5. If they do attack your King, "your" move causing that move is Invalid.
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        # Either check_mate or stale_mate
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    """
    Determine if the current player is in Check or not.
    """
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation)
        else:
            return self.squareUnderAttack(self.blackKingLocation)

    """
    Determine if the enemy can attack the square (r, c) in focus or not.
    """
    def squareUnderAttack(self, focusPos):
        r, c = focusPos
        self.whiteToMove = not self.whiteToMove  # Switch to opponent's POV
        oppMoves = self.getAllPossiblesMoves()
        self.whiteToMove = not self.whiteToMove  # Switch the turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    """
    All moves without considering checks.
    """
    def getAllPossiblesMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'b' and not self.whiteToMove) or (turn == 'w' and self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves

    """
    Get all the Pawn moves for a Pawn located at given row, col and add these moves to the list.
    """
    def getPawnMoves(self, r, c, moves):
        # Set of Moves for the white pawns
        if self.whiteToMove:
            if self.board[r-1][c] == '--':  # 1 square pawn advance.
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--':  # 2 square pawn advance from the starting position.
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:  # Captures to the left
                if self.board[r-1][c-1][0] == 'b':  # Enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:  # Captures to the right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        # Set of moves for the black pawns0
        else:
            if self.board[r + 1][c] == '--':  # 1 square pawn advance.
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':  # 2 square pawn advance from the starting position.
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # Captures to the left
                if self.board[r + 1][c - 1][0] == 'w':  # Enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # Captures to the right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
        # TODO Add pawn promotions
    """
    Get all the Rook moves for a Rook located at given row, col and add these moves to the list.
    """
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else:
                        break
                else:
                    break

    """
    Get all the Bishop moves for a Bishop located at given row, col and add these moves to the list.
    """
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else:
                        break
                else:
                    break

    """
    Get all the Knight moves for a Knight located at given row, col and add these moves to the list.
    """
    def getKnightMoves(self, r, c, moves):
        possibleJumps = [(r-1, c+2), (r+1, c+2), (r+2, c-1), (r+2, c+1),
                         (r-1, c-2), (r+1, c-2), (r-2, c-1), (r-2, c+1)]
        allyColor = 'w' if self.whiteToMove else 'b'
        for jump in possibleJumps:
            if 0 <= jump[0] <= 7 and 0 <= jump[1] <= 7:
                nrow = jump[0]
                ncol = jump[1]
                if self.board[nrow][ncol][0] != allyColor:
                    moves.append(Move((r, c), (nrow, ncol), self.board))

    """
    Get all the Queen moves for a Queen located at given row, col and add these moves to the list.
    """
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    """
    Get all the King moves for a King located at given row, col and add these moves to the list.
    """
    def getKingMoves(self, r, c, moves):
        possibleMoves = [(r, c+1), (r+1, c+1), (r+1, c), (r+1, c-1),
                         (r, c-1), (r-1, c-1), (r-1, c), (r-1, c+1)]
        allyColor = 'w' if self.whiteToMove else 'b'
        for move in possibleMoves:
            if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                nrow, ncol = move
                if self.board[nrow][ncol][0] != allyColor:
                    moves.append(Move((r, c), (nrow, ncol), self.board))

class Move:
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = int(str(self.startRow) + str(self.startCol) + str(self.endRow) + str(self.endCol))

    """
    Overriding the Equals operator
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # [HINT] You can work upon this in future and make proper Chess Notation.
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
