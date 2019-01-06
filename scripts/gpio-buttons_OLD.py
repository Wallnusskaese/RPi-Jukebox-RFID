#!/usr/bin/python3

from gpiozero import Button
from gpiozero import LED

from signal import pause
from subprocess import check_call
from time import sleep
from threading import Thread


###---------------------- Status-LED RGB
red = LED(14)
green = LED(17)
blue = LED(22)


def onStartup():
	red.on()
	green.on()
	blue.on()

onStartup()
###-------------------- Short / Long / Doulbe Click
# these are the finished functions.
# Add the magic here:

def onShortpress(Button):
	print("onShortpress"+str(Button+1))
	cmd = "./scripts/rfid_trigger_play.sh --cardid="+str(Button+1)
	blue.off()
	check_call (cmd, shell=True)
	blue.on()

def onDoubleclick(Button):
	print("onDoubleclick"+str(Button+1))

	green.off()
	#poem = open("shared/shortcuts/"+str(Button+1)).read()
	#cmd = "./scripts/rfid_trigger_play.sh --cardid="+str(Button+1)

	check_call ("./scripts/playout_controls.sh -c=playernext", shell=True)
	check_call ("./scripts/playout_controls.sh -c=playerplay", shell=True)
#	check_call ("./scripts/NetworkOn.sh",shell=True)

	green.on()


def onLongpress(Button):
	print("onLongpress"+str(Button+1))
	green.off()

	#check_call ("./scripts/playout_controls.sh -c=mute", shell=True)
	#check_call ( "./scripts/rfid_trigger_play.sh --cardid="+str(Button+1), shell=True)
	#check_call ( "./scripts/playout_controls.sh -c=playerpause", shell=True)
	#check_call ( "./scripts/resume_play.sh -c=resume -v=0", shell=True)
	#check_call ("./scripts/playout_controls.sh -c=mute", shell=True)

    #----better then the above, bc no jittersound.
	check_call ("./scripts/playout_controls.sh -c=mute", shell=True)
	cmd = "./scripts/rfid_trigger_play.sh --cardid="+str(Button+1)
	check_call (cmd, shell=True)
	check_call ("./scripts/resume_play.sh -c=disableresume", shell=True)
	check_call ("mpc clear", shell=True)
	check_call ("./scripts/playout_controls.sh -c=mute", shell=True)
	check_call (cmd, shell=True)
	check_call ("./scripts/resume_play.sh -c=enableresume", shell=True)

	#print('./scripts/resume_play.sh -c=enableresume -v=\"'+poem+'\"')
    #-------------------

	green.on()



###----------------------- translating the when_pressed and when_released events to onShortpress, onDoubleclick, onLongpress

#dc = Array for Doubleclick status
#presslenght = Array for Longpress status
# the arraylenght represents the count of buttons.
dc = [0,0,0,0,0,0,0,0,0] # = 9 Buttons
presslenght = [0,0,0,0,0,0,0,0,0] # = 9 Buttons

# when_pressed and when_released are strangely reversed in my setup!!!
def released(button): #<- press function

	# indicate that it was a first press
	global presslenght
	presslenght[button] = 1

	#start count function in a thread to indicate a longpress
	lpthread = Thread(target=count, args=(button,))
	lpthread.start()

secToLongPress = 1
def count(button):
	#check every 0.2 sec whether button was released within secToLongPress
	#and if so, break the loop
	global secToLongPress
	w = 0
	while w <= secToLongPress * 5:
		w = w + 1
		# presslenght[i] = 0 indicates, that button was released
		if presslenght[button] == 0:
			break
		sleep (0.2)

	# if button is still pressed, start longpress action in Thread.
	if presslenght[button] == 1:
		lpthread = Thread(target=onLongpress, args=(button,))
		lpthread.start()
		#indicate that longpress was confirmed
		presslenght[button] = 2

def pressed(button): #<-- this means button was released
	global dc
	global presslenght

	# dc[i] = 0 represents no Doubleclick (yet)
	# dc[i] = 1 represents Doubleclick
	if dc[button] == 1:
		# start onDoubleclick as thread
		ddcthread = Thread(target=onDoubleclick, args=(button,))
		ddcthread.start()
		# reset dc[i]
		dc[button] = 0
		# reset presslenght[i]
		presslenght[button] = 0
	elif dc[button]== 0:
		#we got our first release, we first check if we got a longpress.
		#If not, we start the timer for doubbleclick.
		if presslenght[button] != 2:
			dcthread = Thread(target=dctimer, args=(button,))
			dcthread.start()
			# indicate that we're now in doubleclick timeframe.
			dc[button] = 1
			# reset presslenght[i]
			presslenght[button] = 0

doubleclickThreshold = 0.4
def dctimer(button):
	#Start onShortpress no matter what (because it otherwise takes so long)
	spthread = Thread(target=onShortpress, args=(button,))
	spthread.start()
	global doubleclickThreshold
	sleep(doubleclickThreshold)
	# Alternatively start shortpress after threshold
		#global dc
		#if dc[i] != 2:
		#	print(i , " shortpress")
		#	spthread = Thread(target=onShortpress, args=(i,))
		#	spthread.start()
	#reset dc[button]
	dc[button] = 0



###---------------------- Initializing my buttons

#Name = Button(GPIO)
b1 = Button(6)
b2 = Button(16)
b3 = Button(19)
b4 = Button(5)
b5 = Button(26)
b6 = Button(21)
b7 = Button(13)
b8 = Button(12)
b9 = Button(20)

# Because we want all buttons to behave the same in respect to Short / Long and Dubble Click,
# we link the distinct funktions to one (referenced by button ID).
def press1(): pressed(0)
def press2(): pressed(1)
def press3(): pressed(2)
def press4(): pressed(3)
def press5(): pressed(4)
def press6(): pressed(5)
def press7(): pressed(6)
def press8(): pressed(7)
def press9(): pressed(8)

def release1(): released(0)
def release2(): released(1)
def release3(): released(2)
def release4(): released(3)
def release5(): released(4)
def release6(): released(5)
def release7(): released(6)
def release8(): released(7)
def release9(): released(8)

# In my setup, when_pressed and when_released are somehow reversed:
# when_released is activated when a button is pushed and when_pressed is called when the button is released.

# link events to references of functions
# Because gpiozero events do not run the function but rather create a reference to the function,
# we need to add one function for each event.

b1.when_pressed = press1
b2.when_pressed = press2
b3.when_pressed = press3
b4.when_pressed = press4
b5.when_pressed = press5
b6.when_pressed = press6
b7.when_pressed = press7
b8.when_pressed = press8
b9.when_pressed = press9

b1.when_released = release1
b2.when_released = release2
b3.when_released = release3
b4.when_released = release4
b5.when_released = release5
b6.when_released = release6
b7.when_released = release7
b8.when_released = release8
b9.when_released = release9






pause()
