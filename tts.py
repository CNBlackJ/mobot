#!/usr/bin/python3
# -*- coding:utf8 -*-

from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '14824302'
API_KEY = 'TfB9GUXWFmRcDsz5YxuRHHx6'
SECRET_KEY = '3y4magVAflIrfeeXI09OfmHcmQHraXod'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

result  = client.synthesis('你好百度，今天天气怎么样', 'zh', 1, {
    'vol': 5,
})

# 识别正确返回语音二进制 错误则返回dict 参照下面错误码
if not isinstance(result, dict):
    with open('auido.mp3', 'wb') as f:
        f.write(result)