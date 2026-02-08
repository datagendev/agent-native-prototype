---
name: poem
description: Write a poem about a given topic in a specified language
argument-hint: "[topic] [language]"
---

Parse the arguments from: $ARGUMENTS

The arguments contain a topic and optionally a language. Examples:
- "Italy Italian" -> topic: Italy, language: Italian
- "the ocean French" -> topic: the ocean, language: French
- "mountains" -> topic: mountains, language: English (default)

If only one argument is provided, treat it as the topic and default to English.

Write a poem about the topic in the specified language.

Guidelines:
- Use vivid imagery and sensory details
- Keep it between 8-20 lines
- Choose an appropriate form (sonnet, free verse, haiku, etc.) based on the topic
- Write the entire poem in the specified language
- End with a memorable closing line
