# pylint: disable=wrong-import-order
import logging  # nopep8 pylint: disable=unused-import
import openrecall.log_config  # nopep8
from openrecall.log_config import log_always  # nopep8

openrecall.log_config.setup_logging()  # nopep8

from threading import Thread, Event  # pylint: disable=wrong-import-position
import numpy as np  # pylint: disable=wrong-import-position
from flask import Flask, render_template_string, request, send_from_directory  # pylint: disable=wrong-import-position
from jinja2 import BaseLoader  # pylint: disable=wrong-import-position

from openrecall.config import appdata_folder, screenshots_path  # pylint: disable=wrong-import-position disable=ungrouped-imports
from openrecall.database import create_db, get_all_entries, get_timestamps  # pylint: disable=wrong-import-position
from openrecall.nlp import cosine_similarity, get_embedding  # pylint: disable=wrong-import-position
from openrecall.screenshot import record_screenshots_thread  # pylint: disable=wrong-import-position
from openrecall.utils import human_readable_time, timestamp_to_human_readable, read_file_to_string  # pylint: disable=wrong-import-position
from openrecall.trayapp import create_system_tray_icon  # pylint: disable=wrong-import-position

app = Flask(__name__)

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
    return render_template_string(
        read_file_to_string("./openrecall/templates/timeline.html"),
        timestamps=timestamps,
    )


@app.route("/search")
def search():
    q = request.args.get("q")
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


@app.route("/static/<filename>")
def serve_image(filename):
    return send_from_directory(screenshots_path, filename)


if __name__ == "__main__":
    create_db()
    log_always(f"Appdata folder: {appdata_folder}")
    # Start the thread to record screenshots
    # and pass event that stops the thread after ctrl-c is pressed
    stop_event = Event()
    t = Thread(target=record_screenshots_thread, args=(stop_event,))
    t.start()
    tray_icon_thread = Thread(target=create_system_tray_icon().run)
    tray_icon_thread.start()

    log_always("Screenshot thread started, pid=", t.native_id)
    app.run(port=8082)
    # App was terminated, shutting down the threads
    print("Stop the Screenshot thread")
    stop_event.set()
    print("Wait for the Screenshot thread to terminate")
    t.join()
    print("Server & Screenshots stopped")
