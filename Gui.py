import csv
import hashlib
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
from tkinter import ttk

from Exceptions.BookExistsException import BookExistsException
from Exceptions.BookNotExistsException import BookNotExistsException
from Models.Customer import Customer
from Exceptions.NegativeCopiesException import NegativeCopiesException
from Exceptions.NoCopyAvailableException import NoCopyAvailableException
from Exceptions.NonIntegerException import NonIntegerException
from Exceptions.ReturnBookNeverLoand import ReturnBookNeverLoand
# ייבוא המחלקות הרלוונטיות
from search.Search import Search
from search.SearchStrategy import TitleSearchStrategy, AuthorSearchStrategy, GenreSearchStrategy, YearSearchStrategy
from Models.Book import Book
from Services.Library import Library


class Gui:
    def __init__(self, master):
        self.master = master
        self.master.title("ספרייה - מסך התחברות")
        self.master.state("zoomed")
        self.library = Library("Files/books.csv")

        # טוענים את תמונת הרקע
        self.original_background_image = Image.open("Files/הספרייה הלאומית.jpg")

        # לייבל לתמונת הרקע
        self.bg_image_label = tk.Label(self.master)
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)

        # מבצעים התאמה חד פעמית של התמונה
        self.master.after(0, self.set_background_once)

        # מאתחלים את המסך הראשון (מסך ההתחברות)
        self.show_login_screen()

    def set_background_once(self):
        """מתאים את תמונת הרקע למידות החלון הנוכחיות."""
        self.master.update_idletasks()

        width = self.master.winfo_width()
        height = self.master.winfo_height()

        resized_image = ImageOps.contain(self.original_background_image, (width, height))
        self.bg_image = ImageTk.PhotoImage(resized_image)
        self.bg_image_label.config(image=self.bg_image)

    def show_login_screen(self):
        """מציג את מסך ההתחברות."""
        # מנקה את כל מה שהיה בחלון
        for widget in self.master.winfo_children():
            widget.destroy()

        # מגדיר מחדש את תמונת הרקע
        self.bg_image_label = tk.Label(self.master)
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.master.after(0, self.set_background_once)

        # מסגרת למסך ההתחברות
        self.main_frame = tk.Frame(self.master, bg=None, width=100, height=100)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # תווית ראשית
        self.label_title = tk.Label(self.main_frame, text="ברוכים הבאים לספרייה", font=("Gisha", 16), bg=None)
        self.label_title.pack(pady=20)

        # שדה שם משתמש
        self.label_username = tk.Label(self.main_frame, text="שם משתמש:", font=("Gisha", 12), bg=None)
        self.label_username.pack()
        self.entry_username = tk.Entry(self.main_frame, width=30)
        self.entry_username.pack(pady=10)

        # שדה סיסמא
        self.label_password = tk.Label(self.main_frame, text="סיסמא:", font=("Gisha", 12), bg=None)
        self.label_password.pack()
        self.entry_password = tk.Entry(self.main_frame, show="*", width=30)
        self.entry_password.pack(pady=10)

        # כפתורי LOGIN ו-REGISTER
        self.frame_buttons = tk.Frame(self.main_frame, bg=None)
        self.frame_buttons.pack(pady=10)

        self.btn_login = tk.Button(self.frame_buttons, text="LOGIN", font=("Gisha", 12),
                                   command=lambda: self.login())
        self.btn_login.grid(row=0, column=0, padx=10)

        # תיקן את הבעיה עם REGISTER
        self.btn_register = tk.Button(self.frame_buttons, text="REGISTER", font=("Gisha", 12),
                                      command=lambda: self.register())  # שים לב: ללא סוגריים
        self.btn_register.grid(row=0, column=1, padx=10)

    # פונקציה שתתאים את התמונה פעם אחת בלבד למידות החלון הנוכחיות
    def set_background_once(self):
        # מודיעים ל-Tkinter לסיים לצייר/להגיב, כדי ש-winfo_width/height יחזירו ערך עדכני
        self.master.update_idletasks()

        new_width = self.master.winfo_width()
        new_height = self.master.winfo_height()

        # שינוי גודל התמונה בצורה ששומרת על יחס הממדים ואיכות התמונה
        resized_image = ImageOps.contain(self.original_background_image, (new_width, new_height))
        self.bg_image = ImageTk.PhotoImage(resized_image)

        self.bg_image_label.config(image=self.bg_image)

    def show_main_screen(self):
        # ניקוי חלון קודם
        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.title("מסך ראשי")

        # יוצרים מחדש Label רקע
        self.bg_image_label = tk.Label(self.master)
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)

        # מבצעים שוב התאמה חד-פעמית של התמונה לאחר הרענון
        self.master.after(0, self.set_background_once)

        # יצירת מסגרת למרכז הכפתורים במסך הראשי
        buttons_frame = tk.Frame(self.master, bg="white")
        buttons_frame.place(relx=0.5, rely=0.5, anchor="center")

        # רשימת הטקסטים והפונקציות לכל כפתור
        button_actions = {
            "Add Book": lambda: self.open_add_book_window(self.library),
            "Remove Book": lambda: self.open_remove_book_window(),
            "Search Book": lambda: self.search_books_window(),
            "View Books": lambda: self.open_view_books_window(),
            "Lend Book": lambda: self.open_lend_book_window(),
            "Return Book": lambda: self.open_return_book_window(),
            "Popular Books": lambda: self.show_popular_books_window()
        }

        max_cols = 4
        row, col = 0, 0

        def create_buttons():
            nonlocal row, col

            for text, command in button_actions.items():
                btn = tk.Button(
                    buttons_frame,
                    text=text,
                    font=("Gisha", 12),
                    width=20,
                    height=2,
                    command=command
                )
                btn.grid(row=row, column=col, padx=10, pady=10)

                col += 1
                if col == max_cols:
                    col = 0
                    row += 1

            # כפתור LOGOUT להתנתקות וחזרה למסך ההתחברות
            btn_logout = tk.Button(buttons_frame, text="LOGOUT", font=("Gisha", 12),
                                   width=20, height=2, command=lambda :self.logout())
            row += 1
            btn_logout.grid(row=row, column=0, columnspan=max_cols, pady=10)

        # יוצרים את הכפתורים באופן מיידי
        create_buttons()

    # ===================== פונקציות רקע ותפעול =====================

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        with open("Files/user.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    if row[0] == username and row[1] == self.hash_password(password):
                        messagebox.showinfo("Login", "Logged in successfully!")
                        self.library.logger.info("logged in successfully")
                        self.main_frame.pack_forget()
                        self.show_main_screen()
                        return
        messagebox.showerror("Login", "Incorrect username or password.")
        self.library.logger.error("logged in fail")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # ===================== ממשק הוספת ספר =====================
    def open_add_book_window(self, library):
        add_book_window = tk.Toplevel(self.master)
        add_book_window.title("Add Book")
        add_book_window.geometry("400x400")

        # תווית כותרת למעלה
        title_label = tk.Label(add_book_window, text="ADD BOOK", font=("Gisha", 18, "bold"), fg="blue")
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        field_names = ["Title", "Author", "Year", "Genre", "Copies"]
        self.book_fields = {}

        for i, field_name in enumerate(field_names):
            label = tk.Label(add_book_window, text=f"{field_name}:", font=("Gisha", 12))
            label.grid(row=i + 1, column=0, padx=10, pady=5, sticky="e")  # שינוי ל-i + 1 כדי להשאיר שורה 0 לכותרת
            if field_name == "Genre":
                genres = ["Fiction", "Dystopian", "Classic", "Adventure", "Romance", "Historical Fiction",
                          "Psychological Drama", "Philosophy", "Epic Poetry", "Gothic Fiction", "Gothic Romance",
                          "Realism", "Modernism", "Satire", "Science Fiction", "Tragedy", "Fantasy"]

                genre_combobox = ttk.Combobox(add_book_window, values=genres, font=("Gisha", 12), state="readonly")
                genre_combobox.grid(row=i + 1, column=1, padx=10, pady=5, sticky="e")
                genre_combobox.set(genres[0])  # Default selection

                # שמירת ה-Combobox במילון
                self.book_fields[field_name] = genre_combobox
            else:
                entry = tk.Entry(add_book_window, width=30)
                entry.grid(row=i + 1, column=1, padx=10, pady=5)

                # שמירת ה-Entry במילון
                self.book_fields[field_name] = entry

        def save_book():
            # קריאת ערכים מהשדות
            book_data = {}
            for field, widget in self.book_fields.items():
                if isinstance(widget, ttk.Combobox):
                    book_data[field] = widget.get()  # עבור Combobox, קבל את הבחירה הנוכחית
                else:
                    book_data[field] = widget.get()  # עבור Entry, קבל את הטקסט

            if all(book_data.values()):
                try:
                    # יצירת אובייקט ספר עם ערכים כפי שהם
                    new_book = Book(
                        title=book_data["Title"],
                        author=book_data["Author"],
                        year=book_data["Year"],  # הערך יועבר כמו שהוא
                        genre=book_data["Genre"],  # קבלת הז'אנר מה-Combobox
                        copies=book_data["Copies"],  # הערך יועבר כמו שהוא
                        available_copies=book_data["Copies"],  # אותו דבר
                        is_loaned="No"
                    )

                    # ניסיון להוסיף ספר דרך הספרייה
                    library.add_book(new_book)
                    messagebox.showinfo("Success", "Book added successfully!")
                    add_book_window.destroy()

                except (NonIntegerException, NegativeCopiesException, BookExistsException) as e:
                    # טיפול בשגיאות שנזרקו מהספרייה
                    messagebox.showerror("Error", str(e))
                except Exception as e:
                    # טיפול בשגיאות אחרות
                    add_book_window.destroy()
                    messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            else:
                # טיפול במקרה שבו לא כל השדות מלאים
                add_book_window.destroy()
                messagebox.showwarning("Error", "Please fill in all fields!")

        save_button = tk.Button(add_book_window, text="Add Book", font=("Gisha", 12), command=save_book)
        save_button.grid(row=len(field_names) + 1, column=0, columnspan=2, pady=20)

    # ===================== ממשק הסרת ספר =====================
    def open_remove_book_window(self):
        remove_book_window = tk.Toplevel(self.master)
        remove_book_window.title("Remove Book")
        remove_book_window.geometry("350x350")

        # כותרת החלון
        title_label = tk.Label(remove_book_window, text="Remove Book", font=("Gisha", 18, "bold"), fg="blue")
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # תוויות ושדות להזנת שם הספר ושם המחבר
        tk.Label(remove_book_window, text="Title:", font=("Gisha", 12)).grid(row=1, column=0, padx=10, pady=10,
                                                                             sticky="e")
        title_entry = tk.Entry(remove_book_window, width=30)
        title_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(remove_book_window, text="Author:", font=("Gisha", 12)).grid(row=2, column=0, padx=10, pady=10,
                                                                              sticky="e")
        author_entry = tk.Entry(remove_book_window, width=30)
        author_entry.grid(row=2, column=1, padx=10, pady=10)

        def delete_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()

            if not title or not author:
                messagebox.showwarning("Error", "Please fill in both fields!")
                return

            try:
                # קריאה למחיקת הספר באמצעות Title ו-Author
                self.library.delete_book(title, author)

                # הודעת הצלחה
                messagebox.showinfo("Success", f"Book '{title}' by '{author}' removed successfully!")
                remove_book_window.destroy()

            except ValueError:
                # הודעת שגיאה במקרה שהספר לא נמצא
                messagebox.showerror("Error", "The book not found")
                remove_book_window.destroy()

        # כפתור למחיקת הספר
        delete_button = tk.Button(remove_book_window, text="Remove Book", font=("Gisha", 12), command=delete_book)
        delete_button.grid(row=3, column=0, columnspan=2, pady=20)

    # ===================== ממשק הצגת ספרים =====================
    def open_view_books_window(self):
        view_books_window = tk.Toplevel(self.master)
        view_books_window.title("View Books")
        view_books_window.geometry("800x600")

        title_label = tk.Label(view_books_window, text="View Books", font=("Gisha", 18, "bold"), fg="blue")
        title_label.pack(pady=10)

        # הגדרת סגנון עבור הטאבים
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Gisha", 12, "bold"), padding=[10, 5])  # פונט גדול יותר ומרווח פנימי
        style.configure("TNotebook", tabmargins=[5, 5, 5, 5])  # מרווחים חיצוניים לטאבים

        # יצירת טאבים
        tab_control = ttk.Notebook(view_books_window, style="TNotebook")
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        # יצירת טאבים עבור כל קטגוריה
        all_books_tab = ttk.Frame(tab_control)
        available_books_tab = ttk.Frame(tab_control)
        borrowed_books_tab = ttk.Frame(tab_control)
        category_books_tab = ttk.Frame(tab_control)

        tab_control.add(all_books_tab, text="All Books")
        tab_control.add(available_books_tab, text="Available Books")
        tab_control.add(borrowed_books_tab, text="Borrowed Books")
        tab_control.add(category_books_tab, text="Books by Category")

        # עמודות
        columns = ("Title", "Author", "Genre", "Year", "Copies Available", "Total Copies", "Loan Status")

        def create_treeview(parent):
            tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
            tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center")
            return tree

        all_books_tree = create_treeview(all_books_tab)
        available_books_tree = create_treeview(available_books_tab)
        borrowed_books_tree = create_treeview(borrowed_books_tab)
        category_books_tree = create_treeview(category_books_tab)

        # פונקציות למילוי הטבלאות
        search = Search(
            books=self.library.books.read_all_as_objects("title"),
            waiting_list=self.library.waiting_list,
            books_borrowed=self.library.loaned_books.read_all_as_objects("title"),
        )

        def populate_treeview(tree, books):
            tree.delete(*tree.get_children())
            for book in books:
                loan_status = "Yes" if book.is_loaned == "Yes" else "No"
                tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                               book.available_copies, book.copies, loan_status))

        def populate_all_books():
            books = search.display_all_books()
            populate_treeview(all_books_tree, books)

        def populate_available_books():
            books = search.display_available_books()
            populate_treeview(available_books_tree, books)

        def populate_borrowed_books():
            books = search.display_borrowed_books()
            populate_treeview(borrowed_books_tree, books)

        def populate_category_books():
            selected_genre = genre_combobox.get()
            if not selected_genre:
                messagebox.showwarning("Warning", "Please select a genre first")
                return
            books = search.display_books_by_genre(selected_genre)
            populate_treeview(category_books_tree, books)

        # מאזין לאירוע של מעבר טאבים
        def on_tab_selected(event):
            selected_tab = event.widget.tab(event.widget.index("current"))["text"]

            if selected_tab == "All Books":
                populate_all_books()
            elif selected_tab == "Available Books":
                populate_available_books()
            elif selected_tab == "Borrowed Books":
                populate_borrowed_books()

        tab_control.bind("<<NotebookTabChanged>>", on_tab_selected)

        # ממשק בחירת קטגוריה
        genres = ["Fiction", "Dystopian", "Classic", "Adventure", "Romance", "Historical Fiction",
                  "Psychological Drama", "Philosophy", "Epic Poetry", "Gothic Fiction", "Gothic Romance",
                  "Realism", "Modernism", "Satire", "Science Fiction", "Tragedy", "Fantasy"]

        genre_frame = tk.Frame(category_books_tab)
        genre_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(genre_frame, text="Select Genre:", font=("Gisha", 12)).pack(side=tk.LEFT, padx=5)
        genre_combobox = ttk.Combobox(genre_frame, values=genres, width=20)
        genre_combobox.pack(side=tk.LEFT, padx=5)

        genre_button = tk.Button(genre_frame, text="Filter", command=populate_category_books, fg="black")
        genre_button.pack(side=tk.LEFT, padx=5)

    def show_books_in_popup(self, books_df):
        popup_window = tk.Toplevel(self.master)
        popup_window.title("Books List")
        popup_window.geometry("600x600")

        table_frame = tk.Frame(popup_window)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = list(books_df.columns)
        books_table = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        books_table.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=books_table.yview)

        for col in columns:
            books_table.heading(col, text=col)
            books_table.column(col, width=100, anchor="center")

        for _, row in books_df.iterrows():
            books_table.insert("", tk.END, values=list(row))

        close_button = tk.Button(popup_window, text="Close", font=("Gisha", 12), command=popup_window.destroy)
        close_button.pack(pady=10)

    # ===================== ממשק השאלת ספר =====================
    def open_lend_book_window(self):
        lend_book_window = tk.Toplevel(self.master)
        lend_book_window.title("Lend Book")
        lend_book_window.geometry("350x350")

        tk.Label(lend_book_window, text="Title:", font=("Gisha", 12)).grid(row=0, column=0,
                                                                           padx=10, pady=10, sticky="e")
        title_entry = tk.Entry(lend_book_window, width=30)
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        def lend_book():
            title = title_entry.get().strip()  # קבלת שם הספר מהשדה והסרת רווחים מיותרים
            if not title:  # בדיקה אם השדה ריק
                messagebox.showwarning("Error", "Please enter the title!")

                return

            try:
                # קריאה לפונקציה במחלקת הספרייה
                self.library.lend_book(title)
                # הודעת הצלחה
                messagebox.showinfo("Success", f"The book '{title}' has been lent successfully!")
                lend_book_window.destroy()
            except NoCopyAvailableException as e:
                # טיפול במקרה שאין עותקים זמינים
                messagebox.showerror("Error", str(e))
                ans = messagebox.askquestion("No Copies Available",
                                             f"No copy available for '{title}'. Would you like to get on the waiting list?")
                if ans == "yes":
                    self.fill_customer_details(title)  # שימוש במתודה של המחלקה
                lend_book_window.destroy()

            except BookNotExistsException as e:
                self.library.logger.error("book borrowed failed")
                # טיפול במקרה שבו הספר לא נמצא
                messagebox.showerror("Error", str(e))
            except Exception as e:
                # טיפול בכל שגיאה אחרת
                 messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
                 lend_book_window.destroy()

        # כפתור השאלה
        lend_button = tk.Button(lend_book_window, text="Lend Book", font=("Gisha", 12), command=lend_book)
        lend_button.grid(row=1, column=0, columnspan=2, pady=20)

    # ===================== ממשק חיפוש ספרים =====================
    def search_books_window(self):
        search_window = tk.Toplevel(self.master)
        search_window.title("Search Books")
        search_window.geometry("350x350")


        search = Search(
            books=self.library.books.read_all_as_objects("title"),
            waiting_list=self.library.waiting_list,
            books_borrowed=self.library.loaned_books.read_all_as_objects("title"),
        )

        tk.Label(search_window, text="Enter search:", font=("Gisha", 14,"bold"),
                 fg="Black").pack(pady=25)
        search_entry = tk.Entry(search_window, font=("Gisha", 12), width=25,bg="white")
        search_entry.pack(pady=5)

        search_criteria = ["Title", "Author", "Genre", "Year"]
        search_criteria_combobox = ttk.Combobox(search_window, values=search_criteria,
                                                font=("Gisha", 12), width=25)
        search_criteria_combobox.set(search_criteria[0])
        search_criteria_combobox.pack(pady=10)

        def display_results(results):
            if results:
                result_window = tk.Toplevel(search_window)
                result_window.title("Search Results")

                treeview = ttk.Treeview(
                    result_window,
                    columns=("Title", "Author", "Genre", "Year", "Available Copies", "Total Copies", "Status"),
                    show="headings"
                )
                treeview.pack(pady=20, padx=20)

                columns = [
                    ("Title", "Title", 150),
                    ("Author", "Author", 150),
                    ("Genre", "Genre", 100),
                    ("Year", "Year", 70),
                    ("Available Copies", "Available", 70),
                    ("Total Copies", "Total", 70),
                ]

                for col, heading, width in columns:
                    treeview.heading(col, text=heading)
                    treeview.column(col, width=width)

                for book in results:
                    treeview.insert("", "end", values=(
                        book.title,
                        book.author,
                        book.genre,
                        book.year,
                        book.available_copies,
                        book.copies,
                    ))
            else:
                messagebox.showinfo("Search Results", "No books found.")
                search_window.destroy()

        def search_submit():
            query = search_entry.get()
            criterion = search_criteria_combobox.get()

            if not query:
                messagebox.showwarning("Search", "Please enter a search query")
                return

            if criterion == "Title":
                strategy = TitleSearchStrategy()
            elif criterion == "Author":
                strategy = AuthorSearchStrategy()
            elif criterion == "Genre":
                strategy = GenreSearchStrategy()
            elif criterion == "Year":
                strategy = YearSearchStrategy()

            search.set_strategy(strategy)
            # try:
            results = search.search(query)
            display_results(results)
            # except Exception as e:
            #     messagebox.showerror("Search Error", f"An error occurred: {str(e)}")

        search_button = tk.Button(search_window, text="Search", command=search_submit,
                                  font=("Gisha", 12), fg="Black", width=20)
        search_button.pack(pady=10)

    # ===================== ממשק החזרת ספר =====================
    def open_return_book_window(self):
        return_book_window = tk.Toplevel(self.master)
        return_book_window.title("Return Book")
        return_book_window.geometry("350x200")

        tk.Label(return_book_window, text="Title:", font=("Gisha", 12)).grid(row=0, column=0,
                                                                             padx=10, pady=10, sticky="e")
        title_entry = tk.Entry(return_book_window, width=30)
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        def return_book():
            title = title_entry.get()
            if title:
                search_strategy = TitleSearchStrategy()
                matching_books = search_strategy.search(title, self.library.books.read_all_as_objects("title"))
                if not matching_books:
                    messagebox.showerror("Error", f"Book '{title}' was not found!")
                    return
                book_to_return = matching_books[0]
                try:
                    self.library.return_book(book_to_return)
                    messagebox.showinfo("Success", f"Book '{book_to_return.title}' returned successfully!")
                    return_book_window.destroy()
                except ReturnBookNeverLoand as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showwarning("Error", "Please enter the title!")

        return_button = tk.Button(return_book_window, text="Return Book", font=("Gisha", 12), command=return_book)
        return_button.grid(row=2, column=0, columnspan=2, pady=20)

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showerror("register", "Username and password cannot be empty.")
            self.library.logger.error("register failed.")
            return

        hashed_password = self.hash_password(password)

        # בדיקה אם המשתמש כבר קיים
        with open("Files/user.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or len(row) < 2:  # דילוג על שורות ריקות או לא תקינות
                    continue
                if row[0] == username:
                    messagebox.showerror("Register", f"User {username} already exists.")
                    self.library.logger.error("register failed")
                    return

        # הוספת משתמש חדש
        with open("Files/user.csv", mode="a", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, hashed_password])

        messagebox.showinfo("Register", f"User {username} registered successfully!")
        self.library.logger.info("registered successfully")
        self.show_main_screen()

    def fill_customer_details(self, title):
        customer_window = tk.Toplevel(self.master)
        customer_window.title("Enter Customer Details")
        customer_window.configure()

        tk.Label(customer_window, text="Enter your name:", font=("Gisha", 12)).pack(
            pady=5)
        name_entry = tk.Entry(customer_window, font=("Gisha", 12), width=30)
        name_entry.pack(pady=5)

        tk.Label(customer_window, text="Enter your phone number:", font=("Gisha", 12)).pack(pady=5)
        phone_entry = tk.Entry(customer_window, font=("Gisha", 12), width=30)
        phone_entry.pack(pady=5)


        def submit_customer_details():
            name = name_entry.get()
            phone = phone_entry.get()

            if name and phone :
                try:
                    customer = Customer(name, phone)
                    self.library.waiting_for_book(title, customer)
                    messagebox.showinfo("waiting list", f"'{name}' added to waiting list for '{title}'.")
                    customer_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", str(e))  # הודעה שהלקוח כבר רשום
                # except Exception as e:
                    # messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            else:
                messagebox.showerror("Error", "Please fill all fields.")

        submit_button = tk.Button(customer_window, text="Submit", command=submit_customer_details,
                                  font=("Gisha", 12), fg="black", width=20)
        submit_button.pack(pady=10)

    def show_popular_books_window(self):

        """
        פותח חלון חדש שמציג את רשימת הספרים הפופולריים ביותר.
        """
        import tkinter as tk
        from tkinter import ttk

        # יצירת חלון חדש
        popular_window = tk.Toplevel(self.master)
        popular_window.title("Popular Books")

        # יצירת כותרת לחלון
        label = tk.Label(popular_window, text="Popular Books", font=("Gisha", 16, "bold"))
        label.pack(pady=10)

        # יצירת טבלה להצגת הנתונים
        tree = ttk.Treeview(popular_window, columns=("Title", "Total Demand", "Borrowed Copies", "Waiting List"),
                            show="headings")
        tree.heading("Title", text="Title")
        tree.heading("Total Demand", text="Total Demand")
        tree.heading("Borrowed Copies", text="Borrowed Copies")
        tree.heading("Waiting List", text="Waiting List")

        # יישור תוכן התאים למרכז
        for column in ("Title", "Total Demand", "Borrowed Copies", "Waiting List"):
            tree.column(column, anchor="center")
            tree.heading(column, anchor="center")

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # קבלת הספרים הפופולריים
        popular_books = self.library.get_popular_books()

        # הוספת הנתונים לטבלה
        for book in popular_books:
            tree.insert("", tk.END, values=book)

        # כפתור לסגירת החלון
        close_button = tk.Button(popular_window, text="Close", command=popular_window.destroy)
        close_button.pack(pady=10)

    def logout(self):
      self.library.logger.info("log out successful")  # הדפסת הודעה ללוג
      self.show_login_screen()



if __name__ == '__main__':
    root = tk.Tk()
    app = Gui(root)
    root.mainloop()
