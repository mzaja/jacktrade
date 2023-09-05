class ProgressBar:
    """
    Displays a progress bar.

    When used as a context manager, returns a queue through which the
    other threads/processes need to signal that a job is done by putting
    any value in the queue.
    """

    def __init__(self, total_jobs: int, job_done_queue: mp.Queue = None):
        self._job_done_queue = job_done_queue or mp.Queue()
        self._total_jobs = total_jobs
        self._progress_bar = tqdm(total=total_jobs)

    def _update_progress_bar(self):
        jobs_done = 0
        while True:
            increment = self._job_done_queue.get()
            self._progress_bar.update(increment)
            jobs_done += increment
            if jobs_done >= self._total_jobs:
                break

    def __enter__(self):
        self._thread = threading.Thread(
            target=self._update_progress_bar, name=self.__class__, daemon=True
        )
        self._thread.start()
        return self._job_done_queue

    def __exit__(self, *args, **kwargs):
        self._thread.join(1)
        self._progress_bar.close()
