# -*- coding: utf-8 -*-
from sqlite3 import Cursor
from GUI_interface import error
import os
import sys
import json as js
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from tkinter import colorchooser
from Window import Window, Input_String
from Graphicks import Grafick
import copy
import ctypes
import easygui as eg
import numpy as np
import re
from io import StringIO
import pandas as pd
from PIL import Image
from scipy import ndimage
from Math_functions import to_function
import winreg

import gzip

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Собираем точный абсолютный путь к файлу конфигурации
SYSTEM_JSON_PATH = os.path.join(BASE_DIR, "system.json")


if not os.path.isfile(SYSTEM_JSON_PATH):
    error("The program is incomplete!")
    sys.exit()
else:
    with open(SYSTEM_JSON_PATH, "r", encoding="utf-8") as file:
        sett = js.load(file)
        names = sett[sett["language"]]
        
MODULES_PATH = os.path.join(BASE_DIR, "modules")
if not os.path.isdir(MODULES_PATH):
    error("The program is incomplete!")
    os.makedirs(MODULES_PATH, exist_ok=True)

self_modules = os.listdir(MODULES_PATH)
        
checklist = {"Can_lab_ind": False,
             "Can_labax_ind": False
             }

def сanvas_label():
    def save_label(event):
        focus_win.can_lab = inp.get("1.0", "1.end")
        focus_win.ax.set_title(focus_win.can_lab, fontsize=26)
        focus_win.canvas.draw()
        inp.destroy() 
        return

    checklist["Can_lab_ind"] = not checklist["Can_lab_ind"]
    for win in list_wins:
        current_tab = tab_control.select()
       
        if checklist["Can_lab_ind"]:
            if current_tab == str(win.frame):
                focus_win = win
                inp = tk.Text(win.frame, width=10, height=1, font="Times 26")
                inp.place(relx=0.55, rely=0.02)
                inp.insert("1.0", win.can_lab)
                inp.focus()
                inp.bind('<Return>', save_label)
            else:
                win.ax.set_title(win.can_lab, fontsize=26)
                win.canvas.draw()
        else:
            win.ax.set_title("")
            win.canvas.draw()

def axis_label():
    def save_label_x(event):
        focus_win.can_labx = inp_x.get("1.0", "1.end")
        focus_win.ax.set_xlabel(focus_win.can_labx, fontsize=14)
        focus_win.canvas.draw()
        inp_x.destroy() 
        x_l.destroy()
        return
    def save_label_y(event):
        focus_win.can_laby = inp_y.get("1.0", "1.end")
        if win.polar_ax:
            focus_win.ax.set_ylabel(focus_win.can_laby, fontsize=14, labelpad=30)
        else:
            focus_win.ax.set_ylabel(focus_win.can_laby, fontsize=14)
        focus_win.canvas.draw()
        inp_y.destroy() 
        y_l.destroy()
        return

    checklist["Can_labax_ind"] = not checklist["Can_labax_ind"]
    for win in list_wins:
        current_tab = tab_control.select()
       
        if checklist["Can_labax_ind"]:
            if current_tab == str(win.frame):
                focus_win = win
                x_l = tk.Label(win.frame, font="Times 12", text="x:")
                x_l.place(relx=0.49, rely=0.89)
                inp_x = tk.Text(win.frame, width=10, height=1, font="Times 14")
                inp_x.place(relx=0.5, rely=0.89)
                inp_x.insert("1.0", win.can_labx)
                inp_x.bind('<Return>', save_label_x)
                y_l = tk.Label(win.frame, font="Times 12", text="y:")
                y_l.place(relx=0.59, rely=0.89)
                inp_y = tk.Text(win.frame, width=10, height=1, font="Times 14")
                inp_y.place(relx=0.6, rely=0.89)
                inp_y.insert("1.0", win.can_laby)
                inp_y.focus()
                inp_y.bind('<Return>', save_label_y)
            else:
                win.ax.set_xlabel(win.can_labx, fontsize=14)
                win.canvas.draw()
                win.ax.set_ylabel(win.can_laby, fontsize=14)
                win.canvas.draw()
        else:
            win.ax.set_xlabel("")
            win.ax.set_ylabel("")
            win.canvas.draw()

def new_graph():
        
    win_dubl = Window(tab_control, names, create_graph_in_new_win, sett["default_params"], names["Grafick"])
    
    list_wins.append(win_dubl)
    
def leg_split():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
    win.legend_include()
    
def maj_ax_include():
    sett["default_params"]["maj_ax"] = not sett["default_params"]["maj_ax"]
    for win in list_wins:
        win.ax.grid(which='major')
        win.canvas.draw()
        
def min_ax_include():
    sett["default_params"]["min_ax"] = not sett["default_params"]["min_ax"]
    for win in list_wins:
        if sett["default_params"]["min_ax"]:
            win.ax.minorticks_on()
            win.ax.grid(which='minor', linestyle=':')
        else:
            win.ax.minorticks_off()
            win.ax.grid(which='minor', linestyle=':')
        win.canvas.draw()
        
def x_log_scale():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
    if win.polar_ax:
        error(names["Error_polar_x_log"])
        return
    if win.x0_log == 'linear':
        win.x0_log = win.ax.get_xlim()[0]
        if win.x0_log < 1:
            win.ax.set_xlim(1, win.ax.get_xlim()[1])
        win.ax.set_xscale('log')
    else:
        win.ax.set_xscale('linear')
        win.ax.set_xlim(win.x0_log, win.ax.get_xlim()[1])
        win.x0_log = 'linear'
    win.canvas.draw()
    
def y_log_scale():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
    if win.y0_log == 'linear':
        win.y0_log = win.ax.get_ylim()[0]
        if win.y0_log < 1:
            win.ax.set_ylim(1, win.ax.get_ylim()[1])
        win.ax.set_yscale('log')
    else:
        win.ax.set_yscale('linear')
        win.ax.set_ylim(win.y0_log, win.ax.get_ylim()[1])
        win.y0_log = 'linear'
    win.canvas.draw()

def dublicate():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    win.params["scale"][0], win.params["scale"][2] = win.ax.get_xlim()[0], win.ax.get_xlim()[1]
    win.params["scale"][1], win.params["scale"][3] = win.ax.get_ylim()[0], win.ax.get_ylim()[1]
    win_dubl = Window(tab_control, names, create_graph_in_new_win, copy.copy(win.params), title=copy.copy(win.title), title_c=copy.copy(win.can_lab), title_x=copy.copy(win.can_labx), title_y=copy.copy(win.can_laby), x_log=copy.copy(win.x0_log), y_log=copy.copy(win.y0_log), polar_test=copy.copy(win.polar_ax))
    
    win_dubl.legend = copy.copy(win.legend)
    
    win_dubl.cx1 = copy.copy(win.cx1)
    win_dubl.cx2 = copy.copy(win.cx2)
    win_dubl.cy1 = copy.copy(win.cy1)
    win_dubl.cy2 = copy.copy(win.cy2)
    
    win_dubl.fields_tree.copy_tree(win.fields_tree)
    
    win_dubl.update()
    
    list_wins.append(win_dubl)

def pollar_ax():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
    win.polar()

def delete_wind():
    if len(list_wins) < 2:
        return
    
    c = 0
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        c += 1
     
    win.frame.destroy()
    list_wins.pop(c)
    return

def create_graph_in_new_win(x, y, dx=[], dy=[], leg_label=" ", name_graph="\"None\""):
    win_dubl = Window(tab_control, names, create_graph_in_new_win, sett["default_params"], names["Grafick"])
    graph = Grafick(x, y, win_dubl.ax, win_dubl.canvas, dx, dy, True)
    graph.leg_label = leg_label
    graph.show()
    win_dubl.fields_tree.visible_button.select()
    win_dubl.fields_tree.graf = graph
    win_dubl.fields_tree.changed_scale()
    win_dubl.fields_tree.string.insert(0, name_graph)
    
    list_wins.append(win_dubl)

def add_graph_in_win(wind, x, y, dx=[], dy=[], leg_label=" ", name_graph="\"None\""):
    new_str = wind.fields_tree.add_string()
    graph = Grafick(x, y, new_str.ax, new_str.canvas, dx, dy, True)
    graph.leg_label = leg_label
    graph.show()
    new_str.visible_button.select()
    new_str.graf = graph
    new_str.fields_tree.changed_scale()
    new_str.fields_tree.string.insert(0, name_graph)
    new_str.fields_tree.legend_draw()
    
def read_file(type_xlsx=1, filepath=None):
    "Читает файл и возвращает архив numpy"

    if filepath == None:
        filepath = eg.fileopenbox(default=sett["default_path_file"], filetypes=["*.txt", "*.npy", "*.xlsx", "*.graph"])
        if filepath == None:
            return None, ""
    name_file = os.path.basename(filepath)
    types = name_file.split(".")[-1]
    default_del = sett["default_del"]
    data = np.array([])
    
    with open("system.json", "w", encoding="utf-8") as file:
        sett["default_path_file"] = filepath
        js.dump(sett, file, ensure_ascii=False, indent=4)
    
    if types == 'txt' or types == 'csv' or types == 'CSV' or types == 'TXT':
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Определяем начало числовых данных (первая строка без букв)
        data_start = 0
        letter_pattern = re.compile(r'[a-zA-Zа-яА-Я]')  # Английские и русские буквы
    
        for i, line in enumerate(lines):
            if not letter_pattern.search(line) and any(c.isdigit() for c in line):
                data_start = i
                break
    
        # Обрабатываем числовые строки
        cleaned_lines = []
        for line in lines[data_start:]:
            # # Удаляем все буквы и мусорные символы (кроме цифр, точек, запятых, знаков и разделителей)
            cleaned = re.sub(r'[a-df-zA-DF-Zа-яА-Я!@#$%^&*()_+=|<>?{}\[\]~`]', '', line.strip())
            #print(cleaned)
            #cleaned = re.sub(r'[^0-9eE\.\+\-\,]', '', line.strip())
            #print(cleaned)
            # Заменяем запятые на точки в числах (0,1 -> 0.1)
            cleaned = re.sub(r'(?<=\d),(?=\d)', '.', cleaned)
            # Удаляем оставшиеся запятые (которые не в числах)
            cleaned = cleaned.replace(',', ' ')
            cleaned_lines.append(cleaned)
    
        # Автоматически определяем разделитель
        test_line = cleaned_lines[0] if cleaned_lines else ""
        if default_del == 'AUTO':
            possible_delimiters = ['\t', ';', ':', ' ', '  ', '    ', '; ', ': ']
        elif default_del == 'TAB':
            possible_delimiters = ['\t']
        else:
            possible_delimiters = [default_del]
    
        for delim in possible_delimiters:
            parts = [p for p in test_line.split(delim) if p]
            if len(parts) > 1:
                try:
                    # Пробуем преобразовать все части в числа
                    [float(p) for p in parts]
                    # Если успешно, пробуем загрузить весь файл
                    data = np.loadtxt(StringIO('\n'.join(cleaned_lines)), delimiter=delim)
                    break
                except:
                    continue
        if data.shape[0] == 0:
            # Если не удалось определить разделитель, пробуем split() по whitespace
            try:
                data = np.loadtxt(StringIO('\n'.join(cleaned_lines)))
            except:
                pass
        
        if data.shape[0] == 0:
            data = []
            # Резервный метод для сложных случаев
            for line in cleaned_lines:
                # Разбиваем по любому whitespace
                parts = re.split(r'\s+', line.strip())
                row = []
                for p in parts:
                    if p:
                        try:
                            row.append(float(p))
                        except:
                            pass
                if row:
                    data.append(row)
            try:
                data = np.array(data)
            except:
                error(names["Error_not_read_files"])
                return None, ""
    elif types == "xlsx" or types == "XLSX":
        if type_xlsx:
            data = pd.read_excel(filepath, names=None)
        else:
            cols = eg.enterbox(title="Test")
            cols = cols.split("\t")
            data = pd.read_excel(filepath, names=cols)
        data = data.to_numpy().T
    elif types == 'png' or types == 'jpg' or types == 'jpeg' or types == 'PNG'or types == 'JPG' or types == 'JPEG':
        try:
            x, y = extract_points_from_graph(filepath)
            y = y.max() - y
            return np.array([x, y]).T, name_file
        except:
            error(names["Error_image_file"])
            return None, ''
    elif types == 'npy' or types == 'NPY':
        data = np.load(filepath)
    else:
        error(names["Error_not_read_files"])
        return None, ""
    return data, name_file

#Открыть график    
def open_file_all(filepath=None):
    if filepath == None:
        filepath = eg.fileopenbox(default=sett["default_path_file"], filetypes=["*.txt", "*.npy", "*.xlsx", "*.graph"])
    if filepath == None:
        return
    
    with open("system.json", "w", encoding="utf-8") as file:
        sett["default_path_file"] = filepath
        js.dump(sett, file, ensure_ascii=False, indent=4)

    name_file = os.path.basename(filepath)
    types = name_file.split(".")[-1]
    if types != 'graph' and types != 'GRAPH':
        open_file_graph_one_x(filepath)
    else:
        with gzip.open(filepath, "rb") as f:
            win_datas = f.read().split(b'\n')
            settings_win = js.loads(win_datas[0].decode("utf-8"))
            
        for win in list_wins:
            current_tab = tab_control.select()
            if current_tab == str(win.frame):
                break

        new_win = Window(tab_control, names, create_graph_in_new_win, settings_win['params'], settings_win["title"], settings_win["can_lab"], settings_win["can_labx"], settings_win["can_laby"], settings_win["polar_ax"], settings_win["x0_log"], settings_win["y0_log"])
        new_win.save_file = filepath

        if settings_win['legend']:
            new_win.legend_include()
                
        strings = new_win.fields_tree
        for st in range(1, len(win_datas)):
            sett_st = js.loads(win_datas[st].decode("utf-8"))
                
            strings.params = sett_st["params"]
            strings.color = sett_st["color"]
            strings.col["bg"] = strings.color
            strings.title_f = sett_st["title_f"]
            strings.test_datas = sett_st["test_datas"]
            strings.visialize_annotates = sett_st["visialize_annotates"]
            strings.string.insert(0, sett_st["string"])
            if sett_st["x_datas"]:
                strings.x_datas = np.array(sett_st["x_datas"])
            if sett_st["graf"]:
                strings.graf = Grafick(np.array(sett_st["graf"][-4]), np.array(sett_st["graf"][-3]), new_win.ax, new_win.canvas, np.array(sett_st["graf"][-2]), np.array(sett_st["graf"][-1]), sett_st["graf"][8], sett_st["graf"][6], sett_st["graf"][7])
                strings.graf.leg_label = sett_st["graf"][0]
                strings.graf.point = sett_st["graf"][1]
                strings.graf.line = sett_st["graf"][2]
                strings.graf.color = sett_st["graf"][3]
                strings.graf.width = sett_st["graf"][4]
                strings.graf.capsize = sett_st["graf"][5]
                strings.graf.d = sett_st["graf"][9]
                strings.graf.weight = sett_st["graf"][10]
                strings.graf.fill = sett_st["graf"][11]
                strings.graf.show(sett=sett_st["graf"][12])
            strings.add(add_s=0)
            if sett_st["visible"] and strings.graf:
                strings.graf.hide(1)
                strings.visible_button.select()
            else:
                if strings.graf:
                    strings.graf.hide(0)
                strings.visible_button.deselect()
                
            if st+1 != len(win_datas):
                strings.next_string = Input_String(strings.frame, strings.names, strings.ax, strings.canvas, params=strings.params, i=strings.i+1)
                strings.next_string.prev_string = strings
                strings.next_string.create_graph_in_new_win = strings.create_graph_in_new_win
                strings.next_string.paront_win = strings.paront_win
                strings = strings.next_string
            else:
                break

        if settings_win['cx1'] != None:
            new_win.add_x_cursors()
            new_win.cx1.x, new_win.cx1.vert, new_win.cx1.color, new_win.cx1.line, new_win.cx1.width, new_win.cx1.polar = settings_win['cx1'][4], settings_win['cx1'][0], settings_win['cx1'][1], settings_win['cx1'][2], settings_win['cx1'][3], settings_win['cx1'][-1]
            new_win.cx2.x, new_win.cx2.vert, new_win.cx2.color, new_win.cx2.line, new_win.cx2.width, new_win.cx2.polar = settings_win['cx2'][4], settings_win['cx2'][0], settings_win['cx2'][1], settings_win['cx2'][2], settings_win['cx2'][3], settings_win['cx2'][-1]
            new_win.fields_tree.curs_x_translate(settings_win['cx1'][4], settings_win['cx2'][4])
        if settings_win['cy1'] != None:
            new_win.add_y_cursors()
            new_win.cy1.x, new_win.cy1.vert, new_win.cy1.color, new_win.cy1.line, new_win.cy1.width, new_win.cy1.polar = settings_win['cy1'][4], settings_win['cy1'][0], settings_win['cy1'][1], settings_win['cy1'][2], settings_win['cy1'][3], settings_win['cy1'][-1]
            new_win.cy2.x, new_win.cy2.vert, new_win.cy2.color, new_win.cy2.line, new_win.cy2.width, new_win.cy2.polar = settings_win['cy2'][4], settings_win['cy2'][0], settings_win['cy2'][1], settings_win['cy2'][2], settings_win['cy2'][3], settings_win['cy2'][-1]
            new_win.fields_tree.curs_y_translate(settings_win['cy1'][4], settings_win['cy2'][4])
        new_win.update()
        list_wins.append(new_win)

def open_file_graph_one_x(filepath=None):
    data, path = read_file(filepath=filepath)
    if type(data) == type(None):
        return
    
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    if data.shape == (data.shape[0],):
        new_string = win.fields_tree.add_string()
        y, test = read_file()
        if type(y) == type(None):
            x = np.arange(data.shape[0])
            y = data
        else:
            x = data
        if x.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        g = Grafick(x, y, win.ax, win.canvas, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    elif data.shape == (1, data.shape[1]):
        new_string = win.fields_tree.add_string()
        y, test = read_file()
        if type(y) == type(None):
            x = np.arange(data.shape[1])
            y = data[0]
        else:
            x = data[0]
        if x.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        g = Grafick(x, y[0], win.ax, win.canvas, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    else:
        data = data.T
        x = data[0]
        c = 0
        for y in data:
            if c != 0:
                new_string = win.fields_tree.add_string()
                g = Grafick(x, y, win.ax, win.canvas, test=True)
                g.color = new_string.color
                new_string.graf = g
                new_string.string.insert(0, "\""+path+"\"")
                new_string.graf.show(new_string.graf.sett)
                new_string.visible_button.select()
                new_string.changed_scale()
            c += 1
    win.legend_repaint()
    
def open_file_graph_without_x():
    data, path = read_file()
    if type(data) == type(None):
        return
    
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    if data.shape == (data.shape[0],):
        new_string = win.fields_tree.add_string()
        x = np.arange(data.shape[0])
        y = data
        g = Grafick(x, y, win.ax, win.canvas, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    elif data.shape == (1, data.shape[1]):
        new_string = win.fields_tree.add_string()
        x = np.arange(data.shape[1])
        y = data[0]
        g = Grafick(x, y, win.ax, win.canvas, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    else:
        data = data.T
        x = np.arange(data[0].shape[0])
        for y in data:
            new_string = win.fields_tree.add_string()
            g = Grafick(x, y, win.ax, win.canvas, test=True)
            g.color = new_string.color
            new_string.graf = g
            new_string.string.insert(0, "\""+path+"\"")
            new_string.graf.show(new_string.graf.sett)
            new_string.visible_button.select()
            new_string.changed_scale()
    win.legend_repaint()
    
def open_file_graph_different_x():
    data, path = read_file()
    if type(data) == type(None):
        return
    
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    if data.shape == (data.shape[0],):
        new_string = win.fields_tree.add_string()
        y, test = read_file()
        if type(y) == type(None):
            x = np.arange(data.shape[0])
            y = data
        else:
            x = data
        if x.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        g = Grafick(x, y, win.ax, win.canvas, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    elif data.shape == (1, data.shape[1]):
        new_string = win.fields_tree.add_string()
        y, test = read_file()
        if type(y) == type(None):
            x = np.arange(data.shape[1])
            y = data[0]
        else:
            x = data[0]
            
        if x.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        g = Grafick(x, y[0], win.ax, win.canvas, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    else:
        data = data.T
        x = data[0]
        c = 0
        for y in data:
            if c != 0:
                new_string = win.fields_tree.add_string()
                g = Grafick(x, y, win.ax, win.canvas, test=True)
                g.color = new_string.color
                new_string.graf = g
                new_string.string.insert(0, "\""+path+"\"")
                new_string.graf.show(new_string.graf.sett)
                new_string.visible_button.select()
                new_string.changed_scale()
            c += 1
    win.legend_repaint()
    
#Открыть график с погрешностями
def open_file_errgraph_different_x():
    data, path = read_file()
    if type(data) == type(None):
        return
    
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    if data.shape == (data.shape[0],):
        new_string = win.fields_tree.add_string()
        y, test = read_file()
        if type(y) == type(None):
            x = np.arange(data.shape[0])
            y = data
        else:
            x = data
            
        if x.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        
        dx, test = read_file()
        if type(dx) == type(None):
            dx = []
        elif dx.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        
        dy, test = read_file()
        if type(dy) == type(None):
            dy = []
        elif dy.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        
        g = Grafick(x, y, win.ax, win.canvas, dx, dy, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    elif data.shape == (1, data.shape[1]):
        new_string = win.fields_tree.add_string()
        y, test = read_file()
        if type(y) == type(None):
            x = np.arange(data.shape[1])
            y = data
        else:
            x = data[0]
            
        if x.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        
        dx, test = read_file()
        if type(dx) == type(None):
            dx = [[]]
        elif dx.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        
        dy, test = read_file()
        if type(dy) == type(None):
            dy = [[]]
        elif dy.shape != y.shape:
            error(names["Error_open_different_size"])
            return

        g = Grafick(x, y[0], win.ax, win.canvas, dx[0], dy[0], test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    else:        
        dy, test = read_file()
        if type(dy) == type(None):
            dy = copy.copy(data)
            dy.fill(np.nan)
            
        null_test = False
        if dy.shape == (dy.shape[0],):
            null_test = True
            if dy.shape[0] != data.shape[0]:
                error(names["Error_open_different_size"])
                return
        else:
            if dy.shape[0] != data.shape[0] or (data.shape[1] - dy.shape[1] > 1):
                error(names["Error_open_different_size"])
                return
        
        data = data.T
        x = data[0]
        dy = dy.T
        c = 0
        for y in data:
            if c != 0:
                new_string = win.fields_tree.add_string()
                if null_test:
                    g = Grafick(x, y, win.ax, win.canvas, dy=dy, test=True)
                else:
                    if (data.shape[0] - dy.shape[0] == 0):
                        g = Grafick(x, y, win.ax, win.canvas, dx=dy[0], dy=dy[c], test=True)
                    else:
                        g = Grafick(x, y, win.ax, win.canvas, dy=dy[c-1], test=True)
                g.color = new_string.color
                new_string.graf = g
                new_string.string.insert(0, "\""+path+"\"")
                new_string.graf.show(new_string.graf.sett)
                new_string.visible_button.select()
                new_string.changed_scale()
            c += 1
    win.legend_repaint()
    
def open_file_errgraph_without_x():
    data, path = read_file()
    if type(data) == type(None):
        return
    
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    if data.shape == (data.shape[0],):
        new_string = win.fields_tree.add_string()
        x = np.arange(data.shape[0])
        y = data
        dy, test = read_file()
        if type(dy) == type(None):
            dy = []
        elif dy.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        g = Grafick(x, y, win.ax, win.canvas, dy=dy, test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    elif data.shape == (1, data.shape[1]):
        new_string = win.fields_tree.add_string()
        x = np.arange(data.shape[1])
        y = data[0]
        dy, test = read_file()
        if type(dy) == type(None):
            dy = []
        elif dy.shape != y.shape:
            error(names["Error_open_different_size"])
            return
        g = Grafick(x, y, win.ax, win.canvas, dy=dy[0], test=True)
        g.color = new_string.color
        new_string.graf = g
        new_string.string.insert(0, "\""+path+"\"")
        new_string.graf.show(new_string.graf.sett)
        new_string.visible_button.select()
        new_string.changed_scale()
    else:
        dx, test = read_file()
        if type(dx) == type(None):
            dx = copy.copy(data)
            dx.fill(np.nan)
        elif dx.shape != data.shape:
            error(names["Error_open_different_size"])
            return
        
        dy, test = read_file()
        if type(dy) == type(None):
            dy = copy.copy(data)
            dy.fill(np.nan)
        elif dy.shape != data.shape:
            error(names["Error_open_different_size"])
            return
        
        data = data.T
        dy = dy.T
        dx = dx.T
        x = np.arange(data[0].shape[0])
        c = 0
        for y in data:
            new_string = win.fields_tree.add_string()
            g = Grafick(x, y, win.ax, win.canvas, dx=dx[c], dy=dy[c], test=True)
            g.color = new_string.color
            new_string.graf = g
            new_string.string.insert(0, "\""+path+"\"")
            new_string.graf.show(new_string.graf.sett)
            new_string.visible_button.select()
            new_string.changed_scale()
            c += 1
    win.legend_repaint()
    
#Открыть гистограмму
def open_file_hist(parent):
    def result(event=0):
        if check.get():
            weights = True
        else:
            weights = False
        if e.get() == "":
            n = 0
        else:
            try:
                n = int(to_function(e.get())(0))
            except:
                n = 0
        root.destroy()
            
        data, path = read_file()
        if type(data) == type(None):
            return
        
        if weights:
            weight, path2 = read_file()
            if type(weight) == type(None):
                error(names["Error_not_weight"])
                weights = False
            elif weight.shape != data.shape:
                error(names["Error_open_different_size"])
                weights = False
    
        for win in list_wins:
            current_tab = tab_control.select()
            if current_tab == str(win.frame):
                break
        
        if data.shape == (data.shape[0],):
            new_string = win.fields_tree.add_string()
            if weights:
                if n:
                    y, x = np.histogram(data, bins=n, weights=weight)
                else:
                    y, x = np.histogram(data, weights=weight)
                g = Grafick((x[:-1] + x[1:])/2, y, win.ax, win.canvas, test=True)
                g.weight = weight
            else:
                if n:
                    y, x = np.histogram(data, bins=n)
                else:
                    y, x = np.histogram(data)
                g = Grafick((x[:-1] + x[1:])/2, y, win.ax, win.canvas, test=True)
            g.d = x[1] - x[0]
            g.color = new_string.color
            new_string.graf = g
            new_string.string.insert(0, "\""+path+"\"")
            new_string.graf.show([0, 0, 1])
            new_string.visible_button.select()
            new_string.changed_scale()
        elif data.shape == (1, data.shape[1]):
            new_string = win.fields_tree.add_string()
            if weights:
                if n:
                    y, x = np.histogram(data[0], bins=n, weights=weight)
                else:
                    y, x = np.histogram(data[0], weights=weight)
                g = Grafick((x[:-1] + x[1:])/2, y, win.ax, win.canvas, test=True)
                g.weight = weight
            else:
                if n:
                    y, x = np.histogram(data[0], bins=n)
                else:
                    y, x = np.histogram(data[0])
                g = Grafick((x[:-1] + x[1:])/2, y, win.ax, win.canvas, test=True)
            g.d = x[1] - x[0]
            g.color = new_string.color
            new_string.graf = g
            new_string.string.insert(0, "\""+path+"\"")
            new_string.graf.show([0, 0, 1])
            new_string.visible_button.select()
            new_string.changed_scale()
        else:
            data = data.T
            for di in data:
                new_string = win.fields_tree.add_string()
                if weights:
                    if n:
                        y, x = np.histogram(di, bins=n, weights=weight)
                    else:
                        y, x = np.histogram(di, weights=weight)
                    g = Grafick((x[:-1] + x[1:])/2, y, win.ax, win.canvas, test=True)
                    g.weight = weight
                else:
                    if n:
                        y, x = np.histogram(di, bins=n)
                    else:
                        y, x = np.histogram(di)
                    g = Grafick((x[:-1] + x[1:])/2, y, win.ax, win.canvas, test=True)
                g.d = x[1] - x[0]
                g.color = new_string.color
                new_string.graf = g
                new_string.string.insert(0, "\""+path+"\"")
                new_string.graf.show([0, 0, 1])
                new_string.visible_button.select()
                new_string.changed_scale()
    
    root = tk.Toplevel(parent)    
    root.attributes('-toolwindow', True)
    root.transient(parent)
    root.grab_set()
    
    root.title(names["Settings_hist"])
    root.geometry('300x100+400+200')
    root.iconbitmap(r'icon.ico')
    root.resizable(width=False, height=False)
    
    check = ctk.CTkCheckBox(root, text=names["Weights"], font=('Times', 16))
    check.place(relx=0.5, rely=0.25)
    
    ctk.CTkLabel(root, text=names["Bins_count"], font=('Times', 16)).place(relx=0.01, rely=0.03)
    e = ctk.CTkEntry(root, font=('Times', 16))
    e.place(relx=0.01, rely=0.25)
    e.bind('<Return>', command=result)
    
    tk.Button(root, font=('Times', 16), text=names["String_names"]["Ok"], command=result).place(rely=0.6, relx=0.45)
    

#Дополнительные функции
def extract_points_from_graph(image_path, min_size=5, max_size=50, threshold=200):
    """
    Извлекает координаты точек с изображения графика без OpenCV.
    
    Параметры:
        image_path: путь к файлу изображения
        min_size: минимальный размер объекта в пикселях
        max_size: максимальный размер объекта
        threshold: порог яркости (0-255)
    
    Возвращает:
        x_coords, y_coords: массивы numpy с координатами точек
    """
    # Загрузка изображения
    img = Image.open(image_path)
    img_gray = img.convert('L')  # Конвертация в grayscale
    img_array = np.array(img_gray)
    
    # Бинаризация
    binary = img_array < threshold
    
    # Поиск объектов
    labeled, num_features = ndimage.label(binary)
    centers = []
    
    for i in range(1, num_features + 1):
        # Маска для текущего объекта
        obj_mask = labeled == i
        size = np.sum(obj_mask)
        
        if min_size < size < max_size:
            # Вычисляем центр масс
            y, x = ndimage.center_of_mass(obj_mask)
            centers.append((x, y))
    
    # Сортировка точек слева направо
    centers.sort(key=lambda p: p[0])
    
    # Разделение координат
    if centers:
        x_coords = np.array([p[0] for p in centers])
        y_coords = np.array([p[1] for p in centers])
        return x_coords, y_coords
    else:
        return np.array([]), np.array([])    
    
#Курсоры
def curs_x():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    win.add_x_cursors()
    
def curs_y():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    win.add_y_cursors()
    
def new_module(file):
    pass

def open_sett(parent):
    """Создает окно настроек программы"""
    values_lang_orig = ["russian", "english"]
    values_lang = ["Русский", "English"]

    def choose_color():
        p = colorchooser.askcolor()[1]
        if p != None:
            color_btn.configure(fg_color=p)
            
    def push():
        with open("system.json", "w", encoding="utf-8") as file:
            sett["language"] = values_lang_orig[values_lang.index(lang.get())]
            sett["default_del"] = delimit.get()
            sett["default_params"]["maj_ax"] = maj_ax_check.get()
            sett["default_params"]["min_ax"] = min_ax_check.get()
            sett["default_params"]["default_params_string"][1] = color_btn.cget("fg_color")
            
            x0 = to_function(x0_entry.get())(0)
            x1 = to_function(x1_entry.get())(0)
            y0 = to_function(y0_entry.get())(0)
            y1 = to_function(y1_entry.get())(0)
            
            if (type(x0) != int and type(x0) != float and type(x0) != complex) or (type(x1) != int and type(x1) != float and type(x1) != complex) or (type(y0) != int and type(y0) != float and type(y0) != complex) or (type(y1) != int and type(y1) != float and type(y1) != complex):
                error(names["String_names"]["Error_input"])
                return
            
            sett["default_params"]["scale"] = [x0, y0, x1, y1]
            
            names = sett[sett["language"]]
            js.dump(sett, file, ensure_ascii=False, indent=4)
        window.destroy()
    
    # Создание окна
    window = tk.Toplevel(parent)
    
    window.attributes('-toolwindow', True)
    window.transient(parent)
    window.grab_set()
    
    window.iconbitmap(r'icon.ico')
    window.title(names["Settings"])
    window.geometry("500x600")
    window.resizable(False, False)
    
    lang = ctk.CTkOptionMenu(window, values=values_lang)
    lang.set(values_lang[values_lang_orig.index(sett["language"])])
    lang.place(relx=0.05, rely=0.01)
    
    ctk.CTkLabel(window, text=names["Delimiter_def"], font=('Times', 14)).place(relx=0.05, rely=0.06)    
    delimit = ctk.CTkEntry(window)
    delimit.insert(0, sett["default_del"])
    delimit.place(relx=0.05, rely=0.1)
    
    maj_ax_check = ctk.CTkCheckBox(window, text=names["Major_ax"])
    if sett["default_params"]["maj_ax"]:
        maj_ax_check.select()
    maj_ax_check.place(relx=0.05, rely=0.16)
    min_ax_check = ctk.CTkCheckBox(window, text=names["Minor_ax"])
    if sett["default_params"]["min_ax"]:
        min_ax_check.select()
    min_ax_check.place(relx=0.3, rely=0.16)
    
    ctk.CTkLabel(window, font=('Times', 14), text=names["Scale_sett"]).place(relx=0.05, rely=0.21)
    ctk.CTkLabel(window, font=('Times', 14), text="x:").place(relx=0.05, rely=0.25)
    x0_entry = ctk.CTkEntry(window, width=45)
    x0_entry.insert(0, sett["default_params"]["scale"][0])
    x0_entry.place(relx=0.08, rely=0.25)
    #----------------------------------------
    x1_entry = ctk.CTkEntry(window, width=45)
    x1_entry.insert(0, sett["default_params"]["scale"][2])
    x1_entry.place(relx=0.2, rely=0.25)
    
    ctk.CTkLabel(window, font=('Times', 14), text="y:").place(relx=0.05, rely=0.31)
    y0_entry = ctk.CTkEntry(window, width=45)
    y0_entry.insert(0, sett["default_params"]["scale"][1])
    y0_entry.place(relx=0.08, rely=0.31)
    #----------------------------------------
    y1_entry = ctk.CTkEntry(window, width=45)
    y1_entry.insert(0, sett["default_params"]["scale"][3])
    y1_entry.place(relx=0.2, rely=0.31)
    
    ctk.CTkLabel(window, font=('Times', 14), text=names["Default_color"]).place(relx=0.05, rely=0.37)
    color_btn = ctk.CTkButton(window, text="", width=30, height=30, fg_color=sett["default_params"]["default_params_string"][1], command=choose_color)
    color_btn.place(relx=0.05, rely=0.41)

    ok_button = ctk.CTkButton(window, text=names["Save"], command=push)
    ok_button.place(relx=0.4, rely=0.95)
    
def save_win():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    win.save_file = save_file(win)
    
def save_how():
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        
    win.save_file = save_file(win, 'how')
    
def save_all():
    for win in list_wins:
        save_file(win)
    
def save_file(win, mode='standart'):
    if (win.save_file == '' or not os.path.isfile(win.save_file)) or mode!='standart':
        filepath = eg.filesavebox(default=sett["default_path_file_save"], filetypes=["\*.graph"])
        if filepath == None:
            return ''
        if not '.graph' in filepath:
            filepath += ".graph"
    else:
        filepath = win.save_file
    
    with open("system.json", "w", encoding="utf-8") as file:
        sett["default_path_file_save"] = filepath
        js.dump(sett, file, ensure_ascii=False, indent=4)
        
    with gzip.open(filepath, "wb") as file:
        #Window settings
        if win.legend:
            leg = True
        else:
            leg = False
            
        settings_win = {"params": win.params,
                        "title": win.title,
                        "can_lab": win.can_lab,
                        "can_labx": win.can_labx,
                        "can_laby": win.can_laby,
                        "x0_log": win.x0_log,
                        "y0_log": win.y0_log,
                        "polar_ax": win.polar_ax,
                        "legend": leg
            }
        if win.cx1 != None:
            settings_win["cx1"] = win.cx1.save()
            settings_win["cx2"] = win.cx2.save()
        else:
            settings_win["cx1"] = win.cx1
            settings_win["cx2"] = win.cx2
            
        if win.cy1 != None:
            settings_win["cy1"] = win.cy1.save()
            settings_win["cy2"] = win.cy2.save()
        else:
            settings_win["cy1"] = win.cy1
            settings_win["cy2"] = win.cy2
        
        json_str = js.dumps(settings_win, ensure_ascii=False)
        #file.write(f"WS:{len(json_str)}\n".encode('utf-8')) #Window Settings
        file.write(json_str.encode('utf-8'))
        file.write(b'\n')
        
        #Tree
        #file.write(f"Tr:\n".encode('utf-8')) #Tree
        tree_unit = win.fields_tree
        while(1):
            #file.write(f"TS:\n".encode('utf-8')) #Tree settings
            settings_win = tree_unit.save()
            json_str = js.dumps(settings_win, ensure_ascii=False)
            file.write(json_str.encode('utf-8'))
            #file.write(b"\n._.\n")
            if tree_unit.next_string:
                tree_unit = tree_unit.next_string
            else:
                break
            file.write(b'\n')
        
    return filepath

def rename():
    def save_title(event):
        win.title = lab.get("1.0", 'end')[:-1]
        lab.destroy()
        tab_control.tab(index, text=win.title)
    
    c = 0
    index = 0
    for win in list_wins:
        current_tab = tab_control.select()
        if current_tab == str(win.frame):
            break
        c += len(win.title)
        index += 1
    
    #x_coords = (c+1)/len(list_wins)
    lab = tk.Text(tab_control, width=7, height=0.5, font='Times 11')
    lab.place(relx=0.002+0.00555*(c), rely=0.0015)
    lab.insert("1.0", win.title)
    lab.focus_set()
    lab.bind('<Return>', save_title)
    

def help_client():
    if os.path.isfile('documentation.pdf'):
        os.startfile(r"documentation.pdf")
    
# Собираем точный абсолютный путь к иконке
ICON_PATH = os.path.join(BASE_DIR, "icon.ico")

#Создание главного окна
root = tk.Tk()
root.wm_title("MatGraf")
root.state('zoomed')
root.iconbitmap(ICON_PATH)

#Главное меню
menu = tk.Menu(root, font="Times 14")

#Каскады первого пункта
menu_major = tk.Menu(menu, tearoff=0, font='Times 12')
open_how_item = tk.Menu(menu, tearoff=0, font='Times 12')
graph_item = tk.Menu(menu, tearoff=0, font='Times 12')
graph_item_err = tk.Menu(menu, tearoff=0, font='Times 12')
view = tk.Menu(menu, tearoff=0, font='Times 12')
sign = tk.Menu(menu, tearoff=0, font='Times 12')
axes = tk.Menu(menu, tearoff=0, font='Times 12')
curs = tk.Menu(menu, tearoff=0, font='Times 12')
mods = tk.Menu(menu, tearoff=0, font='Times 12')

#Открыть как график
graph_item.add_command(label=names["One_x"], command=open_file_graph_one_x)
graph_item.add_command(label=names["Without_x"], command=open_file_graph_without_x)
graph_item.add_command(label=names["Different_x"], command=open_file_graph_different_x)

#Открыть как график с погрешностями
graph_item_err.add_command(label=names["Different_x"], command=open_file_errgraph_different_x)
graph_item_err.add_command(label=names["Without_x"], command=open_file_errgraph_without_x)

#Открыть как
open_how_item.add_cascade(label=names["Grafick"], menu=graph_item)
open_how_item.add_cascade(label=names["Grafick_error"], menu=graph_item_err)
open_how_item.add_command(label=names["Histogram"], command=lambda: open_file_hist(root))
#open_how_item.add_command(label=names["Excel_data"])

#Файл
menu_major.add_command(label=names["New"], command=new_graph)
menu_major.add_cascade(label=names["Open_how"], menu=open_how_item)
menu_major.add_command(label=names["Save"], command=save_win)
menu_major.add_command(label=names["Save_how"], command=save_how)
menu_major.add_command(label=names["Save_all"], command=save_all)
menu_major.add_separator()
menu_major.add_command(label=names["Settings"], command=lambda: open_sett(root))

#Первый пункт меню
menu.add_cascade(label=names["File"], menu=menu_major)

menu.add_command(label=names["Open"], command=open_file_all)

menu.add_command(label=names["Save"], command=save_win)

#Вид
view.add_cascade(label=names["Signature"], menu=sign)
sign.add_command(label=names["Legend"], command=leg_split)
sign.add_checkbutton(label=names["Canvas_label"], command=сanvas_label)
sign.add_checkbutton(label=names["Axis_label"], command=axis_label)

view.add_cascade(label=names["Axes"], menu=axes)
axes.add_checkbutton(label=names["Major_ax"], command=maj_ax_include)
axes.add_checkbutton(label=names["Minor_ax"], command=min_ax_include)
axes.add_command(label=names["X_log_scale"], command=x_log_scale)
axes.add_command(label=names["Y_log_scale"], command=y_log_scale)
axes.add_command(label=names["Polar_ax"], command=pollar_ax)

view.add_cascade(label=names["Cursors"], menu=curs)
curs.add_command(label=names["X_cursor"], command=curs_x)
curs.add_command(label=names["Y_cursor"], command=curs_y)

menu.add_cascade(label=names["View"], menu=view)
menu.add_separator()

menu.add_cascade(label=names["Modules"], menu=mods)
for file in self_modules:
    if file.endswith('.py'):
        mods.add_command(label=file[:-3], command=lambda: new_module(file))
mods.add_separator()
mods.add_command(label=names["Add_mod"])

menu.add_command(label=names["Help"], command=help_client)

root.config(menu=menu)

#Вкладки
tab_control = ttk.Notebook(root)
menu_note = tk.Menu(tearoff=0)
menu_note.add_command(label=names["New"], command=new_graph)
menu_note.add_command(label=names["Rename"], command=rename)
menu_note.add_command(label=names["Dublicate"], command=dublicate)
menu_note.add_command(label=names["Delete"], command=delete_wind)
tab_control.bind("<Button-3>", lambda event: menu_note.post(event.x_root, event.y_root))

#Первое окно
tab_base = Window(tab_control, names, create_graph_in_new_win, sett["default_params"], names["Grafick"])

list_wins = [tab_base]

if len(sys.argv) > 1:
    open_file_all(sys.argv[1])

ttk.tkinter.mainloop()
