from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime, timedelta
import time
import serial
import sqlite3 as sql
import threading

# To run the app: flask --app web --debug run --port 5001
app = Flask(__name__)
conn = sql.connect("database.db", check_same_thread=False)
c = conn.cursor()
prioritizedReset = ['']
prioritizedShutOff = ['']

# Creates the Table if it doesn't exist
c.execute("""CREATE TABLE IF NOT EXISTS times(
    prioritized TEXT,
    weekdays TEXT,
    weekends TEXT,
    weekdayNights TEXT,
    weekendNights TEXT,
    cancel INTEGER
)""")

# Formats the time to 24 Hours
def formatTime(amPm, tableValName, userTimeInput):
    alarmTime = f"{userTimeInput} {amPm}"
    inTime = datetime.strptime(alarmTime, "%I:%M %p")
    outTime = inTime.strftime("%H:%M")
    checkTimeFormat(outTime, tableValName)

# Checking for an empty DB-- allows for updating data
def checkValues():
    c.execute("SELECT * FROM times")
    times = c.fetchone()
    if times is None:
        c.execute("INSERT INTO times VALUES (' ', ' ', ' ', ' ', ' ', 0)")
        conn.commit()
        print("Created Query")

# Prints the values of the DB
def printDB(dbMessage):
    print(dbMessage)
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        print(items)

# Checks the format of the input, if correct, adds to the DB
def checkTimeFormat(outTime, tableValName):
    try:
        hours, minutes = outTime.split(':')
        if hours.isdigit() and minutes.isdigit():
            updateDB = f'UPDATE times SET {tableValName} = (?)'
            c.execute(updateDB, (outTime,))
            conn.commit()
        else:
            print("Something went wrong with time format")
    except ValueError as e:
        print("Error in time format, ensure it's in 24-hour format:", e)

# Compares value to database, if different runs moves to format checking
def pullDifferences(prioritized, weekdays, weekends, weekdayNights, weekendNights):
    c.execute("SELECT * FROM times")
    times = c.fetchall()
    for items in times:
        if items[0] != prioritized:
            c.execute("UPDATE times SET prioritized = (?)", (prioritized if prioritized else "None",))
        if items[1] != weekdays:
            formatTime("AM", "weekdays", weekdays)
        if items[2] != weekends:
            formatTime("AM", "weekends", weekends)
        if items[3] != weekdayNights:
            formatTime("PM", "weekdayNights", weekdayNights)
        if items[4] != weekendNights:
            formatTime("PM", "weekendNights", weekendNights)
        conn.commit()

# Adds 12 Hours to the Time so it will disregard the morning alarm
def triggerPrioritizedFunc(prioritizedFromDB):
    firstTwoDigits, secondTwoDigits = prioritizedFromDB.split(':')
    firstTwoDigits = int(firstTwoDigits) + 12
    if firstTwoDigits >= 24:
        firstTwoDigits -= 24
    turnOffTime = f"{firstTwoDigits:02}:{secondTwoDigits}:00"
    prioritizedReset[0] = turnOffTime

def morningFunc():
    ser.write(b"ON\n")  # Turns LED Lights on
    print("Currently running the morning code :)")

def nightTimeFunc():
    ser.write(b"ON\n")  # Turns LED Lights on
    print("Currently running the nighttime code: ")

def onOff():
    ser.write(b"ON\n")  # Turns LED Lights on/off
    print("Turn Off")

def prioritizedFunc(prioritizedReset, prioritizedFromDB):
    print("PRIORITIZED! Prioritized will reset at:", prioritizedReset)
    prioritizedDateTime = datetime.strptime(prioritizedFromDB, "%H:%M:%S")
    addedMinutes = (prioritizedDateTime + timedelta(minutes=5)).strftime("%H:%M:%S")
    prioritizedShutOff[0] = addedMinutes
    onOff()

# Setting the alarm when pulling from the DB
def setAlarm():
    while True:
        c.execute("SELECT * FROM times")
        times = c.fetchone()
        if times[5] != 1:
            break
        
        prioritizedFromDB = f"{times[0]}:00" if times[0] != "None" else times[0]
        weekdaysFromDB = f"{times[1]}:00"
        weekendsFromDB = f"{times[2]}:00"
        weekdayNightsFromDB = f"{times[3]}:00"
        weekendNightsFromDB = f"{times[4]}:00"

        dayOfWeek = datetime.now().strftime('%w')
        itsAWeekend = dayOfWeek in ('0', '6')
        currentTime = datetime.now().strftime("%H:%M:%S")
        
        if prioritizedFromDB != "None":  # Prioritizing the Prioritized Time
            if prioritizedFromDB == currentTime:
                triggerPrioritizedFunc(prioritizedFromDB)
                prioritizedFunc(prioritizedReset, prioritizedFromDB)
            elif currentTime == prioritizedShutOff[0]:
                onOff()  # Turns off after 5 minutes
            elif currentTime == prioritizedReset[0]:
                prioritizedReset[0] = ""
                c.execute('UPDATE times SET prioritized = "None"')
                conn.commit()
                printDB("Updating Priority to None")
        else:
            handleWeekends(currentTime, itsAWeekend, weekendsFromDB, weekendNightsFromDB)
            handleWeekdays(currentTime, itsAWeekend, weekdaysFromDB, weekdayNightsFromDB)
        
        print(currentTime)
        time.sleep(1)

def handleWeekends(currentTime, itsAWeekend, weekendsFromDB, weekendNightsFromDB):
    if itsAWeekend:
        weekendNightsTurnOn = (datetime.strptime(weekendNightsFromDB, "%H:%M:%S") - timedelta(hours=3)).strftime("%H:%M:%S")
        weekendTurnOff = (datetime.strptime(weekendsFromDB, "%H:%M:%S") + timedelta(minutes=30)).strftime("%H:%M:%S")

        if weekendNightsTurnOn == currentTime:
            nightTimeFunc()
        elif weekendNightsFromDB == currentTime:
            onOff()
        if weekendsFromDB == currentTime:
            morningFunc()
        if weekendTurnOff == currentTime:
            onOff()

def handleWeekdays(currentTime, itsAWeekend, weekdaysFromDB, weekdayNightsFromDB):
    if not itsAWeekend:
        weekdayNightsTurnOn = (datetime.strptime(weekdayNightsFromDB, "%H:%M:%S") - timedelta(hours=3)).strftime("%H:%M:%S")
        weekdayTurnOff = (datetime.strptime(weekdaysFromDB, "%H:%M:%S") + timedelta(minutes=30)).strftime("%H:%M:%S")

        if weekdayNightsTurnOn == currentTime:
            nightTimeFunc()
        elif weekdayNightsFromDB == currentTime:
            onOff()
        if weekdaysFromDB == currentTime:
            morningFunc()
        elif weekdayTurnOff == currentTime:
            onOff()

@app.route('/', methods=["GET", "POST"])
def index():
    checkValues()
    if request.method == "POST":
        try:
            handleToggleAlarms(request.form['toggleAlarms'])
        except:
            try:
                prioritized = request.form['prioritized']
                weekdays = request.form['weekdays']
                weekends = request.form['weekends']
                weekdayNights = request.form['weekdayNights']
                weekendNights = request.form['weekendNights']
                pullDifferences(prioritized, weekdays, weekends, weekdayNights, weekendNights)
                conn.commit()
            except TypeError as e:
                print("Exception Thrown!", e)
    printDB("Searching db")
    c.execute("SELECT * FROM times")
    data = c.fetchall()
    alarm = "Turn Off Alarms" if data[0][5] == 1 else "Turn On Alarms"
    startAlarmThread()
    return render_template('index.html', data=data, alarm=alarm)

def handleToggleAlarms(alarmToggle):
    if alarmToggle == "Toggle":
        c.execute("SELECT * FROM times")
        alarms = c.fetchall()
        toggle = 0 if alarms[0][5] == 1 else 1
        c.execute("UPDATE times SET cancel = (?)", (toggle,))
        conn.commit()

def startAlarmThread():
    if threading.active_count() <= 2:
        threading.Thread(target=setAlarm).start()

@app.route('/database', methods=['POST', 'GET'])
def postDB():
    c.execute("SELECT * FROM times")
    data = c.fetchall()
    alarm = "On" if data[0][5] == 1 else "Off"
    return render_template('template.html', data=data, alarm=alarm)

if __name__ == "__main__":
    ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
    ser.flush()
    app.run(debug=True, use_reloader=False, port=5001)
# TO RUN ON HOST MACHINE host="0.0.0.0"