from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Define UAE timezone
uae_tz = pytz.timezone('Asia/Dubai')

from ramadan_schedule import ramadan_schedule

def get_current_ramadan_day():
    today = datetime.now(uae_tz).strftime("%d %B")  # e.g., "03 March"
    for day in ramadan_schedule:
        if day["date"] == today:
            return day
    return None

def get_next_critical_time(current_day):
    now = datetime.now(uae_tz)
    imsak_time = datetime.strptime(current_day["imsak"], "%I:%M %p").replace(tzinfo=uae_tz)
    maghrib_time = datetime.strptime(current_day["maghrib"], "%I:%M %p").replace(tzinfo=uae_tz)

    # Combine date with time for accurate comparison
    imsak_time = datetime.combine(now.date(), imsak_time.time(), tzinfo=uae_tz)
    maghrib_time = datetime.combine(now.date(), maghrib_time.time(), tzinfo=uae_tz)

    # Check if it's closer to Imsak (Suhoor) or Maghrib (Iftar)
    if now < imsak_time:
        return "Suhoor (Imsak)", imsak_time
    elif now < maghrib_time:
        return "Iftar (Maghrib)", maghrib_time
    else:
        # If Maghrib has passed, next critical time is Imsak of the next day
        next_day_index = ramadan_schedule.index(current_day) + 1
        if next_day_index < len(ramadan_schedule):
            next_day = ramadan_schedule[next_day_index]
            imsak_time_next_day = datetime.strptime(next_day["imsak"], "%I:%M %p").replace(tzinfo=uae_tz)
            imsak_time_next_day = datetime.combine(now.date() + timedelta(days=1), imsak_time_next_day.time(), tzinfo=uae_tz)
            return "Suhoor (Imsak)", imsak_time_next_day
        else:
            return None, None

@app.route("/")
def index():
    current_day = get_current_ramadan_day()
    return render_template("index.html", current_day=current_day)

@app.route("/next-critical-time")
def next_critical_time():
    current_day = get_current_ramadan_day()
    if current_day:
        next_critical_name, next_critical_time = get_next_critical_time(current_day)
        if next_critical_time:
            return jsonify({
                "next_critical_name": next_critical_name,
                "next_critical_time": next_critical_time.strftime("%I:%M %p"),
                "imsak": current_day["imsak"],
                "asr": current_day["asr"],
                "maghrib": current_day["maghrib"],
                "fajr": current_day["fajr"],
                "date": current_day["date"],
                "ramadan_date": current_day["ramadan_day"]
            })
    return jsonify({"error": "Ramadan has not started yet."})

@app.route("/directory")
def directory():
    current_date = datetime.now(uae_tz).strftime("%d %B")
    return render_template("directory.html", ramadan_schedule=ramadan_schedule, current_date=current_date)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
