"""Configuration dataclass."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

CONFIG_DIR = Path.home() / ".genie-git"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    """Represent the configurations for the genie-git tool."""

    model: str = "gemini-2.5-flash"
    api_key: str = ""
    exclude_files: list[str] = field(default_factory=list)
    message_specifications: str = "concise and clear"
    number_of_commits: int = (
        5  # The number of commits to include in the AI prompt as a reference.
    )

    def save(self) -> None:
        """Save the configurations to a JSON file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls) -> "Config":
        """Load the configurations from the config JSON file."""
        if not CONFIG_FILE.exists():
            return cls()

        with open(CONFIG_FILE) as f:
            data = json.load(f)
            return cls(**data)

    def show(self) -> None:
        """Show the current configurations."""
        print(json.dumps(asdict(self), indent=2))
