import time
from slackclient import SlackClient

token = "xoxp-60436121012-65408873184-66963802256-44fd56010a"
sc = SlackClient(token)
if sc.rtm_connect():
    while True:
        message = sc.rtm_read()
        try:
            message = message[0]
        except IndexError:
            continue
        except KeyError:
            continue
        if 'username' in message.keys():
            if message['username'] == 'blackms':
                lista = [x.encode('utf8').replace('<', '').replace('>', '') for x in message["text"].split("\n")]
                print lista
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
