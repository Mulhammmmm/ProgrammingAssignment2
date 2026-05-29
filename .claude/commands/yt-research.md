# YouTube Research Skill

Search YouTube for videos on a given topic and return structured metadata (title, channel, views, duration, URL).

## Usage

Trigger this skill when the user asks to:
- Search YouTube for videos on a topic
- Find the latest/trending videos about something
- Get YouTube URLs for a list of videos on a subject

## Instructions

When invoked, follow these steps:

1. **Get the topic**: If no topic is specified in the user's message, ask: "What topic would you like me to research on YouTube?"

2. **Determine the count**: Default to 25 results unless the user specifies a different number.

3. **Run the search** using the yt_research.py script:

```bash
python3 /home/user/ProgrammingAssignment2/scripts/yt_research.py "$TOPIC" -n $COUNT
```

For JSON output (useful when piping results to another skill):

```bash
python3 /home/user/ProgrammingAssignment2/scripts/yt_research.py "$TOPIC" -n $COUNT --json
```

4. **Present results** in a clean table showing: rank, title, channel, views, duration, and URL.

5. **Offer next steps**: Ask if the user wants to send these URLs to NotebookLM for analysis.

## Example

User: "Use the yt-research skill to find the 25 latest trending videos on AI agents"

Action: Run the search for "AI agents trending 2025" with n=25, display results, then ask if they want to proceed to NotebookLM analysis.
