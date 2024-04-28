import cv2
from ultralytics import YOLO
from collections import deque

FPS = 30 # frames per second
CONFIDENCE_THRESHOLD = 0.75 # face detection confidence threshold
LOWER_VIDEO_FRAMES_THRESHOLD = 3 * FPS # shortest video duration in seconds
UPPER_VIDEO_FRAMES_THRESHOLD = 30 * FPS # longest video duration in seconds
PASSIVE_FRAMES = 10 * FPS # frames to export before person is detected

def detect_person(image, model):
	results = model.predict(source=image, verbose=False, conf=CONFIDENCE_THRESHOLD)
	for r in results:
		boxes = r.boxes
		for box in boxes:
			iclass = int(box.cls[0])
			if (iclass == 0):
				confidence = float(box.conf)
				return (True, confidence)
	return (False, 0)

# Start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

model = YOLO('yolov9e.pt')
model.to('cuda')

def frames_to_mp4(frames, filename):
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter(filename, fourcc, 30.0, (640, 480))
	for frame in frames:
		out.write(frame)
	out.release()

pframes = deque(maxlen=PASSIVE_FRAMES) # 10 seconds of frames at 30fps
iframe = 0 # number of frames recorded
frames = [] # start recording when person is detected and record until person is not detected
pdetected = False
ivideo = 0
while (True):
	success, img = cap.read()
	bdetected, confidence = detect_person(img, model)

	if (bdetected):
		print('Person detected!', confidence)
		frames.append(img)
		iframe += 1
		if (iframe > UPPER_VIDEO_FRAMES_THRESHOLD):
			frames_to_mp4(list(pframes) + frames, f'output_{ivideo}.mp4')
			ivideo += 1
			frames = []
			pframes.clear()
			iframe = 0
		pdetected = True
	else:
		print('No person detected.', confidence)
		pframes.append(img)
		pdetected = False

		if (len(frames) > LOWER_VIDEO_FRAMES_THRESHOLD):
			frames_to_mp4(list(pframes) + frames, f'output_{ivideo}.mp4')
			ivideo += 1
			frames = []
			pframes.clear()

	cv2.imshow('Webcam', img)
	if cv2.waitKey(1) == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
