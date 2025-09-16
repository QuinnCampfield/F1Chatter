import os
import sys
import json
from typing import List, Dict, Any
from google import genai
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append('..')

# Import our F1 data functions and types
from crud.f1_getters import get_sessions, get_drivers, get_laps

# Load environment variables
load_dotenv()

class F1ChatAgent:
    def __init__(self, verbose: bool = True):
        """Initialize the F1 Chat Agent with Gemini client and function definitions"""
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set!")

        if verbose:
            print(f"API key loaded: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")

        # New Google GenAI client automatically reads GEMINI_API_KEY
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash-lite"
        self.conversation_history = []
        self.function_definitions = self._get_function_definitions()
        self.verbose = verbose  # Control print statements
        
    def _get_function_definitions(self) -> List[Dict[str, Any]]:
        """Define the available F1 functions for Gemini function calling"""
        return [
            {
                "name": "get_sessions",
                "description": "Get F1 sessions for a specific year, session type, session name, or country. Use this to find session keys for specific races or events.",
                "parameters": {
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "The year to fetch sessions for (e.g., 2024, 2025)"
                        },
                        "session_type": {
                            "type": "string",
                            "description": "Type of session (e.g., 'Race', 'Qualifying', 'Practice 1', 'Practice 2', 'Practice 3')"
                        },
                        "session_name": {
                            "type": "string",
                            "description": "Name of session (e.g., 'Race', 'Qualifying', 'Practice 1', 'Practice 2', 'Practice 3', 'Sprint', 'Sprint Qualifying')"
                        },
                        "country_name": {
                            "type": "string",
                            "description": "Country name for the race (e.g., 'Bahrain', 'Saudi Arabia', 'Australia')"
                        }
                    },
                    "required": ["year"]
                }
            },
            {
                "name": "get_drivers",
                "description": "Get F1 drivers for a specific session. Use this to find driver numbers and names for a particular race or session.",
                "parameters": {
                    "properties": {
                        "session_key": {
                            "type": "string",
                            "description": "The session key from get_sessions function. Use 'latest' for the most recent session."
                        }
                    },
                    "required": ["session_key"]
                }
            },
            {
                "name": "get_laps",
                "description": "Get F1 lap data for a specific session and optionally a specific driver. Use this to get lap times, sector times, and other lap data.",
                "parameters": {
                    "properties": {
                        "session_key": {
                            "type": "string",
                            "description": "The session key from get_sessions function. Use 'latest' for the most recent session."
                        },
                        "driver_number": {
                            "type": "integer",
                            "description": "Optional driver number to filter laps for a specific driver. Get this from get_drivers function."
                        }
                    },
                    "required": ["session_key"]
                }
            }
        ]
    
    def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute the specified function with given arguments"""
        try:
            if function_name == "get_sessions":
                return get_sessions(
                    year=arguments.get("year", 2025),
                    session_type=arguments.get("session_type"),
                    country_name=arguments.get("country_name")
                )
            elif function_name == "get_drivers":
                return get_drivers(session_key=arguments["session_key"])
            elif function_name == "get_laps":
                return get_laps(
                    session_key=arguments["session_key"],
                    driver_number=arguments.get("driver_number")
                )
            else:
                return f"Unknown function: {function_name}"
        except Exception as e:
            return f"Error calling {function_name}: {str(e)}"
    
    def _format_function_result(self, function_name: str, result: Any) -> str:
        """Format function results for the AI model"""
        if result is None:
            return f"No data returned from {function_name}"
        
        if function_name == "get_sessions" and isinstance(result, list):
            sessions_info = []
            for session in result:
                sessions_info.append({
                    "session_key": session.session_key,
                    "session_name": session.session_name,
                    "location": session.location,
                    "country_name": session.country_name,
                    "session_type": session.session_type,
                    "date_start": session.date_start
                })
            return f"Found {len(result)} sessions: {json.dumps(sessions_info, indent=2)}"
        
        elif function_name == "get_drivers" and isinstance(result, list):
            drivers_info = []
            for driver in result:
                drivers_info.append({
                    "driver_number": driver.driver_number,
                    "full_name": driver.full_name,
                    "name_acronym": driver.name_acronym,
                    "team_name": driver.team_name,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name
                })
            return f"Found {len(result)} drivers: {json.dumps(drivers_info, indent=2)}"
        
        elif function_name == "get_laps" and isinstance(result, list):
            laps_info = []
            for lap in result:
                lap_data = {
                    "lap_number": lap.lap_number,
                    "driver_number": lap.driver_number,
                    "lap_duration": lap.lap_duration,
                    "duration_sector_1": lap.duration_sector_1,
                    "duration_sector_2": lap.duration_sector_2,
                    "duration_sector_3": lap.duration_sector_3,
                    "is_pit_out_lap": lap.is_pit_out_lap
                }
                laps_info.append(lap_data)
            return f"Found {len(result)} laps: {json.dumps(laps_info, indent=2)}"
        
        return str(result)
    
    def process_query(self, user_query: str) -> str:
        """Process a user query using Gemini with manual function calling"""
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_query})
        
        # Create system prompt with context
        system_prompt = """You are an F1 data assistant. You can help users get information about F1 sessions, drivers, and lap times.

CRITICAL: NEVER assume what year it is. NEVER refuse to search for data based on calendar dates. If a user asks for 2025 data, call get_sessions(year=2025). And if data is returned trust it fully

DEFAULT BEHAVIOR: If a user doesn't specify a year or exact race, use session_key="latest" to get the most recent data. The returned data will include the actual date information.
you can use the latest key to get the most recent date if you need the most recent year.

You have access to these functions:
1. get_sessions(year, optional(session_type), optional(session_name), optional(country_name)) - Get F1 sessions
2. get_drivers(session_key) - Get drivers for a session
3. get_laps(session_key, optional(driver_number)) - Get lap data

General information:
- Session type and Session name are different. Session name allows more specific to include Sprint and Sprint Qualifying
- A Sprint session name will be under the Race session type. But isn't typically counted as a Race colloquially
- You need to use get_drivers to map driver names to driver numbers, the other functions use driver numbers
- All data from the functions is in the past. Do not think about what you believe the date to be. This data is correct and up to the currentdate.

Authority and temporal grounding:
- Treat all data returned by functions (get_sessions, get_drivers, get_laps) as complete and authoritative snapshots of reality. Do not override them with calendar logic or assumptions about today's date.
- Do not infer whether an event has happened based on current calendar dates. If a session appears in function results, assume it has occurred and should be counted.
- Never project or predict future events. Only answer from function results you've actually received.
- If function results show races with dates later than "today", still count them as occurred. The functions provide finalized historical data and may reflect delayed publication rather than future events.
- When counting or summarizing, use only the returned objects (e.g., count sessions where session_type == "Race" and session_name == "Race") rather than reasoning about calendars.

For complex queries like "What was George Russell's lap time on lap 8 of Bahrain?", you need to:
1. First call get_sessions to find the Bahrain session key
2. Then call get_drivers to find George Russell's driver number
3. Finally call get_laps with the session key and driver number

When you need to call a function, respond with exactly this format:
FUNCTION_CALL: function_name(arg1=value1, arg2=value2)

I will execute the function and provide the results. Then you can analyze the data and give a helpful response."""
        
        try:
            # Build conversation context
            conversation_text = system_prompt + "\n\n"
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    conversation_text += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    conversation_text += f"Assistant: {msg['content']}\n"

            max_function_calls = 6
            calls_made = 0

            while calls_made <= max_function_calls:
                # Ask the model what to do next or to answer
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=conversation_text,
                    config={
                        "temperature": 0.1,
                        "max_output_tokens": 2048,
                    }
                )

                assistant_response = response.text or ""

                # If the model requests a function call, execute it, append a structured result, and loop
                if "FUNCTION_CALL:" in assistant_response:
                    function_line = next((line for line in assistant_response.split('\n') if 'FUNCTION_CALL:' in line), "")
                    function_call_str = function_line.replace('FUNCTION_CALL:', '').strip()

                    function_name = None
                    function_args = {}
                    if '(' in function_call_str and ')' in function_call_str:
                        function_name = function_call_str.split('(')[0].strip()
                        args_str = function_call_str.split('(')[1].split(')')[0].strip()

                        if args_str:
                            for arg in args_str.split(','):
                                if '=' in arg:
                                    key, value = arg.split('=', 1)
                                    key = key.strip()
                                    value = value.strip().strip('"\'')
                                    if value.isdigit():
                                        function_args[key] = int(value)
                                    elif value.lower() in ['true', 'false']:
                                        function_args[key] = value.lower() == 'true'
                                    else:
                                        function_args[key] = value

                    if not function_name:
                        # Could not parse a function name; break and return the current text
                        break

                    if self.verbose:
                        print(f"\nCalling function: {function_name}")
                        print(f"Arguments: {function_args}")

                    function_result = self._call_function(function_name, function_args)
                    formatted_result = self._format_function_result(function_name, function_result)

                    if self.verbose:
                        print(f"Result: {formatted_result[:200]}...")

                    # Crucial: explicitly provide a structured FUNCTION_RESULT the model can detect
                    conversation_text += (
                        f"Assistant: {assistant_response}\n"
                        f"FUNCTION_RESULT: {function_name} -> {formatted_result}\n"
                    )

                    calls_made += 1
                    continue

                # No function call requested; treat as final answer
                self.conversation_history.append({"role": "assistant", "content": assistant_response})
                return assistant_response

            # Safety fallback if too many calls
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            return assistant_response
                
        except Exception as e:
            error_msg = str(e)
            print(f"Full error details: {error_msg}")
            print(f"Error type: {type(e)}")
            
            if "api key" in error_msg.lower():
                return "API key error. Please check your GEMINI_API_KEY in the .env file."
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "API quota exceeded. Please check your Gemini API usage limits."
            elif "permission" in error_msg.lower():
                return "Permission error. Please check your Gemini API key permissions."
            else:
                return f"Error processing query: {error_msg}"
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("Welcome to F1 Chat Agent!")
        print("Ask me anything about F1 data - sessions, drivers, lap times, etc.")
        print("Example: 'What was George Russell's lap time on lap 8 of Bahrain?'")
        print("Type 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Thanks for using F1 Chat Agent!")
                    break
                
                if not user_input:
                    continue
                
                print("\nProcessing your query...")
                response = self.process_query(user_input)
                print(f"\nF1 Agent: {response}\n")
                
            except KeyboardInterrupt:
                print("\nThanks for using F1 Chat Agent!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

def main():
    """Main function to run the F1 Chat Agent"""
    # Check if Gemini API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set!")
        print("Please create a .env file with your Gemini API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        return
    
    # Initialize and start the chat agent
    agent = F1ChatAgent()
    agent.start_chat()

if __name__ == "__main__":
    main()
