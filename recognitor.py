import face_recognition
import cv2
import multiprocessing


class FaceRecognitor:
    def __init__(self, known):
        self.names = []
        self.encodings = []

        self.d = multiprocessing.Manager().dict()
        self.d["face"] = None
        self.d["name"] = ""  # 存储当前最新识别到的人脸的姓名

        for path in known:
            # 读取所有已知人脸识别存入数组
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(
                image, known_face_locations=[self.__get_face_location(image)])[0]
            self.names.append(known[path])
            self.encodings.append(encoding)

        multiprocessing.Process(target=self.__run).start()

    def __call__(self, detection, image):
        if not self.d["face"]:
            self.d["face"] = [detection, image]

    def __start_recognition(self, img_path):
        unknown_image = face_recognition.load_image_file(img_path)  # 读取待识别图片
        unknown_encoding = face_recognition.face_encodings(
            unknown_image, known_face_locations=[self.__get_face_location(unknown_image)])[0]
        # tolerance value more lower more strict
        results = face_recognition.compare_faces(
            self.encodings, unknown_encoding, tolerance=0.45)  # tolerance参数越低越严格
        for i, p in enumerate(results):
            if p:
                return self.names[i]
        return ""

    def __get_face_location(self, img):
        height, width, _ = img.shape
        location = (0, width, height, 0)
        return location

    def __resize_image(self, detection, image):
        # 右眼、左眼、鼻尖、嘴巴中心、右耳、左耳
        if detection.score[0] >= 0.4:
            # 下面代码的作用是裁切大头照
            box = detection.location_data.relative_bounding_box
            height, width, _ = image.shape
            add_y = box.height * height * 0.2
            add_x = box.width * width * 0.2

            # 防止截取范围越界
            def l(n):
                n = int(n)
                if n > 0:
                    return n
                else:
                    return 0

            def r(n, max):
                n = int(n)
                if n < max:
                    return n
                else:
                    return max

            y = [l(box.ymin*height - add_y),
                 r((box.ymin+box.height)*height + add_y, height)]
            x = [l(box.xmin*width - add_x),
                 r((box.xmin+box.width)*width + add_x, width)]
            res_image = image[y[0]:y[1], x[0]:x[1]]
            return res_image

    def __run(self):
        while 1:
            try:
                if self.d["face"]:
                    detection, image = self.d["face"]
                    image = self.__resize_image(detection, image)
                    cv2.imwrite('unknown.jpg', image)
                    who = self.__start_recognition('unknown.jpg')
                    self.d["name"] = who
                    self.d["face"] = None
            except Exception as err:
                print(err)
