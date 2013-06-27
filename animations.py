import wiringpi2 as wiringpi

INPUT = 0
OUTPUT = 1
OFF = 0
ON = 1

RED = 0
GREEN = 1
LED_OFFSET = [ 0, 9 ]
RED_LEDS = range( 0, 9 )
GREEN_LEDS = range( 9, 18 )

def init():
  wiringpi.wiringPiSetup()

  for pin in RED_LEDS:
    wiringpi.pinMode( pin, OUTPUT )

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



###

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

#####

def main():
  init()

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

if __name__ == "__main__":
  main()

