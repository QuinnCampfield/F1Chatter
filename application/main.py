import os
import sys
import json
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append('..')

# Import our F1 data functions and types
from crud.f1_getters import get_sessions, get_drivers, get_laps

# Load environment variables
load_dotenv()

class F1ChatAgent:
    def __init__(self, verbose: bool = True):
        """Initialize the F1 Chat Agent with OpenAI client and function definitions"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = []
        self.function_definitions = self._get_function_definitions()
        self.model = "gpt-4o-mini"  # Default model
        self.verbose = verbose  # Control print statements
        
    def _get_function_definitions(self) -> List[Dict[str, Any]]:
        """Define the available F1 functions for OpenAI function calling"""
        return [
            {
                "name": "get_sessions",
                "description": "Get F1 sessions for a specific year, session type, session name, or country. Use this to find session keys for specific races or events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "The year to fetch sessions for (e.g., 2024, 2025)",
                            "default": 2025
                        },
                        "session_type": {
                            "type": "string",
                            "description": "Type of session (e.g., 'Race', 'Qualifying', 'Practice 1', 'Practice 2', 'Practice 3')",
                            "enum": ["Race", "Qualifying", "Practice 1", "Practice 2", "Practice 3", "Sprint", "Sprint Qualifying"]
                        },
                        "session_name": {
                            "type": "string",
                            "description": "Name of session (e.g., 'Race', 'Sprint', 'Qualifying', 'Sprint Qualifying', 'Practice 1', 'Practice 2', 'Practice 3')",
                            "enum": ["Race", "Qualifying", "Practice 1", "Practice 2", "Practice 3", "Sprint", "Sprint Qualifying"]
                        },
                        "country_name": {
                            "type": "string",
                            "description": "Country name for the race (e.g., 'Bahrain', 'Saudi Arabia', 'Australia')"
                        }
                    }
                }
            },
            {
                "name": "get_drivers",
                "description": "Get F1 drivers for a specific session. Use this to find driver numbers and names for a particular race or session.",
                "parameters": {
                    "type": "object",
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
                    "type": "object",
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
                    session_name=arguments.get("session_name"),
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
        """Process a user query using OpenAI function calling"""
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_query})
        
        # Create system message with context
        system_message = {
            "role": "system",
            "content": """You are an F1 data assistant. You can help users get information about F1 sessions, drivers, and lap times.

General information:
- Session type and Session name are different. Session name allows more specific to include Sprint and Sprint Qualifying
- A Sprint session name will be under the Race session type. But isn't typically counted as a Race colloquially
- You need to use get_drivers to map driver names to driver numbers, the other functions use driver numbers

Available functions:
1. get_sessions - Get F1 sessions for a year, session type, session name, or country
2. get_drivers - Get drivers for a specific session (need session_key)
3. get_laps - Get lap data for a session and optionally a specific driver

For complex queries like "What was George Russell's lap time on lap 8 of Bahrain?", you need to:
1. First call get_sessions to find the Bahrain session key
2. Then call get_drivers to find George Russell's driver number
3. Finally call get_laps with the session key and driver number to get his lap times

For complex queries like "How many races have happened in 2025?", you need to:
1. First call get_sessions with 2025 as year specified
2. Then count in the results and get the instances of session type being Race and session name being Race.

Always use the function calling feature to get real data before answering questions. Be helpful and provide detailed information."""
        }
        
        # Prepare messages for OpenAI
        messages = [system_message] + self.conversation_history
        
        try:
            # Keep calling functions until we have a final response
            max_function_calls = 5  # Prevent infinite loops
            function_call_count = 0
            
            while function_call_count < max_function_calls:
                # Call OpenAI with function calling
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    functions=self.function_definitions,
                    function_call="auto",
                    temperature=0.1
                )
                
                message = response.choices[0].message
                
                # Check if the model wants to call a function
                if message.function_call:
                    function_name = message.function_call.name
                    function_args = json.loads(message.function_call.arguments)
                    
                    if self.verbose:
                        print(f"\nCalling function: {function_name}")
                        print(f"Arguments: {function_args}")
                    
                    # Execute the function
                    function_result = self._call_function(function_name, function_args)
                    formatted_result = self._format_function_result(function_name, function_result)
                    
                    if self.verbose:
                        print(f"Result: {formatted_result[:200]}...")
                    
                    # Add function call and result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": message.function_call.arguments
                        }
                    })
                    
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": formatted_result
                    })
                    
                    function_call_count += 1
                    if self.verbose:
                        print(f"Function call {function_call_count}/{max_function_calls} completed")
                    
                else:
                    # No more function calls needed, return the response
                    assistant_response = message.content
                    self.conversation_history.append({"role": "assistant", "content": assistant_response})
                    return assistant_response
            
            # If we hit the max function calls, get a final response
            if self.verbose:
                print(f"Reached maximum function calls ({max_function_calls}), generating final response...")
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            
            assistant_response = final_response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            return assistant_response
                
        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                return "Model access error. Please check your OpenAI API key and model access. Try using a different model or contact OpenAI support."
            elif "api key" in error_msg.lower():
                return "API key error. Please check your OPENAI_API_KEY in the .env file."
            else:
                print(f"Error: {error_msg}")
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
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    # Initialize and start the chat agent
    agent = F1ChatAgent()
    agent.start_chat()

if __name__ == "__main__":
    main()
