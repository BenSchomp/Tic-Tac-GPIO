import wiringpi2 as wiringpi

INPUT = 0
OUTPUT = 1
OFF = 0
ON = 1

def init():
  wiringpi.wiringPiSetup()

  for pin in range( 0, 9 ):
    wiringpi.pinMode( pin, OUTPUT )

def ledOn( pin, delay=0 ):
  ledsOn( [pin], delay )

def ledOff( pin, delay=0 ):
  ledsOff( [pin], delay )

def ledOnOff( pin, delay=1000 ):
  ledsOnOff( [pin], delay )

def ledsOn( pins, delay=0 ):
  for pin in pins:
    wiringpi.digitalWrite( pin, ON )
  wiringpi.delay( delay )

def ledsOff( pins, delay=0 ):
  for pin in pins:
    wiringpi.digitalWrite( pin, OFF )
  wiringpi.delay( delay )

def ledsOnOff( pins, delay=1000 ):
  ledsOn( pins, delay )
  ledsOff( pins, delay )



###

def flashEach( delay ):
  for pin in range(0,9):
    ledOnOff( pin, delay )

def flashAll( delay ):
  ledsOnOff( range(0, 9 ), delay )

def flashRows( delay ):
  for row in range( 0, 3 ):
    ledsOnOff( [row*3 + 0, row*3 + 1, row*3 + 2 ], delay )

def flashCols( delay ):
  for col in range( 0, 3 ):
    ledsOnOff( [col + 0, col + 3, col + 6 ], delay )

def snake( delay ):
  trail = [0, 1, 2, 5, 4, 3, 6, 7, 8]
  for pin in trail:
    ledOn( pin, delay )

  for pin in trail:
    ledOff( pin, delay )

def spiral( delay ):
  trail = [0, 3, 6, 7, 8, 5, 2, 4, 1 ]
  for pin in trail:
    ledOn( pin, delay )

  wiringpi.delay( delay )

  trail.reverse()
  for pin in trail:
    ledOff( pin, delay )

def flatWipe( delay ):
  rows = [ [0,1,2], [3,4,5], [6,7,8] ]
  cols = [ [0,3,6], [1,4,7], [2,5,8] ]

  for i in range( 0, 2 ):
    for col in cols:
      ledsOn( col, delay )

    for row in rows:
      ledsOff( row, delay )

    cols.reverse()
    rows.reverse()

def diagWipe( delay ):
  diag1 = [ [0], [3,1], [6,4,2], [7,5], [8] ]
  diag2 = [ [2], [1,5], [0,4,8], [3,7], [6] ]

  for i in range( 0, 2 ):
    for diag in diag1:
      ledsOn( diag, delay )

    for diag in diag2:
      ledsOff( diag, delay )

    diag1.reverse()
    diag2.reverse()

#####

init()

while 1:
  flashEach( 125 )
  flashRows( 150 )
  flashCols( 150 )
  snake( 100 )
  flatWipe( 200 )
  for i in range( 0, 2 ):
    spiral( 75 )
  diagWipe( 150 )
  for i in range( 0, 4 ):
    flashAll( 125 )
  wiringpi.delay( 500 )


