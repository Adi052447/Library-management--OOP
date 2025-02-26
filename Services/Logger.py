import logging
import os

class Logger:
    _instance = None

    def __new__(cls, log_file=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # יצירת logger
            cls._instance.logger = logging.getLogger("LibraryLogger")
            cls._instance.logger.setLevel(logging.INFO)

            # פורמט של הלוגים
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

            # הגדרת נתיב דינמי לקובץ הלוג
            if log_file:
                log_file = cls.get_dynamic_path(log_file)
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                cls._instance.logger.addHandler(file_handler)

            # כתיבה לקונסול
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(console_handler)

        return cls._instance

    @staticmethod
    def get_dynamic_path(relative_path):
        """מחשב את הנתיב הדינמי לקובץ בהתאם לתיקיית הבסיס של הפרויקט"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, relative_path)

    def get_logger(self):
        """מחזיר את האובייקט של logging.Logger"""
        return self.logger

    def error(self, message):
        self.logger.error(message)
