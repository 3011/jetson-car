import utils
import time


class PoseDetector:
    # l: left左, r: right右 c: center中心(c_hip为l_hip与r_hip的中心点) d: distance距离
    def __init__(self):
        # fall
        self.is_fall = False
        self.fall_timing = 0
        self.fall_last_c_shoulder = None

        # jump
        self.is_jump = False
        self.jump_timing = 0
        self.jump_last_c_shoulder = None
        self.jump_last_c_hip = None

    def __call__(self, results):
        if results.pose_landmarks is not None:
            self.__fall_detector(results.pose_landmarks.landmark)
            self.__jump_detector(results.pose_landmarks.landmark)
        return self.is_fall, self.is_jump

    def __fall_detector(self, landmark):
        l_shoulder = landmark[11]
        r_shoulder = landmark[12]
        c_shoulder = utils.get_center(l_shoulder, r_shoulder)

        l_hip = landmark[23]
        r_hip = landmark[24]
        c_hip = utils.get_center(l_hip, r_hip)

        d_shoulder_hip = utils.get_distance(c_shoulder, c_hip)

        if not self.is_fall:
            # 每间隔0.2s计算肩膀在y轴的前后改变值，达到一定阈值判断正处于跌落状态
            if not self.fall_timing or time.time() - self.fall_timing >= 0.2:
                self.fall_timing = time.time()
                if self.fall_last_c_shoulder:
                    d_last_c_shoulder_c_shoulder = utils.get_y_distance(
                        self.fall_last_c_shoulder, c_shoulder)
                    # d_shoulder_hip当作参考值?，使人物离远离近的时阈值都一致。（肩膀到臀部的距离相对比较固定）
                    self.is_fall = d_last_c_shoulder_c_shoulder/d_shoulder_hip >= 0.25

                self.fall_last_c_shoulder = c_shoulder

        if self.is_fall:
            # 进入跌落状态后，每间隔0.2s检测，若脚踝到臀部距离达到一定阈值时，退出跌落状态
            l_ankle = landmark[27]
            r_ankle = landmark[28]
            c_ankle = utils.get_center(l_ankle, r_ankle)

            d_hip_ankle = utils.get_y_distance(c_hip, c_ankle)
            print(d_hip_ankle/d_shoulder_hip)
            if d_hip_ankle/d_shoulder_hip >= 0.8:
                self.is_fall = False

    def __jump_detector(self, landmark):  # 感觉会删掉这个功能，不准也暂时没啥用处
        l_shoulder = landmark[11]
        r_shoulder = landmark[12]
        c_shoulder = utils.get_center(l_shoulder, r_shoulder)

        l_hip = landmark[23]
        r_hip = landmark[24]
        c_hip = utils.get_center(l_hip, r_hip)

        if not self.is_jump:
            if not self.jump_timing or time.time() - self.jump_timing >= 0.2:
                self.jump_timing = time.time()
                if self.jump_last_c_shoulder:
                    last_y_d_shoulder_hip = utils.get_y_distance(
                        self.jump_last_c_shoulder, self.jump_last_c_hip)
                    y_d_shoulder_hip = utils.get_y_distance(c_shoulder, c_hip)

                    d_shoulder_hip = utils.get_distance(c_shoulder, c_hip)

                    d_last_c_shoulder_c_shoulder = utils.get_y_distance(
                        self.jump_last_c_shoulder, c_shoulder)

                    self.is_jump = d_last_c_shoulder_c_shoulder/d_shoulder_hip <= -0.3 and - \
                        0.1 <= (last_y_d_shoulder_hip -
                                y_d_shoulder_hip) <= 0.1
                self.jump_last_c_shoulder = c_shoulder
                self.jump_last_c_hip = c_hip
        elif time.time() - self.jump_timing >= 0.2:
            self.jump_timing = time.time()
            d_shoulder_hip = utils.get_distance(c_shoulder, c_hip)

            d_last_c_shoulder_c_shoulder = utils.get_y_distance(
                self.jump_last_c_shoulder, c_shoulder)
            self.is_jump = not (-0.05 <=
                                (d_last_c_shoulder_c_shoulder / d_shoulder_hip) <= 0.06)
            self.jump_last_c_shoulder = c_shoulder
