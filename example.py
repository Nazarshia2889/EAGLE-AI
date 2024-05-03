import google.generativeai as genai
import os
from framesParser import upload_to_gemini
from notify import send_message
from email.message import EmailMessage
import smtplib

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vzwpix.com",
    "sprint": "@messaging.sprintpcs.com"
}

genai.configure(api_key="AIzaSyCUAR7qw9UPOay8T8Pg9-ExH0OJSCNU89E")

video_file_name = "Burglary004_x264.mp4" # CRIME VIDEO

uploaded_files = upload_to_gemini(genai, video_file_name, full_video=False)

# Create the prompt.
prompt = "You are analyzing the security camera footage to inform a homeowner for any potential criminal activity aimed at their property. Assume all individuals that appear in the video footage are not the homeowner.  This is a Text message keep it concise and highly informative and include no markup or special charecters. Keep the message short at ~250 characters."

# Set the model to Gemini 1.5 Pro.
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# Make GenerateContent request with the structure described above.
def make_request(prompt, files):
  request = [prompt]
  for file in files:
    print(file.timestamp)
    print(file.response)
    request.append(file.timestamp)
    request.append(file.response)
  return request

# Make the LLM request.
request = make_request(prompt, uploaded_files)
print(request)
response = model.generate_content(request,
                                  request_options={"timeout": 600}, 
                                  safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })

# 8582910362 levi 
# 8582105220 kathik
EMAIL = os.environ.get("EMAIL") # eail to send sms from
PASSWORD = os.environ.get("PASSWORD") # app password/authentication
def send_message(phone_number, carrier, message):
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)
    print(f"Usage: python3 {phone_number, carrier, message}")
send_message("8584420958", "verizon", "Subject: ALERT\n\n " + response.text) 
print(response.text)


# import google.generativeai as genai
# import os
# from framesParser import upload_to_gemini

# genai.configure(api_key="AIzaSyCUAR7qw9UPOay8T8Pg9-ExH0OJSCNU89E")

# video_file_name = "Burglary004_x264.mp4" # CRIME VIDEO

# uploaded_files = upload_to_gemini(genai, video_file_name, full_video=False)

# # Create the prompt.
# prompt = "Describe this video."

# # Set the model to Gemini 1.5 Pro.
# model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# # Make GenerateContent request with the structure described above.
# def make_request(prompt, files):
#   request = [prompt]
#   for file in files:
#     request.append(file.timestamp)
#     request.append(file.response)
#   return request

# # Make the LLM request.
# request = make_request(prompt, uploaded_files)
# response = model.generate_content(request,
#                                   request_options={"timeout": 600})
# print(response.text)

