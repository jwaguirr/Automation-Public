# Alarm Control System

## Overview
** This project was originially commited to a private repo on January 10, 2023. However, I re-commited without any changes to the code (besides deleting security issues) on June 23, 2024.  **

This is my first project finished in August 10, 2022. This project is a Flask web application that interacts with a SQLite database and a serial device (like an LED light) to manage alarms. The system allows users to set and control alarms for different times and scenarios, such as weekdays, weekends, and nights. It is intended to run on a Raspberry Pi, utilizing its GPIO pins and serial interface for hardware control.

## Features
- Set alarms for different times of the day (weekdays, weekends, nights).
- Manage prioritized alarms.
- Control connected LED lights through serial communication.
- View and update alarm settings through a web interface.

## Requirements
- Raspberry Pi with Raspbian OS installed.
- Python 3.7+.
- Flask.
- SQLite3.
- pySerial.
- Threading module.

## Setup Instructions

### Hardware Setup
1. Connect the Raspberry Pi to the serial device (e.g., LED lights) using the GPIO pins.
2. Ensure the serial device is properly configured to communicate via `/dev/ttyUSB0`.

### Software Setup
1. **Install necessary libraries:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip sqlite3
   pip3 install flask pyserial
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/alarm-control-system.git
   cd alarm-control-system
   ```

3. **Initialize the SQLite database:**
   ```bash
   python3
   ```
   If you encounter an errors, in the Python shell, run the following commands to create the necessary database structure:
   ```python
   import sqlite3 as sql
   conn = sql.connect("database.db", check_same_thread=False)
   c = conn.cursor()
   c.execute("""CREATE TABLE IF NOT EXISTS times(
       prioritized TEXT,
       weekdays TEXT,
       weekends TEXT,
       weekdayNights TEXT,
       weekendNights TEXT,
       cancel INTEGER
   )""")
   conn.commit()
   conn.close()
   exit()
   ```

## Running the Application

### Running Locally
1. **Start the Flask application:**
   ```bash
   flask --app web --debug run --port 5001
   ```

2. Open a web browser and navigate to `http://localhost:5001` to access the web interface.

### Running on Raspberry Pi
1. **Ensure the serial device is connected and configured correctly.**
2. **Start the Flask application:**
   ```bash
   sudo python3 web.py
   ```

3. Open a web browser on any device in the same network and navigate to `http://<raspberry-pi-ip>:5001` to access the web interface.

## Project Structure
- `web.py`: The main Flask application script.
- `templates/`: Directory containing HTML templates for the web interface.
- `static/`: Directory for static files (CSS, JavaScript).
- `database.db`: SQLite database file.

## Usage
1. **Access the web interface** by navigating to the specified IP and port.
2. **Set alarm times** for weekdays, weekends, and nights through the web interface.
3. **Toggle alarms** on and off using the provided button in the interface.
4. **View current alarm settings** and make adjustments as needed.


## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- Flask documentation: [Flask Docs](https://flask.palletsprojects.com/)
- SQLite documentation: [SQLite Docs](https://www.sqlite.org/docs.html)
- Raspberry Pi documentation: [Raspberry Pi Docs](https://www.raspberrypi.org/documentation/)
