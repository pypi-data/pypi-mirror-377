import threading
import subprocess
import re
from queue import Queue
from . import DOWNLOAD_FOLDER

# Global queue that the server will add jobs to.
DOWNLOAD_QUEUE = Queue()

# Global dictionary that stores the real-time state of all downloads.
# This is what the API endpoints will read from.
DOWNLOAD_TASKS = {}

def download_worker_thread():
    """
    The single worker thread that runs forever, processing one item
    from the download queue at a time.
    """
    while True:
        # This line will block and wait until a new item is put into the queue.
        task_id, command, title = DOWNLOAD_QUEUE.get()
        
        print(f"Worker picked up task: {task_id} ({title})")
        
        # Set the initial status for the UI.
        DOWNLOAD_TASKS[task_id]['status'] = 'downloading'
        DOWNLOAD_TASKS[task_id]['stage'] = 'Initializing...'
        
        try:
            # Start the yt-dlp command as a background subprocess.
            # We read its output line-by-line to get live progress.
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding='utf-8', 
                bufsize=1
            )
            
            # Regular expressions to parse yt-dlp's text output.
            progress_regex = re.compile(
                r"\[download\]\s+(?P<percent>[\d.]+)%\s+of\s+(?:~)?\s*(?P<size>[\d.]+\w+B)\s+at\s+(?P<speed>[\d.]+\w+B/s)\s+ETA\s+(?P<eta>[\d:]+)"
            )
            destination_regex = re.compile(r"\[download\] Destination: (.*)")
            post_process_regex = re.compile(r"\[(Merger|ExtractAudio|ffmpeg)\]")
            
            # Read each line of output from the subprocess as it comes in.
            for line in iter(process.stdout.readline, ''):
                prog_match = progress_regex.search(line)
                dest_match = destination_regex.search(line)
                post_match = post_process_regex.search(line)

                if prog_match:
                    data = prog_match.groupdict()
                    DOWNLOAD_TASKS[task_id].update({
                        'progress': float(data['percent']),
                        'size': data['size'],
                        'speed': data['speed'],
                        'eta': data['eta'],
                        'stage': 'Downloading...'
                    })
                    continue

                if dest_match:
                    DOWNLOAD_TASKS[task_id]['stage'] = 'Downloading...'
                    continue

                if post_match:
                    stage_name = post_match.group(1).capitalize()
                    DOWNLOAD_TASKS[task_id]['stage'] = f'{stage_name} files...'
                    DOWNLOAD_TASKS[task_id]['progress'] = 100.0 # Download part is done
                    continue
            
            # After the loop, wait for the process to fully finish.
            stdout, stderr = process.communicate()
            
            # Check the final exit code to determine success or failure.
            if process.returncode != 0:
                error_msg = stderr.strip().split('ERROR:')[-1].strip()
                DOWNLOAD_TASKS[task_id]['status'] = 'error'
                DOWNLOAD_TASKS[task_id]['error'] = error_msg or "Unknown yt-dlp error."
                print(f"Error for task {task_id}: {stderr.strip()}")
            else:
                DOWNLOAD_TASKS[task_id]['status'] = 'completed'
                DOWNLOAD_TASKS[task_id]['progress'] = 100.0
                DOWNLOAD_TASKS[task_id]['stage'] = 'Finished'

        except Exception as e:
            DOWNLOAD_TASKS[task_id]['status'] = 'error'
            DOWNLOAD_TASKS[task_id]['error'] = str(e)
            print(f"Exception during download for task {task_id}: {e}")
        
        # Signal that this task is complete.
        DOWNLOAD_QUEUE.task_done()

# This is a crucial part:
# When this module is first imported by the application, it creates a single
# worker thread, marks it as a "daemon" (so it exits when the main app exits),
# and starts it. This thread will then run forever.
worker = threading.Thread(target=download_worker_thread, daemon=True)
worker.start()
