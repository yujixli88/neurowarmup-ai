# NeuroWarmup AI

Adaptive cognitive warm-up assistant for students: a 5-minute training before studying or exams.

## Features
- Adaptive Mental Math: difficulty goes up or down based on the accuracy and speed of your answers. A Gemini-powered coach gives short feedback.
- Stroop Effect trainer: attention switching with a rule that changes between font color and word meaning.
- Brain and Hand Challenge: bimanual coordination exercise with a visual timer and AI-generated logic puzzles.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Get a free API key at aistudio.google.com and paste it into the sidebar (or set the GEMINI_API_KEY environment variable). Mental Math, Stroop and the hand exercise work without a key.

## Tech stack
Python, Streamlit, Google Gemini API (gemini-2.5-flash)

## Hackathon
HackGlobal 2026, track: Artificial Intelligence
