from microblocks_messaging_library import MicroblocksSerialMessage
import siot,time
srv="121.5.75.157"
port=1883
user='nyt'
psw='nyt88837306'
topic='v23CjunaD4UKJEjzn615Bq9Prhumm9jq/Lux'
siot.init('',srv,user=user,password=psw)
siot.connect()
m = MicroblocksSerialMessage()
m.connect("COM5")
while True:
    m.sendBroadcast('light')
    while True:
        msg=m.receiveBroadcasts()
        if not msg is None:
            light=msg.split(':')
            break    
    if light[0]=='light':
        print(f"环境光强:{light[1]}")
        siot.publish(topic,light[1])
    time.sleep(3)