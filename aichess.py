
import tkinter as tk
from pygame.mixer import Sound as pySound
import random, pygame
from copy import deepcopy
from time import sleep

def choosePlayer():
    PlayerChooser = tk.Tk()
    PlayerChooser.title("Yo Choose your own version of the game?")
    PlayerChooser.geometry("500x400")

    PlayerChooser_Title0 = tk.Label(PlayerChooser, text="Chess game made by Tejas", font=("Helvetica",16))
    PlayerChooser_Title0.place(relx=.5, rely=.1, anchor="n")
    PlayerChooser_Title1 = tk.Label(PlayerChooser, text="What mode would you like to choose?", font=("Helvetica",13))
    PlayerChooser_Title1.place(relx=.5, rely=.2, anchor="n")
    
    def setPlayer(choice):
        global whitePlayer, blackPlayer
        match choice:
            case 0:
                whitePlayer, blackPlayer = True, False
            case 1:
                whitePlayer, blackPlayer = False, True
            case 2:
                whitePlayer, blackPlayer = True, True
            case 3:
                whitePlayer, blackPlayer = False, False
        PlayerChooser.destroy()

    PlayerChooser_Button0 = tk.Button(PlayerChooser, text="Play as white", command=lambda : setPlayer(0))
    PlayerChooser_Button0.place(relx=.5, rely=.4, anchor="center")
    PlayerChooser_Button1 = tk.Button(PlayerChooser, text="Play as black", command=lambda : setPlayer(1))
    PlayerChooser_Button1.place(relx=.5, rely=.5, anchor="center")
    PlayerChooser_Button2 = tk.Button(PlayerChooser, text="Play as both", command=lambda : setPlayer(2))
    PlayerChooser_Button2.place(relx=.5, rely=.6, anchor="center")
    PlayerChooser_Button3 = tk.Button(PlayerChooser, text="Let the AI play itself", command=lambda : setPlayer(3))
    PlayerChooser_Button3.place(relx=.5, rely=.7, anchor="center")
    
    PlayerChooser.mainloop()

pieceScore = {"K":100, "Q":10, "R":5, "B":3, "N":3, "p":1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

def FLIP(LISTIN):
    LISTOUT = deepcopy(LISTIN)
    LISTOUT.reverse()
    return LISTOUT

def NEGATE(LISTIN):
    return [-i for i in LISTIN]

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]
def findBestMove(state, valid):
    TEMP_CASTLING = deepcopy(state.currentCastling)
    global nextMove
    nextMove = None
    alphabeta = [-CHECKMATE, CHECKMATE]
    random.shuffle(valid)
    findNMAlphaBetaMove(state, valid, DEPTH, alphabeta, 1 if state.whiteMove else -1)
    state.currentCastling = TEMP_CASTLING
    return nextMove

def findMinMaxMove(state, valid, depth, whiteMove):
    global nextMove
    if not depth:
        return findBoardScore(state)
    
    if whiteMove:
        maxScore = -CHECKMATE
        for move in valid:
            state.makeMove(move)
            nextMoves = state.getVMoves()
            score = findMinMaxMove(state, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            state.undoMov()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in valid:
            state.makeMove(move)
            nextMoves = state.getVMoves()
            score = findMinMaxMove(state, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            state.undoMove()
        return minScore

def findNegaMaxMove(state, valid, depth, turnMulti):
    global nextMove
    if not depth:
        return turnMulti * findBoardScore(state)
    
    maxScore = -CHECKMATE
    for move in valid:
        state.makeMove(move)
        nextMoves = state.getVMoves()
        score = -findNegaMaxMove(state, nextMoves, depth - 1, -turnMulti)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        state.undoMove()
    return maxScore

def findNMAlphaBetaMove(state, valid, depth, alphabeta, turnMulti):
    global nextMove
    if not depth:
        return turnMulti * findBoardScore(state)

    maxScore = -CHECKMATE
    for move in valid:
        state.makeMove(move)
        nextMoves = state.getVMoves()
        score = -findNMAlphaBetaMove(state, nextMoves, depth-1, NEGATE(FLIP(alphabeta)), -turnMulti)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        state.undoMove()

        if maxScore > alphabeta[0]:
            alphabeta[0] = maxScore
        if alphabeta[0] >= alphabeta[1]:
            break
    return maxScore


def findBoardScore(state):
    if state.checkmate:
        if state.whiteMove:
            return -CHECKMATE
        else:
            return CHECKMATE 
    elif state.stalemate:
        return STALEMATE
    SCORE = 0
    for row in state.board:
        for square in row:
            match square[0]:
                case "w":
                    SCORE += pieceScore[square[1]]
                case "b":
                    SCORE -= pieceScore[square[1]]
    
    return SCORE
class GameState:
    def __init__(self):
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        self.functions = {"p": self.getPawnMoves,
                          "R": self.getRookMoves,
                          "B": self.getBishopMoves,
                          "N": self.getKnightMoves,
                          "Q": self.getQueenMoves,
                          "K": self.getKingMoves}
        self.whiteMove = True
        self.log = []
        self.turnsSinceCapture = 0
        self.wKlocation = (7, 4)
        self.bKlocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.fiftymove = False
        self.enpassant = ()
        self.currentCastling = Castling(True, True, True, True)
        self.castlingLog = [Castling(self.currentCastling.kingside[0],
                                     self.currentCastling.kingside[1],
                                     self.currentCastling.queenside[0],
                                     self.currentCastling.queenside[1])]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.log.append(move) 
        self.whiteMove = not self.whiteMove 
        if move.pieceMoved == "wK": 
            self.wKlocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK": 
            self.bKlocation = (move.endRow, move.endCol)

        if move.isPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        
        if move.isEnPassant:
            self.board[move.startRow][move.endCol] = "--"
        
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassant = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassant = ()
        
        if move.isCastle:
            match (move.endCol - move.startCol):
                case 2: 
                    self.board[move.endRow][move.endCol-1], self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol+1], self.board[move.endRow][move.endCol-1]
                case _: 
                    self.board[move.endRow][move.endCol+1], self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol-2], self.board[move.endRow][move.endCol+1]
        
        self.updateCastling(move)
        self.castlingLog.append(Castling(self.currentCastling.kingside[0],
                                         self.currentCastling.kingside[1],
                                         self.currentCastling.queenside[0],
                                         self.currentCastling.queenside[1]))
    
    def undoMove(self):
        """Undo a move."""
        if len(self.log) != 0: 
            move = self.log.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteMove = not self.whiteMove 
            if move.pieceMoved == "wK":
                self.wKlocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.bKlocation = (move.startRow, move.startCol)
            
            if move.isEnPassant:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassant = (move.endRow, move.endCol)
            
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassant = ()
            
            self.castlingLog.pop()
            self.currentCastling = self.castlingLog[-1]
            
            if move.isCastle:
                match (move.endCol - move.startCol):
                    case 2: 
                        self.board[move.endRow][move.endCol-1], self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol+1], self.board[move.endRow][move.endCol-1]
                    case _: 
                        self.board[move.endRow][move.endCol+1], self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol-2], self.board[move.endRow][move.endCol+1]
                
    
    def updateCastling(self, move):
        match move.pieceMoved:
            case "wK":
                self.currentCastling.kingside[0] = False
                self.currentCastling.queenside[0] = False
            case "bK":
                self.currentCastling.kingside[1] = False
                self.currentCastling.queenside[1] = False
            case "wR":
                if move.startRow == 7:
                    if move.startRow == 0:
                        self.currentCastling.queenside[0] = False
                    elif move.startRow == 7:
                        self.currentCastling.kingside[0] = False
            case "bR":
                if move.startRow == 0:
                    if move.startCol == 0:
                        self.currentCastling.queenside[1] = False
                    elif move.startCol == 7:
                        self.currentCastling.kingside[1] = False
        match move.pieceCaptured:
            case "wR":
                if move.endRow == 7:
                    if move.endCol == 0:
                        self.currentCastling.queenside[0] = False
                    elif move.endCol == 7:
                        self.currentCastling.kingside[0] = False
            case "bR":
                if move.endRow == 0:
                    if move.endCol == 0:
                        self.currentCastling.queenside[1] = False
                    elif move.endCol == 7:
                        self.currentCastling.kingside[1] = False
                
    def getVMoves(self):     
        tempenpassant = self.enpassant
        tempCastling = Castling(self.currentCastling.kingside[0],
                                self.currentCastling.kingside[1],
                                self.currentCastling.queenside[0],
                                self.currentCastling.queenside[1])
        
        moves = self.getPMoves()
        if self.whiteMove:
            self.getCastlingMoves(self.wKlocation[0], self.wKlocation[1], moves)
        else:
            self.getCastlingMoves(self.bKlocation[0], self.bKlocation[1], moves)
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteMove = not self.whiteMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteMove = not self.whiteMove
            self.undoMove()
        if len(moves) == 0:
            self.checkmate, self.stalemate = (True, False) if self.inCheck() else (False, True)
        else:
            self.checkmate, self.stalemate = False, False
        self.enpassant = tempenpassant
        self.currentCastling = tempCastling
        return moves
    
    def inCheck(self):
        if self.whiteMove:
            return self.squareAttacked(self.wKlocation[0], self.wKlocation[1])
        else:
            return self.squareAttacked(self.bKlocation[0], self.bKlocation[1])
    
    def squareAttacked(self, row, column):
        self.whiteMove = not self.whiteMove 
        opponentMoves = self.getPMoves()
        self.whiteMove = not self.whiteMove 
        for move in opponentMoves:
            if move.endRow == row and move.endCol == column:
                return True
        return False
        
    
    def getPMoves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                piece = (self.board[row][column][0], self.board[row][column][1])
                if (piece[0] == "w" and self.whiteMove) or (piece[0] == "b" and not self.whiteMove):
                    self.functions[piece[1]](row, column, moves)
        return moves
    
    def getPawnMoves(self, row, column, moves):
        if self.whiteMove: 
            if self.board[row - 1][column] == "--":
                moves.append(Move((row, column), (row - 1, column), self.board))
                if row == 6 and self.board[row - 2][column] == "--": 
                    moves.append(Move((row, column), (row - 2, column), self.board))
            if column - 1 >= 0:
                if self.board[row - 1][column - 1][0] == "b":
                    moves.append(Move((row, column), (row - 1, column - 1), self.board))
                elif (row - 1, column - 1) == self.enpassant:
                    moves.append(Move((row, column), (row - 1, column - 1), self.board, isEnPassant = True))
            if column + 1 <= 7: 
                if self.board[row - 1][column + 1][0] == "b":
                    moves.append(Move((row, column), (row - 1, column + 1), self.board))
                elif (row - 1, column + 1) == self.enpassant:
                    moves.append(Move((row, column), (row - 1, column + 1), self.board, isEnPassant = True))
        else:
            if self.board[row + 1][column] == "--":
                moves.append(Move((row, column), (row + 1, column), self.board))
                if row == 1 and self.board[row + 2][column] == "--": 
                    moves.append(Move((row, column), (row + 2, column), self.board))
            if column - 1 >= 0: 
                if self.board[row + 1][column - 1][0] == "w":
                    moves.append(Move((row, column), (row + 1, column - 1), self.board))
                elif (row + 1, column - 1) == self.enpassant:
                    moves.append(Move((row, column), (row + 1, column - 1), self.board, isEnPassant = True))
            if column + 1 <= 7:
                if self.board[row + 1][column + 1][0] == "w":
                    moves.append(Move((row, column), (row + 1, column + 1), self.board))
                elif (row + 1, column + 1) == self.enpassant:
                    moves.append(Move((row, column), (row + 1, column + 1), self.board, isEnPassant = True))
                
                
    def getRookMoves(self, row, column, moves):
        directions = ( (-1, 0), (0, -1), (1, 0), (0, 1) )
        enemyColor = "b" if self.whiteMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = column + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": 
                        moves.append(Move((row, column), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((row, column), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break
                    
    def getBishopMoves(self, row, column, moves):
        directions = ( (-1, -1), (-1, 1), (1, -1), (1, 1) )
        enemyColor = "b" if self.whiteMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = column + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: 
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": 
                        moves.append(Move((row, column), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((row, column), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break
                
    def getKnightMoves(self, row, column, moves):
        directions = ( (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1) )
        friendlyColor = "w" if self.whiteMove else "b"
        for d in directions:
            endRow = row + d[0]
            endCol = column + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != friendlyColor:
                    moves.append(Move((row, column), (endRow, endCol), self.board))
                    
    def getQueenMoves(self, row, column, moves):
        self.getRookMoves(row, column, moves)
        self.getBishopMoves(row, column, moves)
        
    def getKingMoves(self, row, column, moves):
        kingMoves = ( (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1) )
        friendlyColor = "w" if self.whiteMove else "b"
        for i in range(8):
            endRow = row + kingMoves[i][0]
            endCol = column + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != friendlyColor:
                    moves.append(Move((row, column), (endRow, endCol), self.board))
    
    def getCastlingMoves(self, row, column, moves):
        if self.squareAttacked(row, column):
            return
        if (self.whiteMove and self.currentCastling.kingside[0]) or (not self.whiteMove and self.currentCastling.kingside[1]):
            self.castleShort(row, column, moves)
        if (self.whiteMove and self.currentCastling.queenside[0]) or (not self.whiteMove and self.currentCastling.queenside[1]):
            self.castleLong(row, column, moves)
        
    def castleShort(self, row, column, moves):
        if self.board[row][column + 1] == self.board[row][column + 2] == "--":
            if not (self.squareAttacked(row, column + 1) or self.squareAttacked(row, column + 2)):
                moves.append(Move( (row, column), (row, column + 2), self.board, isCastle=True ))
    def castleLong(self, row, column, moves):
        if self.board[row][column - 1] == self.board[row][column - 2] == self.board[row][column - 3] == "--":
            if not (self.squareAttacked(row, column - 1) or self.squareAttacked(row, column - 2)):
                moves.append(Move( (row, column), (row, column - 2), self.board, isCastle=True ))
    
class Castling():
    def __init__(self, shortW, shortB, longW, longB):
        self.kingside = [shortW, shortB]
        self.queenside = [longW, longB]
        
class Move():
    rankstoRows = {'1':7, '2':6, '3':5, '4':4, '5':3, '6':2, '7':1, '8':0}
    rowstoRanks = {v: k for k, v in rankstoRows.items()}
    filestoCols = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
    colstoFiles = {v: k for k, v in filestoCols.items()}
    
    def __init__(self, start, end, board, isEnPassant = False, isCastle = False):
        def getID(*args):
            length = len(args)
            temp = 0
            for i in range(length, 0, -1):
                item = args[(length - i)]
                temp += item * (10 ** (i - 1))
            return temp
        
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.ID = getID(self.startRow, self.startCol, self.endRow, self.endCol)
        self.isCapture = self.pieceCaptured != "--"
        
        self.isPromotion = False
        self.isPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        
        self.isEnPassant = isEnPassant
        if self.isEnPassant:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCastle = isCastle

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.ID == other.ID

    def __str__(self):
        if self.isCastle: 
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getEndMove()
        
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colstoFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare
    
    def getNotation(self):
        return self.getRF(self.startRow, self.startCol) + self.getRF(self.endRow, self.endCol)
    
    def getEndMove(self):
        return self.getRF(self.endRow, self.endCol)
    
    def getStartMove(self):
        return self.getRF(self.startRow, self.startCol)
    
    def getRF(self, row, column):
        return self.colstoFiles[column] + self.rowstoRanks[row]

BWIDTH, BHEIGHT = 512, 512
LOGWIDTH, LOGHEIGHT = 250, BHEIGHT
DIMENSION = 8
squareSize = BHEIGHT // DIMENSION
FPS = 15
IMAGES = {} 
SFX = {}
def loadImages():
    pieces = ["wp","wR","wN","wB","wQ","wK","bp","bR","bN","bB","bQ","bK"]
    for p in pieces:
        IMAGES[p] = pygame.transform.scale(pygame.image.load(r"C:\Users\Dr Poonam Pandey\Desktop\projects\chessgame\images\%s.png" % p), (squareSize, squareSize))

def loadSounds():
    for S in ["capture","castle","move-check","game-end","move-self","game-start"]:
        SFX[S] = pySound(fr"C:\Users\Dr Poonam Pandey\Desktop\projects\chessgame\sounds\{S}.mp3")
def main():
    
    pygame.init() 
    screen = pygame.display.set_mode((BWIDTH + LOGWIDTH, BHEIGHT)) 
    
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    logFont = pygame.font.SysFont("Consolas", 14, False, False)
    
    state = GameState()
    valid = state.getVMoves()
    
    anim = False
    moveMade = False

    global gameOver
    gameOver = False 
    loadImages() 
    loadSounds()
    
    global MANUAL_QUIT, restartGame
    MANUAL_QUIT = False
    restartGame = False 
    selected = () 
    clicks = [] 
    global done
    done = False
    while not done:
        humanTurn = (state.whiteMove and whitePlayer) or (not state.whiteMove and blackPlayer)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_r:
                    state = GameState()
                    valid = state.getVMoves()
                    selected = ()
                    clicks = []
                    moveMade = False
                    anim = False
            elif event.type == pygame.MOUSEBUTTONDOWN: 
                if not gameOver and humanTurn:
                    mousepos = pygame.mouse.get_pos() 
                    column = mousepos[0] // squareSize
                    row = mousepos[1] // squareSize
                    if (row, column) == selected or column >= 8:
                        selected = ()
                        clicks = [] 
                    else:
                        selected = (row, column)
                        clicks.append(selected) 
                    if len(clicks) == 2: 
                        move = Move(clicks[0], clicks[1], state.board)
                        for i in range(len(valid)):
                            if move == valid[i]:
                                state.makeMove(valid[i])
                                if move.isCastle or move.isPromotion:
                                    pySound.play(SFX["castle"])
                                    state.turnsSinceCapture += 1
                                elif move.isCapture or move.isEnPassant:
                                    pySound.play(SFX["capture"])
                                    state.turnsSinceCapture = 0
                                else:
                                    pySound.play(SFX["move-self"])
                                    state.turnsSinceCapture += 1
                                anim = True
                                moveMade = True
                                selected = ()
                                clicks = []
                        if not moveMade:
                            clicks = [selected] 
        if not (gameOver or humanTurn):
            AIMove = findBestMove(state, valid)
            if AIMove is None:
                AIMove = findRandomMove(valid)
            state.makeMove(AIMove)
            moveMade = True
            anim = True
        if moveMade:
            if anim:
                animate(screen, state.log[-1], state.board, clock)
            valid = state.getVMoves()
            moveMade = False
            anim = False
        drawState(screen, state, valid, selected, logFont)
        
        global RESULT
        if state.checkmate:
            gameOver = True
            done = True
            pySound.play(SFX["game-end"])
            if state.whiteMove:
                RESULT = "Black won by checkmate!"
            else:
                RESULT = "White won by checkmate!"
        elif state.stalemate:
            gameOver = True
            done = True
            pySound.play(SFX["game-end"])
            RESULT = "Draw by stalemate..."
        elif state.turnsSinceCapture >= 50:
            gameOver = True
            done = True
            pySound.play(SFX["game-end"])
            RESULT = "Draw by 50-move rule..."
        
        clock.tick(FPS)
        pygame.display.flip()
    if not gameOver:
        MANUAL_QUIT = True
        pygame.quit()
    else:
        pass
def squareHighlight(screen, state, moves, squareSelected):
    if squareSelected != ():
        row, column = squareSelected
        if state.board[row][column][0] == ("w" if state.whiteMove else "b"):
            SQUARE = pygame.Surface((squareSize, squareSize))
            SQUARE.set_alpha(100)
            SQUARE.fill(pygame.Color("blue"))
            screen.blit(SQUARE, (column * squareSize, row * squareSize))
            SQUARE.fill(pygame.Color("yellow"))
            for move in moves:
                if move.startRow == row and move.startCol == column:
                    screen.blit(SQUARE, (squareSize * move.endCol, squareSize * move.endRow))

def drawState(screen, state, validMoves, selectedSquare, logFont):
    drawBoard(screen) # Draw the squares on the board
    squareHighlight(screen, state, validMoves, selectedSquare)
    drawPieces(screen, state.board)
    drawMoveLog(screen, state, logFont)

def drawMoveLog(screen, state, font):
    logRect = pygame.Rect(BWIDTH, 0, LOGWIDTH, LOGHEIGHT)
    pygame.draw.rect(screen, pygame.Color("black"), logRect)
    
    moveLog = state.log
    moveTexts = []
    
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ": " + str(moveLog[i]) + ", "
        
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)
        
    textY = padding = 5
    
    for i in range(len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, True, pygame.Color("white"))
        
        textLocation = logRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        
        textY += textObject.get_height()

def drawBoard(screen):
    global colors
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(column * squareSize, row * squareSize, squareSize, squareSize))

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--": 
                screen.blit(IMAGES[piece], pygame.Rect(column * squareSize, row * squareSize, squareSize, squareSize))

def animate(screen, move, board, clock):
    global colors
    rowChange = move.endRow - move.startRow
    columnChange = move.endCol - move.startCol
    frames = 5 # frames per square
    frame_count = frames * (abs(rowChange) + abs(columnChange))
    
    for f in range(frame_count + 1):
        temp = [rowChange*f/frame_count, columnChange*f/frame_count]
        row, column = move.startRow + temp[0], move.startCol + temp[1]
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        finalSquare = pygame.Rect(move.endCol * squareSize, move.endRow * squareSize, squareSize, squareSize)
        pygame.draw.rect(screen, color, finalSquare)
        if move.pieceCaptured != "--":
            if move.isEnPassant:
                enpassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                finalSquare = pygame.Rect(move.endCol * squareSize, enpassantRow * squareSize, squareSize, squareSize)
            screen.blit(IMAGES[move.pieceCaptured], finalSquare)
        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(column * squareSize, row * squareSize, squareSize, squareSize))
        
        pygame.display.flip()
        clock.tick(60)

def playAgain(result):
    window = tk.Tk()
    window.title("Play again?")
    window.geometry("250x200")
    
    label0 = tk.Label(window, text=result, font=("Helvetica",12))
    label0.place(relx=.5, rely=.2, anchor="n")
    label1 = tk.Label(window, text="Would you like to play again?", font=("Helvetica",10))
    label1.place(relx=.5, rely=.4, anchor="n")
    
    def setPlayAgain(n, w):
        global restartGame
        if n: 
            restartGame = True
        elif not n:
            restartGame = False
        w.destroy()
    
    button0 = tk.Button(window, text="Yes", command=lambda : setPlayAgain(1, window))
    button0.place(relx=.5, rely=.6, anchor="center")
    button1 = tk.Button(window, text="No", command=lambda : setPlayAgain(0, window))
    button1.place(relx=.5, rely=.8, anchor="center")
    
    window.mainloop()

def drawEndGameText(text, screen):
    FONT = pygame.font.SysFont("Arial", 24, True, False)
    textObj = FONT.render(text, 0, pygame.Color("red"))
    textLoc = pygame.Rect(0, 0, BWIDTH, BHEIGHT).move(BWIDTH/2 - textObj.get_width()/2, BHEIGHT/2 - textObj.get_height()/2)
    screen.blit(textObj, textLoc)

if __name__ == "__main__":
    while True:
        choosePlayer()
        main()
        if MANUAL_QUIT:
            pygame.quit()
            break
        else:
            playAgain(RESULT)
            if restartGame:
                restartGame = False
            else:
                pygame.quit()
                break
