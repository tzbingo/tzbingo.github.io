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
    while True:
            light=m.receiveBroadcasts()
            if not light is None:
                print(msg)
                break
    print(f"环境光强:{lux}")
    siot.publish(topic,str(lux))
    time.sleep(3)