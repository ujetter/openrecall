# pylint: disable=wrong-import-order
import logging  # nopep8 pylint: disable=unused-import
import openrecall.log_config  # nopep8
from openrecall.log_config import log_always  # nopep8

openrecall.log_config.setup_logging_new()  # nopep8

from threading import Thread, Event  # pylint: disable=wrong-import-position
import multiprocessing
from queue import Queue
import signal
import atexit
import numpy as np  # pylint: disable=wrong-import-position
from flask import Flask, render_template_string, request, send_from_directory  # pylint: disable=wrong-import-position
from jinja2 import BaseLoader  # pylint: disable=wrong-import-position

from openrecall.config import appdata_folder, screenshots_path  # pylint: disable=wrong-import-position disable=ungrouped-imports
from openrecall.database import create_db, get_all_entries, get_timestamps  # pylint: disable=wrong-import-position
from openrecall.nlp import cosine_similarity, get_embedding  # pylint: disable=wrong-import-position
from openrecall.screenshot import record_screenshots_thread, record_screenshots_process  # pylint: disable=wrong-import-position
from openrecall.utils import human_readable_time, timestamp_to_human_readable, read_file_to_string  # pylint: disable=wrong-import-position
from openrecall.trayapp import create_system_tray_icon  # pylint: disable=wrong-import-position

app = Flask(__name__)
app._static_folder = screenshots_path

app.jinja_env.filters["human_readable_time"] = human_readable_time
app.jinja_env.filters["timestamp_to_human_readable"] = timestamp_to_human_readable

base_template = read_file_to_string("./openrecall/templates/base.html")


class StringLoader(BaseLoader):
    def get_source(self, environment, template):
        if template == "base_template":
            return base_template, None, lambda: True
        return None, None, None


app.jinja_env.loader = StringLoader()


@app.route("/")
def timeline():
    # connect to db
    timestamps = get_timestamps()
    number = str(len(timestamps))
    logging.info(f"/ got {number} timestamps")
    return render_template_string(
        read_file_to_string("./openrecall/templates/timeline.html"),
        timestamps=timestamps,
    )


@app.route("/search")
def search():
    q = request.args.get("q")
    logging.info(f"/search for {q}")
    entries = get_all_entries()
    embeddings = [
        np.frombuffer(entry.embedding, dtype=np.float64) for entry in entries
    ]
    query_embedding = get_embedding(q)
    similarities = [cosine_similarity(query_embedding, emb)
                    for emb in embeddings]
    indices = np.argsort(similarities)[::-1]
    sorted_entries = [entries[i] for i in indices]

    return render_template_string(
        read_file_to_string("./openrecall/templates/search.html"),
        entries=sorted_entries,
    )


def run_as_threads():
    stop_event = Event()
    t = Thread(target=record_screenshots_thread, args=(stop_event,))
    t.start()
    tray_icon = create_system_tray_icon()
    tray_icon_thread = Thread(target=tray_icon.run)
    tray_icon_thread.start()

    log_always("Screenshot thread started, pid=", t.native_id)
    app.run(port=8082)
    log_always("Shutting down the server threads...")
    # App was terminated, shutting down the threads
    logging.info("...Stop tray icon")
    tray_icon.stop()
    logging.info("...Stop the Screenshot thread")
    stop_event.set()
    logging.info("Wait for the threads to terminate")
    t.join()
    log_always("Server & Screenshots stopped correctly.")


def run_as_processes():
    global processes
    processes = [
        multiprocessing.Process(target=record_screenshots_process),
        # multiprocessing.Process(target=create_system_tray_icon().run),
        # multiprocessing.Process(target=app.run)
    ]
    tray_icon = create_system_tray_icon()
    tray_icon_thread = Thread(target=tray_icon.run)
    tray_icon_thread.start()

    for process in processes:
        process.start()

    app.run(port=8082)
    tray_icon.stop()
    shutdown_processes()


def shutdown_processes():
    log_always("Terminating Processes")
    for process in processes:
        process.terminate()
        process.join()


# atexit.register(shutdown_processes)


def signal_handler(sig, frame):
    log_always('Shutting down...')
    shutdown_processes()
    exit(0)


if __name__ == "__main__":
    from flask.logging import default_handler

    app.logger.removeHandler(default_handler)
    print(app.name)
    create_db()
    log_always(f"Appdata folder: {appdata_folder}")
    from openrecall.log_config import show_registered_loggers
    config_logger = logging.getLogger("logging_config")
    config_logger.info(show_registered_loggers())
    config_logger = None
    # Start the thread to record screenshots
    # and pass event that stops the thread after ctrl-c is pressed
    # run_as_threads()
    run_as_processes()
