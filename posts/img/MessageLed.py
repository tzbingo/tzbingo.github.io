from microblocks_messaging_library import MicroblocksSerialMessage
import time
m = MicroblocksSerialMessage()
m.connect("COM5")
m.sendBroadcast("on(255,0,0)")
time.sleep(2)
m.sendBroadcast("on(0,255,0)")
time.sleep(2)
m.sendBroadcast("on(0,0,255)")
time.sleep(2)
m.sendBroadcast("on(0,0,0)")