from microblocks_wifi_radio import Radio
import time
r = Radio()
r.send_string("on(255,0,0)")
time.sleep(2)
r.send_string("on(0,255,0)")
time.sleep(2)
r.send_string("on(0,0,255)")
time.sleep(2)
r.send_string("on(0,0,0)")