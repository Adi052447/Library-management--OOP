import csv
from pathlib import Path

import pandas as pd
from Models.Book import Book
from Models.Customer import Customer


class ManageCsv:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data_frame = self.load_csv()

    def load_csv(self):
        """
        טוען את קובץ ה-CSV לתוך DataFrame של Pandas
        """
        try:
            return pd.read_csv(self.file_path)
        except FileNotFoundError:
            print(f"File '{self.file_path}' not found. Creating an empty DataFrame.")
            return pd.DataFrame()

    def save_csv(self):
        """
        שומר את ה-DataFrame בקובץ ה-CSV
        """
        self.data_frame.to_csv(self.file_path, index=False)

    def read_all(self):
        """
        מחזיר את כל הנתונים בקובץ ה-CSV
        """
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        return self.data_frame

    def read_row(self, row_index):
        """
        מחזיר שורה מסוימת לפי אינדקס
        """
        if 0 <= row_index < len(self.data_frame):
            return self.data_frame.iloc[row_index]
        else:
            raise IndexError("Row index out of range.")

    def read_column(self, column_name):
        """
        מחזיר עמודה מסוימת לפי שם
        """
        if column_name in self.data_frame.columns:
            return self.data_frame[column_name]
        else:
            raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    def add_row(self, obj):
        """
        מוסיף שורה על בסיס אובייקט מסוג כלשהו (למשל Book) בהתאמה לעמודות הקיימות ב-DataFrame,
        ושומר את ה-DataFrame המעודכן בקובץ CSV אם השורה לא קיימת על בסיס שני השדות הראשונים (title ו-author).
        """
        # המרה של האובייקט למילון
        row_dict = obj.__dict__

        # בדיקה אם השדות 'title' ו-'author' קיימים ב-DataFrame
        if 'title' not in self.data_frame.columns or 'author' not in self.data_frame.columns:
            raise ValueError("Columns 'title' and 'author' must exist in the DataFrame.")

        # בדיקה אם השורה כבר קיימת על בסיס 'title' ו-'author'
        is_duplicate = (
                (self.data_frame['title'] == row_dict['title']) &
                (self.data_frame['author'] == row_dict['author'])
        ).any()

        if is_duplicate:
            return

        # סינון מפתחות כדי להתאים לעמודות הקיימות
        filtered_row = {key: value for key, value in row_dict.items() if key in self.data_frame.columns}

        # הוספת השורה ל-DataFrame
        self.data_frame = self.data_frame._append(filtered_row, ignore_index=True)

        # שמירת ה-DataFrame המעודכן בקובץ CSV
        self.data_frame.to_csv(self.file_path, index=False)


    def delete_row(self, book):
        """
        מוחק שורה על בסיס אובייקט ספר לפי שם הספר ושם המחבר בלבד,
        ושומר את ה-DataFrame המעודכן בקובץ CSV.
        :param book: אובייקט מסוג Book
        :return: True אם השורה נמחקה, אחרת False
        """
        if not isinstance(book, Book):
            raise ValueError("The provided object is not of type 'Book'")

        # יצירת מסיכה למחיקת השורה המתאימה לפי שם הספר ושם המחבר
        mask = (self.data_frame["title"] == book.title) & (self.data_frame["author"] == book.author)

        if mask.any():
            row_index = self.data_frame.index[mask][0]
            self.data_frame.drop(index=row_index, inplace=True)
            self.data_frame.reset_index(drop=True, inplace=True)

            # שמירת ה-DataFrame המעודכן לקובץ CSV
            self.data_frame.to_csv(self.file_path, index=False)  # עדכן את נתיב הקובץ בהתאם

            return True  # מציין שהשורה נמחקה
        else:
            return False  # מציין שהשורה לא נמצאה

    def update_row(self, row_index, update_dict):
        """
        מעדכן שורה מסוימת לפי אינדקס עם ערכים חדשים מתוך מילון
        ושומר את ה-DataFrame המעודכן בקובץ CSV.
        """
        if 0 <= row_index < len(self.data_frame):
            for key, value in update_dict.items():
                if key in self.data_frame.columns:
                    self.data_frame.at[row_index, key] = value
                else:
                    raise ValueError(f"Column '{key}' not found in DataFrame.")

            # שמירת ה-DataFrame המעודכן בקובץ CSV
            self.data_frame.to_csv(self.file_path, index=False)  # עדכן את נתיב הקובץ לפי הצורך

        else:
            raise IndexError("Row index out of range.")

    def get_book_by_title(self, title: str, author: str) -> Book:
        """
        מחפש ספר לפי שם הספר ושם המחבר בקובץ, ויוצר אובייקט מסוג Book מהשורה שנמצאה.
        :param title: שם הספר לחיפוש.
        :param author: שם המחבר לחיפוש.
        :return: אובייקט מסוג Book אם הספר נמצא, אחרת None.
        """
        # קריאת כל הספרים ממסד הנתונים (קובץ ה-CSV)
        books_df = self.read_all()

        # סינון השורה המתאימה לפי title ו-author
        mask = (books_df['title'] == title) & (books_df['author'] == author)
        filtered_rows = books_df[mask]

        if not filtered_rows.empty:
            # קבלת הערכים מהשורה הראשונה המסוננת
            row = filtered_rows.iloc[0]
            book = Book(
                title=row['title'],
                author=row['author'],
                year=row['year'],
                genre=row['genre'],
                copies=row['copies'],
                available_copies=row['available_copies'],
                is_loaned=row['is_loaned']
            )
            return book
        else:
            return None

    def create_file_avialable_books(self):
        """
        יוצר קובץ CSV חדש עם כל השורות בהן העמודה 'is_loaned' שווה ל-NO.
        """
        # סינון השורות בהן is_loaned == 'No'
        unloaned_df = self.data_frame[self.data_frame['is_loaned'] == 'No']

        # שמירה לקובץ CSV חדש
        unloaned_df.to_csv("available_books.csv", index=False)

    def create_file_loaned_books(self):
        """
        יוצר קובץ CSV חדש עם כל השורות בהן העמודה 'is_loaned' שווה ל-Yes.
        """
        # סינון השורות בהן is_loaned == 'Yes'
        loaned_df = self.data_frame[self.data_frame['is_loaned'] == 'Yes']

        # שמירה לקובץ CSV חדש עם סיומת .csv
        loaned_df.to_csv("loaned_books.csv", index=False)

    def load_waiting_list_from_csv(file_path=None):
        """טוען את רשימת ההמתנה מקובץ CSV."""
        waiting_list = {}
        try:
            base_dir = Path(__file__).resolve().parent.parent  # חישוב תיקיית הבסיס
            file_path = base_dir / "Files/waiting_list.csv"

            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        book_title = row['Book Title']
                        customer = Customer(
                            name=row['Customer Name'],
                            phone=row['Customer Phone'],
                        )
                        if book_title not in waiting_list:
                            waiting_list[book_title] = []
                        waiting_list[book_title].append(customer)
        except Exception as e:
            print(f"Error loading waiting list from {"waiting_list.csv"}: {str(e)}")
        return waiting_list

    def read_all_as_objects(self, key_column: str):
        """
        ממיר את הנתונים למילון שבו הערכים הם אובייקטים של Book.
        המפתח במילון יהיה מבוסס על עמודה מסוימת (key_column).
        """
        if key_column not in self.data_frame.columns:
            raise ValueError(f"Key column '{key_column}' not found in DataFrame.")

        # המרה של ה-DataFrame למילון של אובייקטים
        data_dict = self.data_frame.to_dict(orient="records")
        return {row[key_column]: Book(**row) for row in data_dict}

    def save_waiting_list_to_csv(waiting_list):
        """שומר את רשימת ההמתנה בקובץ CSV."""
        try:
            base_dir = Path(__file__).resolve().parent.parent
            file_path = base_dir / "Files/waiting_list.csv"

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['Book Title', 'Customer Name', 'Customer Phone']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()

                for book_title, customers in waiting_list.items():
                    for customer in customers:
                        writer.writerow({
                            'Book Title': book_title,
                            'Customer Name': customer.name,
                            'Customer Phone': customer.phone,
                        })
        except Exception as e:
            print(f"Error saving waiting list to {"waiting_list.csv"}: {str(e)}")
