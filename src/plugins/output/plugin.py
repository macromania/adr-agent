import os
import uuid
from semantic_kernel.functions import kernel_function

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs')

def to_kebab_case(s: str) -> str:
    return s.replace('_', '-').replace(' ', '-').lower()

class OutputPlugin:
    @kernel_function(name="save_partial_progress", description="Saves partial progress of a section to a Markdown file.")
    def save_partial_progress(self, adr_id: str, section:str, text: str) -> str:
        """
        Save the given text as a Markdown file in the outputs folder, named by adr_id.
        """
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        short_uuid = str(uuid.uuid4())[:5]
        kebab_section = to_kebab_case(section)
        file_path = os.path.join(OUTPUTS_DIR, f"{adr_id}-{kebab_section}-{short_uuid}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return f"Saved progress to {file_path}"