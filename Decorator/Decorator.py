from functools import wraps

def log_operation(operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # רישום הודעת DEBUG לתחילת פעולה
                self.logger.debug(f"Starting operation: {operation_name}")

                # הפעלת הפונקציה המקורית
                result = func(self, *args, **kwargs)

                # רישום הודעת INFO במקרה של הצלחה
                self.logger.info(f"{operation_name} successfully")
                return result
            except Exception as e:
                # רישום הודעת ERROR במקרה של שגיאה
                self.logger.error(f"{operation_name} fail")
                raise e  # זריקת השגיאה שוב לטיפול חיצוני אם צריך
        return wrapper
    return decorator
