# EagleAI Security Assist

![Basic example of Eagle AI](./docs/images/eagleai.gif)

## Overview:

We enhance security systems by leveraging AI to provide immediate, actionable security reports. Our system, EAGLE (Enhanced Automated Guardian for Living Environments) AI, reduces false positive notifications and provides detailed summaries of any detected irregularities. *We use camera feed from a Google Nest Camera in order to carry out our project.*

## Inspiration:

After using popular security systems, we noticed a large amount of false positive notifications. Eventually, many of us became desensitized to these notifications, making it hard to determine if the alert was for an actual emergency or for something as minor as a stray animal. Receiving notifications such as "There Is Motion Detected at Your Front Door" didn't tell us the severity of the notification. This is a huge problem, especially in home security, where every second counts.

## Features:

* Detailed summary of irregularities instead of generic notifications.
* Estimates severity and provides options for next steps.
* Applications in personal security and large-scale surveillance.

This empowers the users with the immediate information needed to respond to the situation instead of them needing to manually classify the severity of the situation by rewatching security footage.

## How It Works:

- Part 1: Google Nest API: Using the Google Device Access API, we are able to access the camera feed of a wired Nest camera. We then process the WebRTC stream frames through the YOLOv8n model and analyze whether or not there is a person being detected. If it detects a person, a video batch will be sent to Gemini.

- Part 2: Gemini: Once the frames are sent to Gemini, the model will process the frames and also, with a given prompt that asks for a detailed report, it will generate a detailed report ergarding the main events, the suspicion level, and recommended steps if needed.

- Part 3: Text Message: Once the report is finalized, using Python's EmailMessage library, we will send a text message of the report to the individual user notifying them of the situation and what the recommended next steps are.

### Want to use with your Nest Camera?

In order to get access to your Nest camera feed, you will need to register for Device Access to use the Google Device Access API. Follow the instructions on this page (https://developers.google.com/nest/device-access/project) to register for Device Access ($5) and retrieve the following:
* Access Token
* Project ID
* Device ID
* Client ID
* Client Secret
* Refresh Token

You will also need to set up an app password with your email: https://support.google.com/mail/answer/185833?hl=en.

Next, clone this repository and input the above variables in the corresponding fields of the `server.py` file from the `webrtc_server` folder, including the tokens listed above. Run `server.py` in order to run the backend server locally that collects the camera feed. Add the email and app password generated in the previous step in the corresponding EMAIL and PASSWORD fields in `nestcam.py`, as well as your phone number in this format: 1234567890. Make sure to also change the carrier to your current phone carrier (set to Verizon right now). In a separate instance from the server, run `nestcam.py`, and the system should be active as long as your Nest Camera and server are still on. When a person is detected in the scene, video batches are sent to Gemini to process and send a text message.

### Don't have a Nest Camera?

We have also created a Streamlit version of the product using your computer's webcam as the "security camera" for demos. To run, clone this repository, download the dependencies in requirements.txt, and run the app `webcam.py` with:
```shell
$ streamlit run webcam.py
```
This should open the app. Input your phone number and hit 'start' to turn on your webcam. This will execute the same algorithm as the Nest camera version.

:warning: Please note, MMS messages may experience delays due to processing via your carrier’s SMTP server. In the final product, we plan to implement our own VoIP system for improved efficiency. However, due to current constraints, this feature is not yet available. We appreciate your understanding and patience.
