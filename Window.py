# -*- coding: utf-8 -*-
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.ticker
import numpy as np
import sympy as sp
import re
from scipy.integrate import cumtrapz
from scipy import interpolate
import scipy as scp
from scipy.ndimage import uniform_filter1d
from scipy.signal import argrelextrema
#Собственные библиотеки
from Math_functions import to_function, extract_special_functions
from GUI_interface import error
from Graphicks import Grafick, convert_data, Cursor
from PIL import Image
import tkinter as tk
from tkinter import colorchooser
import copy
import easygui as eg
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))



class Window:
    def __init__(self, notebook, names, create_fun, default_params, title="Graphick", title_c='', title_x='', title_y='', polar_test=0, x_log='linear', y_log='linear'):
            
        #Создание рабочей рамки
        self.frame = ctk.CTkFrame(notebook)
        notebook.add(self.frame, text=title)
        notebook.pack(expand=1, fill='both')
        
        #Список переменных окна
        self.params = copy.deepcopy(default_params)
        #self.params["scale"] = [-10, -6, 10, 6]
        self.names = names
        self.title = title
        self.can_lab = title_c
        self.can_labx = title_x
        self.can_laby = title_y
        
        #Список дополнительных виджетов
        self.cx1 = None
        self.cx2 = None
        self.cy1 = None
        self.cy2 = None
        
        self.legend = 0
        
        self.x0_log = x_log
        self.y0_log = y_log
        
        self.polar_ax = polar_test
        self.p_l_x0 = default_params["scale"][0]
        self.p_l_x1 = default_params["scale"][2]
        self.p_l_y0 = default_params["scale"][1]
        self.p_l_y1 = default_params["scale"][3]
        
        #Путь к сохранённому файлу
        self.save_file = ""
        
        if self.polar_ax:
            self.create_polar_scale(self.p_l_y0, self.p_l_y1, self.p_l_x0, self.p_l_x1, self.can_lab, self.can_labx, self.can_laby)
        else:
            self.create_linear_scale(self.p_l_x0, self.p_l_x1, self.p_l_y0, self.p_l_y1, self.can_lab, self.can_labx, self.can_laby)

        #Древо графиков
        self.entry_frame = ctk.CTkScrollableFrame(self.frame, height=700, width=350)
        self.entry_frame.place(x=0, y=0)
        self.fields_tree = Input_String(self.entry_frame, names["String_names"], ax=self.ax, canvas=self.canvas, params=default_params["default_params_string"])
        self.fields_tree.create_graph_in_new_win = create_fun
        self.fields_tree.legend_draw = self.legend_repaint
        self.fields_tree.paront_win = self
        
      
    def x_change_lab(self, event):
        x = self.ax.get_xlim()
        self.str_x0.delete(0, "end")
        self.str_x1.delete(0, "end")
        self.str_x0.insert(0, str(x[0]))
        self.str_x1.insert(0, str(x[1]))
        self.params["scale"][0] = x[0]
        self.params["scale"][2] = x[1]
        
    def y_change_lab(self, event):
        y = self.ax.get_ylim()
        self.str_y0.delete(0, "end")
        self.str_y1.delete(0, "end")
        self.str_y0.insert(0, str(y[0]))
        self.str_y1.insert(0, str(y[1]))
        self.params["scale"][1] = y[0]
        self.params["scale"][3] = y[1]

    def scale_changed(self, event):
        x0, x1 = self.str_x0.get(), self.str_x1.get()
        y0, y1 = self.str_y0.get(), self.str_y1.get()
        x0, x1 = convert_data(x0), convert_data(x1)
        y0, y1 = convert_data(y0), convert_data(y1)
        
        if np.isnan(x0):
            x0 = self.ax.get_xlim()[0]
            
        if np.isnan(y0):
            y0 = self.ax.get_ylim()[0]
            
        if np.isnan(x1):
            x1 = self.ax.get_xlim()[1]
            
        if np.isnan(y1):
            y1 = self.ax.get_ylim()[1]
        

        self.ax.set_xlim(x0, x1)
        self.ax.set_ylim(y0, y1)
        self.params["scale"] = [x0, y0, x1, y1]
        self.fields_tree.repaint()
        self.canvas.draw()
        
    def x0_right_event(self, event):
        if self.str_x0.index("insert") == len(self.str_x0.get()): 
            self.str_x1.focus()

    def x1_right_event(self, event):
        if self.str_x1.index("insert") == len(self.str_x1.get()): 
            self.str_y0.focus()
            
    def y0_right_event(self, event):
        if self.str_y0.index("insert") == len(self.str_y0.get()): 
            self.str_y1.focus()
            
    def y1_left_event(self, event):
        if self.str_y1.index("insert") == 0: 
            self.str_y0.focus()
            
    def y0_left_event(self, event):
        if self.str_y0.index("insert") == 0: 
            self.str_x1.focus()
            
    def x1_left_event(self, event):
        if self.str_x1.index("insert") == 0: 
            self.str_x0.focus()
            
    def legend_include(self):
        if self.legend:
            self.legend.remove()
            self.legend = 0
        else:
            test1, test2 = self.fields_tree.leg_find([], [])
            self.legend = self.ax.legend(test1, test2, loc="upper right")
            self.legend.set_draggable(True)
        self.canvas.draw()
        
    def legend_repaint(self):
        if self.legend:
            self.legend.remove()
            test1, test2 = self.fields_tree.leg_find([], [])
            self.legend = self.ax.legend(test1, test2, loc="upper right")
            self.legend.set_draggable(True)
        self.canvas.draw()
        
    def add_x_cursors(self):
        def sig(event):
            if event.xdata != None and self.cx1 != None:
                if event.button == plt.MouseButton.LEFT:
                    self.cx1.step(event.xdata)
                    self.cx2.step(event.xdata)
                    self.canvas.draw()
                        
        
        def rule(event):
            if event.xdata != None and self.cx1 != None:
                if (abs(event.xdata - self.cx1.x) <= abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0])/100) and (event.button == plt.MouseButton.LEFT):
                    self.cx1.active = 1
                    self.cx2.active = 0
                elif (abs(event.xdata - self.cx2.x) <= abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0])/100) and (event.button == plt.MouseButton.LEFT):
                    self.cx2.active = 1
                    self.cx1.active = 0
                else:
                    self.cx1.active = 0
                    self.cx2.active = 0
                       
        def cx(event):
            if self.cx1 != None:
                self.fields_tree.curs_x_translate(self.cx1.x, self.cx2.x)

        if self.cx1 == None:
            self.cx1 = Cursor(self.ax, x=(self.ax.get_xlim()[1] - abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0])/10))
            self.cx2 = Cursor(self.ax, x=(self.ax.get_xlim()[0] + abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0])/10))
            self.canvas.mpl_connect('motion_notify_event', sig)
            self.canvas.mpl_connect('button_press_event', rule)
            self.canvas.mpl_connect('button_release_event', cx)
            self.fields_tree.curs_x_translate(self.cx1.x, self.cx2.x)
        else:
            self.cx1.remove()
            self.cx2.remove()
            self.cx1 = None
            self.cx2 = None
            self.fields_tree.curs_x_translate(None, None)
        self.canvas.draw()
    
    def add_y_cursors(self):
        def sig(event):
            if event.ydata != None and self.cy1 != None:
                if event.button == plt.MouseButton.LEFT:
                    self.cy1.step(event.ydata)
                    self.cy2.step(event.ydata)
                    self.canvas.draw()
                        
        
        def rule(event):
            if event.ydata != None and self.cy1 != None:
                if (abs(event.ydata - self.cy1.x) <= abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])/100) and (event.button == plt.MouseButton.LEFT):
                    self.cy1.active = 1
                    self.cy2.active = 0
                elif (abs(event.ydata - self.cy2.x) <= abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])/100) and (event.button == plt.MouseButton.LEFT):
                    self.cy2.active = 1
                    self.cy1.active = 0
                else:
                    self.cy1.active = 0
                    self.cy2.active = 0
                       
        def cx(event):
            if self.cy1 != None:
                self.fields_tree.curs_y_translate(self.cy1.x, self.cy2.x)

        if self.cy1 == None:
            self.cy1 = Cursor(self.ax, x=(self.ax.get_ylim()[1] - abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])/10), vert=False, polar=self.polar_ax)
            self.cy2 = Cursor(self.ax, x=(self.ax.get_ylim()[0] + abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])/10), vert=False, polar=self.polar_ax)
            self.canvas.mpl_connect('motion_notify_event', sig)
            self.canvas.mpl_connect('button_press_event', rule)
            self.canvas.mpl_connect('button_release_event', cx)
            self.fields_tree.curs_y_translate(self.cy1.x, self.cy2.x)
        else:
            self.cy1.remove()
            self.cy2.remove()
            self.cy1 = None
            self.cy2 = None
            self.fields_tree.curs_y_translate(None, None)
        self.canvas.draw()
        
    def polar(self):
        self.polar_ax = not self.polar_ax
        if self.polar_ax:
            self.p_l_x0, self.p_l_x1 = self.ax.get_xlim()[0], self.ax.get_xlim()[1]
            self.p_l_y0, self.p_l_y1 = self.ax.get_ylim()[0], self.ax.get_ylim()[1]
            
            r0 = 0
            r1 = max(abs(self.p_l_y0), abs(self.p_l_y1))
            f0 = 0
            f1 = 2*np.pi
            
            title = self.ax.get_title()
            x_title = self.ax.get_xlabel()
            y_title = self.ax.get_ylabel()

            self.ax.clear()
            self.ax.remove()
            self.toolbar.destroy()

            self.canvas.get_tk_widget().destroy()  # Удаляем виджет канваса

            plt.close(self.fig)  # Закрываем фигуру
            del self.fig
            
            self.create_polar_scale(r0, r1, f0, f1, title, x_title, y_title)
            
            self.fields_tree.repaint(self.ax, self.canvas)
        else:
            x0, x1 = self.p_l_x0, self.p_l_x1
            y0, y1 = self.p_l_y0, self.p_l_y1
            
            title = self.ax.get_title()
            x_title = self.ax.get_xlabel()
            y_title = self.ax.get_ylabel()

            self.ax.clear()
            self.ax.remove()
            self.toolbar.destroy()

            self.canvas.get_tk_widget().destroy()  # Удаляем виджет канваса

            plt.close(self.fig)  # Закрываем фигуру
            del self.fig
            
            self.create_linear_scale(x0, x1, y0, y1, title, x_title, y_title)
            self.entry_frame.lift()
            
            self.fields_tree.repaint(self.ax, self.canvas)
            
        self.legend_repaint()
        
    def create_linear_scale(self, x0, x1, y0, y1, title='', x_title='', y_title=''):
        #Создание рабочей области
        self.fig = Figure(figsize=(12.6, 7.2))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().place(relx=0.2, rely=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        self.ax.grid(which='minor', linestyle=':')
        #grid_stepx = 1
        #grid_stepy = 1 # Шаг сетки
        #self.ax.set_xticks(np.arange(x0 - np.sign(x0)*x0*10, x1 + np.sign(x1)*x1*10 + grid_stepx, grid_stepx))  # Сетка по x
        #self.ax.set_yticks(np.arange(y0 - np.sign(y0)*y0*10, y1 + np.sign(y1)*y1*10 + grid_stepy, grid_stepy))  # Сетка по y
        if self.params["maj_ax"]:
            self.ax.grid(which='major')
        if self.params["min_ax"]:
            self.ax.minorticks_on()
        formatter = matplotlib.ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-3, 5))
        formatter2 = matplotlib.ticker.ScalarFormatter(useMathText=True)
        formatter2.set_powerlimits((-2, 4))
        self.ax.xaxis.set_major_formatter(formatter)
        self.ax.yaxis.set_major_formatter(formatter2)
        
        if not (self.x0_log == "linear"):
            self.ax.set_xscale('log')
            self.ax.set_xlim(1, x1)
        else:
            self.ax.set_xlim(x0, x1)
            
        if not (self.y0_log == "linear"):
            self.ax.set_yscale('log')
            self.ax.set_ylim(1, y1)
        else:
            self.ax.set_ylim(y0, y1)
        
        self.ax.set_title(title, fontsize=26)
        self.ax.set_ylabel(y_title, fontsize=14)
        self.ax.set_xlabel(x_title, fontsize=14)
        
        #Отслеживание изменения масштаба и сдвига осей
        self.canvas.mpl_connect('button_release_event', lambda event: self.fields_tree.repaint())
        #Виджет изменения масштаба
        ctk.CTkLabel(self.toolbar, text="x: ", font=("Times", 14)).place(relx=0.3, rely=0)
        ctk.CTkLabel(self.toolbar, text="y: ", font=("Times", 14)).place(relx=0.7, rely=0)
        
        self.str_x0 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_x0.place(relx=0.31, rely=0)
        self.str_x0.bind('<Right>', self.x0_right_event)
        self.str_x0.bind('<Return>', self.scale_changed)
        
        self.str_x1 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_x1.place(relx=0.35, rely=0)
        self.str_x1.bind('<Right>', self.x1_right_event)
        self.str_x1.bind('<Left>', self.x1_left_event)
        self.str_x1.bind('<Return>', self.scale_changed)
        
        self.str_y0 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_y0.place(relx=0.71, rely=0)
        self.str_y0.bind('<Right>', self.y0_right_event)
        self.str_y0.bind('<Left>', self.y0_left_event)
        self.str_y0.bind('<Return>', self.scale_changed)
        
        self.str_y1 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_y1.place(relx=0.75, rely=0)
        self.str_y1.bind('<Left>', self.y1_left_event)
        self.str_y1.bind('<Return>', self.scale_changed)
        
        self.ax.callbacks.connect('xlim_changed', self.x_change_lab)
        self.ax.callbacks.connect('ylim_changed', self.y_change_lab)
        
        self.ax.set_xlim(x0, x1)
        self.ax.set_ylim(y0, y1)
        
        del self.cx1, self.cx2
        del self.cy1, self.cy2
        
        self.cx1 = None
        self.cx2 = None
        self.cy1 = None
        self.cy2 = None
        
        self.canvas.draw()
    
    def create_polar_scale(self, r0, r1, f0, f1, title='', x_title='', y_title=''):
        #Создание рабочей области
        self.fig = Figure(figsize=(7.2, 7.2))
        self.ax = self.fig.add_subplot(111, projection="polar")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().place(relx=0.4, rely=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        self.ax.grid(which='minor', linestyle=':')
        #grid_stepx = 1
        #grid_stepy = 1 # Шаг сетки
        #self.ax.set_xticks(np.arange(x0 - np.sign(x0)*x0*10, x1 + np.sign(x1)*x1*10 + grid_stepx, grid_stepx))  # Сетка по x
        #self.ax.set_yticks(np.arange(y0 - np.sign(y0)*y0*10, y1 + np.sign(y1)*y1*10 + grid_stepy, grid_stepy))  # Сетка по y
        if not self.params["maj_ax"]:
            self.ax.grid(which='major')
        if self.params["min_ax"]:
            self.ax.minorticks_on()
        formatter = matplotlib.ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-3, 5))
        formatter2 = matplotlib.ticker.ScalarFormatter(useMathText=True)
        formatter2.set_powerlimits((-2, 4))
        self.ax.xaxis.set_major_formatter(formatter)
        self.ax.yaxis.set_major_formatter(formatter2)
        
        self.ax.set_rlim(r0, r1)
        if not (self.y0_log == "linear"):
            self.ax.set_yscale('log')
            self.ax.set_ylim(1, r1)
        else:
            self.ax.set_thetalim(f0, f1)
        
        self.ax.set_title(title, fontsize=26)
        self.ax.set_ylabel(y_title, fontsize=14, labelpad=30)
        self.ax.set_xlabel(x_title, fontsize=14)
        
        #Отслеживание изменения масштаба и сдвига осей
        self.canvas.mpl_connect('button_release_event', lambda event: self.fields_tree.repaint())
        #Виджет изменения масштаба
        ctk.CTkLabel(self.toolbar, text="fi: ", font=("Times", 14)).place(relx=0.3, rely=0)
        ctk.CTkLabel(self.toolbar, text="r: ", font=("Times", 14)).place(relx=0.7, rely=0)
        
        self.str_x0 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_x0.place(relx=0.31, rely=0)
        self.str_x0.bind('<Right>', self.x0_right_event)
        self.str_x0.bind('<Return>', self.scale_changed)
        
        self.str_x1 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_x1.place(relx=0.35, rely=0)
        self.str_x1.bind('<Right>', self.x1_right_event)
        self.str_x1.bind('<Left>', self.x1_left_event)
        self.str_x1.bind('<Return>', self.scale_changed)
        
        self.str_y0 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_y0.place(relx=0.71, rely=0)
        self.str_y0.bind('<Right>', self.y0_right_event)
        self.str_y0.bind('<Left>', self.y0_left_event)
        self.str_y0.bind('<Return>', self.scale_changed)
        
        self.str_y1 = ctk.CTkEntry(self.toolbar, font=("Times", 14), width=50)
        self.str_y1.place(relx=0.75, rely=0)
        self.str_y1.bind('<Left>', self.y1_left_event)
        self.str_y1.bind('<Return>', self.scale_changed)
        
        self.ax.callbacks.connect('xlim_changed', self.x_change_lab)
        self.ax.callbacks.connect('ylim_changed', self.y_change_lab)
        
        self.ax.set_rlim(r0, r1)
        self.ax.set_thetalim(f0, f1)
        
        del self.cx1, self.cx2
        del self.cy1, self.cy2
        
        self.cx1 = None
        self.cx2 = None
        self.cy1 = None
        self.cy2 = None
        
        self.canvas.draw()
        
    def update(self):
        if self.cx1 != None:
            self.cx1.ax, self.cx1.canvas = self.ax, self.canvas
            self.cx1.remove()
            self.cx1.paint()
        if self.cx2 != None:
            self.cx2.ax, self.cx2.canvas = self.ax, self.canvas
            self.cx2.remove()
            self.cx2.paint()
        if self.cy1 != None:
            self.cy1.ax, self.cy1.canvas = self.ax, self.canvas
            self.cy1.remove()
            self.cy1.paint()
        if self.cy2 != None:
            self.cy2.ax, self.cy2.canvas = self.ax, self.canvas
            self.cy2.remove()
            self.cy2.paint()
        
        self.legend_repaint()
        

class Input_String:
    def __init__(self, frame, names, ax, canvas, params, i=0):
        
        #Основные переменные окна
        self.frame = frame
        self.i = i
        self.params = copy.deepcopy(params)
        self.ax = ax
        self.canvas = canvas
        self.names = names
        
        #Ссылка на предыдущие и следующие строки дерева
        self.next_string = 0
        self.prev_string = 0
        
        #Переменные виджетов
        self.color = self.params[1]
        self.title_f = "f" + str(i)
        
        self.graf = 0
        self.func = 0
        self.func3d = 0
        self.func_link = 0
        
        #Дополнительные виджеты для корректной работы ссылочной системы
        self.links = []
        self.x_datas = 0
        self.test_datas = False
        
        #Дополнительные виджеты для обработки
        self.spec_link = 0
        self.spec_func = 0
        self.create_graph_in_new_win = None
        self.visialize_annotates = False
        
        #Хуй пойми зачем эта херь, но надо
        self.paront_win = None
        
        #Местоположение курсоров
        self.cx1 = None
        self.cx2 = None
        self.cy1 = None
        self.cy2 = None
        
        #Всплывающее меню обработки
        menu_proccess = tk.Menu(tearoff=0)
        menu_proccess.add_command(label=self.names["Gradient"], command=self.create_grad)
        menu_proccess.add_command(label=self.names["Antiderivative"], command=self.create_antider)
        menu_proccess.add_command(label=self.names["Swap_axes"], command=self.swap_ax)
        menu_proccess.add_separator()
        menu_proccess.add_command(label=self.names["Fourier"], command=self.create_fourier)
        menu_proccess.add_command(label=self.names["Fourier_reverse"], command=self.create_fourier_reverse)
        menu_proccess.add_command(label=self.names["Laplas"])
        menu_proccess.add_command(label=self.names["Convolution"])
        menu_proccess.add_separator()
        menu_proccess.add_command(label=self.names["Savitsky-Halley_filter"], command=self.saviet_halley_filter)
        menu_proccess.add_command(label=self.names["Running_average"], command=self.run_average)
        menu_proccess.add_separator()
        menu_proccess.add_command(label=self.names["Fitting"], command=self.fitting)
        menu_proccess.add_command(label=self.names["Draw_tangent"], command=self.tangent)
        menu_proccess.add_separator()
        menu_proccess.add_command(label=self.names["Search_peaks"], command=self.find_peaks)
        menu_proccess.add_command(label=self.names["Auto_substrate"], command=self.auto_substrate)
        menu_proccess.add_command(label=self.names["Lissagu"], command=self.lissagu)
        menu_proccess.add_separator()
        menu_proccess.add_separator()
        menu_proccess.add_command(label=self.names["Save_txt"], command=self.save_txt)
        menu_proccess.add_command(label=self.names["Save_npy"], command=self.save_npy)
        
        #Строка
        self.string = ctk.CTkEntry(frame)
        self.string.grid(column=1, row=i)
        self.string.bind('<Return>', self.add)
        self.string.bind('<Down>', self.down_string)
        self.string.bind('<Up>', self.up_string)
        self.string.bind('<Button-3>', lambda event: menu_proccess.post(event.x_root, event.y_root))
        
        ICON_PATH_del = os.path.join(BASE_DIR, "delete_sett_w.png")
        ICON_PATH_set = os.path.join(BASE_DIR, "paint_sett_w.png")
        ICON_PATH_scale = os.path.join(BASE_DIR, "scale_sett.png")

        #Кнопка удаления
        image_del = ctk.CTkImage(light_image=Image.open(ICON_PATH_del)) #, dark_image=Image.open("delete_sett_d.png")
        self.del_button = ctk.CTkButton(frame, width=28, text=None, image=image_del, fg_color="transparent", command=self.delete_str)
        self.del_button.grid(column=5, row=i)
        
        #Выбор цвета
        self.col = tk.Canvas(self.frame, bg=self.color, width=15, height=15)
        self.col.grid(column=0, row=i)
        self.col.bind('<Button-1>', self.color_get)
        
        #Кнопка настроек
        image_set = ctk.CTkImage(light_image=Image.open(ICON_PATH_set)) #, dark_image=Image.open("paint_sett_d.png")
        self.sett_button = ctk.CTkButton(frame, width=28, image=image_set, text=None, fg_color="transparent", command=self.sett_str)
        self.sett_button.grid(column=2, row=i)
        
        #Кнопка масштабирования
        image_scale = ctk.CTkImage(light_image=Image.open(ICON_PATH_scale)) #, dark_image=Image.open("paint_sett_d.png")
        self.scale_button = ctk.CTkButton(frame, width=28, image=image_scale, text=None, fg_color="transparent", command=self.changed_scale)
        self.scale_button.grid(column=3, row=i)
        
        #Кнопка видимости 4
        self.visible_button = ctk.CTkCheckBox(frame, width=28, text=None, command=self.graph_visible)
        self.visible_button.grid(column=4, row=i)
        

    #Функции дерева
    #Сдвигает всё дерево наверх
    def up(self):
        if self.i > 0:
            self.string.grid(column=1, row=self.i-1)
            self.col.grid(column=0, row=self.i-1)
            self.del_button.grid(column=5, row=self.i-1)
            self.visible_button.grid(column=4, row=self.i-1)
            self.sett_button.grid(column=2, row=self.i-1)
            self.scale_button.grid(column=3, row=self.i-1)
            self.i = self.i - 1
            if self.next_string:
                self.next_string.up()    
                
    def delete_str(self):
        if self.graf:
            self.graf.remove()
            self.graf = 0
        if self.next_string:
            self.string.destroy()
            self.del_button.destroy()
            self.col.destroy()
            self.sett_button.destroy()
            self.scale_button.destroy()
            self.visible_button.destroy()
            if self.prev_string:
                self.prev_string.next_string = self.next_string
                self.next_string.prev_string = self.prev_string
            else:
                self.next_string.prev_string = 0
                self.paront_win.fields_tree = self.next_string

            self = self.next_string
            self.up()
        else:
            if self.string.get() == "":
                return
            self.add_string()
            self.string.destroy()
            self.del_button.destroy()
            self.col.destroy()
            self.sett_button.destroy()
            self.scale_button.destroy()
            self.visible_button.destroy()
            if self.prev_string:
                self.prev_string.next_string = self.next_string
                self.next_string.prev_string = self.prev_string
            else:
                self.next_string.prev_string = 0
                self.paront_win.fields_tree = self.next_string

            self = self.next_string
            self.up()
            
        self.paront_win.legend_repaint()
        
    def repaint(self, ax=0, canvas=0):
        if ax:
            self.ax = ax
            self.canvas = canvas
            
        if self.graf:
            self.graf.ax = self.ax
            self.graf.canvas = self.canvas
            if self.func:
                scal_x0, scal_x1 = self.ax.get_xlim()[0], self.ax.get_xlim()[1]
                x = np.linspace(scal_x0 - 10*abs(scal_x0), scal_x1 + 10*abs(scal_x1), 10000)
                y = self.func(x)
            elif self.func_link:
                if type(self.x_datas) != int:
                    x = self.x_datas
                else:
                    if not self.links[0].graf:
                        error(self.names["Error_name"])
                        return
                    x = self.links[0].graf.x

                y = [x]
                    
                for lnk in self.links:
                    if not lnk.graf:
                        error(self.names["Error_name"])
                        return
                    if lnk.func:
                        y.append(lnk.func(x))
                    else:
                        y.append(lnk.graf.y)
                
                y = self.func_link(*y)
            elif self.spec_link:
                if type(self.x_datas) != int:
                    x = self.x_datas
                else:
                    if not self.links[0].graf:
                        error(self.names["Error_name"])
                        return
                    x = self.links[0].graf.x
                    
                y_all = [x]
                for lnk in self.links:
                    if not lnk.graf:
                        error(self.names["Error_name"])
                    if lnk.func:
                        y_all.append(lnk.func(x))
                    else:
                        y_all.append(lnk.graf.y)
                
                y = extract_special_functions(self.spec_link[0], y_all, self.spec_link[1])
                x = y_all[0]
                

                if type(y) != np.ndarray and type(y) != int and type(y) != float and type(y) != complex:
                    error(self.names["Error_input"])
                    return
            elif self.spec_func:
                scal_x0, scal_x1 = self.ax.get_xlim()[0], self.ax.get_xlim()[1]
                x = np.linspace(scal_x0 - 10*abs(scal_x0), scal_x1 + 10*abs(scal_x1), 10000)
                x = [x]
                y = extract_special_functions(self.string.get(), x)
                x = x[0]
                if type(y) != np.ndarray and type(y) != int and type(y) != float and type(y) != complex:
                    error(self.names["Error_input"])
                    self.spec_func = 0
                    self.graf.remove()
                    self.graf = 0
                    return
            else:
                return
            if type(y) != np.ndarray:
                y0 = y
                y = np.array([y0])
                y.resize(x.shape)
                y.fill(y0)
            self.graf.x = x
            self.graf.y = y
            self.graf.repaint(sett=self.graf.sett)
            if not self.visible_button.get():
                self.graf.hide(0)
        if self.paront_win.cx1 != None:
            self.paront_win.cx1.remove()
            self.paront_win.cx1.paint()
        if self.paront_win.cx2 != None:
            self.paront_win.cx2.remove()
            self.paront_win.cx2.paint()
        if self.paront_win.cy1 != None:
            self.paront_win.cy1.remove()
            self.paront_win.cy1.paint()
        if self.paront_win.cy2 != None:
            self.paront_win.cy2.remove()
            self.paront_win.cy2.paint()
        if self.next_string:
            self.next_string.repaint(ax, canvas)
            
    def add_string(self):
        if self.string.get() == "":
            return self
        elif self.next_string:
            return self.next_string.add_string()
        else:
            self.next_string = Input_String(self.frame, self.names, self.ax, self.canvas, params=self.params, i=self.i+1)
            self.next_string.prev_string = self
            self.next_string.create_graph_in_new_win = self.create_graph_in_new_win
            self.next_string.paront_win = self.paront_win
            return self.next_string
    
    
    #Функции комбинаций клавиш
    def add(self, event=0, add_s=1):
        string = self.string.get()
                    
        if not ("\"" in string or string == ""):
            if self.graf:
                self.graf.remove()
                self.graf = 0
                self.visible_button.deselect()
                
            if "; " in string:
                string = string.replace("[", "")
                string = string.replace("]", "")
                lst = string.split("; ")
                if len(lst) == 2:
                    if lst[0][0] == "(":
                        lst[0] = lst[0][1:len(lst[0])-1]
                    ls1 = lst[0].split(", ")
                    ls2 = lst[1].split(", ")
                    if len(ls1) == 2 and len(ls2) == 2:
                        try:
                            x = to_function(ls1[0])(np.nan)
                            y = to_function(ls1[1])(np.nan)
                            dx = to_function(ls2[0])(np.nan)
                            dy = to_function(ls2[1])(np.nan)
                        except:
                            error(self.names["Error_input"])
                            return
                        if dx == 0:
                            dx = np.nan
                        if dy == 0:
                            dy = np.nan
                        if (type(x) != int and type(x) != float and type(x) != complex) or (type(y) != int and type(y) != float and type(y) != complex):
                            error(self.names["Error_input"])
                            return
                        elif (type(dx) == int or type(dx) == float or type(dx) == complex) and (type(dy) == int or type(dy) == float or type(dy) == complex):
                            g = Grafick(np.array([x]), np.array([y]), self.ax, self.canvas, np.array([dx]), np.array([dy]), test=True)
                            g.color = self.color
                            g.show()
                            self.graf = g
                        elif (type(x) != int and type(x) != float and type(x) != complex) and (type(dy) == int or type(dy) == float or type(dy) == complex):
                            g = Grafick(np.array([x]), np.array([y]), self.ax, self.canvas, dy=np.array([dy]), test=True)
                            g.color = self.color
                            g.show()
                            self.graf = g
                        else:
                            g = Grafick(np.array([x]), np.array([y]), self.ax, self.canvas, np.array([dx]), test=True)
                            g.color = self.color
                            g.show()
                            self.graf = g
                    elif len(ls1) == 2 and len(ls2) == 1:
                        try:
                            x = to_function(ls1[0])(np.nan)
                            y = to_function(ls1[1])(np.nan)
                            dy = to_function(ls2[0])(np.nan)
                        except:
                            error(self.names["Error_input"])
                            return
                        if dy == 0:
                            dy = np.nan
                        if x == None or y == None or dy == None:
                            error(self.names["Error_input"])
                            return
                        else:
                            g = Grafick(np.array([x]), np.array([y]), self.ax, self.canvas, dy=np.array([dy]), test=True)
                            g.color = self.color
                            g.show()
                            self.graf = g
                    else:
                        error(self.names["Error_input"])
                        return
            elif ", " in string:
                if string[0] == "(":
                    string = string[1:len(string)-1]
                lst = string.split(", ")
                if len(lst) == 2:
                    try:
                        x = to_function(lst[0])(np.nan)
                        y = to_function(lst[1])(np.nan)
                    except:
                        error(self.names["Error_input"])
                        return
                    if (type(x) != int and type(x) != float and type(x) != complex) or (type(y) != int and type(y) != float and type(y) != complex):
                        error(self.names["Error_input"])
                        return
                    else:
                        g = Grafick(np.array([x]), np.array([y]), ax=self.ax, canvas=self.canvas, test=True)
                        g.color = self.color
                        g.show()
                        
                        self.graf = g
                else:
                    error(self.names["Error_input"])
                    return
            elif "&" in string:
                st = string.replace(" ", "")
                
                if '=' in st:
                    error(self.names["Error_mult_link_func"])
                    return
                
                list_f = st.split("&")
                if "" in list_f:
                    list_f.remove("")
                    
                l = len(list_f)
                    
                x_datas = 0
                x_test_d = 0
                test = False
                graf = 0
                dictionary_links = []

                all_strings = ""
                all_variables = "x "

                if st[0] == "&":
                    start = 0
                else:
                    start = 1
                    all_strings += list_f[0]
                    
                for l_f in range(start, l):
                    link, num_f = self.give_link(list_f[l_f])
                    if not link:
                        return
                    if not link.graf:
                        error(self.names["Error_nothing_graph"])
                        return
                    
                    if type(link.x_datas) != int:
                        x_test_d = link.x_datas
                        test = link.test_datas
                    elif link.func or link.func_link or link.spec_func or link.spec_link:
                        x_datas = link.graf.x
                    else:
                       if type(x_test_d) == int:
                           x_test_d = link.graf.x
                           test = link.graf.test
                           graf = link.graf
                       else:
                           if x_test_d.shape != link.graf.x.shape:
                               error(self.names["Error_differenf_size"])
                               return

                    all_variables += "variables_" + str(l_f) + " "
                    all_strings += "variables_" + str(l_f) + list_f[l_f][num_f:]
                    
                    dictionary_links.append(link)
                    
                if type(x_test_d) != int:
                    self.x_datas = x_test_d
                    self.test_datas = test
                    x_datas = x_test_d
                    
                dict_y = [x_datas]
                self.links = dictionary_links
                for lnk in dictionary_links:
                    if lnk.func:
                        dict_y.append(lnk.func(x_datas))
                    else:
                        dict_y.append(lnk.graf.y)
                        
                if "#" in string:
                    y_datas = extract_special_functions(all_strings, dict_y, all_variables)

                    if type(y_datas) != np.ndarray and type(y_datas) != int and type(y_datas) != float and type(y_datas) != complex:
                        error(self.names["Error_input"])
                        return

                    self.spec_link = (all_strings, all_variables)
                else:
                    function_links = to_function(all_strings, var=all_variables)
                    try:
                        y_datas = function_links(*dict_y)
                        if type(y_datas) != np.ndarray:
                            y0 = y_datas
                            y_datas = np.array([y0])
                            y_datas.resize(x_datas.shape)
                            y_datas.fill(y0)
                    except:
                        error(self.names["Error_input"])
                        return
                
                    if type(y_datas) != np.ndarray and type(y_datas) != int and type(y_datas) != float and type(y_datas) != complex:
                        error(self.names["Error_input"])
                        return
                
                    self.func_link = function_links

                x_datas = dict_y[0]
                g = Grafick(x_datas, y_datas, ax=self.ax, canvas=self.canvas, test=test)
                if not graf:
                    graf = dictionary_links[0].graf
                g.point = graf.point
                g.line = graf.line
                g.color = self.color
                g.width = graf.width
                g.capsize = graf.capsize
                g.d = graf.d
                try:
                    g.show(graf.sett)
                    g.leg_label = st
                    self.graf = g
                except:
                    error(self.names["Error_input"])
                    self.spec_link = 0
                    self.func_link = 0
                    self.graf = 0
                    return
            else:
                scal_x0, scal_x1 = self.ax.get_xlim()[0], self.ax.get_xlim()[1]
                if "=" in string:
                    if '#' in string:
                        error(self.names["Error_spec_func_in_seq"])
                        return
                    stl = string.split("=")
                    if len(stl) > 2:
                        error(self.names["Error_more_eq"])
                        return
                    
                    string = stl[0] + "-" + "(" + stl[1] + ")"
                    x = np.linspace(scal_x0, scal_x1, 5000)
                    y = np.linspace(self.ax.get_ylim()[0], self.ax.get_ylim()[1], 5000)
                    x, y = np.meshgrid(x, y)

                    func = to_function(string, "x y")
                    try:
                        z = func(x, y)
                    except:
                        error(self.names["Error_input"])
                        return
                    
                    if type(z) != np.ndarray and type(z) != int and type(z) != float and type(z) != complex:
                        error(self.names["Error_input"])
                        return

                    # Получаем контур и извлекаем точки
                    contour = plt.contour(x, y, z, levels=[0])
                    paths = contour.collections[0].get_paths()

                    # Собираем все точки контура
                    xy = np.vstack([path.vertices for path in paths])
                    x_contour, y_contour = xy[:, 0], xy[:, 1]

                    g = Grafick(x_contour, y_contour, self.ax, self.canvas)
                    g.color = self.color
                    g.leg_label = string
                    try:
                        g.show(sett=[0, 1, 0])

                        self.graf = g
                        self.func3d = func
                    except:
                        error(self.names["Error_input"])
                        self.graf = 0
                        self.func3d = 0
                        return
                else:
                    x = np.linspace(scal_x0 - 10*abs(scal_x0), scal_x1 + 10*abs(scal_x1), 10000)
                    if "#" in string:
                        x = [x]
                        y = extract_special_functions(string, x)
                        if type(y) != np.ndarray and type(y) != int and type(y) != float and type(y) != complex:
                            error(self.names["Error_input"])
                            return
                        self.spec_func = 1
                        x = x[0]
                    else:
                        func = to_function(string)
                        try:
                            y = func(x)
                        except:
                            error(self.names["Error_input"])
                            return
                    
                        if type(y) != np.ndarray and type(y) != int and type(y) != float and type(y) != complex:
                            error(self.names["Error_input"])
                            return
                    
                        if type(y) != np.ndarray:
                            y0 = y
                            y = np.array([y0])
                            y.resize(x.shape)
                            y.fill(y0)
                        self.func = func
                        
                    g = Grafick(x, y, self.ax, self.canvas)
                    g.color = self.color
                    g.leg_label = string
                    try:
                        g.show(sett=[0, 1, 0])
                        self.graf = g
                    except:
                        error(self.names["Error_input"])
                        self.graf = 0
                        self.spec_func = 0
                        self.func = 0
                        return
                    
            if self.cx1 != None:
                self.graf.x = np.ma.masked_where(self.graf.x < self.cx1, self.graf.x)
            if self.cx2 != None:
                self.graf.x = np.ma.masked_where(self.graf.x > self.cx2, self.graf.x)
            if self.cy1 != None:
                self.graf.y = np.ma.masked_where(self.graf.y < self.cy1, self.graf.y)
            if self.cy2 != None:
                self.graf.y = np.ma.masked_where(self.graf.y > self.cy2, self.graf.y)
            self.graf.repaint(self.graf.sett)
                    
            self.visible_button.select()
            
            if self.next_string:
                self.next_string.repaint()
            
            self.paront_win.legend_repaint()
            
        if add_s:
            if not self.next_string:
                self.next_string = Input_String(self.frame, self.names, self.ax, self.canvas, params=self.params, i=self.i+1)
                self.next_string.prev_string = self
                self.next_string.create_graph_in_new_win = self.create_graph_in_new_win
                self.next_string.paront_win = self.paront_win
        
            self.down_string(0)
        
    def down_string(self, event):
        if self.next_string:
            self.next_string.string.focus()
        
    def up_string(self, event):
        if self.prev_string:
            self.prev_string.string.focus()
            

    #Функции для остальных клавиш
    def color_get(self, event):
        p = colorchooser.askcolor()[1]
        if p != None:
            self.color = p
            #self.params[1] = p
        self.col["bg"] = self.color
        if self.graf:
            self.graf.color = self.color
            self.graf.repaint(self.graf.sett)
            if not self.visible_button.get():
                self.graf.hide(0)
            self.paront_win.legend_repaint()
        
    def sett_str(self):
            root2 = tk.Toplevel(self.frame)
            root2.attributes('-toolwindow', True)
            root2.transient(self.frame)
            root2.grab_set()

            root2.wm_title(self.names["Settings"])
            root2.geometry('500x400+400+200')
            root2.iconbitmap(r'icon.ico')
            
            self.vis_line, self.vis_dot = 0, 0
            
            def dest(event=0):
                if self.graf:
                    self.graf.line = lin.get()
                    self.graf.point = dt.get()
                    self.graf.width = lin_width.get()
                    self.graf.capsize = dot_width.get()
                    sett = [0, 0, 0]
                    if lin_check.get():
                        sett[1] = 1
                    if dot_check.get():
                        sett[0] = 1
                    if visual_hist.get():
                        sett[2] = 1
                    self.graf.repaint(sett)
                    
                    if self.visialize_annotates:
                        if self.visible_button.get():
                            if vis_ann_check.get():
                                self.graf.vis_ann = True
                                self.graf.repaint(self.graf.sett)
                            else:
                                self.graf.hide(0)
                        else:
                            self.graf.hide(0)
                    else:
                        self.graf.vis_ann = False
                        self.graf.repaint(self.graf.sett)
                        
                    if not self.visible_button.get():
                        self.graf.hide(0)
                    self.paront_win.legend_repaint()
                    self.graf.leg_label = leg_label.get("1.0", "1.end")
                    self.paront_win.legend_repaint()
                self.title_f = name_string.get("1.0", "1.end")
                
                root2.destroy()
                
            def line_change(event):
                if self.vis_line:
                    self.vis_line.remove()
                    self.vis_line, = visual_line.plot([0, 1], [0.5, 0.5], color=self.color, linestyle=lin.get(), linewidth=event)
                    canvas2.draw()
                
            def dot_change(event):
                if self.vis_dot:
                    self.vis_dot.remove()
                    self.vis_dot = visual_dot.scatter(0.5, 0.5, marker=dt.get(), s=event, color=self.color)
                    canvas.draw()
                    
            def ann():
                if self.graf:
                    if self.graf.s == [] or self.graf.vis_ann:
                        self.visialize_annotates = False
                        vis_ann_check.deselect()
                    else:
                        self.visialize_annotates = True
                else:
                    self.visialize_annotates = not self.visialize_annotates
              
            lines = ["-", "--", "-.", ":"]
            dots = ["o", ".", "s", "v", "^", "8", "p", "*", "D", "d", "P", "X"]
            #Выбор типа линии
            ctk.CTkLabel(root2, text=self.names["Lines"], font=("Times", 18)).place(relx=0.1, rely=0.1)
            lin = ctk.CTkComboBox(root2, values=lines)
            lin.place(relx=0.1, rely=0.2)
            
            #Отображать линию или нет
            lin_check = ctk.CTkCheckBox(root2, text=self.names["Line"])
            lin_check.place(relx=0.4, rely=0.2)
            
            #Толщина линии
            lin_width = ctk.CTkSlider(root2, from_=0.1, to=20, command=line_change)
            lin_width.place(relx=0.6, rely=0.2)
            
            fig2 = Figure(figsize=(2, 0.2), facecolor="#f0f0f0")
            visual_line = fig2.add_subplot(111, frame_on=False)
            visual_line.set_xticks([])  # Убираем метки осей
            visual_line.set_yticks([])
            visual_line.set_xlim(0, 1)
            visual_line.set_ylim(0, 1)
            canvas2 = FigureCanvasTkAgg(fig2, master=root2)
            canvas2.get_tk_widget().place(relx=0.6, rely=0.3)

            #Выбор типа точки
            ctk.CTkLabel(root2, text=self.names["Dotteds"], font=("Times", 18)).place(relx=0.1, rely=0.5)
            dt = ctk.CTkComboBox(root2, values=dots)
            dt.place(relx=0.1, rely=0.6)
            
            #Отображать ли точку
            dot_check = ctk.CTkCheckBox(root2, text=self.names["Point"])
            dot_check.place(relx=0.4, rely=0.6)
            
            dot_width = ctk.CTkSlider(root2, from_=0.1, to=120, command=dot_change)
            dot_width.place(relx=0.6, rely=0.6)
                
            fig = Figure(figsize=(0.2, 0.2), facecolor="#f0f0f0")
            visual_dot = fig.add_subplot(111, frame_on=False)
            visual_dot.set_xticks([])  # Убираем метки осей
            visual_dot.set_yticks([])
            visual_dot.set_xlim(0, 1)
            visual_dot.set_ylim(0, 1)
            canvas = FigureCanvasTkAgg(fig, master=root2)
            canvas.get_tk_widget().place(relx=0.775, rely=0.7)
            
            name_string = ctk.CTkTextbox(root2, width=80, height=1, font=("Times", 14))
            name_string.place(relx=0.45, rely=0.0)
            name_string.insert("1.0", self.title_f)
            
            ctk.CTkLabel(root2, text=self.names["Legend_lab"], font=("Times", 18)).place(relx=0.1, rely=0.34)
            leg_label = ctk.CTkTextbox(root2, width=80, height=1, font=("Times", 14))
            leg_label.place(relx=0.1, rely=0.4)
            
            vis_ann_check = ctk.CTkCheckBox(root2, text=self.names["Annotate"], command=ann)
            vis_ann_check.place(relx=0.4, rely=0.4)
            
            visual_hist = ctk.CTkCheckBox(root2, text=self.names["Stairs"])
            visual_hist.place(relx=0.4, rely=0.8)
            
            # ctk.CTkLabel(root2, text=self.names["Bins_count"], font=("Times", 16)).place(relx=0.1, rely=0.74)
            # visual_hist2 = ctk.CTkEntry(root2, width=70)
            # visual_hist2.place(relx=0.1, rely=0.8)
            # visual_hist2.bind('<Return>', command=dest)
            # visual_hist3 = ctk.CTkCheckBox(root2, text=self.names["With_weights"], command=hist_weights)
            # visual_hist3.place(relx=0.7, rely=0.8)
            
            if self.graf:
                lin.set(self.graf.line)
                
                if self.graf.sett[1]:
                    lin_check.select()
                else:
                    lin_check.deselect()
                    
                lin_width.set(self.graf.width)
                lin.set(self.graf.line)
                dt.set(self.graf.point)
                dot_width.set(self.graf.capsize)
                self.vis_line, = visual_line.plot([0, 1], [0.5, 0.5], color=self.graf.color, linestyle=self.graf.line, linewidth=self.graf.width)
                self.vis_dot = visual_dot.scatter(0.5, 0.5, marker=self.graf.point, s=self.graf.capsize, color=self.color)
                leg_label.insert("1.0", self.graf.leg_label)
                
                if self.graf.s != [] and self.graf.vis_ann:
                    vis_ann_check.select()
                    self.visialize_annotates = True
                
                if self.graf.sett[0]:
                    dot_check.select()
                else:
                    dot_check.deselect()
                    
                if self.graf.sett[2]:
                    visual_hist.select()
                else:
                    visual_hist.deselect()
            else:
                lin_width.set(0.8)
                dot_width.set(20)
                self.vis_line, = visual_line.plot([0, 1], [0.5, 0.5], color=self.color, linestyle=lin.get(), linewidth=0.8)
                self.vis_dot = visual_dot.scatter(0.5, 0.5, marker=dt.get(), s=20, color=self.color)
            canvas.draw()
            canvas2.draw()
                
            ctk.CTkButton(root2, text=self.names["Ok"], font=("Times", 18), command=dest).place(relx=0.4, rely=0.9)
            
    #Вспомогательные функции
    #Ищет элемент на который ссылаются
    def give_link(self, s):
        s = s.replace("+", " ")
        s = s.replace("*", " ")
        s = s.replace("-", " ")
        s = s.replace("**", " ")
        s = s.replace("^", " ")
        s = s.replace("/", " ")
        s = s.replace("(", " ")
        s = s.replace(")", " ")
        st = s.split(" ")
        s = st[0]
        link = self.find_string(s)
        if link:
            return link, len(s)
        else:
            error(self.names["Error_name"])
            return 0, 0
        
    #Находит ближайшую строку по параметру названия функции
    def find_string(self, title):
        if self.graf and title == self.title_f:
            return self
        elif self.prev_string:
            return self.prev_string.find_string(title)
        else:
            return 0
        
    #Передаёт во всё древо данные о х курсорах
    def curs_x_translate(self, x0, x1):
        if x0 != None:
            self.cx1 = min(x0, x1)
            self.cx2 = max(x1, x0)
            if self.graf:
                self.graf.x = np.ma.masked_where(np.array(self.graf.x.data) >= self.cx2, self.graf.x.data)
                self.graf.x = np.ma.masked_where(self.graf.x <= self.cx1, self.graf.x)
                self.graf.repaint(self.graf.sett)
                if not self.visible_button.get():
                    self.graf.hide(0)
        else:
            if self.graf:
                self.graf.x = self.graf.x.data
                self.graf.repaint(self.graf.sett)
                if not self.visible_button.get():
                    self.graf.hide(0)
        if self.next_string:
            self.next_string.curs_x_translate(x0, x1)
            
    #Передаёт во всё древо данные о х курсорах
    def curs_y_translate(self, y0, y1):
        if y0 != None:    
            self.cy1 = min(y0, y1)
            self.cy2 = max(y0, y1)
            if self.graf:
                self.graf.y = np.ma.masked_where(self.graf.y.data >= self.cy2, self.graf.y.data)
                self.graf.y = np.ma.masked_where(self.graf.y <= self.cy1, self.graf.y)
                self.graf.repaint(self.graf.sett)
                if not self.visible_button.get():
                    self.graf.hide(0)
        else:
            if self.graf:
                self.graf.y = self.graf.y.data
                self.graf.repaint(self.graf.sett)
                if not self.visible_button.get():
                    self.graf.hide(0)
        if self.next_string:
            self.next_string.curs_y_translate(y0, y1)
        
    #Графические функции для работы с полем
    #Масштабирует ось под график
    def changed_scale(self):
        if self.graf and not self.func and (not self.func_link or type(self.x_datas) != int):
            max_x = np.nanmax(self.graf.x)
            max_y = np.nanmax(self.graf.y)
            min_x = np.nanmin(self.graf.x)
            min_y = np.nanmin(self.graf.y)

            self.ax.set_xlim(min_x-0.1*abs(min_x), max_x + 0.1*abs(max_x))
            self.ax.set_ylim(min_y-0.1*abs(min_y), max_y + 0.1*abs(max_y))

            self.canvas.draw()
            
    #Отображает график
    def graph_visible(self):
        if self.graf:
            if self.visible_button.get() and (self.graf.sett[0] or self.graf.sett[1] or self.graf.sett[2]):
                self.graf.hide(1)
            else:
                self.graf.hide(0)
                self.visible_button.deselect()
        else:
            self.visible_button.deselect()
            
    def leg_find(self, objects, names):
        if self.graf:
            if self.graf.scatter:
                objects.append(self.graf.scatter)
                names.append(self.graf.leg_label)
            elif self.graf.plot:
                objects.append(self.graf.plot)
                names.append(self.graf.leg_label)
            elif self.graf.plot_h:
                objects.append(self.graf.plot_h)
                names.append(self.graf.leg_label)
        if self.next_string:
            return self.next_string.leg_find(objects, names)
        else:
            return objects, names
            

    #Функции преобразований графиков
    def create_grad(self):
        if self.graf:
            y = np.gradient(self.graf.y, self.graf.x)
            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(self.graf.x, y, self.ax, self.canvas, test=self.graf.test)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            if type(self.x_datas) != int:
                new_string.x_datas = self.x_datas
            
            new_string.graf = g
            new_string.string.insert(0, "#Gradient(&" + self.title_f + ")")
            new_string.spec_link = ("#Gradient(variables_1)", "x variables_1 ")
            new_string.links = [self]
            new_string.visible_button.select()
            self.paront_win.legend_repaint()
            
    def create_antider(self):
        if self.graf:
            y = cumtrapz(self.graf.y, self.graf.x, initial=0)
            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(self.graf.x, y, self.ax, self.canvas, test=self.graf.test)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            if type(self.x_datas) != int:
                new_string.x_datas = self.x_datas
            
            new_string.graf = g
            new_string.string.insert(0, "#Antider(&" + self.title_f + ")")
            new_string.spec_link = ("#Antider(variables_1)", "x variables_1 ")
            new_string.links = [self]
            new_string.visible_button.select()
            self.paront_win.legend_repaint()

    def create_fourier(self):
        """
        Неравномерное БПФ.
        """
        if self.graf:
            # Интерполяция на равномерную сетку
            f_interp = interpolate.interp1d(self.graf.x, self.graf.y, kind='cubic', fill_value='extrapolate')
            t_uniform = np.linspace(self.graf.x.min(), self.graf.x.max(), self.graf.x.shape[0])
            y_uniform = f_interp(t_uniform)
    
            # Стандартное FFT
            fft_values = np.fft.fft(y_uniform)
            freqs = np.fft.fftfreq(len(t_uniform), d=t_uniform[1]-t_uniform[0])
    
            #fft_values = np.absolute(fft_values)
            self.create_graph_in_new_win(freqs, fft_values, name_graph="\"Fourier: "+self.string.get()+"\"")
            
    def create_fourier_reverse(self):
        if self.graf:
            # Интерполяция на равномерную сетку
            df_min = np.min(np.diff(np.sort(self.graf.x)))
            t_max = 1/df_min
            t_uniform = np.linspace(0, t_max, self.graf.x.shape[0])
    
            freqs_uniform = np.linspace(self.graf.x.min(), self.graf.x.max(), self.graf.x.shape[0])
    
            # Интерполяция комплексного спектра (раздельно Re и Im)
            fft_interp_real = interpolate.interp1d(self.graf.x, self.graf.y.real, kind='cubic', fill_value=0.0, bounds_error=False)
            fft_interp_imag = interpolate.interp1d(self.graf.x, self.graf.y.imag, kind='cubic', fill_value=0.0, bounds_error=False)
    
            fft_uniform = fft_interp_real(freqs_uniform) + 1j * fft_interp_imag(freqs_uniform)
            # Стандартное FFT
            y_uniform = np.fft.ifft(np.fft.ifftshift(fft_uniform))
    
            self.create_graph_in_new_win(t_uniform, y_uniform, name_graph="\"Fourier reverse: "+self.string.get()+"\"")
            
    def saviet_halley_filter(self):
        def savgol(event=0):
            w = w_wind.get()
            n = n_wind.get()
            w, n = convert_data(w), convert_data(n)
            if w == np.nan or n == np.nan:
                error(self.names["Error_savgol_params"])
                return
            w, n = int(w), int(n)
            #Интерполяция на равномерную сетку
            f_interp = interpolate.interp1d(self.graf.x, self.graf.y, kind='cubic', fill_value='extrapolate')
            x_uniform = np.linspace(self.graf.x.min(), self.graf.x.max(), self.graf.x.shape[0])
            y_uniform = f_interp(x_uniform)
            
            y = scp.signal.savgol_filter(y_uniform, w, n)
            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(x_uniform, y, self.ax, self.canvas)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            new_string.graf = g
            new_string.string.insert(0, "\"SavgolFilter: " + self.string.get() + "\"")
            new_string.visible_button.select()
            self.paront_win.legend_repaint()
            root2.destroy()

        if self.graf:
            root2 = tk.Toplevel(self.frame)
            root2.attributes('-toolwindow', True)
            root2.transient(self.frame)
            root2.grab_set()
            
            root2.wm_title(self.names["Savgol_title"])
            root2.geometry('585x120+400+200')
            root2.iconbitmap(r'icon.ico')
            
            ctk.CTkLabel(root2, text=self.names["Savgol_params_window"], font=("Times", 18)).grid(row=0, column=0)
            ctk.CTkLabel(root2, text=self.names["Savgol_params_polinomial"], font=("Times", 18)).grid(row=0, column=1)
            
            w_wind = ctk.CTkEntry(root2, font=("Times", 18))
            w_wind.grid(row=1, column=0) 
            
            n_wind = ctk.CTkEntry(root2, font=("Times", 18))
            n_wind.grid(row=1, column=1)
            
            w_wind.bind("<Right>", lambda event: n_wind.focus())
            n_wind.bind("<Left>", lambda event: w_wind.focus())
            w_wind.bind('<Return>', savgol)
            n_wind.bind('<Return>', savgol)
            
            ctk.CTkButton(root2, text=self.names["Ok"], font=("Times", 18), command=savgol).place(relx=0.4, rely=0.7)
            
    def run_average(self):
        def rav(event=0):
            w = w_wind.get()
            w = convert_data(w)
            if w == np.nan:
                error(self.names["Error_raverage_params"])
                return
            w = int(w)
            #Интерполяция на равномерную сетку
            f_interp = interpolate.interp1d(self.graf.x, self.graf.y, kind='cubic', fill_value='extrapolate')
            x_uniform = np.linspace(self.graf.x.min(), self.graf.x.max(), self.graf.x.shape[0])
            y_uniform = f_interp(x_uniform)
            
            y = uniform_filter1d(y_uniform, size=w, mode='nearest')
            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(x_uniform, y, self.ax, self.canvas)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            new_string.graf = g
            new_string.string.insert(0, "\"RunAverage: " + self.string.get() + "\"")
            new_string.visible_button.select()
            self.paront_win.legend_repaint()
            root2.destroy()

        if self.graf:
            root2 = tk.Toplevel(self.frame)
            root2.attributes('-toolwindow', True)
            root2.transient(self.frame)
            root2.grab_set()
            root2.wm_title(self.names["RAverage_title"])
            root2.geometry('360x120+400+200')
            root2.iconbitmap(r'icon.ico')
            ctk.CTkLabel(root2, text=self.names["RAverage_params_window"], font=("Times", 18)).grid(row=0, column=0)
            
            w_wind = ctk.CTkEntry(root2, font=("Times", 18))
            w_wind.grid(row=1, column=0) 
            w_wind.bind('<Return>', rav)
            
            ctk.CTkButton(root2, text=self.names["Ok"], font=("Times", 18), command=rav).place(relx=0.3, rely=0.7)
            
    def find_peaks(self):
        if self.graf:
            i = argrelextrema(self.graf.y, np.greater)
            i2 = argrelextrema(self.graf.y, np.less)
            j = np.append(i, i2)
            
            new_string = self.add_string()
            new_string.col["bg"] = "black"
            
            x = self.graf.x[j]
            y = self.graf.y[j]

            string_ann = []
            for i in range(x.shape[0]):
                if "e" in str(x[i]):
                        x0 = str(x[i])
                        s = x0.split("e")
                        x0 = s[0] + "*10^" + s[1]
                else:
                    x0 = '%.5f' %  x[i]

                if "e" in str(y[i]):
                        y0 = str(y[i])
                        s = y0.split("e")
                        y0 = s[0] + "*10^" + s[1]
                else:
                    y0 = '%.5f' %  y[i]

                string_ann.append("(" + x0 + ", " + y0 + ")")
            
            g = Grafick(x, y, self.ax, self.canvas, s=string_ann, visual_annotates=self.visialize_annotates)
            g.point = "+"
            g.line = self.graf.line
            g.color = "black"
            new_string.color = "black"
            g.width = self.graf.width
            g.capsize = 160
            g.show()
            
            new_string.graf = g
            new_string.string.insert(0, "\"Extremums: " + self.title_f + "\"")
            new_string.visible_button.select()
            self.paront_win.legend_repaint()
            
    def auto_substrate(self):
        if self.graf:
            min_y = self.graf.y.min()
            y = self.graf.y-min_y
            max_y = y.max()
            
            y = (np.exp(-y/max_y))
            y0 = np.mean(y)
            y = -np.log(y0)*max_y+min_y
            
            y = self.graf.y - y

            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(self.graf.x, y, self.ax, self.canvas)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            new_string.graf = g
            new_string.string.insert(0, "\"Without substrate: " + self.title_f + "\"")
            new_string.visible_button.select()
            self.paront_win.legend_repaint()
            
    def tangent(self):
        def tan_tan(event=0):
            try:
                x0 = x_wind.get()
                x0.replace(",", ".")
                x0 = convert_data(x0)
                if x0 == np.nan:
                    error(self.names["Error_tangent_start_point"])
                    return
                dy = self.graf.y[self.graf.x>x0][0] - self.graf.y[self.graf.x<x0][-1]
                dx = self.graf.x[self.graf.x>x0][0] - self.graf.x[self.graf.x<x0][-1]
                k = (dy/dx)
                c = (dy/dx)*(-self.graf.x[self.graf.x>x0][0]) + self.graf.y[self.graf.x>x0][0]
                y = k*(self.graf.x) + c
            except:
                error(self.names["Error_tangent_start_point"])
                return

            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(self.graf.x, y, self.ax, self.canvas)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            new_string.graf = g
            new_string.string.insert(0, str(k)+"*x + "+str(c))
            new_string.visible_button.select()
            new_string.func = lambda x: k*x + c
            self.paront_win.legend_repaint()
            root2.destroy()
            
        if self.graf:
            root2 = tk.Toplevel(self.frame)
            root2.attributes('-toolwindow', True)
            root2.transient(self.frame)
            root2.grab_set()
            root2.wm_title(self.names["Tangent_title"])
            root2.geometry('150x120+400+200')
            root2.iconbitmap(r'icon.ico')
            ctk.CTkLabel(root2, text=self.names["Tangent_x0"], font=("Times", 18)).grid(row=0, column=0)
            
            x_wind = ctk.CTkEntry(root2, font=("Times", 18))
            x_wind.grid(row=1, column=0)
            x_wind.bind('<Return>', tan_tan)
            
            ctk.CTkButton(root2, text=self.names["Ok"], font=("Times", 18), command=tan_tan).place(relx=0.05, rely=0.7)
            
    def fitting(self):
        def fit(event=0):
            string = start_params.get()                
            str_fun = func_fit.get()
            possible_coeffs = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', str_fun)
    
            # Исключаем зарезервированные имена (функции, переменные и т. д.)
            reserved_words = {'exp', 'sin', 'cos', 'tan', 'log', 'x', 'pi', 'e', 'H', 'mean', 'sgn', 'sign', 'lg', 'ln', "arccos", 'acos', "arcsin",
                              "tg", 'tan', 'ctg', 'cot', "arctg", 'atan', "arcctg", "sh", "ch", 'sinh', "ch", 'cosh', 'asin', "th",
                              "tanh", "cth", 'coth', "arcsh", 'asinh', "arcch", 'acosh', 'abs', 'absolute', "arcth", 'atanh', "arccth",
                              "arccoth", 'Heaviside', 'sinc', 'sec', 'csc', 'real', 'im', 're'}
            coefficients = [coeff for coeff in possible_coeffs if coeff not in reserved_words]
    
            # Убираем дубликаты (если один коэффициент встречается несколько раз)
            unique_coefficients = list(dict.fromkeys(coefficients))
            
            if string == '':
                start_coeffs = list(map(lambda x: 1, unique_coefficients))
            else:
                if ", " in string:
                    s = string.split(", ")
                elif "; " in string:
                    s = string.split(", ")
                elif ";" in string:
                    s = string.split(";")
                elif "; " in string:
                    s = string.split(";")
                elif " " in string:
                    s = string.split(" ")
                else:
                    s = [string]
                
                start_coeffs = []
                for c in s:
                    cf = convert_data(c)
                    if cf == np.nan:
                        error(self.names["Error_fit_coeffs"])
                        return
                    start_coeffs.append(cf)
    
            # Собираем результат в строку
            all_coeffs = ' '.join(unique_coefficients) + ' '
            f = to_function(str_fun, 'x ' + all_coeffs)
            
            try:
                coefs, q = scp.optimize.curve_fit(f, self.graf.x, self.graf.y, start_coeffs)
            except:
                error(self.names["Error_fit_coeffs"])
                return
            y = f(np.array(self.graf.x.data), *coefs)
            if type(y) != np.ndarray and type(y) != int and type(y) != float and type(y) != complex:
                error(self.names["Error_input"])
                return
                    
            if type(y) != np.ndarray:
                y0 = y
                y = np.array([y0])
                y.resize(self.graf.x.shape)
                y.fill(y0)
            
            self.func = lambda x: f(x, *coefs)
            
            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(self.graf.x, self.func(self.graf.x), self.ax, self.canvas)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize

            if len(unique_coefficients) != len(coefs):
                raise ValueError(f"Ожидалось {len(unique_coefficients)} коэффициентов, но получено {len(coefs)}")
            coeffs_dict = dict(zip(unique_coefficients, coefs))
            for coeff, value in coeffs_dict.items():
                str_fun = re.sub(rf'\b{coeff}\b', str(value), str_fun)
                
            try:
                g.show(sett=self.graf.sett)
                new_string.visible_button.select()
                new_string.graf = g
                new_string.string.insert(0, str_fun)
            except:
                new_string.graf = 0
                new_string.visible_button.deselect()
                error(self.names["Error_input"])
                return
            
            info_string = self.add_string()
            dr = np.diag(q)
            dr = np.sqrt(dr)
            miss = str(dr)[1:-1]
            miss = miss.replace(" ", "; ")
            info_string.string.insert(0, "\"" + miss + "\"")
            

            self.paront_win.legend_repaint()
            root2.destroy()

        if self.graf:
            root2 = tk.Toplevel(self.frame)
            root2.attributes('-toolwindow', True)
            root2.transient(self.frame)
            root2.grab_set()
            root2.wm_title(self.names["Fit_title"])
            root2.geometry('200x220+400+200')
            root2.iconbitmap(r'icon.ico')
            ctk.CTkLabel(root2, text=self.names["Fitting_function"], font=("Times", 18)).grid(row=0, column=0)
            ctk.CTkLabel(root2, text=self.names["Fitting_params"], font=("Times", 18)).grid(row=2, column=0)
            
            func_fit = ctk.CTkEntry(root2, font=("Times", 18))
            func_fit.grid(row=1, column=0)
            
            start_params = ctk.CTkEntry(root2, font=("Times", 18))
            start_params.grid(row=3, column=0)
            
            func_fit.bind('<Down>', lambda event: start_params.focus())
            start_params.bind('<Up>', lambda event: func_fit.focus())
            func_fit.bind('<Return>', fit)
            start_params.bind('<Return>', fit)
            
            ctk.CTkButton(root2, text=self.names["Ok"], font=("Times", 18), command=fit).place(relx=0.12, rely=0.85)
            
    def swap_ax(self):
        if self.graf:
            y, x = self.graf.x, self.graf.y
            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(x, y, self.ax, self.canvas, test=self.graf.test)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            if type(self.x_datas) != int:
                new_string.x_datas = self.x_datas
            
            new_string.graf = g
            new_string.string.insert(0, "#ReverseAx(&" + self.title_f + ")")
            new_string.spec_link = ("#ReverseAx(variables_1)", "x variables_1 ")
            new_string.links = [self]
            new_string.visible_button.select()
            self.paront_win.legend_repaint()
            
    def lissagu(self):
        if self.graf:
            if not (self.next_string or self.prev_string):
                error(self.names["Error_lissagu"])
                return
            
            if self.next_string and self.next_string.graf:
                g2 = self.next_string.graf
                title = self.next_string.title_f
            elif self.prev_string and self.prev_string.graf:
                g2 = self.prev_string.graf
                title = self.prev_string.title_f
            else:
                error(self.names["Error_lissagu"])
                return
            
            new_string = self.add_string()
            new_string.col["bg"] = self.graf.color
            
            g = Grafick(self.graf.y, g2.y, self.ax, self.canvas, self.graf.dy, g2.dy)
            g.point = self.graf.point
            g.line = self.graf.line
            g.color = self.graf.color
            self.color = self.graf.color
            g.width = self.graf.width
            g.capsize = self.graf.capsize
            g.show(sett=self.graf.sett)
            
            new_string.graf = g
            new_string.string.insert(0, "\"Lissagu: " + self.title_f + " and " + title + "\"")
            new_string.visible_button.select()
            
            self.paront_win.legend_repaint()
            
    #копирование дерева
    def copy_tree(self, tree):
        self.params = copy.copy(tree.params)
        self.color = copy.copy(tree.color)
        self.col["bg"] = self.color
        self.title_f = copy.copy(tree.title_f)
          
        if tree.string.get() != "":
            self.string.insert(0, tree.string.get())
            self.add(add_s=0)

            if tree.graf:
                if self.graf:
                    self.graf.remove()
                    
                self.graf = Grafick(copy.copy(tree.graf.x), copy.copy(tree.graf.y), self.ax, self.canvas, copy.copy(tree.graf.dx), copy.copy(tree.graf.dy), copy.copy(tree.graf.s), copy.copy(tree.graf.test), copy.copy(tree.graf.vis_ann))
                
                self.graf.leg_label = copy.copy(tree.graf.leg_label)
                self.graf.point = copy.copy(tree.graf.point)
                self.graf.line = copy.copy(tree.graf.line)
                self.graf.color = copy.copy(tree.graf.color)
                self.graf.width = copy.copy(tree.graf.width)
                self.graf.capsize = copy.copy(tree.graf.capsize)
                self.graf.ann = copy.copy(tree.graf.ann)
                self.graf.d = copy.copy(tree.graf.d)
                self.graf.weight = copy.copy(tree.graf.weight)
                self.graf.fill = copy.copy(tree.graf.fill)
                self.graf.repaint(copy.copy(tree.graf.sett))
                
        if tree.visible_button.get():
            self.visible_button.select()
            if self.graf:
                self.graf.hide(1)
        else:
            self.visible_button.deselect()
            if self.graf:
                self.graf.hide(0)

        self.cx1 = copy.copy(tree.cx1)
        self.cx2 = copy.copy(tree.cx2)
        self.cy1 = copy.copy(tree.cy1)
        self.cy2 = copy.copy(tree.cy2)

        if tree.next_string:
            self.add_string().copy_tree(tree.next_string)
            
    #сохранить данные
    def save_txt(self):
        if self.graf:
            filepath = eg.filesavebox(default="C:\\", filetypes=["\*.txt"])
            if filepath == None:
                return
            
            filepath2 = filepath + "_dxdy.txt"
            if not '.txt' in filepath:
                filepath += ".txt"
            
            np.savetxt(filepath, np.array([self.graf.x, self.graf.y]).T)
            

            if not (np.all(np.isnan(self.graf.dx)) and np.all(np.isnan(self.graf.dy))):
                dx = self.graf.dx
                dy = self.graf.dy
                
                np.savetxt(filepath2, np.array([dx, dy]).T)
    
    def save_npy(self):
        if self.graf:
            filepath = eg.filesavebox(default="C:\\", filetypes=["\*.npy"])
            if filepath == None:
                return
            
            filepath2 = filepath + "_dxdy.npy"
            if not '.npy' in filepath:
                filepath += ".npy"
            
            np.save(filepath, np.array([self.graf.x, self.graf.y]).T)
            

            if not (np.all(np.isnan(self.graf.dx)) and np.all(np.isnan(self.graf.dy))):
                dx = self.graf.dx
                dy = self.graf.dy
                
                np.save(filepath2, np.array([dx, dy]).T)
                
    def save(self):
        "Сохраняет все параметры строки и выдаёт их в виде списка"
        file = {"params": self.params,
                "color": self.color,
                "title_f": self.title_f,
                "test_datas": self.test_datas,
                "visialize_annotates": self.visialize_annotates,
                "string": self.string.get(),
                "visible": self.visible_button.get()}
        if self.graf:
            file["graf"] = self.graf.save()
        else:
            file["graf"] = 0
            
        if type(self.x_datas) != int:
            file['x_datas'] = list(self.x_datas.data)
        else:
            file['x_datas'] = 0
            
        return file
            

        