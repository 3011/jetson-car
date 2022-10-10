import multiprocessing
import cv2
import time
import copy


class SavePhoto():
    def __init__(self):
        self.dict = multiprocessing.Manager().dict()
        self.dict["count"] = 0

        multiprocessing.Process(
            target=SavePhoto.auto_record, args=(self,)).start()

    def __call__(self, frame):
        self.dict["count"] += 1
        self.dict["frame"] = frame

    def auto_record(self):
        count = 0
        # 每0.1秒内都有检测到跌落，持续8次(0.8s)则保存图片，约等于检测到持续跌落的第0.8秒保存图片
        while True:
            last_count = self.dict["count"]
            time.sleep(0.1)
            while self.dict["count"] > last_count:
                count += 1
                last_count = self.dict["count"]
                time.sleep(0.1)
                if count >= 8:
                    cv2.imwrite("photo/"+str(time.time()) +
                                ".png", self.dict["frame"])
                    time.sleep(2)  # sleep 3秒才能进行下次保存图片
                    count = 0
                    self.dict["count"] = 0
                    break


class SaveVideo():
    def __init__(self):
        self.timeout = 2.5
        self.frames = multiprocessing.Manager().list()
        self.last_record_time = 0

        multiprocessing.Process(
            target=SaveVideo.del_time_out, args=(self,)).start()

    def __call__(self, frame):
        self.frames.append((time.time(), frame))

    def del_time_out(self):
        while True:
            if len(self.frames) > 0:
                if self.frames[0][0] <= (time.time() - self.timeout):
                    self.frames.pop(0)

    def record(self):
        if time.time()-self.last_record_time < 3:
            return
        self.last_record_time = time.time()
        multiprocessing.Process(
            target=SaveVideo.__record, args=(self,)).start()

    def __record(self):
        front_frames = copy.deepcopy(self.frames)
        time.sleep(self.timeout)
        back_frames = copy.deepcopy(self.frames)

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(
            'output/'+str(time.time())+'.avi', fourcc, (len(front_frames)+len(back_frames))/(self.timeout*2), (1280, 720))

        for frame in front_frames:
            out.write(frame[1])

        for frame in back_frames:
            out.write(frame[1])

        out.release()
