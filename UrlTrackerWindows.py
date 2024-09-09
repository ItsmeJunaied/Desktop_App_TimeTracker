import time
from pywinauto import Application
import threading

# Initialize variables
url_data = {}
data_lock = threading.Lock()

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
