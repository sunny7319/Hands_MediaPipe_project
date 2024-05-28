import cv2

cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)  # 캠 최대 해상도가 1280x720 / ToDo 1 : cv2 함수로 늘려야 함
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 4000)  # 가로세로 기본값 640x480 ??

toggle = 0

if cap.isOpened():
	w = cap.get(3)
	h = cap.get(4)
	print('width: {}, height : {}'.format(w, h))  # 화면크기 ???x???를 프린트
                                                  # cap.get(3) = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
while True:
	ret, fram = cap.read()
	
	if ret:
		fram = fram[ : , int(w*1/8):int(w*7/8)]
		ratio = 1080/h*(4/3.)  # 전체화면 full-HD 1920x1080 기준, 현재 컴 2560x1440
		fram = cv2.resize(cv2.flip(fram, 1), None, fx=ratio, fy=ratio,
					      interpolation=cv2.INTER_LINEAR)
		cv2.imshow('game', fram)

		key = cv2.waitKey(10)

		if key == ord('a'):
			print('key "a" pressed')  # -> 이 이벤트도 DB에 저장해보세요
			print('width: {}, height : {}'.format(w*ratio, h*ratio))
			toggle = 1

		elif (key & 0xFF) == 27:  # ESC 키(27?)를 누르면 break, 캠화면 닫힘
			print('Closing windows')
			cap.release()
			cv2.destroyAllWindows()
			break
	else:
		print('error')

# ToDo 2 : mediapipe 사용