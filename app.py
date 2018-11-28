#!/usr/bin/python3
# -*- coding:utf8 -*-

import multiprocessing
import ast

# vioce detecotor
import sys
import time
import webrtcvad
import numpy as np
from mic_array import MicArray

# face recognition
import face_recognition
import picamera
import numpy as np

# stop / wake process
import psutil

# dueros
from app.utils.prompt_tone import PromptTone


direction = -1

RATE = 16000
CHANNELS = 4
VAD_FRAMES = 10     # ms
DOA_FRAMES = 200    # ms

DETECT_VOICE_PID = -1
DETECT_FACE_PID = -1
RUN_ALEXA_PID = -1
FACE_COUNT = 0

def detect_voice(vioce_detect_queue):
    vad = webrtcvad.Vad(3)

    speech_count = 0
    chunks = []
    doa_chunks = int(DOA_FRAMES / VAD_FRAMES)

    try:
        with MicArray(RATE, CHANNELS, RATE * VAD_FRAMES / 1000)  as mic:
            for chunk in mic.read_chunks():
                if vad.is_speech(chunk[0::CHANNELS].tobytes(), RATE):
                    speech_count += 1
                    sys.stdout.write('1')
                # else:
                    # sys.stdout.write('0')

                sys.stdout.flush()

                chunks.append(chunk)
                if len(chunks) == doa_chunks:
                    if speech_count > (doa_chunks / 2):
                        frames = np.concatenate(chunks)
                        direction = mic.get_direction(frames)
                        direction = int(direction)
                        print('\n{}'.format(direction))
                        global DETECT_VOICE_PID
                        DETECT_VOICE_PID = os.getpid()
                        payload = { 'direction': direction, 'DETECT_VOICE_PID': DETECT_VOICE_PID }
                        vioce_detect_queue.put(str(payload))

                    speech_count = 0
                    chunks = []

    except KeyboardInterrupt:
        pass

def detect_face(vioce_detect_queue, face_detect_queue):
    global DETECT_FACE_PID
    global DETECT_VOICE_PID
    DETECT_FACE_PID = os.getpid()
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)
    output = np.empty((240, 320, 3), dtype=np.uint8)

    prompt_tone_player = PromptTone()

    face_locations = []

    while True:
        vioce_queue_dict = ast.literal_eval(vioce_detect_queue.get(True))
        direction = vioce_queue_dict.get('direction')
        if DETECT_VOICE_PID == -1:
            DETECT_VOICE_PID = vioce_queue_dict.get('DETECT_VOICE_PID')
        if direction:
            # stop detect voice
            stop_process(DETECT_VOICE_PID)
            print("Capturing image.")
            camera.capture(output, format="rgb")

            face_locations = face_recognition.face_locations(output)
            face_count = len(face_locations)
            print("Found {} faces in image.".format(face_count))
            if face_count:
                payload = { 'face_count': face_count, 'DETECT_FACE_PID': DETECT_FACE_PID, 'DETECT_VOICE_PID': DETECT_VOICE_PID }
                print("say hi")
                prompt_tone_player.play()
                face_detect_queue.put(str(payload))
        wake_process(DETECT_VOICE_PID)

def stop_process(pid):
    print('stop process: %s ' %(pid))
    if pid > -1:
        p = psutil.Process(pid)
        p.suspend()

def wake_process(pid):
    print('wake process: %s ' %(pid))
    if pid > -1:
        p = psutil.Process(pid)
        p.resume()


def main():
    vioce_detect_queue = multiprocessing.Queue()
    face_detect_queue = multiprocessing.Queue()

    process_detect_voice = multiprocessing.Process(target=detect_voice, args=(vioce_detect_queue,))
    process_detect_face = multiprocessing.Process(target=detect_face, args=(vioce_detect_queue, face_detect_queue))

    process_detect_voice.start()
    process_detect_face.start()
    process_detect_voice.join()
    process_detect_face.join()

if __name__ == '__main__':
    main()
