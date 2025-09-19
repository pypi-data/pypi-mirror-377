"""Groq API client for commit message generation."""

from __future__ import annotations
import re
from groq import Groq
from .error import KnownError
from .prompt import generate_prompt
from .git import chunk_diff, split_diff_by_file, estimate_token_count

# Conventional commit prefixes for parsing
CONVENTIONAL_PREFIXES = [
    "feat:", "fix:", "docs:", "style:", "refactor:", "perf:", 
    "test:", "build:", "ci:", "chore:", "revert:"
]


def sanitize_message(message: str) -> str:
    """Clean up generated commit message."""
    return message.strip().replace("\n", "").replace("\r", "").rstrip(".")


def deduplicate_messages(messages: list[str]) -> list[str]:
    """Remove duplicate messages while preserving order."""
    seen = set()
    result = []
    for msg in messages:
        if msg not in seen:
            seen.add(msg)
            result.append(msg)
    return result


def derive_message_from_reasoning(text: str, max_length: int) -> str | None:
    """Extract commit message from reasoning text as fallback."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    
    # Try to find a conventional-style line inside reasoning
    match = re.search(
        r"\b(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)\b\s*:?\s+[^.\n]+",
        cleaned,
        re.I
    )
    
    candidate = match.group(0) if match else cleaned.split(".")[0]
    if not candidate:
        return None
    
    # Ensure prefix formatting: if starts with a known type w/o colon, add colon
    lower = candidate.lower()
    for prefix in CONVENTIONAL_PREFIXES:
        prefix_without_colon = prefix[:-1]  # Remove colon
        if lower.startswith(prefix_without_colon + " ") and not lower.startswith(prefix):
            candidate = prefix_without_colon + ": " + candidate[len(prefix_without_colon) + 1:]
            break
    
    candidate = sanitize_message(candidate)
    if not candidate:
        return None
    
    if len(candidate) > max_length:
        candidate = candidate[:max_length]
    
    return candidate


def create_chat_completion(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
    max_tokens: int,
    n: int,
    timeout: int,
    proxy: str | None = None
):
    """Create a chat completion using Groq API."""
    client = Groq(api_key=api_key, timeout=timeout / 1000.0)  # Convert ms to seconds
    
    try:
        if n > 1:
            # Generate multiple completions
            completions = []
            for _ in range(n):
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    max_tokens=max_tokens,
                    n=1,
                )
                completions.append(completion)
            
            return {
                "choices": [choice for completion in completions for choice in completion.choices]
            }
        
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=max_tokens,
            n=1,
        )
    
    except Exception as error:
        # Handle Groq API errors
        if hasattr(error, 'status_code'):
            error_message = f"Groq API Error: {error.status_code}"
            
            if hasattr(error, 'message'):
                error_message += f"\n\n{error.message}"
            
            if hasattr(error, 'status_code') and error.status_code == 500:
                error_message += "\n\nCheck the API status: https://console.groq.com/status"
            
            if (hasattr(error, 'status_code') and error.status_code == 413) or \
               (hasattr(error, 'message') and 'rate_limit_exceeded' in str(error.message)):
                error_message += (
                    "\n\n💡 Tip: Your diff is too large. Try:\n"
                    "1. Commit files in smaller batches\n"
                    "2. Exclude large files with --exclude\n"
                    "3. Use a different model with --model\n"
                    "4. Check if you have build artifacts staged (dist/, .next/, etc.)"
                )
            
            raise KnownError(error_message)
        
        # Handle connection errors
        if hasattr(error, 'errno') and 'ENOTFOUND' in str(error):
            hostname = getattr(error, 'hostname', 'API server')
            raise KnownError(
                f"Error connecting to {hostname}. Are you connected to the internet?"
            )
        
        raise error


def generate_commit_message(
    api_key: str,
    model: str,
    locale: str,
    diff: str,
    completions: int,
    max_length: int,
    commit_type: str,
    timeout: int,
    proxy: str | None = None
) -> list[str]:
    """Generate commit messages from git diff."""
    try:
        completion = create_chat_completion(
            api_key=api_key,
            model=model,
            messages=[
                {"role": "system", "content": generate_prompt(locale, max_length, commit_type)},
                {"role": "user", "content": diff},
            ],
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            max_tokens=max(200, max_length * 8),
            n=completions,
            timeout=timeout,
            proxy=proxy
        )
        
        # Extract messages from completion
        messages = []
        for choice in completion.choices:
            content = getattr(choice.message, "content", "") or ""
            if content:
                messages.append(sanitize_message(content))
        
        if messages:
            return deduplicate_messages(messages)
        
        # Fallback: some Groq models return reasoning with empty content
        for choice in completion.choices:
            reasoning = getattr(choice.message, "reasoning", "") or ""
            if reasoning:
                derived = derive_message_from_reasoning(reasoning, max_length)
                if derived:
                    return [derived]
        
        return []
    
    except Exception as error:
        if hasattr(error, 'errno') and 'ENOTFOUND' in str(error):
            hostname = getattr(error, 'hostname', 'API server')
            raise KnownError(
                f"Error connecting to {hostname}. Are you connected to the internet?"
            )
        raise error


def generate_commit_message_from_chunks(
    api_key: str,
    model: str,
    locale: str,
    diff: str,
    completions: int,
    max_length: int,
    commit_type: str,
    timeout: int,
    proxy: str | None = None,
    chunk_size: int = 6000
) -> list[str]:
    """Generate commit messages from chunked diff for large changes."""
    # Strategy: split by file first to avoid crossing file boundaries
    file_diffs = split_diff_by_file(diff)
    per_file_chunks = []
    for file_diff in file_diffs:
        per_file_chunks.extend(chunk_diff(file_diff, chunk_size))
    
    chunks = per_file_chunks if per_file_chunks else chunk_diff(diff, chunk_size)
    
    if len(chunks) == 1:
        try:
            return generate_commit_message(
                api_key, model, locale, diff, completions, 
                max_length, commit_type, timeout, proxy
            )
        except Exception as error:
            error_msg = str(error) if hasattr(error, 'message') else 'Unknown error'
            raise KnownError(f"Failed to generate commit message: {error_msg}")
    
    # Multiple chunks - generate commit messages for each chunk
    chunk_messages = []
    
    for i, chunk in enumerate(chunks):
        approx_input_tokens = estimate_token_count(chunk) + 1200  # Reserve for prompt/system
        effective_max_tokens = max(200, max_length * 8)
        
        # If close to model limit, reduce output tokens
        if approx_input_tokens + effective_max_tokens > 7500:
            effective_max_tokens = max(200, 7500 - approx_input_tokens)
        
        chunk_prompt = (
            f"Analyze this git diff and propose a concise commit message limited to {max_length} characters. "
            f"Focus on the most significant intent of the change.\n\n{chunk}"
        )
        
        try:
            messages = create_chat_completion(
                api_key=api_key,
                model=model,
                messages=[
                    {"role": "system", "content": generate_prompt(locale, max_length, commit_type)},
                    {"role": "user", "content": chunk_prompt},
                ],
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                max_tokens=effective_max_tokens,
                n=1,
                timeout=timeout,
                proxy=proxy
            )
            
            # Extract text from response
            texts = []
            for choice in getattr(messages, 'choices', []):
                content = getattr(choice.message, 'content', None)
                if content:
                    texts.append(content)
            
            if texts:
                chunk_messages.append(sanitize_message(texts[0]))
            else:
                # Try reasoning fallback
                for choice in getattr(messages, 'choices', []):
                    reasoning = getattr(choice.message, 'reasoning', '') or ''
                    if reasoning:
                        derived = derive_message_from_reasoning(reasoning, max_length)
                        if derived:
                            chunk_messages.append(derived)
                            break
        
        except Exception as error:
            print(f"Warning: Failed to process chunk {i + 1}: {error}")
            continue
    
    if not chunk_messages:
        # Fallback: summarize per-file names only to craft a high-level message
        file_names = []
        for block in split_diff_by_file(diff):
            first_line = block.split('\n', 1)[0] if block else ''
            parts = first_line.split(' ')
            if len(parts) > 2:
                file_name = parts[2].replace('a/', '')
                if file_name:
                    file_names.append(file_name)
        
        file_names = file_names[:15]  # Limit to first 15 files
        
        if file_names:
            fallback_prompt = (
                f"Generate a single, concise commit message (<= {max_length} chars) "
                f"summarizing changes across these files:\n" +
                '\n'.join(f"- {f}" for f in file_names)
            )
            
            try:
                completion = create_chat_completion(
                    api_key=api_key,
                    model=model,
                    messages=[
                        {"role": "system", "content": generate_prompt(locale, max_length, commit_type)},
                        {"role": "user", "content": fallback_prompt},
                    ],
                    temperature=0.7,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    max_tokens=max(200, max_length * 8),
                    n=1,
                    timeout=timeout,
                    proxy=proxy
                )
                
                texts = []
                for choice in getattr(completion, 'choices', []):
                    content = getattr(choice.message, 'content', None)
                    if content:
                        texts.append(content)
                
                if texts:
                    return [sanitize_message(texts[0])]
            except Exception:
                pass
        
        raise KnownError("Failed to generate commit messages for any chunks")
    
    # If we have multiple chunk messages, try to combine them intelligently
    if len(chunk_messages) > 1:
        combined_prompt = (
            f"I have {len(chunk_messages)} commit messages for different parts of a large change:\n\n" +
            '\n'.join(f"{i+1}. {msg}" for i, msg in enumerate(chunk_messages)) +
            "\n\nPlease generate a single, comprehensive commit message that captures the overall changes. "
            "The message should be concise but cover the main aspects of all the changes."
        )
        
        try:
            combined_messages = generate_commit_message(
                api_key, model, locale, combined_prompt, completions,
                max_length, commit_type, timeout, proxy
            )
            return combined_messages
        except Exception:
            # If combining fails, return the individual chunk messages
            return chunk_messages
    
    return chunk_messages


def generate_commit_message_from_summary(
    api_key: str,
    model: str,
    locale: str,
    summary: str,
    completions: int,
    max_length: int,
    commit_type: str,
    timeout: int,
    proxy: str | None = None
) -> list[str]:
    """Generate commit message from a compact summary."""
    prompt = (
        f"This is a compact summary of staged changes. Generate a single, concise commit message "
        f"within {max_length} characters that reflects the overall intent.\n\n{summary}"
    )
    
    completion = create_chat_completion(
        api_key=api_key,
        model=model,
        messages=[
            {"role": "system", "content": generate_prompt(locale, max_length, commit_type)},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        max_tokens=max(200, max_length * 8),
        n=completions,
        timeout=timeout,
        proxy=proxy
    )
    
    messages = []
    for choice in getattr(completion, 'choices', []):
        content = getattr(choice.message, 'content', '') or ''
        if content:
            messages.append(sanitize_message(content))
    
    if messages:
        return deduplicate_messages(messages)
    
    # Try reasoning fallback
    for choice in getattr(completion, 'choices', []):
        reasoning = getattr(choice.message, 'reasoning', '') or ''
        if reasoning:
            derived = derive_message_from_reasoning(reasoning, max_length)
            if derived:
                return [derived]
    
    return []


# Legacy function aliases for backward compatibility
generate_from_diff = generate_commit_message_from_chunks