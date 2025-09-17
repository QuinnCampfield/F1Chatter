#!/usr/bin/env python3
"""
F1 Chat Agent - Gradio Web Interface
A web-based chat interface for the F1 data assistant
"""

import os
import sys
import gradio as gr
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        
        # Email configuration
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'recipient_email': os.getenv('RECIPIENT_EMAIL'),
        }
        
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
            print("\n=== DEBUG: Processing message ===")
            print(f"User message: {message}")
            
            response = self.agent.process_query(message)
            
            print(f"Agent response: {response}")
            print(f"Response type: {type(response)}")
            print(f"Response length: {len(str(response)) if response else 0}")
            print("=== END DEBUG ===\n")
            
            # Update the last message with the response
            history[-1][1] = response
            
            return "", history
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history[-1][1] = error_msg
            return "", history
    
    def send_bug_report(self, chat_history: List[List[str]]) -> str:
        """
        Send a bug report email with chat logs
        
        Args:
            chat_history: Current chat history
            
        Returns:
            Status message
        """
        try:
            # Check if email is configured
            if not all([self.email_config['sender_email'], 
                       self.email_config['sender_password'], 
                       self.email_config['recipient_email']]):
                return "Email not configured. Please contact the administrator."
            
            # Create email content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format chat history
            chat_log = "F1 Chat Agent Bug Report\n"
            chat_log += f"Timestamp: {timestamp}\n"
            chat_log += "=" * 50 + "\n\n"
            
            if chat_history:
                for i, (user_msg, bot_msg) in enumerate(chat_history, 1):
                    chat_log += f"Exchange {i}:\n"
                    chat_log += f"User: {user_msg}\n"
                    chat_log += f"Bot: {bot_msg}\n"
                    chat_log += "-" * 30 + "\n\n"
            else:
                chat_log += "No chat history available.\n"
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"F1 Chat Agent Bug Report - {timestamp}"
            
            msg.attach(MIMEText(chat_log, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], self.email_config['recipient_email'], text)
            server.quit()
            
            return "Bug report sent successfully!"
            
        except Exception as e:
            return f"Failed to send bug report: {str(e)}"
    
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
                - "Who had the fastest Qualifying lap time at the 2025 Monza race?"
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
            
            # Action buttons
            with gr.Row():
                clear_btn = gr.Button("Clear Chat", variant="secondary")
                bug_report_btn = gr.Button("Report Bug", variant="secondary")
            
            # Status message for bug reports
            status_msg = gr.Textbox(
                value="",
                label="Status",
                interactive=False,
                visible=False,
                show_label=False
            )
            
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
            
            # Bug report handler
            def handle_bug_report(history):
                result = self.send_bug_report(history)
                return result, gr.update(visible=True)
            
            bug_report_btn.click(
                handle_bug_report,
                inputs=[chatbot],
                outputs=[status_msg, status_msg]
            )
            
            # Footer
            gr.Markdown(
                """
                ---
                **Powered by OpenAI GPT and OpenF1 API**
                
                This agent can retrieve real-time F1 data including:
                - Race sessions and schedules
                - Driver information and standings  
                - Lap times and sector data
                - And much more!
                """,
                elem_classes=["footer"]
            )
        
        return interface

def main():
    """Main function to launch the Gradio app"""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    # Create and launch the app
    app = F1GradioApp()
    interface = app.create_interface()
    
    print("Starting F1 Chat Agent Web Interface...")
    print("Open your browser and go to the URL shown below")
    print("Ready to answer your F1 questions!")
    
    # Launch with sharing disabled for local use
    interface.launch(
        server_name="127.0.0.1",  # Local only
        server_port=7860,         # Default Gradio port
        share=False,              # Local deployment only
        show_error=True,          # Show errors in the interface
        quiet=False               # Show startup messages
    )

if __name__ == "__main__":
    main()
