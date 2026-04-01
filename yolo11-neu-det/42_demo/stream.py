import cv2

# 替换为树莓派的IP和端口
stream_url = "http://192.168.95.7:8090/stream.mjpg"

# 读取流并显示
cap = cv2.VideoCapture(stream_url)
if not cap.isOpened():
    print("无法打开流，请检查URL或网络")
else:
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Raspberry Pi Camera Stream", frame)
            # 按ESC键退出
            if cv2.waitKey(1) & 0xFF == 27:
                break
        else:
            print("流数据读取失败")
            break
    cap.release()
    cv2.destroyAllWindows()