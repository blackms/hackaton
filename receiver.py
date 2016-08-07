import urllib


decrypted_chunks = []

if __name__ == '__main__':
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
                print("Received new message to decode.")
                if message['username'] == 'blackms':
                    files = [x.encode('utf8').replace('<', '').replace('>', '') for x in message["text"].split("\n")]
                    print("Received: {} files to open and decode.".format(len(files)))
                    for file in files:
                        if ".png" in file:
                            file_name = file.split('/')[-1]
                            urllib.urlretrieve(file, './received/{}'.format(file_name))
                            from stegano import lsbset
                            from stegano.lsbset import generators

                            chunk = lsbset.reveal("./received/{}".format(file_name), generators.eratosthenes())
                            decrypted_chunks.append(chunk)
                        else:
                            file_name = file.split('/')[-1].replace('?dl=1', '')
                            urllib.urlretrieve(file, './received/{}'.format(file_name))
                            from myHackaton.libs.audio_steganography.engine import decode

                            chunk = decode("./received/{}".format(file_name)).decode("utf-8")
                            decrypted_chunks.append(chunk)
                        print("First chunk from: {} contains: {}".format(
                            file_name,
                            chunk
                        ))
                print('Message:\n{}'.format(''.join(decrypted_chunks)))
                decrypted_chunks = []
            time.sleep(1)
    else:
        print "Connection Failed, invalid token?"
