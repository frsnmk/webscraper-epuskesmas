from watchdog.events import FileSystemEventHandler

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, expected_filename, logger):
        self.expected_filename = expected_filename
        self.file_found = False
        self.logger = logger

    def on_created(self, event):
        if self.expected_filename in event.src_path:
            self.logger.info(f"File ditemukan: {event.src_path}")
            self.file_found = True
