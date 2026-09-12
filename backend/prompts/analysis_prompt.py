"""
Analysis prompt builder — used for AI Call #1 (Wake PCA).

Builds ONE optimized prompt that instructs the model to analyze ALL unread
messages in a single API call and return a structured JSON response.
"""

from typing import Any


def build_analysis_prompt(
    messages: list[dict[str, Any]],
    senders: dict[str, dict[str, Any]],
    memory: dict[str, dict[str, Any]],
    user_language: str = "en",
) -> str:
    """
    Construct the message analysis prompt.

    Args:
        messages: List of message dicts with keys:
                  id, sender_id, text, language, timestamp, is_from_user
        senders:  Dict of sender_id → {name, category, default_language}
        memory:   Dict of sender_id → {summary, key_facts, pending_actions}
        user_language: User's preferred language code (e.g. "en", "te")

    Returns:
        A complete prompt string ready to send to the AI provider.
    """

    # Build the messages block
    messages_block = _format_messages(messages, senders)

    # Build the memory context block
    memory_block = _format_memory(memory, senders)

    prompt = f"""
# TASK: MESSAGE_ANALYSIS

You are PCA (Personal Communication Assistant), a multilingual AI assistant.
The user's preferred language is: **{user_language}**

## YOUR JOB
Analyse every message listed below and return a **single JSON object** matching
the schema defined at the bottom. Do not add any prose — pure JSON only.

---

## UNREAD MESSAGES
{messages_block}

---

## MEMORY CONTEXT (previous interactions)
{memory_block}

---

## OUTPUT SCHEMA (return exactly this structure)

```json
{{
  "analyses": [
    {{
      "message_id": "<string>",
      "detected_language": "<ISO 639-1 code>",
      "translated_message": "<English translation of the message>",
      "intent": "<notification|request|question|update|greeting|alert|social>",
      "importance_score": <float 0.0–10.0>,
      "telugu_explanation": "<one-sentence explanation in Telugu script>",
      "reply_required": <true|false>,
      "suggested_action": "<short English action string>"
    }}
  ],
  "memory_updates": [
    {{
      "sender_id": "<string>",
      "summary": "<updated relationship/context summary in English>",
      "key_facts": {{"<key>": "<value>"}},
      "pending_actions": ["<action string>"]
    }}
  ],
  "greeting": "<short Telugu greeting to display in the PCA UI, e.g. నమస్కారం! ...>",
  "summary_telugu": "<2-3 sentence overview of all messages in Telugu script>"
}}
```

## RULES
1. Include one entry per message in `analyses`.
2. `importance_score`: 0=spam, 5=normal, 8=urgent, 10=critical.
3. `memory_updates`: only include senders where something worth remembering happened.
4. `telugu_explanation`: MUST be in Telugu script (not transliteration).
5. Respond with **raw JSON only** — no markdown fences, no explanation.
""".strip()

    return prompt


def _format_messages(
    messages: list[dict[str, Any]],
    senders: dict[str, dict[str, Any]],
) -> str:
    if not messages:
        return "No unread messages."

    lines: list[str] = []
    for msg in messages:
        sender = senders.get(msg["sender_id"], {})
        sender_name = sender.get("name", "Unknown")
        sender_lang = sender.get("default_language", "?")
        lines.append(
            f"- ID: {msg['id']}\n"
            f"  From: {sender_name} (language: {sender_lang}, "
            f"category: {sender.get('category', 'unknown')})\n"
            f"  Time: {msg.get('timestamp', 'unknown')}\n"
            f"  Text: {msg['text']}"
        )

    return "\n\n".join(lines)


def _format_memory(
    memory: dict[str, dict[str, Any]],
    senders: dict[str, dict[str, Any]],
) -> str:
    if not memory:
        return "No previous memory available."

    lines: list[str] = []
    for sender_id, mem in memory.items():
        sender_name = senders.get(sender_id, {}).get("name", sender_id)
        lines.append(
            f"### {sender_name} (id: {sender_id})\n"
            f"Summary: {mem.get('summary', 'none')}\n"
            f"Key facts: {mem.get('key_facts', {})}\n"
            f"Pending actions: {mem.get('pending_actions', [])}"
        )

    return "\n\n".join(lines)
