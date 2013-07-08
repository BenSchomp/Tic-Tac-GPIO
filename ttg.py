# import libraries
import wiringpi2 as wiringpi
import led

# global constants
LEFT_BUTTON_PIN = 18
RIGHT_BUTTON_PIN = 19

EMPTY = ' '
RED = 'X'
GREEN = 'O'

UP = 0
DOWN = 1

NOT_PRESSED = 0
PRESSED = 1

PLAYING = 0
READY = 1
ANIMATING = 2
GAME_OVER = 3

READY_FLASHES = 50

FLASH_ON =  20000
FLASH_OFF = 10000

ANIMATION_SPEED = 6000
OFF = -1
END = -2
ANIMATION = [
  [0,1,2], [3,4,5], [6,7,8], [OFF,0,1,2], [OFF,3,4,5], [OFF,6,7,8], # top down wipe
  [0,3,6], [1,4,7], [2,5,8], [OFF,0,3,6], [OFF,1,4,7], [OFF,2,5,8], # left right wipe
  [0], [1,3], [2,4,6], [5,7], [8], # diag on
  [OFF,0], [OFF,1,3], [OFF,2,4,6], [OFF,5,7], [OFF,8], # diag off
  [0],[3],[6],[OFF,0],[OFF,3],[OFF,6],
  [1],[4],[7],[OFF,1],[OFF,4],[OFF,7],
  [2],[5],[8],[OFF,2],[OFF,5],[OFF,8],
  [0],[1],[2],[5],[4],[3],[6],[7],[8], # snake on
  [OFF,0],[OFF,1],[OFF,2],[OFF,5],[OFF,4],[OFF,3],[OFF,6],[OFF,7],[OFF,8], # snake off
  [END] ]

SHORT_PAUSE = 150
MED_PAUSE =   350
LONG_PAUSE =  500

# global variables
Turn = RED
Board = []

#####

def checkForWin():
  winLines = [
    [ 0, 1, 2 ], # top row
    [ 3, 4, 5 ], # middle row
    [ 6, 7, 8,], # bottom row
    [ 0, 3, 6,], # left col
    [ 1, 4, 7,], # middle col
    [ 2, 5 ,8,], # right col
    [ 0, 4, 8,], # diagonal 1
    [ 2, 4, 6,]  # diagonal 2
  ]
  
  for line in winLines :
    if Board[ line[0] ] == Turn and Board[ line[1] ] == Turn and Board[ line[2] ] == Turn:
      print (Turn) + " wins!"
      return line

  return False
  
def winningAnimation( winningLine ):
  # convert line to pins
  winningPins = winningLine
  if Turn == GREEN:
    for i in range( 0, 3 ):
      winningPins[i] = winningLine[i] + 9
      
  wiringpi.delay( LONG_PAUSE )
  led.ledsOff( winningPins, MED_PAUSE )

  # flash all three
  for i in range ( 0, 2 ):
    led.ledsOnOff( winningPins, MED_PAUSE )
  
  led.ledsOn( winningPins, LONG_PAUSE )
  
  # flash one at a time
  for i in range ( 0, 2 ):  
    led.ledsOff( winningPins, SHORT_PAUSE )
    for j in range ( 0, 3 ):
      led.ledOn( winningPins[ j ], MED_PAUSE )
    wiringpi.delay( SHORT_PAUSE )

  led.ledsOff( winningPins, SHORT_PAUSE )
  
  # flash all three again
  for i in range ( 0, 2 ):
    led.ledsOnOff( winningPins, SHORT_PAUSE )

  # turn back on for final board
  led.ledsOn( winningPins )

def drawBoard( invert=False):
  # handle board inversion
  redOffset = 9 if invert else 0
  greenOffset = 0 if invert else 9

  led.allOff()
  for i in range( 0, 9 ):
    if Board[i] == RED:
      led.ledOn( i + redOffset )
    elif Board[i] == GREEN:
      led.ledOn( i + greenOffset )
        
def gameTiedAnimation():
  wiringpi.delay( LONG_PAUSE )
  
  # flip the colors back and forth
  for i in range( 0, 3 ):
    drawBoard( True )
    wiringpi.delay( MED_PAUSE )
    
    drawBoard()
    wiringpi.delay( MED_PAUSE )

def resetAnimation():
  # flash existing board
  for i in range( 0, 3 ):
    led.allOff()
    led.wiringpi.delay( SHORT_PAUSE )
  
    drawBoard()
    led.wiringpi.delay( SHORT_PAUSE )

  led.allOff()
  led.wiringpi.delay( LONG_PAUSE )
    
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
      return -1, -1 # tie

  return square, squareToPin( square )
  

def gameInit():
  global Turn, Board, GameState
  Turn = RED
  Board = [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY]
 
  GameState = ANIMATING
  led.allOff()
  
  # for testing, initial conditions
  if False:
    Board = [EMPTY, GREEN, RED, GREEN, GREEN, RED, RED, RED, GREEN]
    led.ledsOn( [2, 5, 6, 7] )
    led.ledsOn( [1+9, 3+9, 4+9, 8+9] )
  elif False:
    Board = [EMPTY, RED, RED, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY]
    led.ledsOn( [1, 2] )

def playGame():
  global GameState
  gameInit()

  moveButtonState = selectButtonState = NOT_PRESSED
  curSquare = curPin = flashCount = readyCount = 0
 
  # the game loop
  while GameState != GAME_OVER:
     
    flashCount += 1
    if GameState == ANIMATING:
      if flashCount % ANIMATION_SPEED == 0:
        curLeds = ANIMATION[ ( flashCount / ANIMATION_SPEED ) - 1 ]
        if curLeds[0] == END:
          flashCount = 0
          led.allOff()
          GameState = READY
          wiringpi.delay( MED_PAUSE )
        else:
          if curLeds[0] == OFF:
            led.ledsOff( curLeds[1:] )
          else:
            led.ledsOn( curLeds)
    else:
      # flash current square
      if flashCount == 1:
        led.ledOn( curPin )
      elif flashCount == FLASH_ON:
        led.ledOff( curPin )
      elif flashCount > FLASH_ON + FLASH_OFF:
        flashCount = 0
        if GameState == READY:
          readyCount += 1

    
    # get button inputs
    moveButton = wiringpi.digitalRead( LEFT_BUTTON_PIN )
    selectButton = wiringpi.digitalRead( RIGHT_BUTTON_PIN )

    # handle select button
    if selectButton == DOWN:
      if selectButtonState == NOT_PRESSED:
        # act right away on button press
        selectButtonState = PRESSED

        if GameState == ANIMATING:
          # stop the animation
          led.allOff()
          GameState = READY
          curSquare = curPin = flashCount = readyCount = 0

        else:
          GameState = PLAYING
          # flash selected square and turn it on
          for i in range( 0, 3 ):
            led.flashOne( curPin, SHORT_PAUSE )
          led.ledOn( curPin )
    
          # update Board and check for game over
          Board[ curSquare ] = Turn
          winningLine = checkForWin()
          
          if winningLine:
            GameState = GAME_OVER
            # flash winning line
            winningAnimation( winningLine )
          
          else:
            nextTurn()
            curSquare, curPin = nextEmpty( 8 )
          
            if curSquare < 0:
              GameState = GAME_OVER
              print "It's a tie!"
              gameTiedAnimation()

        # clear the other button's state
        moveButton = UP
        moveButtonState = NOT_PRESSED

    else:
      if selectButtonState == PRESSED:
        selectButtonState = NOT_PRESSED
        # pause to avoid button flooding
        wiringpi.delay( SHORT_PAUSE )

    # handle move button
    if moveButton == DOWN:
      if moveButtonState == NOT_PRESSED:
        # act right away on button press
        moveButtonState = PRESSED

        if GameState == ANIMATING:
          # stop the animation
          led.allOff()
          GameState = READY
          curSquare = curPin = flashCount = readyCount = 0

        else:
          led.ledOff( squareToPin( curSquare ) )
          curSquare, curPin = nextEmpty( curSquare )
        
        # clear the other button's state
        selectButtonState = NOT_PRESSED

    else:
      if moveButtonState == PRESSED:
        moveButtonState = NOT_PRESSED
        # pause to avoid button flooding
        wiringpi.delay( SHORT_PAUSE )
  
    if GameState == READY and readyCount >= READY_FLASHES:
      GameState = ANIMATING
      readyCount = 0

  # GAME_OVER
  led.wiringpi.delay( LONG_PAUSE * 8 )
  resetAnimation()


#####

def main():
  led.init()

  print "Starting Tic-Tac-GPIO! (ctrl-c to stop)"

  while 2+2 == 4:
    playGame()


if __name__ == "__main__":
  main()

