import cv2

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)  # 캠 최대 해상도가 1280x720 / ToDo 1 : cv2 함수로 늘려야 함
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 4000)

if cap.isOpened():
	print('width: {}, height : {}'.format(cap.get(3), cap.get(4)))  # 화면크기 1280x720를 프린트 -> DB에 저장해보세요

while True:
	ret, fram = cap.read()
	
	if ret:

		cv2.imshow('video', cv2.flip(fram, 1))

		k = cv2.waitKey(10) & 0xFF

		if k == 27:  # ESC 키(27?)를 누르면 break, 캠화면 닫힘
			print('Closing windows')  # -> 이 이벤트도 DB에 저장해보세요
			cv2.destroyAllWindows()
			break

	else:
		print('error')

# cap.release()             # 두 줄 다 있어야 ESC 키를 누른 후 창이 알아서 잘 닫힘
# cv2.destroyAllWindows()   # 두 줄 다 있어야 ESC 키를 누른 후 창이 알아서 잘 닫힘

# ToDo 2 : mediapipe 사용
