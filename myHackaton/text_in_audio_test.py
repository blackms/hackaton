import sys

from libs.audio_steganography.engine import encode, decode

# Constants
DECODE = "decode"  # Operation mode of the software
ENCODE = "encode"
WAV = "wav"  # input type
MP3 = "mp3"  # input type
RATE = 44100  # Sample rate (expected)

if __name__ == '__main__':
    fileToEncode = "./samples/a2002011001-e02.wav"
    messageFile = './samples/message.txt'
    encodedOutputFile = 'encoded.wav'
    decodedOutputFile = 'decoded.wav'
    decodedMessageFile = 'decoded_message.txt'

    print("Encoding file: {}, adding message: {}, and write to: {}".format(fileToEncode,
                                                                           messageFile,
                                                                           encodedOutputFile))
    try:
        encode(fileToEncode, messageFile, encodedOutputFile)
    except:
        print("Nope...")
        sys.exit(1)

    print("Decoding file: {}".format(decodedMessageFile))
    try:
        decode(decodedOutputFile, decodedMessageFile)
    except:
        print("Nope...")
        sys.exit(1)
