import streamlit as st
import cv2
from ultralytics import YOLO
from collections import deque
from threading import Thread
import google.generativeai as genai
import os
import smtplib
import numpy as np
import queue
from streamlit_webrtc import WebRtcMode, webrtc_streamer

FPS = 30 # frames per second
CONFIDENCE_THRESHOLD = 0.6 # face detection confidence threshold
LOWER_VIDEO_FRAMES_THRESHOLD = 2 * FPS # shortest video duration in seconds
UPPER_VIDEO_FRAMES_THRESHOLD = 30 * FPS # longest video duration in seconds
PASSIVE_FRAMES = 10 * FPS # frames to export before person is detected
PROCESSING_FRAMES = 30 # process 1 frame every n frames
NOT_DETECTED_THRESHOLD = 2 * FPS # number of frames to wait before stopping recording

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vzwpix.com",
    "sprint": "@messaging.sprintpcs.com"
}

EMAIL = os.environ.get("EMAIL") # app email/authentication
PASSWORD = os.environ.get("PASSWORD") # app password/authentication

PROMPT = """
Analyze this security footage. Give a detailed descriptions on the actions of all people that appear in the video. Carefully note any criminal activity when suspected, including, but not limited to: theft, burglary, and vandalism. Do not include timestamps. Speak as if you're talking to the homeowner. Make it in the following format:
"ALERT" (don't put this in quotations)
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
	for i, frame in enumerate(frames[1::PROCESSING_FRAMES]):
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

	send_message(phone_number, "verizon", response.text)
	return response.text

genai.configure(api_key='AIzaSyCUAR7qw9UPOay8T8Pg9-ExH0OJSCNU89E')
genai_model = genai.GenerativeModel(model_name='models/gemini-1.5-pro-latest')

st.set_page_config(page_title='EagleAI')
st.title('EagleAI: Security Monitor Descriptor with Google Gemini')
st.caption('EagleAI Demo with your own webcam as the security camera. Powered by OpenCV, Streamlit')

st.text("Input your phone number before starting webcam to receive text alerts.")
phone_number = st.text_input('Phone Number', '1234567890')

yolo_model = YOLO('yolov8n.pt')
# yolo_model.to('cuda')

st.warning("""Please note, MMS messages may experience delays due to processing via your carrier’s SMTP server. In the final product, we plan to implement our own VoIP system for improved efficiency. However, due to current project constraints, this feature is not yet available.""")

pframes = deque(maxlen=PASSIVE_FRAMES) # 10 seconds of frames at 30fps
iframe = 0 # number of frames recorded
frames = [] # start recording when person is detected and record until person is not detected
pdetected = deque(maxlen=NOT_DETECTED_THRESHOLD)
ivideo = 0

threads = []

webrtc_ctx = webrtc_streamer(
    key="video-sendonly",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"video": True},
)

image_place = st.empty()

while True:
	if webrtc_ctx.video_receiver:
		try:
			video_frame = webrtc_ctx.video_receiver.get_frame(timeout=1)
			st.text("here")
		except queue.Empty:
			break

		img = video_frame.to_ndarray(format="rgb24")
		image_place.image(img)
		img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
		bdetected, confidence = detect_person(img, yolo_model)
		if (bdetected):
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

		for thread in threads:
			thread.join()	
	else:
		break
