# Smart Scheduler AI Agent

## Overview

The **Smart Scheduler AI Agent** is an interactive, voice-enabled chatbot designed to help users find, schedule, view, and delete meetings via Google Calendar. It supports natural multi-turn conversations with contextual memory and advanced time understanding, integrating a Large Language Model (Mistral LLM) with Google Calendar APIs and voice services (Speech-to-Text & Text-to-Speech).

---

## Features

- **Voice-Enabled Interaction:** Users can speak their scheduling requests and receive natural spoken responses.
- **Context-Aware Multi-Turn Dialogue:** The agent remembers conversation context (title, date, time, duration) across turns.
- **Google Calendar Integration:** Create, list, find free slots, and delete calendar events using Google Calendar API.
- **Advanced Time Parsing:** Handles complex natural language like "last weekday of this month" or "after my last meeting with a buffer".
- **Conflict Resolution:** Suggests alternative slots if requested time is busy.
- **Smart Scheduling:** Supports usual recurring events and contextual queries.

---

## Technical Stack

- **Language:** Python 3.9+
- **LLM Provider:** Mistral Tiny via HTTP API
- **Voice Providers:**  
  - Speech-to-Text: Google Speech Recognition (via `speech_recognition` Python package)  
  - Text-to-Speech: ElevenLabs API
- **Google Calendar API:** Using `google-api-python-client` with service account credentials
- **Other Libraries:** pytz, dateutil, requests

---

## Project Structure

| File             | Description                                    |
|------------------|------------------------------------------------|
| `app.py`          | Main application loop managing conversation and scheduling logic |
| `calendar_utils.py` | Google Calendar API helpers and event management functions |
| `voice_utils.py`   | Speech-to-text and text-to-speech functions using external APIs |
| `mistral_ll.py`   | Functions to call Mistral LLM API and parse JSON responses |
| `prompt.py`       | System prompt guiding the LLM's behavior and response format |
| `config.py`       | Configuration variables and API keys (excluded from Git) |
| `credentials.json` | Google service account credentials (excluded from Git) |

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/deepakpro190/smart-scheduler.git
cd smart-scheduler
````

2. **Create and activate a Python virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install required packages**

```bash
pip install -r requirements.txt
```

4. **Set up Google Calendar credentials**

* Create a Google Cloud project and enable Google Calendar API.
* Create a service account and download `credentials.json`.
* Place the `credentials.json` file in the project root.
* Make sure `credentials.json` is included in `.gitignore` to avoid leaking secrets.

5. **Configure API keys**

* Add your ElevenLabs API key and voice ID to `config.py` as:

```python
ELEVEN_API_KEY = "your_elevenlabs_api_key"
ELEVENLABS_VOICE_ID = "your_voice_id"
```

* Add your Mistral API key and URL in `config.py`:

```python
MISTRAL_API_KEY = "your_mistral_api_key"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
```

6. **Run the app**

```bash
python app.py
```

Speak your requests clearly when prompted.

---

## Design Choices

* **Context Summarization:** To keep prompts concise, the conversation is summarized after each turn using the LLM itself.
* **JSON-based LLM Responses:** The LLM responds strictly in JSON to enable easy parsing and precise action dispatch.
* **Time Zones:** All times are converted and managed in IST (Asia/Kolkata), converted to UTC for Google Calendar API.
* **Voice Interaction:** Used Google’s STT for accurate speech recognition in English (India), ElevenLabs for expressive TTS.
* **Conflict Handling:** The system automatically checks for scheduling conflicts and suggests alternatives gracefully.
* **Extensible Prompt:** The system prompt clearly guides the LLM on valid actions and rules, ensuring robust conversation management.

---

## Demo Video

\[Link to demo video showing the voice chatbot scheduling meetings interactively]

---

## Future Improvements

* Enhance NLP with deeper natural language time parsing (e.g., “a day after my project kickoff”).
* Integrate user authentication for personal calendar access.
* Support multi-user scheduling and invitees.
* Add fallback to keyboard input if voice recognition fails.
* Expand voice models for multilingual support.

---


---

## Contact

For questions or feedback, please contact Deepak at \[[your-email@example.com](mailto:your-email@example.com)].

---

Thank you for reviewing my submission!

---

**Note:** Sensitive files like `credentials.json` and `config.py` containing API keys are excluded from Git for security. Please set these up manually before running.

```

---

If you want, I can also help prepare the `requirements.txt` file or demo video script! Would you like that?
```
