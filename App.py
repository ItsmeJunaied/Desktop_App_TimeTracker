import sys
import time
import requests
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from AppTracker import track_app_time  # Assuming you have the app tracking in AppTracker.py
from UrlTrackerWindows import track_url_time  # Assuming URL tracking is in UrlTrackerWindows.py


class TimeTrackingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Initialize variables for play/pause tracking
        self.is_tracking = False
        self.start_time = 0
        self.elapsed_time = 0

        # Create a timer to update the time label
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)

        # Background threads for tracking apps and URLs
        self.app_thread = None
        self.url_thread = None

    def init_ui(self):
        # Main vertical layout
        vbox = QVBoxLayout()

        # Timer display at the top
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 24px; background-color: #333; color: #fff; padding: 10px;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.timer_label)

        # Admin section (Title + Subtext)
        self.task_title = QLabel("Admin")
        self.task_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.task_title.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.task_title)

        self.task_description = QLabel("Example of a to-do")
        self.task_description.setStyleSheet("font-size: 14px; color: #1E90F7;")
        self.task_description.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.task_description)

        # Play Button
        self.play_button = QPushButton("▶")
        self.play_button.setStyleSheet("font-size: 60px; padding: 20px; color:#fff; border: 2px solid #1E90F7; border-radius: 40px; background-color: #1E90F7;")
        self.play_button.setFixedSize(80, 80)
        self.play_button.setFocusPolicy(Qt.NoFocus)
        self.play_button.clicked.connect(self.toggle_tracking)
        vbox.addWidget(self.play_button, alignment=Qt.AlignCenter)

        # Spacer for separation
        vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search projects")
        vbox.addWidget(self.search_input)

        # Bottom section (last updated time)
        self.last_updated_label = QLabel("Last updated at: 06/11/2023 06:45 AM")
        self.last_updated_label.setStyleSheet("font-size: 10px; color: grey;")
        self.last_updated_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.last_updated_label)

        # Set layout
        self.setLayout(vbox)

        # Window settings
        self.setWindowTitle('Time Tracker App')
        self.setGeometry(400, 400, 500, 700)

    def toggle_tracking(self):
        if not self.is_tracking:
            # Start tracking
            self.is_tracking = True
            self.play_button.setText("⏸")
            self.start_time = time.time() - self.elapsed_time
            self.timer.start(1000)  # Update the timer every second

            # Start tracking in background threads
            self.app_thread = threading.Thread(target=track_app_time)
            self.url_thread = threading.Thread(target=track_url_time)
            self.app_thread.daemon = True
            self.url_thread.daemon = True
            self.app_thread.start()
            self.url_thread.start()

        else:
            # Pause tracking
            self.is_tracking = False
            self.play_button.setText("▶")
            self.elapsed_time = time.time() - self.start_time
            self.timer.stop()


    def update_timer_display(self):
        elapsed = time.time() - self.start_time
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        self.timer_label.setText(f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")

    def send_data(self, data_type, data):
        """
        Sends the tracked data to localhost:3000.
        :param data_type: Can be either 'app' or 'url' to indicate the type of data.
        :param data: The actual data to send (app/window data or URL data).
        """
        url = 'http://localhost:3000/track'
        payload = {
            "type": data_type,
            "data": data
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"{data_type.capitalize()} data sent successfully: {payload}")
            else:
                print(f"Failed to send {data_type} data: {response.status_code}")
        except Exception as e:
            print(f"Error sending {data_type} data: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTrackingApp()
    window.show()
    sys.exit(app.exec_())
