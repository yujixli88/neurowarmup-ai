# NeuroWarmup AI

Adaptive cognitive warm-up assistant for students: a 5-minute training before studying or exams.

## Features
- Adaptive Mental Math: difficulty goes up or down based on the accuracy and speed of your answers. A Gemini-powered coach gives short feedback.
- Stroop Effect trainer: attention switching with a rule that changes between font color and word meaning.
- Brain and Hand Challenge: bimanual coordination exercise with a visual timer and logic puzzles (AI-generated with an API key, or taken from a built-in set without one).
- Bilingual interface: Russian and English, switchable on the page.
- Vintage engraving-style design with custom ornaments.

## Run locally
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```
Keep all the .png files in the same folder as app.py: they are used for the design.

Get a free API key at aistudio.google.com and paste it into the Settings section at the top of the page (or set the GEMINI_API_KEY environment variable). Mental Math, Stroop, the hand exercise and the built-in puzzles work without a key. The AI coach and AI-generated puzzles need a key.

## Tech stack
Python, Streamlit, Google Gemini API (gemini-2.5-flash)

## Hackathon
HackGlobal 2026, track: Artificial Intelligence
