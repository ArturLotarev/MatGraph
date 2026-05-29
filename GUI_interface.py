# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

def error(error_text, name_error="MatGraph"):
    """
    Создает окно ошибки с заданным текстом.

    :param error_text: Текст ошибки, который будет отображен в окне.
    """
    # Создаем корневое окно (оно будет скрыто)
    root = tk.Tk()
    root.withdraw()  # Скрываем корневое окно

    # Показываем окно ошибки
    messagebox.showerror(name_error, error_text)

    # Завершаем работу tkinter
    root.destroy()
