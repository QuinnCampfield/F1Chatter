---
title: F1 Chat Agent
emoji: 🏎️
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
short_description: An intelligent F1 data assistant powered by Google Gemini
---

# F1 Chat Agent

An intelligent F1 data assistant that uses Google Gemini's function calling to retrieve and analyze Formula 1 data in real-time.

## Features

- **Intelligent Query Processing**: Understands natural language queries about F1 data
- **Multi-step Data Retrieval**: Automatically chains API calls to get complete information
- **Real-time Data**: Fetches live F1 data from the OpenF1 API
- **Continuous Chat**: Maintains conversation context for follow-up questions

## Example Queries

- "What was George Russell's lap time on lap 8 of Bahrain?"
- "Show me all drivers in the latest race"
- "What are the session times for the 2024 season?"
- "Who had the fastest lap in qualifying at Monaco?"

## How It Works

The agent uses Google Gemini's function calling feature to:

1. **Analyze your query** to understand what F1 data you need
2. **Call appropriate functions** from `crud/f1_getters.py`:
   - `get_sessions()` - Find race sessions by year, country, or type
   - `get_drivers()` - Get driver information for a specific session
   - `get_laps()` - Retrieve lap times and sector data
3. **Chain multiple calls** when needed (e.g., session → drivers → specific lap times)
4. **Provide detailed answers** based on the retrieved data

## Architecture

- `application/main.py` - Main chat agent with Gemini integration
- `crud/f1_getters.py` - F1 data retrieval functions
- `crud/f1_data_types.py` - Data models for F1 entities
- `app.py` - Hugging Face Spaces entry point
- `gradio_app.py` - Web interface with Gradio

## Example Conversation

```
User: What was George Russell's lap time on lap 8 of Bahrain?

Agent: I'll help you find George Russell's lap time on lap 8 of the Bahrain race.

[Function calls happen automatically in the background]

Agent: George Russell's lap time on lap 8 of the Bahrain race was 1:32.456. 
This was his 8th lap of the race, and he was driving for Mercedes (driver #63).
```

## Requirements

- Google Gemini API key (set as environment variable `GEMINI_API_KEY`)
- Internet connection for F1 data API calls