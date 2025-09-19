"""Prompt generation for AI commit messages."""

import json

COMMIT_TYPE_FORMATS = {
    "": "<commit message>",
    "conventional": "<type>(<optional scope>): <commit message>",
}

COMMIT_TYPES_INFO = {
    "": "",
    "conventional": """Choose the most appropriate type from the following categories that best describes the git diff:

{
  "feat": "A new feature for the user",
  "fix": "A bug fix",
  "docs": "Documentation only changes",
  "style": "Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)",
  "refactor": "A code change that neither fixes a bug nor adds a feature",
  "perf": "A code change that improves performance",
  "test": "Adding missing tests or correcting existing tests",
  "build": "Changes that affect the build system or external dependencies",
  "ci": "Changes to our CI configuration files and scripts",
  "chore": "Other changes that don't modify src or test files",
  "revert": "Reverts a previous commit"
}

IMPORTANT: Use the exact type name from the list above.""",
}


def specify_commit_format(commit_type: str) -> str:
    """Generate format specification for commit type."""
    return f"The output response must be in format:\n{COMMIT_TYPE_FORMATS[commit_type]}"


def generate_prompt(locale: str, max_length: int, commit_type: str) -> str:
    """Generate system prompt for AI commit message generation."""
    base_prompt = f"""You are an expert software engineer and git commit message writer. Your task is to analyze git diffs and generate clear, concise, and professional commit messages.

## Instructions:
1. Analyze the provided git diff carefully
2. Identify the primary purpose and impact of the changes
3. Generate a commit message that clearly describes what was changed and why
4. Use present tense, imperative mood (e.g., "feat: Add feature" not "Added feature")
5. Be specific about what changed, not just how it changed
6. Focus on the business value or technical improvement

## Quality Guidelines:
- Be concise but descriptive
- Use active voice
- Avoid vague terms like "update", "change", "fix stuff"
- Include context when helpful (e.g., "fix: memory leak in user authentication")
- For bug fixes, briefly describe what was broken
- For features, describe what functionality was added
- For refactoring, mention what was improved (performance, readability, etc.)

## Language: {locale}
## Maximum length: {max_length} characters
## Output format: {COMMIT_TYPE_FORMATS.get(commit_type, '<commit message>')}

{f'## Commit Type Guidelines:\\n{COMMIT_TYPES_INFO[commit_type]}' if COMMIT_TYPES_INFO.get(commit_type) else ''}

## Examples of good commit messages:
- "feat: Add user authentication with JWT tokens"
- "fix: Fix memory leak in image processing pipeline"
- "refactor: Refactor database queries to use prepared statements"
- "docs: Update README with installation instructions"
- "style: Remove deprecated API endpoints"
- "perf: Optimize bundle size by removing unused dependencies"

## Examples of bad commit messages:
- "Update code"
- "Fix bug"
- "Changes"
- "WIP"
- "Stuff"

Remember: Your response will be used directly as the git commit message. Make it professional and informative."""

    return base_prompt

