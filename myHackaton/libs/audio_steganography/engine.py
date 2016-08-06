import os
import random
import warnings
import wave
from math import ceil
from struct import unpack, pack

from numpy.fft import rfft, irfft

from .audioformat import convertformat
from .bits import testbit, setbit

# Hide warnings
warnings.filterwarnings('ignore')

# Constants
SEED = "our cool awesome seed"  # random number generator seed
FRAMEDIST = 7
LOW_LOW_MASK = 0x000000FF  # used for masking off the upper and lower segments of bytes
HIGH_LOW_MASK = 0x00FF0000
LOW_HIGH_MASK = 0x0000FF00  # used for masking off the upper and lower segments of bytes
HIGH_HIGHT_MASK = 0xFF000000
CHUNK_SIZE = 64
BUCKETS_TO_USE = 6
BUCKET_OFFSET = 3
BUCKET_DIFFERENTIAL = 50
BUCKET_DIVISIONS = 3


def reseed():
    """ Resets the random generator """
    random.seed(SEED)


def get_chan_freqs(frames):
    """ Splits the given frames into left and right channel frequencies """
    structsize = len(frames) / 2
    chunk = unpack('<' + 'h' * structsize, frames)
    left = [chunk[j] for j in range(0, len(chunk), 2)]
    right = [chunk[j] for j in range(1, len(chunk), 2)]

    l_freqs = rfft(left)
    r_freqs = rfft(right)

    return rfft(left), rfft(right), structsize


def length_in_bytes(end):
    endlolo = end & LOW_LOW_MASK
    endlohi = (end & LOW_HIGH_MASK) >> 8
    endhilo = (end & HIGH_LOW_MASK) >> 16
    endhihi = (end & HIGH_HIGHT_MASK) >> 24

    return [endlolo, endlohi, endhilo, endhihi]


def encode(carrier_file, message, encoded_file):
    """ Encodes data into a file """
    print("Encoding...")

    tohide = message
    f_bytes = bytearray(tohide)

    inaudio = wave.open(carrier_file, 'rb')
    temp_outfile = encoded_file[:-3] + 'wav'  # temp filename since wav is canonical form
    outaudio = wave.open(temp_outfile, 'wb')
    outaudio.setparams(inaudio.getparams())  # copy over input audio's properties

    # Find the total number of frames in the input file
    totalframes = inaudio.getnframes()

    prbits_len = len(f_bytes) * 8

    # The end of the file occurs at the end of the prbits array if it is shorter than the
    # length of the original file. Otherwise, it is at the end of the original file.
    end = prbits_len if prbits_len * FRAMEDIST < totalframes else (totalframes / FRAMEDIST)

    f_bytes = bytearray(length_in_bytes(end)) + f_bytes

    # opens up the payload file and generate random bits
    reseed()
    bits = []
    for b in f_bytes:
        for i in range(8):
            bits.append(testbit(b, i))
    prbits = [b ^ random.getrandbits(1) for b in bits]
    prbits_len = len(prbits)

    end = prbits_len if prbits_len * FRAMEDIST < totalframes else (totalframes / FRAMEDIST)

    reseed()
    # For each 6 bits to encode
    for i in range(0, end, BUCKETS_TO_USE):
        # grab current input audio frame
        frames = inaudio.readframes(CHUNK_SIZE)
        left_freqs, right_freqs, structsize = get_chan_freqs(frames)

        fbucket = len(left_freqs) / BUCKET_DIVISIONS + 1
        for j in range(BUCKETS_TO_USE):
            bucket = fbucket + j * BUCKET_OFFSET
            if i + j < prbits_len:
                if prbits[i + j]:
                    left_freqs[bucket] = left_freqs[bucket - 1] - BUCKET_DIFFERENTIAL
                    right_freqs[bucket] = right_freqs[bucket - 1] - BUCKET_DIFFERENTIAL
                else:
                    left_freqs[bucket] = left_freqs[bucket - 1]
                    right_freqs[bucket] = right_freqs[bucket - 1]

        # write new frame for output audio
        new_left = irfft(left_freqs)
        new_right = irfft(right_freqs)
        outframe = []
        for j in range(len(new_left)):
            outframe.append(new_left[j].astype('int16'))
            outframe.append(new_right[j].astype('int16'))
        outaudio.writeframes(pack('<' + 'h' * structsize, *outframe))

    # write out the remaining frames
    frames = bytearray(inaudio.readframes(totalframes))
    outaudio.writeframes(frames)

    outaudio.close()
    inaudio.close()

    # if the desired output audio is mp3, then convert it to mp3
    if encoded_file[-3:] == 'mp3':
        convertformat(temp_outfile, 'mp3')


def get_bits_in_bytes(inaudio, end):
    reseed()

    # find the hidden data
    bits = []
    for i in range(0, end, BUCKETS_TO_USE):
        frames = inaudio.readframes(CHUNK_SIZE)
        left_freqs, right_freqs, structsize = get_chan_freqs(frames)

        fbucket = len(left_freqs) / BUCKET_DIVISIONS + 1
        for j in range(BUCKETS_TO_USE):
            if len(bits) < end:
                bucket = fbucket + j * BUCKET_OFFSET
                bitl = 0 if (ceil(left_freqs[bucket - 1]) - ceil(left_freqs[bucket])) <= BUCKET_DIFFERENTIAL / 2 else 1
                bitr = 0 if (
                                ceil(right_freqs[bucket - 1]) - ceil(
                                    right_freqs[bucket])) <= BUCKET_DIFFERENTIAL / 2 else 1
                bit = min(bitr, bitl)
                if bitr == 1:
                    bit = 1

                bits.append(bit)

    # translate the bits
    debits = [b ^ random.getrandbits(1) for b in bits]
    debytes = []
    for i in range(0, len(debits), 8):
        byte = 0
        for j in range(8):
            if debits[i + j] == 1:
                byte = setbit(byte, j)
        debytes.append(byte)

    return debytes


def decode(steganod_file):
    """ Decode data from a file """
    print("Decoding...")

    inaudio = wave.open(steganod_file, 'rb')

    totalframes = inaudio.getnframes()

    # read off metadata
    frame = get_bits_in_bytes(inaudio, 32)
    end = frame[0] | (frame[1] << 8) | (frame[2] << 16) | (frame[3] << 24)

    inaudio.rewind()
    debytes = get_bits_in_bytes(inaudio, end + 32)
    inaudio.close()

    return bytearray(debytes[4:])
