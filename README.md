# Smart Interview System

This repository contains a small Flask application for generating interview feedback reports using an LLM. It exposes a few REST endpoints for retrieving transcripts from MongoDB and emailing generated PDFs to a candidate.  A watcher script can be run to monitor a Gmail inbox for feedback requests and automatically send reports.

## Prerequisites

- Python 3.8+
- MongoDB instance
- Google API credentials for Gmail access
- An API key for OpenRouter (proxy for OpenAI)

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file with at least the following variables:

```
MONGO_URI=<your-mongo-uri>
OPENROUTER_API_KEY=<api-key>
SENDER_EMAIL=<gmail address>
SENDER_PASSWORD=<gmail password>
GOOGLE_CREDENTIALS_JSON='<json credentials>'
```

## Running the Web API

The main API lives in `app.py` and exposes endpoints on port `10000` by default:

```bash
python app.py
```

Open `http://localhost:10000` in your browser to access the simple manager interface.

## Gmail Feedback Watcher

`gmail_feedback_watcher.py` polls a Gmail inbox and sends feedback PDFs when an email with subject `"Request Feedback"` arrives. Start it separately:

```bash
python gmail_feedback_watcher.py
```

## Deployment

A basic `procfile` and `render.yaml` are included for hosting on platforms like Heroku or Render.
