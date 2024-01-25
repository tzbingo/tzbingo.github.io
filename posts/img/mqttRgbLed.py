from microblocks_messaging_library import MicroblocksSerialMessage
import siot
srv="121.5.75.157"
port=1883
user='nyt'
psw='nyt88837306'
topic='v23CjunaD4UKJEjzn615Bq9Prhumm9jq/RgbLed'
#颜色查表计算
color={"red":"255,0,0","green":"0,255,0","blue":"0,0,255","yellow":"255,255,0","cyan":"0,255,255","purple":"128,0,128"}
#连接ESP8266硬件
m = MicroblocksSerialMessage()
m.connect("COM5")
def sub_cb(client,userdata,msg):
    value=eval((msg.payload).decode('utf-8'))
    if msg.topic==topic:
        print(f"控制彩灯颜色为：{value['msg']}")
        m.sendBroadcast(f"on({color[value['msg']]})")        
siot.init('',srv,user=user,password=psw)
siot.connect()
siot.subscribe(topic,sub_cb)
siot.loop()
