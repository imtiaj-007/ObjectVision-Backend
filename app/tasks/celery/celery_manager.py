import time
import subprocess
import threading

from app.tasks.celery import celery_app
from app.utils.logger import log


class CeleryManager:
    def __init__(self):
        self.worker_process = None

    def start_worker(self, loglevel="info", pool="solo"):
        """Starts the Celery worker process."""
        if self.worker_process is None:
            command = [
                "celery",
                "-A", "app.tasks.celery:celery_app",
                "worker",
                "--loglevel", loglevel,
                "-Q", "logging",
                "--pool", pool,
            ]
            log.info(f"🚀 Starting Celery worker: {' '.join(command)}")
            self.worker_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Start a thread to capture logs from Celery process
            self.log_thread = threading.Thread(target=self.capture_logs, daemon=True)
            self.log_thread.start()

            time.sleep(3)
            log.info(f"🚀 Celery worker started successfully: ✅")

        else:
            log.warning("⚠️ Celery worker is already running.")
        
    def capture_logs(self):
        """Capture and display Celery logs."""
        while self.worker_process and self.worker_process.poll() is None:
            output = self.worker_process.stdout.readline()
            if output:
                log.info(f"[Celery] {output.strip()}")

    def stop_worker(self):
        """Stops the Celery worker process."""
        if self.worker_process:
            log.info("🛑 Stopping Celery worker...")
            self.worker_process.terminate()
            self.worker_process.wait()
            self.worker_process = None
            log.info("🛑 Celery worker is closed: ✅")
        else:
            log.warning("⚠️ No Celery worker is running.")

    def check_status(self):
        """Checks if the Celery worker is running."""
        if self.worker_process and self.worker_process.poll() is None:
            return "Celery worker is running."
        return "Celery worker is NOT running."

