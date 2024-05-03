import smtplib
import sys
import os
from email.message import EmailMessage

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com"
}

EMAIL = os.environ.get("EMAIL")

PASSWORD = os.environ.get("PASSWORD")

def send_message(phone_number, carrier, message):
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)
    print(f"Usage: python3 {phone_number, carrier, message}")


if __name__ == "__main__":
  phone_number = "YOUR PHONE NUMBER HERE"
  carrier = "verizon"
  message = "hello, this is from python program"
  print(f"Usage: python3 {phone_number, carrier, message}")
  send_message(phone_number, carrier, message)
