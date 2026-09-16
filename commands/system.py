from datetime import datetime


def system_command(text):

    now = datetime.now()

    # TIME
    if "what time" in text or text == "time":
        return f"It is {now.strftime('%I:%M %p')}, bro."

    # DATE
    if "what date" in text or text == "date":
        return f"Today is {now.strftime('%d %B %Y')}."

    # DAY
    if "what day is it" in text:
        return f"Today is {now.strftime('%A')}."

    return None