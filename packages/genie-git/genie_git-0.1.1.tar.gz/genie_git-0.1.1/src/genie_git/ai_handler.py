"""Uses google genai to generate a commit message."""

from google import genai
from google.genai import types


def suggest_commit_message(
    api_key: str,
    git_logs: str,
    staged_changes: str,
    message_specifications: str = "concise and clear",
) -> str:
    """Suggests a commit message based on the changes in the repository.

    Args:
        api_key: The API key to use for generating the commit message.
        git_logs: The git logs to use as a reference.
        staged_changes: The staged changes to use as a reference.
        message_specifications: Additional specifications for the commit message.

    Returns:
        The suggested commit message.

    """
    client = genai.Client(
        api_key=api_key,
    )

    prompt = f"""Given the following git log:
    {git_logs}
    and the following changes:
    {staged_changes}
    suggest a {message_specifications} commit message.
    ensure that you follow conventional commit message structure.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
        ),
    )
    return response.text
