import random
import uuid
from imgurpython import ImgurClient

steganographyc_methods = ['IMAGE', 'AUDIO']


def upload_file_to_dropbox(file_path):
    import dropbox
    from dropbox.files import WriteMode

    dbxc = dropbox.Dropbox('FydObh6zyKAAAAAAAAAACy48GFaxy8r3vfiSw55buMuvoAAj-f6V46Ub1Tlhh1Xs')
    dbxc.users_get_current_account()
    f = open(file_path, 'rb')
    remote_path = "/{}".format(file_path.split('/')[-1])
    dbxc.files_upload(f, remote_path, mode=WriteMode('overwrite'))
    print ("Generating shared link...")
    shared_link = dbxc.sharing_create_shared_link_with_settings(remote_path)
    return shared_link.url.replace('dl=0', 'dl=1')


def send_telegram_message(message, destination):
    from slackclient import SlackClient
    token = "xoxp-60436121012-65421128289-66951783558-32760d4109"
    sc = SlackClient(token)
    sc.api_call("chat.postMessage",
                channel=destination,
                text=message,
                username="blackms"
                )

if __name__ == '__main__':
    messaggio = "Domani stefano va al mare se non piove altrimenti si abbuffa all'osteria del tatro."

    fixed_split_amount = 3

    group_size = int(round(len(messaggio) / fixed_split_amount, 0))

    chunks = [messaggio[i:i + group_size] for i in range(0, len(messaggio), group_size)]

    ordered_list = []

    for chunk in chunks:
        method = steganographyc_methods[random.randint(0, 1)]
        print("Encoding chunk: '{}' with method: {}".format(chunk, method))
        if method is 'IMAGE':
            from stegano import lsbset
            from stegano.lsbset import generators

            hFile = "./tmp/{}.png".format(uuid.uuid4())
            secret_message = chunk
            secret_image = lsbset.hide("./myHackaton/samples/hackcortona-logo.png",
                                       secret_message,
                                       generators.eratosthenes(),
                                       auto_convert_rgb=True)
            secret_image.save(hFile)

            print('Message hidden in file: {}'.format(hFile))
            client = ImgurClient('0f12475df84a578', 'facd4472f9d18c6aeb51b210b6321f6a2c5b9917')
            uploaded = client.upload_from_path(hFile)
            ordered_list.append(uploaded['link'])
        elif method is 'AUDIO':
            from myHackaton.libs.audio_steganography.engine import encode

            fileToEncode = "./myHackaton/samples/pandeiro_1_152_BPM.wav"
            messageFile = chunk
            file_name = uuid.uuid4()
            encodedOutputFile = "./tmp/{}.wav".format(file_name)

            print("Encoding file: {}, adding message: {}, and write to: {}".format(fileToEncode,
                                                                                   messageFile,
                                                                                   encodedOutputFile))
            encode(fileToEncode, messageFile, encodedOutputFile)
            link = upload_file_to_dropbox(encodedOutputFile)
            ordered_list.append(link)
    send_telegram_message("\n".join(ordered_list), "@lafenice")

