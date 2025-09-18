import logging
import sys

class LogConfiguration:
    def __init__(self, action_name: str, debug_log: str|None = None):
        self.action_name = action_name
        self.debug_log = debug_log


    def config(self):
        """
        Configures the root logger for the application.
        - Logs INFO and above to the console.
        - Logs DEBUG and above to 'app.log' if with_debug is True.
        """
        log = logging.getLogger()  # Get the root logger
        # Clear existing handlers to avoid duplicate logs on re-configuration
        if log.hasHandlers():
            log.handlers.clear()
        # Set the logger's level to the lowest level of its handlers.
        if self.debug_log:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)

        # --- Console Handler ---
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Always log INFO and above to console
        console_formatter = logging.Formatter(f'[{self.action_name}] %(message)s')
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(lambda record: not record.name.startswith('azure.core'))
        log.addHandler(console_handler)

        # --- File Handler (only if debugging) ---
        if self.debug_log:
            file_handler = logging.FileHandler(self.debug_log, mode='w')
            file_handler.setLevel(logging.DEBUG)  # Capture all levels in the file
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            log.addHandler(file_handler)