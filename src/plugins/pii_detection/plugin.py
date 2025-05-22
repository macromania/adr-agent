import os

from openai import AzureOpenAI
from semantic_kernel.functions import kernel_function


class PIIDetectionPlugin:
    def __init__(self):
        self.deployment_name = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_NAME")
        self.api_key = os.getenv("AZURE_OPEN_AI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPEN_AI_API_VERSION")
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )

    @kernel_function(name="detect_pii", description="Detects PII in the input text using Azure OpenAI chat completion.")
    def detect_pii(self, text: str) -> str:
        """
        Uses Azure OpenAI chat completion to detect PII in the input text. Returns a JSON string with detected PII.
        """
        prompt = (
            "Detect all personally identifiable information (PII) in the following text. "
            "Return a JSON array of objects, each with 'type' and 'value' fields.\nText: " + text
        )
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0
        )
        return response.choices[0].message.content.strip()

    @kernel_function(name="redact_pii", description="Redacts PII in the input text using Azure OpenAI chat completion.")
    def redact_pii(self, text: str) -> str:
        """
        Uses Azure OpenAI chat completion to redact PII in the input text. Returns the redacted string.
        """
        prompt = (
            "Redact all personally identifiable information (PII) in the following text. "
            "Replace each PII instance with a suitable [REDACTED <TYPE>] tag.\nText: " + text
        )
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0
        )
        return response.choices[0].message.content.strip()