import sys
import time
import pygetwindow as gw
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt5.QtCore import QTimer, Qt
import threading
from pywinauto import Application

# Initialize variables
current_window = None
start_time = None
app_data = {}
url_data = {}
data_lock = threading.Lock()

class HistoryApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a timer to update the active window
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_active_window)
        self.timer.start(1000)  # Check every 1 second

        self.setWindowTitle("History Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create a table to display window history
        self.history_table = QTableWidget(self)
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Time", "Activity", "Time Spent"])
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Create a table to display URL history
        self.url_table = QTableWidget(self)
        self.url_table.setColumnCount(3)
        self.url_table.setHorizontalHeaderLabels(["Time", "URL", "Time Spent"])
        self.url_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Create a layout for the tables
        layout = QVBoxLayout()
        layout.addWidget(self.history_table)
        layout.addWidget(self.url_table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_active_window(self):
        global current_window, start_time
        new_window = gw.getActiveWindow()

        if new_window != current_window:
            # Calculate the time spent on the previous window
            if current_window is not None:
                end_time = time.time()
                elapsed_time = end_time - start_time
                app_name = current_window.title

                with data_lock:
                    if app_name in app_data:
                        app_data[app_name] += elapsed_time
                    else:
                        app_data[app_name] = elapsed_time

                current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
                with open("TrackRecords.txt", "a", encoding="utf-8") as file:
                    file.write(f"date: {time.strftime('%Y-%m-%d')}, time: {time.strftime('%H:%M:%S')}, app: {app_name.split(' - ')[-1]} : spent time: {elapsed_time:.2f} seconds\n")

            current_window = new_window
            start_time = time.time()

        self.update_tables()

    def update_tables(self):
        # Update window history table
        self.history_table.setRowCount(len(app_data))
        row = 0
        for app, time_spent in app_data.items():
            current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
            app_name = app.split(' - ')[-1]
            self.history_table.setItem(row, 0, QTableWidgetItem(current_datetime))
            self.history_table.setItem(row, 1, QTableWidgetItem(f"{app_name}"))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{time_spent:.2f} seconds"))
            row += 1

        # Update URL history table
        self.url_table.setRowCount(len(url_data))
        row = 0
        for url, time_spent in url_data.items():
            current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
            self.url_table.setItem(row, 0, QTableWidgetItem(current_datetime))
            self.url_table.setItem(row, 1, QTableWidgetItem(url))
            self.url_table.setItem(row, 2, QTableWidgetItem(f"{time_spent:.2f} seconds"))
            row += 1

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

def track_app_time():
    global current_window, start_time

    while True:
        new_window = gw.getActiveWindow()

        if new_window != current_window:
            # Calculate the time spent on the previous window
            if current_window is not None:
                end_time = time.time()
                elapsed_time = end_time - start_time
                app_name = current_window.title

                with data_lock:
                    if app_name in app_data:
                        app_data[app_name] += elapsed_time
                    else:
                        app_data[app_name] = elapsed_time

                # Save the data to TrackRecords.txt
                with open("TrackRecords.txt", "a", encoding="utf-8") as file:
                    current_datetime = time.strftime("%Y-%m-%d")
                    current_time = time.strftime("%H:%M:%S")
                    file.write(f"date: {current_datetime}, time: {current_time}, app: {app_name.split(' - ')[-1]} : spent time: {elapsed_time:.2f} seconds\n")

            # Update current window and start time
            current_window = new_window
            start_time = time.time()

        time.sleep(1)

def track_url_time():
    app = Application(backend='uia').connect(title_re=".*Chrome.*")
    dlg = app.top_window()
    element_name = "Address and search bar"
    previous_url = ""
    url_start_time = time.time()

    while True:
        try:
            url = dlg.child_window(title=element_name, control_type="Edit").get_value()
            if url != previous_url:
                if previous_url != "":
                    end_time = time.time()
                    elapsed_time = end_time - url_start_time

                    with data_lock:
                        if previous_url in url_data:
                            url_data[previous_url] += elapsed_time
                        else:
                            url_data[previous_url] = elapsed_time

                    print(f"URL changed: {url}")

                previous_url = url
                url_start_time = time.time()
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(1)

if __name__ == "__main__":
    current_window = gw.getActiveWindow()
    start_time = time.time()
    
    app = QApplication(sys.argv)
    window = HistoryApp()
    window.show()

    # Start threads for tracking app time and URL time
    tracking_thread = threading.Thread(target=track_app_time)
    tracking_thread.daemon = True
    tracking_thread.start()

    url_tracking_thread = threading.Thread(target=track_url_time)
    url_tracking_thread.daemon = True
    url_tracking_thread.start()

    sys.exit(app.exec_())
