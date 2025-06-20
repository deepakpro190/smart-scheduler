# === app.py with Context Retention, Voice, and Smart Scheduling ===
'''import datetime
from dateutil import parser
from calendar_utils import (
    get_events_by_date, list_events_for_month, create_event,
    delete_event_by_exact_match, is_conflict, suggest_alternative,
    get_last_meeting_time, get_usual_event_template,
    find_next_free_slots, find_free_slots_for_day,
    get_event_time_by_title
)
from mistral_llm import call_mistral, extract_first_json
from prompt import SYSTEM_PROMPT
from voice_utils import transcribe, speak

def get_last_weekday_of_month():
    today = datetime.date.today()
    year, month = today.year, today.month
    if month == 12:
        last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    while last_day.weekday() >= 5:
        last_day -= datetime.timedelta(days=1)
    return last_day

def get_dynamic_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning!"
    elif hour < 17:
        return "Good afternoon!"
    else:
        return "Good evening!"

def parse_datetime_safe(dt_str):
    try:
        return datetime.datetime.fromisoformat(dt_str)
    except ValueError:
        if dt_str.endswith("Z"):
            return datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        raise

def main():
    print("🚀 Starting Smart Scheduler...\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    base_greeting = get_dynamic_greeting()
    greeting_prompt = f"{base_greeting} Greet the user and say you're ready to help schedule."
    messages.append({"role": "user", "content": greeting_prompt})

    try:
        greeting_response = call_mistral(messages)
        first_json = extract_first_json(greeting_response)
        if not first_json:
            greeting_text = f"{base_greeting} I'm ready to help you schedule."
        elif first_json.get("action") == "ask":
            greeting_text = first_json.get("question", f"{base_greeting} Ready when you are.")
        elif "message" in first_json:
            greeting_text = first_json["message"]
        else:
            greeting_text = greeting_response
    except Exception:
        greeting_text = f"{base_greeting} I'm ready to help."

    print(f"🤖 {greeting_text}")
    speak(greeting_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    memory = {}
    context = {
        "title": None,
        "date": None,
        "duration": None,
        "time_pref": None
    }

    while True:
        user_input = transcribe()
        print("🗣️ You:", user_input)
        if user_input.lower() in ['exit', 'quit']:
            break

        messages.append({"role": "user", "content": user_input})
        if len(messages) > 20:
            messages = messages[:1] + messages[-8:]

        try:
            llm_output = call_mistral(messages)
            print("🧠 LLM raw response:", llm_output)
            parsed = extract_first_json(llm_output)

            if not parsed:
                print("❌ JSON parsing failed.")
                continue

            action = parsed.get("action")

            if action == "ask":
                question = parsed["question"]
                print("🤖", question)
                speak(question)
                messages.append({"role": "assistant", "content": llm_output})
                continue

            if action == "schedule":
                if "title" in parsed:
                    context["title"] = parsed["title"]
                if "duration" in parsed:
                    context["duration"] = parsed["duration"]
                if "start_time" in parsed:
                    context["date"] = parsed["start_time"].split("T")[0]
                if "date" in parsed and parsed["date"] != "last_weekday_of_month":
                    context["date"] = parsed["date"]
                if "time_pref" in parsed:
                    context["time_pref"] = parsed["time_pref"]

                # Ask for missing fields only
                if not context["title"]:
                    question = "What is the title of the meeting?"
                    print("🤖", question)
                    speak(question)
                    messages.append({"role": "assistant", "content": f'{{"action": "ask", "question": "{question}"}}'})
                    continue
                if not context["duration"]:
                    question = f"How long should '{context['title']}' be?"
                    print("🤖", question)
                    speak(question)
                    messages.append({"role": "assistant", "content": f'{{"action": "ask", "question": "{question}"}}'})
                    continue
                if not context["date"]:
                    question = f"What date should we schedule '{context['title']}'?"
                    print("🤖", question)
                    speak(question)
                    messages.append({"role": "assistant", "content": f'{{"action": "ask", "question": "{question}"}}'})
                    continue
                if not context["time_pref"]:
                    question = f"What time of day works for '{context['title']}'?"
                    print("🤖", question)
                    speak(question)
                    messages.append({"role": "assistant", "content": f'{{"action": "ask", "question": "{question}"}}'})
                    continue

                # Try to find slot
                date_obj = datetime.datetime.strptime(context["date"], "%Y-%m-%d")
                slots = find_free_slots_for_day(date_obj, context["duration"], context["time_pref"])
                if not slots:
                    speak("No free slots found for that day.")
                    continue

                start_dt = slots[0]
                start_time = start_dt.isoformat()

                if is_conflict(start_dt, context["duration"]):
                    alt = suggest_alternative(start_dt, context["duration"])
                    if alt:
                        alt_str = alt.strftime("%H:%M")
                        question = f"That time is busy. Would you like {alt_str} instead?"
                        print("🤖", question)
                        speak(question)
                        messages.append({"role": "assistant", "content": f'{{"action": "ask", "question": "{question}"}}'})
                        continue
                    else:
                        speak("Sorry, no available time nearby.")
                        continue

                event = create_event(context["title"], start_time, context["duration"])
                summary = event['summary']
                start_str = event['start']['dateTime']
                print(f"✅ Event added: '{summary}' at {start_str}")
                speak(f"Event '{summary}' scheduled at {start_str}")

                context = { "title": None, "date": None, "duration": None, "time_pref": None }

            elif action == "list":
                if "date" in parsed:
                    date = parsed["date"]
                    if date.startswith("200"):
                        date = date.replace(date[:4], str(datetime.datetime.now().year))
                    memory["last_date"] = date
                    events = get_events_by_date(date)
                    if not events:
                        print("📭 No events.")
                        speak("No events found on that date.")
                    else:
                        memory["last_title"] = events[-1]["summary"]
                        for e in events:
                            msg = f"📅 {e['summary']} — {e['start'].get('dateTime')}"
                            print(msg)
                            speak(msg)
                else:
                    year = int(parsed.get("year", datetime.datetime.now().year))
                    month = int(parsed.get("month", datetime.datetime.now().month))
                    events = list_events_for_month(year, month)
                    memory["last_events"] = events
                    for e in events:
                        msg = f"📅 {e['summary']} — {e['start'].get('dateTime')}"
                        print(msg)
                        speak(msg)

            elif action == "delete":
                title = parsed.get("title") or memory.get("last_title")
                date = parsed.get("date") or memory.get("last_date")
                if not date:
                    speak("Please specify the date.")
                    continue
                if not title:
                    events = get_events_by_date(date)
                    for e in events:
                        print(f"• {e['summary']} at {e['start'].get('dateTime')}")
                    speak("Which one would you like to delete?")
                    continue
                result = delete_event_by_exact_match(title, date)
                print(result)
                speak(result)

            elif action == "find_time":
                duration = parsed.get("duration")
                time_pref = parsed.get("time_pref", "any")
                if "after_event" in parsed:
                    event_name = parsed["after_event"]
                    offset_days = parsed.get("offset_days", 1)
                    event_time = get_event_time_by_title(event_name)
                    if not event_time:
                        msg = f"Couldn't find event matching '{event_name}'"
                        print(f"❌ {msg}")
                        speak(msg)
                        continue
                    target_date = event_time.date() + datetime.timedelta(days=offset_days)
                else:
                    target_date = datetime.datetime.now().date() + datetime.timedelta(days=1)

                slots = find_free_slots_for_day(datetime.datetime.combine(target_date, datetime.time(0, 0)), duration, time_pref)
                if not slots:
                    speak("No free slots found.")
                    continue

                slot_strings = [s.strftime("%H:%M") for s in slots]
                options = ", ".join(slot_strings)
                question = f"Free slots: {options}. Which one would you like to book?"
                print(f"🤖 {question}")
                speak(question)
                messages.append({"role": "assistant", "content": f'{{"action": "ask", "question": "{question}"}}'})

            else:
                print("🤖 Unknown action.")
                speak("Sorry, I didn’t understand that.")

            messages.append({"role": "assistant", "content": llm_output})

        except Exception as e:
            print("❌ Error:", e)
            speak("An error occurred while processing your request.")

if __name__ == "__main__":
    main()
'''

# app.py
import datetime
from calendar_utils import (
    get_events_by_date, list_events_for_month, create_event,
    delete_event_by_exact_match, is_conflict, suggest_alternative,
    get_event_time_by_title, find_free_slots_for_day
)
from mistral_llm import call_mistral, extract_first_json
from prompt import SYSTEM_PROMPT
from voice_utils import transcribe, speak

def parse_datetime_safe(dt_str):
    try:
        return datetime.datetime.fromisoformat(dt_str)
    except ValueError:
        if dt_str.endswith("Z"):
            return datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        raise

def summarize_conversation(conv_text, previous_summary=""):
    """
    Ask the LLM to produce a concise summary of the conversation so far.
    This helps keep context bounded and clean.
    """
    prompt = f"Previous summary:\n{previous_summary}\n\nConversation so far:\n{conv_text}\n\nProvide a concise summary:"
    summary_response = call_mistral([{"role":"system","content":"Summarize the conversation."},
                                     {"role":"user","content":prompt}])
    # The summarized text is assumed to be optionally in plain text or JSON field
    return summary_response.strip()

def main():
    memory = {"title": None, "date": None, "time": None, "duration": None}
    raw_conversation = ""
    summary = ""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Initial greeting
    intro = "Hello! I'm here to help with anything—scheduling or chat. How can I assist you today?"
    speak(intro)
    print(intro)

    while True:
        user_input = transcribe()
        if not user_input:
            continue
        print("User:", user_input)

        # Update conversation log
        raw_conversation += f"User: {user_input}\n"
        summary = summarize_conversation(raw_conversation, summary)

        # Build enhanced prompt
        prompt = f"{summary}\nUser: {user_input}"
        messages.append({"role": "user", "content": prompt})
        if len(messages) > 12:
            messages = messages[:1] + messages[-10:]

        try:
            llm_output = call_mistral(messages)
            parsed = extract_first_json(llm_output)
            print("LLM response:", llm_output)

            # Update memory if applicable
            if parsed:
                if "title" in parsed: memory["title"] = parsed["title"]
                if "date" in parsed and parsed["date"] != "last_weekday_of_month":
                    memory["date"] = parsed["date"]
                if "start_time" in parsed or "time_pref" in parsed:
                    memory["time"] = parsed.get("start_time") or parsed.get("time_pref")
                if "duration" in parsed: memory["duration"] = parsed["duration"]

            # Handle actions
            if not parsed:
                speak("Sorry, I didn't get that.")
                continue

            # Scheduling logic
            if parsed["action"] == "schedule":
                if not all([memory["title"], memory["date"], memory["time"], memory["duration"]]):
                    missing = [k for k in memory if not memory[k]]
                    speak(f"Please provide the {', '.join(missing)}.")
                    continue

                start = memory["time"]
                if "T" not in start: start = f"{memory['date']}T{start}:00"
                dt = parse_datetime_safe(start)
                if is_conflict(dt, memory["duration"]):
                    alt = suggest_alternative(dt, memory["duration"])
                    if alt:
                        speak(f"Slot is busy. How about {alt.strftime('%H:%M')} instead?")
                        continue
                    else:
                        speak("No free slots available.")
                        continue

                ev = create_event(memory["title"], start, memory["duration"])
                speak(f"Scheduled: {ev['summary']} at {ev['start']['dateTime']}")
                memory = {"title": None, "date": None, "time": None, "duration": None}
                continue

            # Find-time action
            if parsed["action"] == "find_time":
                dur = parsed["duration"]
                pref = parsed.get("time_pref", "any")
                day = parsed.get("day")
                if not day:
                    day = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                slots = find_free_slots_for_day(
                    datetime.datetime.combine(datetime.date.fromisoformat(day), datetime.time()), dur, pref
                )
                if not slots:
                    speak("No free slots found.")
                    continue
                times = ", ".join(s.strftime("%H:%M") for s in slots)
                speak(f"Available: {times}. Which would you like?")
                continue

            # Listing
            if parsed["action"] == "list":
                now = datetime.datetime.now()
                year = int(parsed.get("year", now.year))
            
                # Prevent unsupported future dates
                if year > 2025:
                    speak(f"Sorry, I can only manage events up to 2025.")
                    continue
            
                if "date" in parsed:
                    events = get_events_by_date(parsed["date"])
                elif "month" in parsed:
                    month = int(parsed["month"])
                    events = list_events_for_month(year, month)
                else:
                    # If only year is given, list each month and collect events
                    all_events = []
                    for m in range(1, 13):
                        month_events = list_events_for_month(year, m)
                        all_events.extend(month_events)
                    if not all_events:
                        speak(f"No events found in {year}.")
                        continue
                    for e in all_events:
                        speak(f"{e['summary']} at {e['start'].get('dateTime')}")
                    continue
            
                # If events exist
                if events:
                    for e in events:
                        speak(f"{e['summary']} at {e['start'].get('dateTime')}")
                else:
                    speak("No events found.")


            # Deleting
            if parsed["action"] == "delete":
                title = parsed.get("title") or memory.get("title")
                date = parsed.get("date") or memory.get("date")
                if not title or not date:
                    speak("Specify what to delete")
                    continue
                res = delete_event_by_exact_match(title, date)
                speak(res)
                continue

            # Ask fallback
            if parsed["action"] == "ask":
                speak(parsed["question"])
                continue

            # Fallback for everything else
            speak("Okay! What next?")
            raw_conversation += f"Assistant: Okay! What next?\n"
            summary = summarize_conversation(raw_conversation, summary)

        except Exception as e:
            print("Error:", e)
            speak("Something went wrong. Let's try again.")


if __name__ == "__main__":
    main()