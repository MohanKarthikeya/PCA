"""
Reply prompt builder — used for AI Call #2 (Reply Generation).

Builds ONE optimized prompt that generates a contextual reply to a specific
message based on the user's instruction and conversation history.
"""

from typing import Any


def build_reply_prompt(
    original_message: dict[str, Any],
    sender: dict[str, Any],
    user_instruction: str,
    conversation_history: list[dict[str, Any]],
    memory: dict[str, Any] | None,
    user_language: str = "en",
) -> str:
    """
    Construct the reply generation prompt.

    Args:
        original_message: The message being replied to (id, text, language, etc.)
        sender:           Sender profile {name, category, default_language}
        user_instruction: What the user wants to say, e.g. "Tell him I'll be there"
        conversation_history: Recent messages between user and sender
        memory:           Memory record for this sender (may be None)
        user_language:    User's preferred language for the translation field

    Returns:
        A complete prompt string ready to send to the AI provider.
    """

    history_block = _format_history(conversation_history)
    memory_block = _format_memory(memory)

    prompt = f"""
# TASK: REPLY_GENERATION

You are PCA (Personal Communication Assistant).
Generate a polite, contextual reply to the message below.

---

## ORIGINAL MESSAGE
From: {sender.get('name', 'Unknown')} (speaks: {sender.get('default_language', 'en')})
Message: {original_message.get('text', '')}

---

## USER'S INSTRUCTION
"{user_instruction}"

---

## CONVERSATION HISTORY (most recent first)
{history_block}

---

## SENDER MEMORY
{memory_block}

---

## OUTPUT SCHEMA (return exactly this structure, raw JSON only)

```json
{{
  "reply_in_sender_language": "<reply text written in the sender's language ({sender.get('default_language', 'en')})>",
  "reply_translation": "<translation of the reply into {user_language}>",
  "confidence": <float 0.0–1.0>,
  "explanation": "<optional: brief note on tone/language choices>"
}}
```

## RULES
1. The reply MUST be in the sender's language: **{sender.get('default_language', 'en')}**
2. Keep the reply natural, culturally appropriate, and within 3 sentences unless the user's instruction requires more.
3. `confidence`: 1.0 = perfectly confident, 0.5 = uncertain about phrasing.
4. Respond with **raw JSON only** — no markdown, no explanation outside the JSON.
""".strip()

    return prompt


def _format_history(history: list[dict[str, Any]]) -> str:
    if not history:
        return "No previous conversation."

    lines: list[str] = []
    for msg in history[:10]:  # Last 10 messages max
        direction = "User →" if msg.get("is_from_user") else "Sender →"
        lines.append(f"{direction} {msg.get('text', '')}")

    return "\n".join(lines)


def _format_memory(memory: dict[str, Any] | None) -> str:
    if not memory:
        return "No memory available for this sender."

    return (
        f"Summary: {memory.get('summary', 'none')}\n"
        f"Key facts: {memory.get('key_facts', {})}\n"
        f"Pending actions: {memory.get('pending_actions', [])}"
    )
