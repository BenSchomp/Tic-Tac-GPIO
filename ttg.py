# import libraries
import wiringpi2 as wiringpi
import led

# global constants
EMPTY = ' '
RED = 'X'
GREEN = 'O'

UP = 0
DOWN = 1

NOT_PRESSED = 0
PRESSED = 1

PLAYING = 0
GAME_OVER = 1

FLASH_ON = 20000
FLASH_OFF = 10000

# global variables
Turn = RED
Board = []

#####

def checkForWin():
  topRow =   [ 0, 1, 2 ]
  midRow =   [ 3, 4, 5 ]
  botRow =   [ 6, 7, 8,]
  leftCol =  [ 0, 3, 6,]
  midCol =   [ 1, 4, 7,]
  rightCol = [ 2, 5 ,8,]
  diag1 =    [ 0, 4, 8,]
  diag2 =    [ 2, 4, 6,]
  
  winLines = [ topRow, midRow, botRow, leftCol, midCol, rightCol, diag1, diag2 ]

  
  for line in winLines :
    if Board[ line[0] ] == Turn and Board[ line[1] ] == Turn and Board[ line[2] ] == Turn:
      print (Turn) + " wins!"
      print
      return line

  return False
  
def winningAnimation ( winningLine ):
  # flash all three
  led.ledsOff( winningLine, 250 )
  for i in range ( 0, 3 ):
    led.ledsOnOff( winningLine, 250 )
  
  wiringpi.delay( 100 )
  
  # flash one at a time
  for i in range ( 0, 2 ):  
    for j in range ( 0, 3 ):
      led.ledOn ( winningLine[ j ], 350 )
    led.ledsOff( winningLine, 350 )
  led.ledsOff( winningLine, 250 )
  
  # flash all three
  for i in range ( 0, 2 ):
    led.ledsOnOff( winningLine, 250 )
  led.ledsOn( winningLine )
        
    
def nextTurn():
  global Turn
  if Turn == RED:
    Turn = GREEN
    print "Green's Turn..."
  else:
    Turn = RED
    print "Red's Turn..."

def squareToPin( square ):
  if Turn == RED:
    return square
  else:
    return square + 9

def nextEmpty( square ):
  count = 0
  square = square + 1
  if square > 8:
    square = 0

  while Board[ square ] != EMPTY:
    square = square + 1
    if square > 8:
      square = 0

    count = count + 1
    if count > 8:
      return -1 # game over

  return square, squareToPin( square )
  

def gameInit():
  global Turn, Board, GameState
  Turn = RED
  Board = [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY]
 
  GameState = PLAYING
  led.allOff()
  
  #Board = [EMPTY, RED, RED, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY]
  #led.ledOn( 1 )
  #led.ledOn( 2 )

def playGame():
  global GameState
  gameInit()

  moveButtonState = selectButtonState = NOT_PRESSED
  curSquare = curPin = 0
  flashCount = 0
 
  # the game loop
  while GameState == PLAYING:
     
    # flash current square
    flashCount = flashCount + 1
    if flashCount == 1:
      led.ledOn( curPin )
    elif flashCount == FLASH_ON:
      led.ledOff( curPin )
    elif flashCount > FLASH_ON + FLASH_OFF:
      flashCount = 0
    
    # get button inputs
    moveButton = wiringpi.digitalRead( 18 )
    selectButton = wiringpi.digitalRead( 19 )

    # handle select button
    if selectButton == DOWN:
      if selectButtonState == NOT_PRESSED:
        selectButtonState = PRESSED

        # flash selected square and turn it on
        for i in range( 0, 3 ):
          led.flashOne( curPin, 100 )
        led.ledOn( curPin )
  
        # update Board and check for game over
        Board[ curSquare ] = Turn
        winningLine = checkForWin()
        
        if winningLine:
          GameState = GAME_OVER
          # flash winning line
          winningAnimation( winningLine )
        
        if GameState == PLAYING:
          nextTurn()
          curSquare, curPin = nextEmpty( 8 )
        
        if curSquare < 0:
          GameState = GameOver

        moveButton = UP
        moveButtonState = NOT_PRESSED

    else:
      if selectButtonState == PRESSED:
        selectButtonState = NOT_PRESSED
        wiringpi.delay( 256 )

    # handle move button
    if moveButton == DOWN:
      if moveButtonState == NOT_PRESSED:
        moveButtonState = PRESSED

        led.ledOff( squareToPin( curSquare ) )
        curSquare, curPin = nextEmpty( curSquare )
        
        selectButtonState = NOT_PRESSED

    else:
      if moveButtonState == PRESSED:
        moveButtonState = NOT_PRESSED
        wiringpi.delay( 256 )

  print " +++ Game Over! +++"
  
  led.wiringpi.delay( 5000 )
  led.allOff()
  for i in range( 0, 3 ):
    if Turn == RED:
      led.ledsOnOff( led.RED_LEDS, 125 )
    else:
      led.ledsOnOff( led.GREEN_LEDS, 125 )

#####

def main():
  led.init()

  print "Starting Tic-Tac-GPIO! (ctrl-c to stop)"

  while 2+2 == 4:
    playGame()


if __name__ == "__main__":
  main()

