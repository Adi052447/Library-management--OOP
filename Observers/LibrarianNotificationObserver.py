from pathlib import Path
import csv
from typing import List
from Models.Book import Book
from Models.Customer import Customer
from Observers.Observer import Observer


class LibrarianNotificationObserver(Observer):
    def __init__(self, logger):
        # חישוב נתיב הבסיס של הפרויקט
        base_dir = Path(__file__).resolve().parent.parent

        # הגדרת הנתיב הדינמי לקובץ users_file
        self.users_file = base_dir / "Files/user.csv"
        self.logger = logger

    def get_librarians_with_notifications(self) -> List[dict]:
        """
        מחזיר את רשימת הספרנים עם שדות username ו-notifications
        """
        librarians = []
        try:
            if self.users_file.exists():
                with self.users_file.open('r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)  # משתמש ב-DictReader לקריאת עמודות לפי שם
                    for row in reader:
                        if row:  # אם השורה לא ריקה
                            librarians.append({
                                "username": row.get("username", ""),  # שם משתמש
                                "Notifictions": row.get("Notifictions", "")  # התראות
                            })
            else:
                self.logger.error(f"Users file does not exist: {self.users_file}")
        except Exception as e:
            self.logger.error(f"Error reading users file: {str(e)}")
        return librarians

    def update_librarian_notifications(self, username: str, new_notification: str):
        """
        מעדכן את שדה ההתראות עבור שם משתמש מסוים
        """
        try:
            if not self.users_file.exists():
                self.logger.error(f"Users file does not exist: {self.users_file}")
                return

            updated_rows = []
            with self.users_file.open('r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row["username"] == username:
                        # בדיקה אם notifications הוא None והמרה למחרוזת ריקה אם כן
                        notifications = row.get("Notifictions", "")
                        if notifications is None:
                            notifications = ""
                        # הוספת ההתראה לשדה הקיים
                        row["Notifictions"] = notifications + f"{new_notification}; "
                    updated_rows.append(row)

            # כתיבה מחדש של הקובץ עם העדכונים
            with self.users_file.open('w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

        except Exception as e:
            self.logger.error(f"Error updating notifications: {str(e)}")

    def update(self, book: Book, customers: List[Customer], event_type: str):
        try:
            librarians = self.get_librarians_with_notifications()
            if event_type == "return":
                message = f"The book '{book.title}' returned and loaned to:"
            elif event_type == "addition":
                message = f"Were added {book.copies} copies of the book '{book.title}' and were loaned to:"
            else:
                return

            for customer in customers:
                message += f"\n- {customer.name} (Phone: {customer.phone})"

            for librarian in librarians:
                self.update_librarian_notifications(librarian["username"], message)
                # self._send_notification(librarian["username"], message)

            self.logger.info("Notifications sent successfully")
        except Exception as e:
            self.logger.error(f"sending notifications fail")