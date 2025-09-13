# F1 Chat Agent

An intelligent F1 data assistant that uses OpenAI's function calling to retrieve and analyze Formula 1 data in real-time.

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

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -e .
   ```

2. **Set up OpenAI API Key**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   Get your API key from: https://platform.openai.com/api-keys

3. **Run the Agent**:
   ```bash
   python run_agent.py
   ```

## How It Works

The agent uses OpenAI's function calling feature to:

1. **Analyze your query** to understand what F1 data you need
2. **Call appropriate functions** from `crud/f1_getters.py`:
   - `get_sessions()` - Find race sessions by year, country, or type
   - `get_drivers()` - Get driver information for a specific session
   - `get_laps()` - Retrieve lap times and sector data
3. **Chain multiple calls** when needed (e.g., session → drivers → specific lap times)
4. **Provide detailed answers** based on the retrieved data

## Architecture

- `application/main.py` - Main chat agent with OpenAI integration
- `crud/f1_getters.py` - F1 data retrieval functions
- `crud/f1_data_types.py` - Data models for F1 entities
- `run_agent.py` - Simple runner script

## Example Conversation

```
🏁 You: What was George Russell's lap time on lap 8 of Bahrain?

🤖 Calling function: get_sessions
📋 Arguments: {'year': 2025, 'country_name': 'Bahrain'}

🤖 Calling function: get_drivers  
📋 Arguments: {'session_key': '12345'}

🤖 Calling function: get_laps
📋 Arguments: {'session_key': '12345', 'driver_number': 63}

🤖 F1 Agent: George Russell's lap time on lap 8 of the Bahrain race was 1:32.456. 
This was his 8th lap of the race, and he was driving for Mercedes (driver #63).
```

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for F1 data API calls
