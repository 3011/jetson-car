import cv2
import mediapipe as mp
import detector
import utils
import save
import recognitor


def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose
    mp_face_detection = mp.solutions.face_detection

    # 需要人脸识别的，"照片路径": "名字"
    known = {
        "cai2.jpg": "cai",
        # "cai1.jpg": "cai",
        # "chen.jpg": "chen",
        # "d2.jpg": "di"
    }
    face_recognitor = recognitor.FaceRecognitor(known)
    pose_detector = detector.PoseDetector()
    save_photo = save.SavePhoto()
    fps = utils.FPS()

    is_verifying = True

    # cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("videos/fall.mp4")
    url = 'rtsp://admin:admin@192.168.1.32:8554/live'
    cap = cv2.VideoCapture(url)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose, mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5) as face_detection:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            if is_verifying:
                # 进入人脸验证
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if face_recognitor.d["name"]:  # 判断是否识别到已知人脸
                    is_verifying = False
                else:
                    face_results = face_detection.process(image)

                    if face_results.detections:
                        for detection in face_results.detections:
                            face_recognitor(detection, image)
                            # 绘制人脸的框
                            mp_drawing.draw_detection(image, detection)
            else:
                pose_results = pose.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # 跌倒检测
                is_fall, is_jump = pose_detector(pose_results)
                if is_fall:
                    save_photo(image)
                    cv2.putText(image, "Fall", (10, 360),
                                cv2.FONT_HERSHEY_SIMPLEX, 3.0, (128, 128, 128), 4, cv2.LINE_AA)
                if is_jump:
                    cv2.putText(image, "Jump", (10, 160),
                                cv2.FONT_HERSHEY_SIMPLEX, 3.0, (128, 128, 128), 4, cv2.LINE_AA)

                # 绘制姿态
                mp_drawing.draw_landmarks(
                    image,
                    pose_results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

            # FPS
            cv2.putText(image, "FPS:" + str(fps()), (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128, 128, 128), 2, cv2.LINE_AA)

            cv2.imshow('???', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()


if __name__ == "__main__":
    main()
