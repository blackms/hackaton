from stegano import lsbset
from stegano.lsbset import generators


if __name__ == '__main__':
    hFile = "./image.png"
    secret_message = 'Prova Druido'
    secret_image = lsbset.hide("./samples/hackcortona-logo.png",
                               secret_message,
                               generators.eratosthenes(),
                               auto_convert_rgb=True)
    secret_image.save(hFile)

    print('Message hidden in file: {}'.format(hFile))

    message = lsbset.reveal(hFile, generators.eratosthenes())
    print('Decrypted message: {}'.format(message))
