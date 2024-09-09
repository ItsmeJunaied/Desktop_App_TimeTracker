import pygetwindow as gw
import time
import threading

# Initialize variables
current_window = None
start_time = None
app_data = {}
data_lock = threading.Lock()

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
