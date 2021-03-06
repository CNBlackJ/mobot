#!/usr/bin/python
# -*- coding:utf8 -*-

import cv2
import zmq
import base64
import numpy as np

context = zmq.Context()
footage_socket = context.socket(zmq.SUB)
footage_socket.bind('tcp://127.0.0.1:5555') # 这里需要指定Steamer的发地址
footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

while True:
    try:
        source = footage_socket.recv_string()
        img = base64.b64decode(source)
        npimg = np.fromstring(img, dtype=np.uint8)
        frame = cv2.imdecode(npimg, 1)
        frame = cv2.flip(frame, flipCode=-1)
        cv2.imshow("Stream", frame)
        cv2.waitKey(1)

    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break