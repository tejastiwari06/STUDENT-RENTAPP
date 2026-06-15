# Hanashi Kikuyo

A professional student rental request platform built with Python Flask and Firebase.

## Features
- **Student Registration Form** — Post rental requests with strict validation
- **Request Dashboard** — Browse, accept, or reject active rental requests
- **Booking Confirmation** — Upload a screenshot to confirm a booking
- **AI Chatbot** — Floating chat widget for rental FAQs

## Quick Start

### 1. Prerequisites
- Python 3.10+
- A Firebase project (Realtime Database)

### 2. Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a project and enable **Realtime Database**
3. Go to **Project Settings → Service Accounts → Generate new private key**
4. Save the downloaded file as `serviceAccountKey.json` in the project root

### 3. Install & Run

```bash
# Clone / unzip the project, then:
cd student-rent-app

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set your FIREBASE_DATABASE_URL

# Run the app
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

```
student-rent-app/
├── app.py                  # Flask application & routes
├── firebase_config.py      # Firebase Admin SDK init
├── requirements.txt
├── .env.example
├── serviceAccountKey.json  # ← YOU provide this (not included)
├── templates/
│   ├── base.html           # Shared layout with Tailwind + chatbot
│   ├── index.html          # Registration / post a request
│   ├── dashboard.html      # Request feed (accept / reject)
│   └── confirmation.html   # Booking confirmation + screenshot upload
└── static/
    ├── css/style.css        # Custom styles
    ├── js/chatbot.js        # Chatbot logic
    └── uploads/            # Uploaded booking screenshots
```

## Notes
- Phone numbers are validated to digits only (7–15 characters).
- Uploaded screenshots are stored locally in `static/uploads/`.
- The AI chatbot is rule-based and requires no external API keys.
