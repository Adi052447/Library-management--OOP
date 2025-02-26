
class Book:
    def __init__(self, title, author, year, genre, copies, available_copies,is_loaned):
        """
        אתחול אובייקט של ספר. נבדק אם הספר כבר קיים בקובץ.
        :param title: כותרת הספר
        :param author: שם המחבר
        :param year: שנת ההוצאה לאור
        :param genre: ז'אנר
        :param copies: מספר העותקים הקיימים
        :param manage_csv: אובייקט מסוג ManageCsv לבדיקת קיום הספר
        """
        # בדיקה אם הספר קיים כבר בקובץ
        # if self._is_book_in_csv(title, author, self.file):
        #     print(f"Book '{title}' by '{author}' already exists in the library. Skipping creation.")
        #     return  # יציאה מהמתודה מבלי ליצור אובייקט חדש

        # אתחול פרטי הספר
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.copies = copies
        self.available_copies = available_copies
        self.is_loaned = is_loaned

    def __repr__(self):
        return (
            f"Book(\n"
            f"  Title: {self.title},\n"
            f"  Author: {self.author},\n"
            f"  Year: {self.year},\n"
            f"  Genre: {self.genre},\n"
            f"  Copies: {self.copies},\n"
            f"  Available Copies: {self.available_copies},\n"
            f"  Is Loaned: {self.is_loaned}\n"
            f")"
        )
