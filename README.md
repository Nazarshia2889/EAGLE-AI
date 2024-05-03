# EagleAI Security Assist

## Overview
We enhance security systems by legeraging AI to provide immediate, actionable security reports. Our system, EAGLE (Enhanced Automated Guardian for Living Environments) AI, reduces false positive notifications and provides detailed summaries of any detected irregularities.

## Inspiration

After using popular security systems, we noticed a large amount of false positive notifications. Eventually, many of us became desensitized to these notifications, making it hard to determine if the alert was for an actual emergency or for something as minor as a stray animal. Receiving notifications such as “There Is Motion Detected at Your Front Door” didn’t tell us the severity of the notification. This is a huge problem, especially in home security, where every second counts. 

## Features
 - Detailed summary of irregularities instead of generic notifications.
 - Estimates severity and provides options for next steps.
 - Applications in personal security and large-scale surveillance.

This empowers the users with the immediate information needed to respond to the situation instead of them needing to manually classify the severity of the situation by rewatching security footage. 

## How It Works
Our system uses a traditional model to detect individuals in the footage. Once detected, it records thirty seconds of footage and leverages Gemini’s multimodal capabilities to summarize the footage, generating a comprehensive report.

