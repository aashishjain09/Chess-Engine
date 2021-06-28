"""
[NOTE] - This is a separate file because the code in the Naive method is drastically different from this.
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

        self.enpassantPossible = ()  # Coordinates of a square where an En Passant capture is possible.

        self.inCheck = False
        self.pins = []
        self.checks = []

    """
    Takes a move as a parameter and executes it.
    The functioning of Castling is not available in this.
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

        # Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # En-passant Move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # Capturing the pawn
            
        # Get the square after a two square pawn advance has been made
        if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:  # Otherwise reset the variable.
            self.enpassantPossible = ()

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

            # Undo an enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # Leave the landing square blank
                self.board[move.startRow][move.endRow] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
    """
    ALl moves considering checks.
    """
    def getValidMoves(self):
        # Temporarily save the value of enpassant variable so as to not loose it in the process
        tempEnpassantPossible = self.enpassantPossible

        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # Only one check, block it, capture the piece or move the King
                moves = self.getAllPossiblesMoves()
                # To block a check, you must move a piece in one of the squares between the attacking piece and the King
                check = self.checks[0]  # Check info
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # The attacking piece
                validSquares = []  # The list of squares the piece can move to block Check
                # If attacking piece is a Knight, either capture it or move the King, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        # check[2] and check[3] are check directions
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        # Once you get to piece and checks
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # Remove the moves that don't block the check or move the King
                for i in range(len(moves) - 1, -1, -1):  # Going through the list backwards
                    if moves[i].pieceMoved[1] != 'K':  # King doesn't move so it must block check or capture enemy piece
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # Move isn't block or capture
                            moves.remove(moves[i])
            else:  # Double check, King has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # Not in check
            moves = self.getAllPossiblesMoves()

        # Check for check_mate or stale_mate
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        # Restore the value of enpassantPossible variable from temp variable
        self.enpassantPossible = tempEnpassantPossible

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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        # Set of Moves for the white pawns
        if self.whiteToMove:
            if self.board[r-1][c] == '--':  # 1 square pawn advance.
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--':  # 2 square pawn advance from the starting position.
                        moves.append(Move((r, c), (r-2, c), self.board))
            # Captures by the pawn
            if c-1 >= 0:  # Captures to the left
                if self.board[r-1][c-1][0] == 'b':  # Enemy piece to capture
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, enpassantPossible=True))
            if c+1 <= 7:  # Captures to the right
                if self.board[r-1][c+1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassantPossible=True))

        # Set of moves for the black pawns0
        else:
            if self.board[r + 1][c] == '--':  # 1 square pawn advance.
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == '--':  # 2 square pawn advance from the starting position.
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # Captures to the left
                if self.board[r + 1][c - 1][0] == 'w':  # Enemy piece to capture
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassantPossible=True))

            if c + 1 <= 7:  # Captures to the right
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassantPossible=True))

    """
    Get all the Rook moves for a Rook located at given row, col and add these moves to the list.
    """
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # Can't remove Queen from pin by Rook, only remove it on Bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # If the piece is pinned, it can still move towards or away from the attacker keeping the pin.
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
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
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        possibleJumps = ((r-1, c+2), (r+1, c+2), (r+2, c-1), (r+2, c+1), (r-1, c-2), (r+1, c-2), (r-2, c-1), (r-2, c+1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for jump in possibleJumps:
            nrow = jump[0]
            ncol = jump[1]
            if 0 <= nrow <= 7 and 0 <= ncol <= 7:
                if not piecePinned:
                    if self.board[nrow][ncol][0] != allyColor:
                        moves.append(Move((r, c), (nrow, ncol), self.board))

    """
    Get all the Bishop moves for a Bishop located at given row, col and add these moves to the list.
    """
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece[0] != allyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        else:  # Ally piece
                            break
                else:  # Off the board
                    break

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
        possibleMoves = [(0, 1), (1, 1), (1, 0), (1, -1),
                         (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        allyColor = 'w' if self.whiteToMove else 'b'
        for move in possibleMoves:
            endRow = r + move[0]
            endCol = c + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Empty or enemy piece
                    # Put King on a square and then see if it's in check.
                    # If not, then append the move onto the list of moves.
                    # Else, do nothing and revert the King position back to original.
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)

                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    """
    Returns if the player is in check, a list of pins, and a list of checks
    """
    def checkForPinsAndChecks(self):
        pins = []  # Squares where the allied pinned piece is and pin direction
        checks = []  # Squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # Check outward from King for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # Reset possible pin
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        piece_type = endPiece[1]
                        # There are 5 enemy pieces which could attack King (except Knight)
                        # 1. Rook attacks orthogonally
                        # 2. Bishop attacks diagonally
                        # 3. Pawn attacks from one square diagonally
                        # 4. Queen attacks from both lines and diagonals
                        # 5. Enemy King attacks from one square away in all directions
                        if (0 <= j <= 3 and piece_type == 'R') or \
                                (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or
                                                                   (enemyColor == 'b' and 4 <= j <= 6))) or \
                                (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            if possiblePin == ():  # No piece blocking, so it's a check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # A piece is blocking attack so it's a pin
                                pins.append(possiblePin)
                        else:  # Enemy piece not attacking King
                            break
                else:
                    break  # Off board

        # Determine if a Knight is giving check
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # On the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks


class Move:
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantPossible=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or \
                               (self.pieceMoved == 'bp' and self.endRow == 7)

        # En-passant
        self.isEnpassantMove = enpassantPossible

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
