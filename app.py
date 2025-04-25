from flask import Flask, render_template_string, request, redirect, url_for
from threading import Thread
import time
from datetime import datetime

app = Flask(__name__)

alarms = []
ring_alarm = False

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Alarm Clock</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; }
        input[type=number] { width: 50px; }
        .alarm-time { margin: 10px 0; }
        #alarmPopup {
            display: none;
            position: fixed;
            top: 20%;
            left: 50%;
            transform: translateX(-50%);
            background: #ffdddd;
            padding: 20px;
            border: 2px solid red;
            border-radius: 10px;
            font-size: 24px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <h1>Flask Alarm Clock</h1>
    <h2 id="clock">{{ current_time }}</h2>

    <form method="POST">
        <label>Set Alarm Time (24h format):</label><br>
        <input type="number" name="hour" min="0" max="23" required> :
        <input type="number" name="minute" min="0" max="59" required>
        <button type="submit">Set Alarm</button>
    </form>

    {% if alarm_set %}
        <p>⏰ Alarm set for {{ alarm_hour }}:{{ alarm_minute }}</p>
    {% endif %}

    <h3>Active Alarms:</h3>
    <ul>
        {% for alarm in alarms %}
            <li>{{ alarm }} <a href="/delete/{{ alarm }}">Delete</a></li>
        {% endfor %}
    </ul>

    <audio id="alarmSound" src="{{ url_for('static', filename='alarm.mp3') }}"></audio>
    <div id="alarmPopup">⏰ Alarm Ringing!</div>

    <script>
        // Live clock
        setInterval(() => {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-GB');
            document.getElementById("clock").innerText = timeStr;
        }, 1000);

        {% if ring_alarm %}
            document.getElementById("alarmPopup").style.display = "block";
            const sound = document.getElementById("alarmSound");
            sound.play();
        {% endif %}
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    global ring_alarm
    alarm_set = False
    alarm_hour = alarm_minute = None

    if request.method == "POST":
        hour = request.form.get("hour")
        minute = request.form.get("minute")
        if hour is not None and minute is not None:
            alarm_time = f"{hour.zfill(2)}:{minute.zfill(2)}"
            alarms.append(alarm_time)
            alarm_set = True
            alarm_hour = hour
            alarm_minute = minute

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    ring = ring_alarm
    ring_alarm = False  # Reset flag

    return render_template_string(html_template,
                                  current_time=current_time,
                                  alarm_set=alarm_set,
                                  alarm_hour=alarm_hour,
                                  alarm_minute=alarm_minute,
                                  alarms=alarms,
                                  ring_alarm=ring)

@app.route("/delete/<alarm>")
def delete_alarm(alarm):
    if alarm in alarms:
        alarms.remove(alarm)
    return redirect(url_for("index"))

def alarm_checker():
    global ring_alarm
    while True:
        now = datetime.now()
        now_time = now.strftime("%H:%M")
        if now_time in alarms:
            print("⏰ Alarm ringing!")
            ring_alarm = True
            time.sleep(60)
        time.sleep(1)

# Background thread
thread = Thread(target=alarm_checker)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    app.run(debug=True)

