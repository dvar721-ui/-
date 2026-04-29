import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class BookTracker:
    """Главный класс приложения для трекинга прочитанных книг"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Автор: Даниил Ильин
        self.author = "Даниил Ильин"
        
        # Файл для хранения данных
        self.data_file = "books.json"
        
        # Загружаем данные
        self.books = self.load_books()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Обновляем таблицу
        self.refresh_table()
        
        # Настройка обработки закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка веса колонок
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок с именем автора
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(title_frame, text="📚 Book Traker", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Label(title_frame, text=f"© {self.author}", font=('Arial', 10)).pack(side=tk.RIGHT)
        
        # ===== Панель ввода данных =====
        input_frame = ttk.LabelFrame(main_frame, text="➕ Добавление новой книги", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Поле: Название книги
        ttk.Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(input_frame, textvariable=self.title_var, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 20))
        
        # Поле: Автор
        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        self.author_var = tk.StringVar()
        self.author_entry = ttk.Entry(input_frame, textvariable=self.author_var, width=30)
        self.author_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # Поле: Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.genre_var = tk.StringVar()
        self.genre_combo = ttk.Combobox(input_frame, textvariable=self.genre_var, width=28)
        self.genre_combo['values'] = ('Роман', 'Детектив', 'Фантастика', 'Фэнтези', 
                                       'Научная литература', 'Биография', 'Поэзия', 
                                       'Драма', 'Приключения', 'Триллер', 'Ужасы',
                                       'Историческая', 'Психология', 'Саморазвитие')
        self.genre_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 20))
        
        # Поле: Количество страниц
        ttk.Label(input_frame, text="Количество страниц:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=5)
        self.pages_var = tk.StringVar()
        self.pages_entry = ttk.Entry(input_frame, textvariable=self.pages_var, width=30)
        self.pages_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="📖 Добавить книгу", command=self.add_book)
        self.add_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
        # ===== Панель фильтрации =====
        filter_frame = ttk.LabelFrame(main_frame, text="🔍 Фильтрация книг", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
        # Фильтр по жанру
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=(0, 10), pady=5)
        self.filter_genre_var = tk.StringVar(value="Все жанры")
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, width=25)
        self.filter_genre_combo['values'] = ['Все жанры'] + list(self.genre_combo['values'])
        self.filter_genre_combo.grid(row=0, column=1, padx=(0, 20), pady=5)
        self.filter_genre_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Фильтр по количеству страниц
        ttk.Label(filter_frame, text="Фильтр по страницам:").grid(row=0, column=2, padx=(0, 10), pady=5)
        
        self.filter_pages_op_var = tk.StringVar(value="больше")
        self.filter_pages_op_combo = ttk.Combobox(filter_frame, textvariable=self.filter_pages_op_var, width=8)
        self.filter_pages_op_combo['values'] = ('больше', 'меньше', 'равно')
        self.filter_pages_op_combo.grid(row=0, column=3, padx=(0, 5), pady=5)
        
        self.filter_pages_var = tk.StringVar()
        self.filter_pages_entry = ttk.Entry(filter_frame, textvariable=self.filter_pages_var, width=10)
        self.filter_pages_entry.grid(row=0, column=4, padx=(0, 10), pady=5)
        
        # Кнопка применения фильтра
        self.apply_btn = ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filters)
        self.apply_btn.grid(row=0, column=5, padx=(10, 0), pady=5)
        
        # Кнопка сброса фильтра
        self.reset_btn = ttk.Button(filter_frame, text="🗑️ Сбросить фильтр", command=self.reset_filters)
        self.reset_btn.grid(row=0, column=6, padx=(10, 0), pady=5)
        
        # ===== Таблица с книгами =====
        table_frame = ttk.LabelFrame(main_frame, text="📚 Список прочитанных книг", padding="10")
        table_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Создание таблицы
        columns = ('ID', 'Название', 'Автор', 'Жанр', 'Страницы', 'Дата добавления')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название книги')
        self.tree.heading('Автор', text='Автор')
        self.tree.heading('Жанр', text='Жанр')
        self.tree.heading('Страницы', text='Страниц')
        self.tree.heading('Дата добавления', text='Дата добавления')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Название', width=250)
        self.tree.column('Автор', width=180)
        self.tree.column('Жанр', width=130)
        self.tree.column('Страницы', width=80, anchor='center')
        self.tree.column('Дата добавления', width=120, anchor='center')
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления данными
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.delete_btn = ttk.Button(btn_frame, text="❌ Удалить выбранную книгу", command=self.delete_book)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(btn_frame, text="✏️ Редактировать книгу", command=self.edit_book)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Сохранить вручную", command=self.save_books)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.stats_btn = ttk.Button(btn_frame, text="📊 Статистика", command=self.show_stats)
        self.stats_btn.pack(side=tk.LEFT, padx=5)
        
        # Статусная строка
        self.status_var = tk.StringVar(value="✅ Готово. Все изменения автоматически сохраняются.")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Подсказки для пользователя
        self.create_tooltips()
    
    def create_tooltips(self):
        """Создание всплывающих подсказок"""
        self.create_tooltip(self.title_entry, "Введите название книги (обязательное поле)")
        self.create_tooltip(self.author_entry, "Введите имя автора (обязательное поле)")
        self.create_tooltip(self.pages_entry, "Введите количество страниц (целое положительное число)")
        self.create_tooltip(self.filter_pages_entry, "Введите число для фильтрации по страницам\nПример: 200")
    
    def create_tooltip(self, widget, text):
        """Создание всплывающей подсказки для виджета"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, padding=5)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)
    
    def validate_book(self, title, author, genre, pages):
        """
        Валидация введенных данных
        
        Возвращает: (is_valid, error_message)
        """
        # Проверка названия
        if not title or not title.strip():
            return False, "❌ Ошибка: Название книги не может быть пустым!"
        
        if len(title.strip()) > 200:
            return False, "❌ Ошибка: Название не может превышать 200 символов!"
        
        # Проверка автора
        if not author or not author.strip():
            return False, "❌ Ошибка: Имя автора не может быть пустым!"
        
        if len(author.strip()) > 100:
            return False, "❌ Ошибка: Имя автора не может превышать 100 символов!"
        
        # Проверка жанра
        if not genre:
            return False, "❌ Ошибка: Выберите жанр книги!"
        
        # Проверка количества страниц
        if not pages:
            return False, "❌ Ошибка: Введите количество страниц!"
        
        try:
            pages_int = int(pages)
            if pages_int <= 0:
                return False, "❌ Ошибка: Количество страниц должно быть положительным числом!"
            if pages_int > 10000:
                return False, "❌ Ошибка: Количество страниц не может превышать 10000!"
        except ValueError:
            return False, "❌ Ошибка: Количество страниц должно быть целым числом!"
        
        return True, ""
    
    def add_book(self):
        """Добавление новой книги"""
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        genre = self.genre_var.get()
        pages = self.pages_var.get().strip()
        
        # Валидация
        is_valid, error_msg = self.validate_book(title, author, genre, pages)
        
        if not is_valid:
            messagebox.showerror("Ошибка ввода", error_msg)
            return
        
        # Генерация ID
        book_id = max([b['id'] for b in self.books], default=0) + 1
        
        # Добавление книги
        book = {
            'id': book_id,
            'title': title,
            'author': author,
            'genre': genre,
            'pages': int(pages),
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.books.append(book)
        self.save_books()
        self.refresh_table()
        
        # Очистка полей
        self.title_var.set("")
        self.author_var.set("")
        self.genre_var.set("")
        self.pages_var.set("")
        
        self.status_var.set(f"✅ Книга «{title}» успешно добавлена! Всего книг: {len(self.books)}")
        
        # Фокус на поле названия для быстрого добавления следующей книги
        self.title_entry.focus()
    
    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите книгу для удаления!")
            return
        
        # Получение ID книги
        item = self.tree.item(selected[0])
        book_id = item['values'][0]
        book_title = item['values'][1]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить книгу:\n«{book_title}»?"):
            # Удаление из списка
            self.books = [b for b in self.books if b['id'] != book_id]
            self.save_books()
            self.refresh_table()
            self.status_var.set(f"🗑️ Книга «{book_title}» успешно удалена! Осталось книг: {len(self.books)}")
    
    def edit_book(self):
        """Редактирование выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите книгу для редактирования!")
            return
        
        # Получение ID и данных книги
        item = self.tree.item(selected[0])
        book_id = item['values'][0]
        
        # Находим книгу в списке
        book_to_edit = next((b for b in self.books if b['id'] == book_id), None)
        
        if book_to_edit:
            # Заполняем поля для редактирования
            self.title_var.set(book_to_edit['title'])
            self.author_var.set(book_to_edit['author'])
            self.genre_var.set(book_to_edit['genre'])
            self.pages_var.set(str(book_to_edit['pages']))
            
            # Удаляем старую запись
            self.books = [b for b in self.books if b['id'] != book_id]
            
            self.status_var.set(f"✏️ Редактирование книги «{book_to_edit['title']}». Измените данные и нажмите «Добавить книгу»")
    
    def load_books(self):
        """Загрузка книг из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return []
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Ошибка загрузки: {e}")
                return []
        return []
    
    def save_books(self):
        """Сохранение книг в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")
            return False
    
    def validate_pages_filter(self, pages_str):
        """Валидация значения фильтра по страницам"""
        if not pages_str:
            return True, None, ""
        
        try:
            pages_int = int(pages_str)
            if pages_int <= 0:
                return False, None, "Количество страниц должно быть положительным числом!"
            if pages_int > 10000:
                return False, None, "Количество страниц не может превышать 10000!"
            return True, pages_int, ""
        except ValueError:
            return False, None, "Введите целое число для фильтрации по страницам!"
    
    def apply_filters(self, event=None):
        """Применение фильтров к таблице с валидацией"""
        # Валидация поля фильтра по страницам
        pages_filter_str = self.filter_pages_var.get().strip()
        
        is_valid, pages_value, error_msg = self.validate_pages_filter(pages_filter_str)
        
        if not is_valid and pages_filter_str:
            messagebox.showerror("Ошибка в фильтре", error_msg)
            return
        
        self.refresh_table(filtered=True)
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_genre_var.set("Все жанры")
        self.filter_pages_op_var.set("больше")
        self.filter_pages_var.set("")
        self.refresh_table()
        self.status_var.set("🔄 Фильтры сброшены. Показаны все книги.")
    
    def refresh_table(self, filtered=False):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение данных
        books_to_show = self.books.copy()
        
        # Применение фильтров
        if filtered:
            # Фильтр по жанру
            selected_genre = self.filter_genre_var.get()
            if selected_genre != "Все жанры":
                books_to_show = [b for b in books_to_show if b['genre'] == selected_genre]
            
            # Фильтр по количеству страниц
            pages_filter_str = self.filter_pages_var.get().strip()
            if pages_filter_str:
                try:
                    pages_value = int(pages_filter_str)
                    operation = self.filter_pages_op_var.get()
                    
                    if operation == "больше":
                        books_to_show = [b for b in books_to_show if b['pages'] > pages_value]
                    elif operation == "меньше":
                        books_to_show = [b for b in books_to_show if b['pages'] < pages_value]
                    elif operation == "равно":
                        books_to_show = [b for b in books_to_show if b['pages'] == pages_value]
                except ValueError:
                    pass
        
        # Сортировка по ID
        books_to_show.sort(key=lambda x: x['id'])
        
        # Заполнение таблицы
        for book in books_to_show:
            self.tree.insert('', tk.END, values=(
                book['id'],
                book['title'],
                book['author'],
                book['genre'],
                book['pages'],
                book.get('date_added', '')
            ))
        
        # Обновление статуса
        filter_status = " (с фильтрацией)" if filtered else ""
        self.status_var.set(f"📊 Показано книг: {len(books_to_show)} из {len(self.books)}{filter_status}")
    
    def show_stats(self):
        """Показ статистики по книгам"""
        if not self.books:
            messagebox.showinfo("Статистика", "В вашей библиотеке пока нет книг.")
            return
        
        total_books = len(self.books)
        total_pages = sum(b['pages'] for b in self.books)
        avg_pages = total_pages // total_books if total_books > 0 else 0
        
        # Статистика по жанрам
        genres_count = {}
        for book in self.books:
            genre = book['genre']
            genres_count[genre] = genres_count.get(genre, 0) + 1
        
        most_common_genre = max(genres_count, key=genres_count.get) if genres_count else "Нет"
        
        # Самая толстая и самая тонкая книга
        thickest_book = max(self.books, key=lambda x: x['pages']) if self.books else None
        thinnest_book = min(self.books, key=lambda x: x['pages']) if self.books else None
        
        stats_text = f"""
📊 СТАТИСТИКА ВАШЕЙ БИБЛИОТЕКИ

📚 Всего книг: {total_books}
📖 Всего страниц: {total_pages}
📏 Среднее количество страниц: {avg_pages}

🏆 Самый популярный жанр: {most_common_genre} ({genres_count.get(most_common_genre, 0)} книг)

📘 Самая толстая книга: {thickest_book['title'] if thickest_book else 'Нет'} ({thickest_book['pages'] if thickest_book else 0} стр.)
📗 Самая тонкая книга: {thinnest_book['title'] if thinnest_book else 'Нет'} ({thinnest_book['pages'] if thinnest_book else 0} стр.)

📊 Распределение по жанрам:
"""
        for genre, count in sorted(genres_count.items(), key=lambda x: x[1], reverse=True):
            stats_text += f"   • {genre}: {count} книг\n"
        
        messagebox.showinfo("Статистика библиотеки", stats_text)
    
    def on_closing(self):
        """Обработка закрытия окна"""
        self.save_books()
        self.root.destroy()


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()


if __name__ "__main__":
    main()