import asyncio
import logging
import os

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
    "You need to use Azure Well Architected Framework to ensure the ADR covers all aspects of the framework for non-functional requirements."
    "You need to use Azure Architecture Center to ensure the ADR visits well known patterns and practices."
    "Decision drivers should be a table comparing the options and provide a score of Yes, No, or Maybe."
    "Ask necessary questions one by one to the user to fill in the sections. "
    "Show the progress of the ADR creation process to the user as you go along. "
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


async def main():
    # Initialize the kernel
    kernel = Kernel()

    # Load environment variables from .env file
    dotenv.load_dotenv()

    logging.info("Starting the Azure OpenAI Chat Completion example...")

    # Add Azure OpenAI chat completion
    deployment_name = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPEN_AI_API_KEY")
    endpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT")
    api_version = os.getenv("AZURE_OPEN_AI_API_VERSION")

    logging.info("Setting up Azure OpenAI chat completion...")
    chat_completion = AzureChatCompletion(
        deployment_name=deployment_name,
        api_key=api_key,
        endpoint=endpoint,
        api_version=api_version,
    )
    kernel.add_service(chat_completion)

    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create a history of the conversation
    history = ChatHistory()

    history.add_developer_message(SYSTEM_PROMPT)

    # Initiate a back-and-forth chat
    userInput = None
    while True:
        # Welcome the user
        if userInput is None:
            print("\nAssistant > " + str(WELCOME_MESSAGE))

        # Collect user input
        userInput = input("\nUser > ")

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
        print("\nAssistant > " + str(result))

        # Add the message from the agent to the chat history
        history.add_message(result)


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
