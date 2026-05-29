# NotebookLM Skill

Interact with Google NotebookLM to create notebooks, upload YouTube sources, ask analytical questions, and generate deliverables (infographics, slide decks, flashcards, audio overviews, mind maps, etc.).

## Prerequisites

Authentication must be completed before first use. If you get an auth error, remind the user to run in a terminal:

```bash
notebooklm login
```

## Usage

Trigger this skill when the user asks to:
- Create a NotebookLM notebook
- Upload YouTube URLs to NotebookLM
- Ask NotebookLM to analyze content
- Generate infographics, slide decks, flashcards, audio overviews, or mind maps

## Pipeline Script

All operations use:
```
/home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py
```

## Operations

### 1. Create a notebook
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py create "Notebook Name"
```
Returns JSON with `id` and `name`. **Save the notebook ID** for subsequent operations.

### 2. Add YouTube URLs as sources
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py add-sources "$NOTEBOOK_ID" \
  "https://youtube.com/watch?v=..." \
  "https://youtube.com/watch?v=..." 
```
Add all YouTube URLs in a single call. Wait for confirmation before proceeding.

### 3. Ask an analytical question
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py ask "$NOTEBOOK_ID" \
  "What are the top findings and common themes across these videos?"
```

### 4. Generate deliverables

**Infographic:**
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py generate "$NOTEBOOK_ID" infographic \
  --instructions "handwritten chalkboard style" --orientation portrait
```

**Slide deck:**
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py generate "$NOTEBOOK_ID" slide-deck
```

**Flashcards:**
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py generate "$NOTEBOOK_ID" flashcards
```

**Audio overview:**
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py generate "$NOTEBOOK_ID" audio \
  --instructions "engaging and conversational"
```

**Mind map:**
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py generate "$NOTEBOOK_ID" mind-map
```

### 5. List all notebooks
```bash
python3 /home/user/ProgrammingAssignment2/scripts/notebooklm_pipeline.py list
```

## Full Pipeline Example

When the user says: "Send these videos to NotebookLM. Give me analysis on top findings, then create an infographic in handwritten chalkboard style."

1. Create notebook named after the topic
2. Add all YouTube URLs as sources (batch them into a single call)
3. Ask: "What are the top findings, key themes, and most important insights across all these videos?"
4. Present the analysis to the user
5. Generate infographic with `--instructions "handwritten chalkboard style" --orientation portrait`
6. Inform user the infographic is generating and will be available in their NotebookLM account at notebooklm.google.com

## Auth Error Handling

If any command fails with an authentication error:
> "You need to authenticate with NotebookLM first. Please open a new terminal and run:
> ```
> notebooklm login
> ```
> Follow the browser prompt to sign in with your Google account, then come back and try again."
