import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime

import dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory

from src.plugins.output.plugin import OutputPlugin
from src.plugins.well_architected.plugin import WellArchitectedPlugin

SYSTEM_PROMPT = (
    "You are an AI assistant for creating Architecture Decision Records (ADRs). "
    "Your task is to help users create ADRs by asking clarifying questions and providing guidance. "
    "You will also assist in generating the ADR content based on user input. "
    "Your goal is to ensure that the ADR is well-structured and comprehensive. "
    "You will ask the user for the necessary information to create the ADR, "
    "and you will provide suggestions and examples to help them fill in the details. "
    "You will also ensure that the ADR follows the standard format and includes all required sections. "
    "Format the ADR content in Markdown. "
    "Sections: Context, Current State, Considered Options, Decision Drivers, Decision Outcome, Consequences. "
    "Provide relevant Azure Well Architected Framework references for each section."
    "Use WellArchitectedPlugin to ensure the ADR covers all aspects of the framework for non-functional requirements."
    "Azure Well Architected Framework guidlines should be used inside every section. Keep a list of references in the end of the ADR."
    "Articulate the considered options using the Azure Well Architected Framework guidelines."
    #"You need to use Azure Architecture Center to ensure the ADR visits well known patterns and practices."
    "Decision drivers should be a table comparing the options and provide a score of Yes, No, or Maybe."
    "Ask necessary questions one by one to the user to fill in the sections. "
    "Show the progress of the ADR creation process to the user as you go along. "
    "Progress should be show as table and completion status of each section with."
    "To show progress if a section is completed, use: ✔️"
    "To show progress if a section is not started, use ➖"
    "To show progress if a section is in Progress, use 🟡. "
    "Show the references found in the WellArchitectedPlugin for each section. "
    "Save the progress of each section to a Markdown file using the OutputPlugin by sending the ADR_ID, section name and section content. "
    "Confirm saved file path to the user as a system info message."
)

WELCOME_MESSAGE = (
    "👋 Welcome! I am your AI assistant for creating Architecture Decision Records (ADRs).\n"
    "I will guide you step-by-step to ensure your ADR is well-structured and comprehensive, "
    "following the standard format and best practices from the Azure Well Architected Framework and Azure Architecture Center.\n"
    "Let's get started! I’ll ask you questions to help fill in each section:\n"
    "Context, Current State, Decision Drivers, Considered Options, Decision Outcome, and Consequences.\n"
    "Feel free to ask for suggestions or examples at any time. Type 'exit' to quit.\n"

    "Let's begin with the first question!\n"
    "What is the context of the decision you are making? "
)

def generate_adr_reference_id():
    """Generate an ADR reference ID in the format 'adr-<5-char-uuid>-<YYYYMMDD>'"""
    short_uuid = str(uuid.uuid4())[:5]
    date_str = datetime.now().strftime("%Y%m%d")
    return f"adr-{date_str}-{short_uuid}"

def user_input(prompt):
    """Get user input with colored prompt."""
    # Cyan color for user prompt
    return input(f"\033[96m{prompt}\033[0m")

def assistant_output(message):
    """Print assistant output: 'Assistant >' in green, rest in black. Bold markdown code blocks."""
    import re
    GREEN = "\033[92m"
    BLACK = "\033[30m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # Split the message into 'Assistant >' and the rest
    prefix = f"{GREEN}Assistant >{RESET}"
    if message.startswith("\nAssistant >"):
        message = message[len("\nAssistant >"):]
        print()  # preserve leading newline
    elif message.startswith("Assistant >"):
        message = message[len("Assistant >"):]

    # Function to bold markdown code blocks
    def bold_markdown_blocks(text):
        pattern = r"```markdown(.*?)```"
        def repl(match):
            content = match.group(1)
            return f"```markdown{BOLD}{content}{RESET}```"
        return re.sub(pattern, repl, text, flags=re.DOTALL)

    rest = bold_markdown_blocks(message)
    print(f"{prefix}{BLACK}{rest}{RESET}")

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    logging.info("Initializing the kernel...")
    # Initialize the kernel
    kernel = Kernel()

    # Load environment variables from .env file
    dotenv.load_dotenv()

    logging.info("Setting up Azure OpenAI Chat Completion...")

    adr_id = generate_adr_reference_id()

    # Add Azure OpenAI chat completion
    deployment_name = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPEN_AI_API_KEY")
    endpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT")
    api_version = os.getenv("AZURE_OPEN_AI_API_VERSION")

    chat_completion = AzureChatCompletion(
        deployment_name=deployment_name,
        api_key=api_key,
        endpoint=endpoint,
        api_version=api_version,
    )
    kernel.add_service(chat_completion)

    logging.info("Enabling function choice behavior...")
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    print("Preparing plugins...")

    # WellArchitectedPlugin
    well_architected_plugin = WellArchitectedPlugin()
    well_architected_plugin.vectorize_pdf()
    kernel.add_plugin(
        well_architected_plugin,
        plugin_name="WellArchitectedPlugin",
    )

    # OutputPlugin
    output_plugin = OutputPlugin()
    kernel.add_plugin(
        output_plugin,
        plugin_name="OutputPlugin",
    )    
    

    # Create a history of the conversation
    history = ChatHistory()

    history.add_developer_message(SYSTEM_PROMPT)
    history.add_user_message("ADR_ID: " + adr_id)

    # Initiate a back-and-forth chat
    userInput = None
    while True:
        # Welcome the user
        if userInput is None:
            assistant_output("\nAssistant > " + str(WELCOME_MESSAGE))

        # Collect user input
        userInput = user_input("\nUser > ")

        # Terminate the loop if the user says "exit"
        if userInput == "exit":
            break

        # Add user input to the history
        history.add_user_message(userInput)

        # Get the response from the AI
        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )

        # Print the results
        assistant_output("\nAssistant > " + str(result))

        # Add the message from the agent to the chat history
        history.add_message(result)


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
