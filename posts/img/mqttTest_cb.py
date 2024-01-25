import siot,time,random
srv="121.5.75.157"
port=1883
user='nyt'
psw='nyt88837306'
topic='v23CjunaD4UKJEjzn615Bq9Prhumm9jq/Lux'
def sub_cb(client,userdata,msg):
    value=(msg.payload).decode('utf-8')
    tp=(msg.topic).split('/')[1]
    if tp=='Lux':
        print(f'接收到消息:{value}')        
siot.init('',srv,user=user,password=psw)
siot.connect()
siot.subscribe(topic,sub_cb)
siot.loop()