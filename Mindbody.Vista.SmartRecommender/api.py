from flask import Flask
from flask import request


api = Flask(__name__)


@api.route("/timeslotinsights", methods=["POST"])
def time_slot_insights():
    content = request.get_json()

    studio_id = content["Studio_ID"]
    category = content["Category"]

    from jobs.job import run_time_slot_insights_job
    time_slot_results = run_time_slot_insights_job(studio_id, category)

    return time_slot_results


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8090
    api.run(host=host, port=port, debug=True)
