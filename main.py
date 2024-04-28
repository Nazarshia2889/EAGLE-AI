import google.generativeai as genai
import os
from framesParser import upload_to_gemini

# genai.configure(api_key="YOUR_API_KEY")

video_file_name = "Burglary004_x264.mp4" # CRIME VIDEO

uploaded_files = upload_to_gemini(genai, video_file_name, full_video=False)

# Create the prompt.
prompt = "Describe this video."

# Set the model to Gemini 1.5 Pro.
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# Make GenerateContent request with the structure described above.
def make_request(prompt, files):
  request = [prompt]
  for file in files:
    request.append(file.timestamp)
    request.append(file.response)
  return request

# Make the LLM request.
request = make_request(prompt, uploaded_files)
response = model.generate_content(request,
                                  request_options={"timeout": 600})
print(response.text)

