
import time
import schedule

from config import config


def start(job_fn) -> None:
    interval = config.SCHEDULE_INTERVAL_SECONDS
    schedule.every(interval).seconds.do(job_fn)

    # Run once immediately, then follow the schedule.
    job_fn()

    while True:
        schedule.run_pending()
        time.sleep(1)
