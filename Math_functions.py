# -*- coding: utf-8 -*-
import numpy as np
import sympy as sp
import math
import re
from scipy.integrate import cumtrapz
import copy


def err(x):
    return sp.core.symbol.Symbol("Error parsing simplofy or lambdify")


def to_function(expression, var=""):
    """
    Преобразует строку с математическим выражением в функцию.

    :param expression: Строка с математическим выражением, например, "x**2 + 2*x + 1".
    :return: Функция, которая принимает x и возвращает результат вычисления выражения.
    """
    
    
    custom_function = {"sgn": sp.sign, "lg": lambda x: sp.log(x, 10), "arccos": sp.acos, "arcsin": sp.asin, "tg": sp.tan, "ctg": sp.cot, "arctg": sp.atan, 
                       "arcctg": lambda x: sp.pi/2 - sp.atan(x), "sh": sp.sinh, "ch": sp.cosh, "th": sp.tanh, "cth": sp.coth, "arcsh": sp.asinh, 
                       "arcch": sp.acosh, "arcth": sp.atanh, "arccth": lambda x: 0.5*sp.log((x+1)/(x-1)), "arccoth": lambda x: 0.5*sp.log((x+1)/(x-1)), "H": sp.Heaviside, "e": np.e}
    

    if expression == "":
        print("Void string in function!")
        return err
    
    
    if var == "":
        x, z, t = sp.symbols('x z t')
        try:
            # Преобразуем строку в символьное выражение
            expr = sp.sympify(expression, locals=custom_function)
            # Создаем функцию из выражения
            return sp.lambdify(x, expr, 'numpy')
        except:
            print("One variable, error parsing simplify or lambdify")
            return err
    else:
        try:
            x = sp.symbols(var)
            # Преобразуем строку в символьное выражение
            expr = sp.sympify(expression, locals=custom_function)
            # Создаем функцию из выражения
            return sp.lambdify(x, expr, 'numpy')
        except:
            print("More variable, error parsing simplofy or lambdify")
            return err
        

def extract_special_functions(expression, x, out_variables=""):
    """
    Разделяет строку на блоки специальных функций.
    
    Args:
        expression (str): Входная строка с математическим выражением
        
    Returns:
        tuple: (modified_expr, function_list)
            modified_expr - строка с заменёнными функциями на var1, var2, ...
            function_list - список найденных функций в исходном виде
    """

    # Шаблон для поиска специальных функций вида #Name(...)
    pattern = re.compile(r'(#[A-Za-z]+\([^()]*(?:\([^()]*\)[^()]*)*\))')
    
    # Находим все совпадения
    matches = list(pattern.finditer(expression))
    functions = []
    modified_expr = expression
    replacements = {}
    
    # Обрабатываем совпадения с конца к началу (чтобы не сбивались индексы при замене)
    for i, match in enumerate(sorted(matches, key=lambda m: -m.start()), 1):
        func = match.group(1)
        var_name = f"var{i}"
        replacements[match.span()] = (var_name, func)
    
    # Собираем модифицированную строку
    parts = []
    last_pos = 0
    for span, (var_name, func) in sorted(replacements.items()):
        start, end = span
        parts.append(modified_expr[last_pos:start])
        parts.append(var_name)
        functions.append(func)
        last_pos = end
    
    parts.append(modified_expr[last_pos:])
    modified_expr = ''.join(parts)
    
    l = len(functions)
    
    if out_variables == "":
        all_var_str = "x "
    else:
        all_var_str = out_variables
    all_var = [*x]
    
    if l == 0:
        try:
            f = to_function(modified_expr, out_variables)
            y = f(*x)
            if type(y) != np.ndarray:
                y0 = y
                y = np.array([y0])
                y.resize(x[0].shape)
                y.fill(y0)
            return y
        except:
            print("1 Error sentences")
            return err(0)
        
    for var_i in range(0, l):
        
        var_f = functions[var_i]
        
        if len(var_f) >= 12 and var_f[:9] == "#Gradient":
            y = extract_special_functions(var_f[9:], x, out_variables)
            if type(y) == sp.core.symbol.Symbol:
                return err(0)
            if len(y) <= 1:
                print("Point in Gradient!")
                return err(0)
            y = np.gradient(y, x[0])
        elif len(var_f) >= 11 and var_f[:8] == "#Antider":
            y = extract_special_functions(var_f[8:], x, out_variables)
            if type(y) == sp.core.symbol.Symbol:
                return err(0)
            if len(y) <= 1:
                print("Point in Antider!")
                return err(0)
            y = cumtrapz(y, x[0], initial=0)
            # dx = np.diff(x[0])  # Шаги по x
            # avg_y = 0.5 * (y[:-1] + y[1:])
            # F = np.zeros_like(y)
            # F[1:] = np.cumsum(avg_y * dx)
            # y = F
        elif len(var_f) >= 13 and var_f[:10] == "#ReverseAx":
            y = extract_special_functions(var_f[10:], x, out_variables)
            if type(y) == sp.core.symbol.Symbol:
                return err(0)
            if len(y) <= 1:
                print("Point in ReverseAx!")
                return err(0)
            y_test = copy.copy(y)
            y = x[0]
            x.pop(0)
            x.insert(0, y_test)
        else:
            print("Not this function")
            return err(0)
        all_var.append(y)
        all_var_str += "var" + str(l-var_i) + " "
        
    try:
        f = to_function(modified_expr, all_var_str)
        y = f(*all_var)
        if type(y) != np.ndarray:
            y0 = y
            y = np.array([y0])
            y.resize(x[0].shape)
            y.fill(y0)
        return y
    except:
        print("2 Error sentences")
        return err(0)