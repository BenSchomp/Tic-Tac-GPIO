# import libraries
import wiringpi2 as wiringpi
import led

# global constants
LEFT_BUTTON_PIN = 18
RIGHT_BUTTON_PIN = 19

EMPTY = ' '
RED = 'Red'
GREEN = 'Green'

UP = 0
DOWN = 1

NOT_PRESSED = 0
PRESSED = 1

PLAYING = 0
READY = 1
ANIMATING = 2
GAME_OVER = 3

READY_FLASHES = 100

FLASH_ON =  20000
FLASH_OFF = 10000

OFF = -1
END = -2
ANIMATION = [
  [0],[3],[6],[OFF,0],[OFF,3],[OFF,6], # left drop
  [1],[4],[7],[OFF,1],[OFF,4],[OFF,7], # mid drop
  [2],[5],[8],[OFF,2],[OFF,5],[OFF,8], # right drop
  [0],[1],[2],[5],[4],[3],[6],[7],[8], # snake on
  [OFF,0],[OFF,1],[OFF,2],[OFF,5],[OFF,4],[OFF,3],[OFF,6],[OFF,7],[OFF,8], # snake off
  [0,1,2], [3,4,5], [6,7,8], [OFF,0,1,2], [OFF,3,4,5], [OFF,6,7,8], # top down wipe
  [0,3,6], [1,4,7], [2,5,8], [OFF,0,3,6], [OFF,1,4,7], [OFF,2,5,8], # left right wipe
  [0], [1,3], [2,4,6], [5,7], [8], # diag on
  [OFF,0], [OFF,1,3], [OFF,2,4,6], [OFF,5,7], [OFF,8], # diag off
  [END] ]
ANIMATION_SPEED = 6000

SHORT_PAUSE = 150
MED_PAUSE =   350
LONG_PAUSE =  500

# global variables
Turn = GREEN
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
    if Board[ line[0] ] == Turn and \
       Board[ line[1] ] == Turn and \
       Board[ line[2] ] == Turn:
      print " + " + Turn + " wins!"
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
  else:
    Turn = RED
  print Turn + "'s Turn..."

def squareToPin( square ):
  if Turn == RED:
    return square
  else:
    return square + 9

def nextEmpty( square ):
  count = 0
  while count < 9:
    square += 1
    if square > 8:
      square = 0
    
    if Board[ square ] != EMPTY:
      return square, squareToPin( square )
    
    count += 1
  
  # no empties: a full board
  return -1, -1

def playGame():
  # set initial conditions
  global Turn, Board
  Board = [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY]
  moveButtonState = selectButtonState = NOT_PRESSED

  nextTurn()

  GameState = READY
  curSquare = flashCount = readyCount = 0
  curPin = squareToPin( curSquare )
  led.allOff()

  # the game loop
  while GameState != GAME_OVER:
    flashCount += 1 # increment the flashing led "timer"
    
    if GameState == ANIMATING:
      # every READY_ANIMATION_SPEED flashCounts, draw one frame of READY_ANIMATION
      if flashCount % ANIMATION_SPEED == 0:
        curLeds = ANIMATION[( flashCount / ANIMATION_SPEED ) - 1]
        if curLeds[0] == END:
          # last frame of ANIMATION: reset and back to READY
          flashCount = 0
          led.allOff()
          GameState = READY
          wiringpi.delay( MED_PAUSE )
        else:
          if curLeds[0] == OFF:
            # turn these leds off
            led.ledsOff( curLeds[1:] )
          else:
            # turn these leds on
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
          # each flash brings us closer to ANIMATION
          readyCount += 1

    
    # get button inputs
    moveButton = wiringpi.digitalRead( LEFT_BUTTON_PIN )
    selectButton = wiringpi.digitalRead( RIGHT_BUTTON_PIN )

    # --- handle select button ---
    if selectButton == DOWN:
      if selectButtonState == NOT_PRESSED:
        # act right away on button press
        selectButtonState = PRESSED
        flashCount = readyCount = 0

        if GameState == ANIMATING:
          # stop the animation
          GameState = READY
          led.allOff()

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
            # we have a winner!
            GameState = GAME_OVER
            
            # flash winning line
            winningAnimation( winningLine )
          
          else:
            # no winner, continue on
            nextTurn()
            curSquare, curPin = nextEmpty( 8 )
          
            if curSquare < 0:
              # no more empty squares? it's a tie!
              GameState = GAME_OVER
              print " + It's a tie!"
              gameTiedAnimation()

        # clear the other button's state
        moveButton = UP
        moveButtonState = NOT_PRESSED

    else:
      if selectButtonState == PRESSED:
        selectButtonState = NOT_PRESSED
        # pause to avoid button flooding
        wiringpi.delay( SHORT_PAUSE )

    # --- handle move button ---
    if moveButton == DOWN:
      if moveButtonState == NOT_PRESSED:
        # act right away on button press
        moveButtonState = PRESSED
        flashCount = readyCount = 0

        if GameState == ANIMATING:
          # stop the animation
          GameState = READY
          led.allOff()

        else:
          # advance the flashing led to the next empty square
          led.ledOff( squareToPin( curSquare ) )
          curSquare, curPin = nextEmpty( curSquare )
        
        # clear the other button's state
        selectButtonState = NOT_PRESSED

    else:
      if moveButtonState == PRESSED:
        moveButtonState = NOT_PRESSED
        # pause to avoid button flooding
        wiringpi.delay( SHORT_PAUSE )
  
    if GameState == READY and readyCount > READY_FLASHES:
      # too long in READY state? play the ANIMATION for attention!
      GameState = ANIMATING
      readyCount = 0

  # GAME_OVER
  led.wiringpi.delay( LONG_PAUSE * 8 )
  resetAnimation()


#####

def main():
  led.init()
  print " ++ Tic-Tac-GPIO! ++"

  while 2+2 == 4:
    playGame()

if __name__ == "__main__":
  main()

