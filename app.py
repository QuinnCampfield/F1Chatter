#!/usr/bin/env python3
"""
F1 Chat Agent - Hugging Face Spaces Entry Point
This is the main entry point for Hugging Face Spaces deployment
"""

import os
import sys
import gradio as gr
from typing import List, Tuple

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from application.main import F1ChatAgent

class F1GradioApp:
    def __init__(self):
        """Initialize the Gradio app with F1 Chat Agent"""
        self.agent = F1ChatAgent(verbose=False)  # Disable verbose mode for web interface
        self.chat_history = []
        
    def process_message(self, message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
        """
        Process a user message and return the response with updated history
        
        Args:
            message: User's input message
            history: Current chat history
            
        Returns:
            Tuple of (empty string for input, updated chat history)
        """
        if not message.strip():
            return "", history
            
        # Add user message to history
        history.append([message, None])
        
        try:
            # Process the message with the agent
            response = self.agent.process_query(message)
            
            # Update the last message with the response
            history[-1][1] = response
            
            return "", history
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history[-1][1] = error_msg
            return "", history
    
    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface"""
        
        # Custom CSS for F1 theming
        css = """
        .gradio-container {
            max-width: 800px !important;
            margin: auto !important;
        }
        .chat-message {
            padding: 10px;
            margin: 5px 0;
            border-radius: 10px;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: 20%;
        }
        .bot-message {
            background-color: #f3e5f5;
            margin-right: 20%;
        }
        /* Hide any remaining label text */
        .gr-textbox label,
        .gr-textbox .label,
        .gr-textbox .gr-label {
            display: none !important;
        }
        """
        
        with gr.Blocks(
            title="F1 Chat Agent",
            css=css,
            theme=gr.themes.Soft()
        ) as interface:
            
            # Header
            gr.Markdown(
                """
                # F1 Chat Agent
                Ask me anything about F1 data - sessions, drivers, lap times, and more!
                
                **Example queries:**
                - "What was George Russell's lap time on lap 8 of Bahrain?"
                - "Show me all drivers in the latest race"
                - "What are the session times for the 2024 season?"
                """,
                elem_classes=["header"]
            )
            
            # Chat interface
            chatbot = gr.Chatbot(
                label="F1 Chat",
                height=500,
                show_label=True,
                container=True,
                bubble_full_width=False,
                avatar_images=("temp.png", "temp2.png")
            )
            
            # Input components
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask me about F1 data...",
                    label=None,
                    lines=1,
                    scale=4,
                    show_label=False
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
            
            # Clear button
            clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            # Event handlers
            def submit_message(message, history):
                return self.process_message(message, history)
            
            # Handle Enter key and button click
            msg_input.submit(
                submit_message,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot]
            )
            
            send_btn.click(
                submit_message,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot]
            )
            
            # Clear chat
            clear_btn.click(
                lambda: ([], []),
                outputs=[chatbot, msg_input]
            )
            
            # Footer
            gr.Markdown(
                """
                ---
                **Powered by Google Gemini and OpenF1 API**
                
                This agent can retrieve real-time F1 data including:
                - Race sessions and schedules
                - Driver information and standings  
                - Lap times and sector data
                - And much more!
                """,
                elem_classes=["footer"]
            )
        
        return interface

# Create the app instance
app = F1GradioApp()
interface = app.create_interface()

# Launch the interface
if __name__ == "__main__":
    interface.launch(share=False)
