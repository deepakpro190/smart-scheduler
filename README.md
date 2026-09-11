# Smart Scheduler AI Agent

An intelligent voice-enabled scheduling assistant that integrates with Google Calendar to help users schedule, manage, and find available meeting times through natural language conversation.

## Features

- 🎤 **Voice-Enabled Interaction:** Speak scheduling requests naturally; receive spoken responses
- 💬 **Multi-Turn Conversation:** Context-aware dialogue that remembers meeting details across turns
- 📅 **Google Calendar Integration:** Create, list, find free slots, and delete calendar events
- ⏰ **Advanced Time Parsing:** Handles natural language like "last weekday of this month" or "after my last meeting"
- 🔄 **Conflict Resolution:** Automatically suggests alternative time slots when requested time is busy
- 🌍 **Timezone Support:** Handles IST (Asia/Kolkata) with conversion to UTC for Google Calendar API

## Technical Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.9+ |
| **LLM** | Mistral Tiny (via API) |
| **Speech-to-Text** | Google Speech Recognition |
| **Text-to-Speech** | ElevenLabs API |
| **Calendar API** | Google Calendar API (service account) |
| **Parsing** | `dateutil`, `pytz` |

## Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud project with Calendar API enabled
- Service account credentials (credentials.json)
- Mistral API key
- ElevenLabs API key and voice ID

### Installation

```bash
# Clone repository
git clone https://github.com/deepakpro190/smart-scheduler.git
cd smart-scheduler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in your credentials in `.env`:**
   ```env
   MISTRAL_API_KEY=your_mistral_api_key
   MISTRAL_API_URL=https://api.mistral.ai/v1/chat/completions
   ELEVEN_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_VOICE_ID=your_voice_id
   ```

3. **Set up Google Calendar:**
   - Create Google Cloud project and enable Calendar API
   - Create service account and download credentials JSON
   - Save as `credentials.json` in project root
   - Add to `.gitignore` (already configured)

### Running the Application

```bash
python app.py
```

When prompted, speak your scheduling requests clearly:
- "Schedule a standup meeting tomorrow at 9 AM for 30 minutes"
- "What meetings do I have next Tuesday?"
- "Find me a free slot next Thursday afternoon"
- "Delete my 3 PM meeting on Friday"

## Project Structure

```
smart-scheduler/
├── app.py                   # Main application loop and scheduling logic
├── calendar_utils.py        # Google Calendar API integration helpers
├── voice_utils.py           # Speech-to-text and text-to-speech functions
├── mistral_llm.py          # Mistral API calls and JSON response parsing
├── prompt.py               # System prompt for LLM behavior
├── config.py               # Configuration (excluded from git)
├── credentials.json        # Google service account (excluded from git)
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Design Decisions

- **Context Summarization:** Conversation is summarized after each turn to keep LLM prompts concise
- **JSON-Based Responses:** LLM responds strictly in JSON for reliable parsing and action dispatch
- **Timezone Management:** All times managed in IST, converted to UTC for Google Calendar
- **Voice I/O:** Google STT for English (India), ElevenLabs for expressive TTS
- **Conflict Handling:** System automatically detects conflicts and suggests alternatives
- **Memory:** Maintains context (title, date, time, duration) across multiple turns

## Setup Instructions

### Step 1: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Calendar API
4. Create a service account (not user account)
5. Generate and download private key as JSON
6. Save as `credentials.json` in project root

### Step 2: Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### Step 3: Run Application

```bash
python app.py
```

## API Key Providers

| Service | Link | Get Key |
|---|---|---|
| **Mistral** | https://console.mistral.ai/ | API Console → Create API Key |
| **ElevenLabs** | https://elevenlabs.io/ | Dashboard → API Keys |
| **Google Calendar** | https://console.cloud.google.com/ | Service Accounts → Create Key |

## Supported Actions

### Schedule Meeting
```
"Schedule a team standup tomorrow at 9 AM for 30 minutes"
"Create a 1-hour meeting with Alice next Monday at 2 PM"
```

### List Events
```
"What meetings do I have tomorrow?"
"Show me all events in December"
"List my meetings next week"
```

### Find Free Time
```
"Find me a 1-hour slot next Thursday afternoon"
"What's free after my last meeting?"
```

### Delete Event
```
"Delete my 3 PM meeting on Friday"
"Cancel the standup from Tuesday"
```

## Troubleshooting

| Issue | Solution |
|---|---|
| **"Failed to transcribe"** | Ensure microphone is working; speak clearly in a quiet environment |
| **"No credentials found"** | Download credentials.json from Google Cloud Console and place in project root |
| **"Missing API key"** | Verify `.env` file exists and all keys are filled in |
| **"Calendar API error"** | Check that Google Calendar API is enabled in Cloud Console |
| **"Conflict resolution not working"** | Ensure credentials.json has appropriate permissions for calendar read/write |

## Future Improvements

- Enhanced natural language time parsing (e.g., "day after project kickoff")
- User authentication for personal calendar access
- Multi-user scheduling and invitees
- Keyboard input fallback if voice recognition fails
- Multilingual voice support
- Integration with other calendar services (Outlook, Notion)

## Security

- Never commit `credentials.json` or `.env` files (both in `.gitignore`)
- API keys are loaded from environment variables only
- See `SECURITY.md` for credential management best practices

## Contact

Questions or feedback? Reach out via:
- 📧 Email: deepak.goel.ug23@nsut.ac.in
- 💼 LinkedIn: [linkedin.com/in/deepak-goel-993b4b337](https://www.linkedin.com/in/deepak-goel-993b4b337)
- 🐙 GitHub: [github.com/deepakpro190](https://github.com/deepakpro190)

## License

MIT License - See LICENSE file for details
