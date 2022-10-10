from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import requests
import base64
import hashlib


def send_image_message(image_url):

    with open(image_url, 'rb') as f:
        # 转换图片为base64格式
        base64_data = base64.b64encode(f.read())
        image_data = str(base64_data, 'utf-8')
    with open(image_url, 'rb') as f:
        # 获取图片的md5值
        md = hashlib.md5()
        md.update(f.read())
        image_md5 = md.hexdigest()
    # 企业微信机器人发送图片消息
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c8c9f59b-2fb9-4e1a-bec6-0438d5d71123'
    headers = {"Content-Type": 'application/json'}
    data = {
        'msgtype': 'image',
        'image': {
            'base64': image_data,
            'md5': image_md5
        }
    }
    # 发送请求
    r = requests.post(url, headers=headers, json=data)


def send_text_message(content):

    URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c8c9f59b-2fb9-4e1a-bec6-0438d5d71123'

    mHeader = {'Content-Type': 'application/json; charset=UTF-8'}

    mBody = {

        "msgtype": "text",

        "text": {
            "content": content
        }

    }
    requests.post(url=URL, json=mBody, headers=mHeader)


class CreatEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            pass
        else:
            # 此处判断为了防止文件上传过程中的缓存文件被误识别，导致报错
            if event.src_path[-8:] == "filepart":
                pass
            else:
                print("图片路径：", event.src_path)
                send_text_message("检测到危险动作")
                send_image_message(event.src_path)


if __name__ == '__main__':
    dir_path = "/root/"
    observer = Observer()
    event_handler = CreatEventHandler()
    observer.schedule(event_handler, dir_path, True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
