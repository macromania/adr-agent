import asyncio
import logging
import os
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


def load_system_prompt():
    """Load system prompt from default-plan.md file."""
    try:
        prompt_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "default-plan.md")
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"System prompt file not found at {prompt_file_path}")
        # Fallback to a basic prompt
        return "You are an AI assistant for creating Architecture Decision Records (ADRs)."


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
        message = message[len("\nAssistant >") :]
        print()  # preserve leading newline
    elif message.startswith("Assistant >"):
        message = message[len("Assistant >") :]

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
    kernel = Kernel()

    logging.info("Loading environment variables from .env file...")
    dotenv.load_dotenv()

    logging.info("Generating ADR reference ID...")
    adr_id = generate_adr_reference_id()

    # Add Azure OpenAI chat completion
    deployment_name = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPEN_AI_API_KEY")
    endpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT")
    api_version = os.getenv("AZURE_OPEN_AI_API_VERSION")

    logging.info("Adding Azure OpenAI chat completion service...")
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

    logging.info("Preparing plugins...")

    logging.info("Adding WellArchitectedPlugin...")
    well_architected_plugin = WellArchitectedPlugin()
    well_architected_plugin.vectorize_pdf()
    kernel.add_plugin(
        well_architected_plugin,
        plugin_name="WellArchitectedPlugin",
    )

    logging.info("Adding OutputPlugin...")
    output_plugin = OutputPlugin()
    kernel.add_plugin(
        output_plugin,
        plugin_name="OutputPlugin",
    )

    logging.info("Plugins added successfully.")
    logging.info("Starting the chat session...")
    logging.info("Initializing chat history...")
    history = ChatHistory()

    logging.info("Loading system prompt...")
    system_prompt = load_system_prompt()
    history.add_developer_message(system_prompt)
    history.add_user_message("ADR_ID: " + adr_id)

    logging.info("System prompt loaded successfully.")
    logging.info("Starting the interactive chat session...")
    userInput = None

    while True:
        if userInput is None:
            assistant_output("\nAssistant > " + str(WELCOME_MESSAGE))

        userInput = user_input("\nUser > ")
        if userInput == "exit":
            break

        history.add_user_message(userInput)

        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )
        history.add_message(result)

        assistant_output("\nAssistant > " + str(result))


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
