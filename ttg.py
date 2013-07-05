import wiringpi2 as wiringpi

INPUT = 0
OUTPUT = 1
OFF = UP = 0
ON = DOWN = 1

NOT_PRESSED = 0
PRESSED = 1

EMPTY = -1
RED = 0
GREEN = 1

PIN_OFFSET = [ 0, 9 ]
RED_LEDS = range( 0, 9 )
GREEN_LEDS = range( 9, 18 )
BUTTONS = range( 18, 21)

Turn = RED
Board = []

### Init Functions ###

def init():
  wiringpi.wiringPiSetup()

  for pin in RED_LEDS:
    wiringpi.pinMode( pin, OUTPUT )

  for pin in GREEN_LEDS:
    wiringpi.pinMode( pin, OUTPUT )

  for pin in BUTTONS:
    wiringpi.pinMode( pin, INPUT )

  allOff()

### LED Functions ###

def ledOn( pin, duration=0 ):
  ledsOn( [pin], duration )

def ledOff( pin, duration=0 ):
  ledsOff( [pin], duration )

def ledOnOff( pin, duration=1000 ):
  ledsOnOff( [pin], duration )

def ledsOn( pins, duration=0 ):
  for pin in pins:
    wiringpi.digitalWrite( pin, ON )
  wiringpi.delay( duration )

def ledsOff( pins, duration=0 ):
  for pin in pins:
    wiringpi.digitalWrite( pin, OFF )
  wiringpi.delay( duration )

def ledsOnOff( pins, duration=1000 ):
  ledsOn( pins, duration )
  ledsOff( pins, duration )

def allOn():
  ledsOn( RED_LEDS )
  ledsOn( GREEN_LEDS )

def allOff():
  ledsOff( RED_LEDS )
  ledsOff( GREEN_LEDS )

### Animation Functions ###

def flashOne( pin, duration ):
  ledOnOff( pin, duration )

def flashAll( duration ):
  ledsOnOff( RED_LEDS, duration )

def flashEach( duration ):
  for pin in RED_LEDS:
    flashOne( pin, duration )

def flashRows( duration ):
  for row in range( 0, 3 ):
    ledsOnOff( [row*3 + 0, row*3 + 1, row*3 + 2 ], duration )

def flashCols( duration ):
  for col in range( 0, 3 ):
    ledsOnOff( [col + 0, col + 3, col + 6 ], duration )

def snake( duration ):
  trail = [0, 1, 2, 5, 4, 3, 6, 7, 8]
  for pin in trail:
    ledOn( pin, duration )

  for pin in trail:
    ledOff( pin, duration )

def spiral( duration ):
  trail = [0, 3, 6, 7, 8, 5, 2, 4, 1 ]
  for pin in trail:
    ledOn( pin, duration )

  wiringpi.delay( duration )

  trail.reverse()
  for pin in trail:
    ledOff( pin, duration )

def flatWipe( duration ):
  rows = [ [0,1,2], [3,4,5], [6,7,8] ]
  cols = [ [0,3,6], [1,4,7], [2,5,8] ]

  for i in range( 0, 2 ):
    for col in cols:
      ledsOn( col, duration )

    for row in rows:
      ledsOff( row, duration )

    cols.reverse()
    rows.reverse()

def diagWipe( duration ):
  diag1 = [ [0], [3,1], [6,4,2], [7,5], [8] ]
  diag2 = [ [2], [1,5], [0,4,8], [3,7], [6] ]

  for i in range( 0, 2 ):
    for diag in diag1:
      ledsOn( diag, duration )

    for diag in diag2:
      ledsOff( diag, duration )

    diag1.reverse()
    diag2.reverse()

def animations():
  global Turn

  allOff()

  while 1:
    flashEach( 125 )
    flashRows( 150 )
    flashCols( 150 )
    snake( 100 )
    flatWipe( 200 )
    spiral( 75 )
    diagWipe( 150 )

    for i in range( 0, 3 ):
      flashAll( 125 )

    wiringpi.delay( 750 )

    if Turn == RED:
      print " -=-=- Green's Turn -=-=-"
      Turn = GREEN
    else:
      print " -=-=- Red's Turn -=-=-"
      Turn = RED

#####

def takeTurn( square ):
  global Turn
  global Board
  pin = squareToPin( square )

  for i in range( 0, 3 ):
    flashOne( pin, 100 )

  ledOn( pin )
  Board[ square ] = Turn

  if Turn == RED:
    Turn = GREEN
    print "Green's Turn..."
  else:
    Turn = RED
    print "Red's Turn..."

def buttonTest( pin ):
  clickCount = -1 
  buttonState = NOT_PRESSED

  while 2 + 2 == 4:
    button = wiringpi.digitalRead( pin )
    if button == DOWN:
      if buttonState == NOT_PRESSED:
        buttonState = PRESSED

        ledOff( clickCount )
        clickCount = clickCount + 1
        if clickCount > 8:
          clickCount = 0
        ledOn( clickCount )

        print "Button CLICKED: {0}".format(clickCount)

    elif button == UP:
      if buttonState == PRESSED:
        buttonState = NOT_PRESSED
        wiringpi.delay(250)

def squareToPin( square ):
  global Turn
  return square + PIN_OFFSET[ Turn ]

def nextEmpty( square ):
  print "nextEmpty( {0} )...".format( square )
  print Board
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

  print "... {0}".format( square )
  return square

def playGame():
  global Turn
  Turn = RED
  global Board
  Board  = [ EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY  ]
  gameOver = 0

  allOff()

  moveButtonState = selectButtonState = NOT_PRESSED
  curSquare = 0
  ledOn( squareToPin( curSquare ) )

  while not gameOver:
    # get button inputs
    moveButton = wiringpi.digitalRead( 18 )
    selectButton = wiringpi.digitalRead( 19 )

    # handle select button
    if selectButton == DOWN:
      if selectButtonState == NOT_PRESSED:
        selectButtonState = PRESSED

        takeTurn( curSquare )
        curSquare = nextEmpty( 8 )
        if curSquare >= 0:
          ledOn( squareToPin( curSquare ) )
        else:
          gameOver = 1

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

        ledOff( squareToPin( curSquare ) )
        curSquare = nextEmpty( curSquare )
        ledOn( squareToPin( curSquare ) )

        selectButtonState = NOT_PRESSED

    else:
      if moveButtonState == PRESSED:
        moveButtonState = NOT_PRESSED
        wiringpi.delay( 256 )

  print " +++ Game Over! +++"
  wiringpi.delay( 5000 )


#####

def main():
  init()

  playGame()

  animations()

if __name__ == "__main__":
  main()

