# --------- ITEMS TO CHANGE: ---------

EMAIL = "YOUR GMAIL HERE" # email to send sms from
PASSWORD = "YOUR GMAIL APP PASSWORD HERE" # app password/authentication (https://support.google.com/mail/answer/185833?hl=en)
PHONE_NUMBER = "YOUR PHONE NUMBER HERE" # phone number to send sms to
API_KEY = "YOUR	GEMINI API KEY HERE" # Gemini API key 
CARRIER = "verizon" # carrier of phone number ('att', 'tmobile', 'verizon', 'sprint')

# --------- END OF ITEMS TO CHANGE ---------

from selenium import webdriver
import time
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Local URL to open
url = "http://0.0.0.0:8080/"  # Adjust as needed

chrome_opt = webdriver.ChromeOptions()
chrome_opt.add_argument("--headless")

# create webdriver object
driver = webdriver.Chrome(options = chrome_opt) 
driver.get(url)

# get element
element = driver.find_element("id", "video")
driver.find_element("id", "start").click()

time.sleep(10)

start_time = time.time()
i = 0

from ultralytics import YOLO
from collections import deque
from threading import Thread
import google.generativeai as genai
import os
import smtplib

FPS = 30 # frames per second
CONFIDENCE_THRESHOLD = 0.6 # face detection confidence threshold
LOWER_VIDEO_FRAMES_THRESHOLD = 2 # shortest video duration in seconds
UPPER_VIDEO_FRAMES_THRESHOLD = 30 # longest video duration in seconds
PASSIVE_FRAMES = 10 # frames to export before person is detected
PROCESSING_FRAMES = 30 # process 1 frame every n frames
NOT_DETECTED_THRESHOLD = 2 # number of frames to wait before stopping recording

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vzwpix.com",
    "sprint": "@messaging.sprintpcs.com"
}

PROMPT = """
Analyze this security footage. Give a detailed descriptions on the actions of all people that appear in the video. Carefully note any criminal activity when suspected, including, but not limited to: theft, burglary, and vandalism. Do not include timestamps. Speak as if you're talking to the homeowner. Make it in the following format:
Description:
{describe the activity, being as straightforward as possible & avoiding repetition}

Next Steps:
{Provide a list of actionable items}

Suspicion Level:
{rank suspicion level as severe(immediate action required) moderate(action required) or no action required}

Please keep each category as readable as possible 
Example:
An individual was spotted in your garage. They appear to be removing items from cabinets and are armed. They are using what appear to be bricks as weapons
"""

genai.configure(api_key=API_KEY)
genai_model = genai.GenerativeModel(model_name='models/gemini-1.5-pro-latest')

def detect_person(image, model) -> tuple[bool, float]:
	results = model.predict(source=image, verbose=False, conf=CONFIDENCE_THRESHOLD)
	for r in results:
		boxes = r.boxes
		for box in boxes:
			iclass = int(box.cls[0])
			if (iclass == 0):
				confidence = float(box.conf)
				return (True, confidence)
	return (False, 0)

def send_message(phone_number, carrier, message):
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)
    print(f"Usage: python3 {phone_number, carrier, message}")

def upload_to_gemini(genai, frames, prompt=PROMPT) -> str:
	global ivideo

	request = [prompt]

	temp_files = []
	for i, frame in enumerate(frames[1:]):
		path = f'{ivideo}_frame_{i}.jpg'
		temp_files.append(path)
		cv2.imwrite(path, frame)
		response = genai.upload_file(path)

		request.append(str(i))
		request.append(response)

	response = genai_model.generate_content(
		request,
		request_options={'timeout': 600},
		safety_settings={
			'HATE': 'BLOCK_NONE',
			'HARASSMENT': 'BLOCK_NONE',
			'SEXUAL' : 'BLOCK_NONE',
			'DANGEROUS' : 'BLOCK_NONE'
		}
	)

	for path in temp_files:
		os.remove(path)

	send_message(PHONE_NUMBER, CARRIER, "Subject: ALERT\n\n " + response.text)
	return response.text

yolo_model = YOLO('yolov8n.pt')

pframes = deque(maxlen=PASSIVE_FRAMES) # 10 seconds of frames at 30fps
iframe = 0 # number of frames recorded
frames = [] # start recording when person is detected and record until person is not detected
pdetected = deque(maxlen=NOT_DETECTED_THRESHOLD)
ivideo = 0

threads = []

while True:
	# Screenshot and save to frames directory
	screenshot_data = element.screenshot_as_png
	# Convert to cv2 image
	nparr = np.frombuffer(screenshot_data, np.uint8)
	frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	
	bdetected, confidence = detect_person(img, yolo_model)

	if (bdetected):
		print("Person detected!", confidence)
		frames.append(img)
		iframe += 1
		if (iframe > UPPER_VIDEO_FRAMES_THRESHOLD):
			print('Uploading to Gemini')
			thread = Thread(target=upload_to_gemini, args=(genai, list(pframes) + frames))
			thread.start()
			threads.append(thread)

			ivideo += 1
			frames = []
			pframes.clear()
			iframe = 0
		pdetected.append(True)
	else:
		print("No person detected.", confidence)
		pframes.append(img)
		pdetected.append(False)

		if (len(frames) > LOWER_VIDEO_FRAMES_THRESHOLD and all(not pd for pd in pdetected)):
			print("Uploading to Gemini")
			thread = Thread(target=upload_to_gemini, args=(genai, list(pframes) + frames))
			thread.start()
			threads.append(thread)

			ivideo += 1
			frames = []
			pframes.clear()

	time.sleep(0.5)

