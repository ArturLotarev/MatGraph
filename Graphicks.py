import numpy as np
from Math_functions import to_function
import sympy as sp

def convert_data(a):
    try:
        return float(a)
    except:
        try:
            f = to_function(a)(0)
            if type(f) != int and type(f) != float and type(f) != complex:
                return np.nan
            else:
                return f
        except:
            return np.nan

class Grafick:
    def __init__(self, x, y, ax, canvas, dx=[], dy=[], s=[], test=False, visual_annotates=False):
        #Список параметров
        self.leg_label = " "
        self.point = "."
        self.line = "-"
        self.color = "blue"
        self.width = 0.8
        self.capsize = 20
        self.test = test
        self.vis_ann = visual_annotates
        self.ann = []
        self.s = s
        self.d = 1
        self.weight = []
        
        self.ax = ax
        self.canvas = canvas
        
        self.plot, self.scatter, self.plot_h = 0, 0, 0
        self.fill = False
        
        self.sett = [1, 0, 0]
        
        # if test:
        #     x = np.array(list(map(convert_data, x)))
        #     y = np.array(list(map(convert_data, y)))

        #     l = max(len(x), len(y))
        #     self.x, self.y = np.resize(x, (l)), np.resize(y, (l))
        # else:
        l = len(x)
        self.x, self.y = x, y

        
        d = np.empty((l))
        d.fill(np.nan)
        if len(dx) != 0:
            if test:
                dx = np.array(list(map(convert_data, dx)))
            else:
                dx = np.array(dx)
            dx = np.append(dx, d)
            self.dx = np.resize(dx, (l))
        else:
            self.dx = d
        if len(dy) != 0:
            if test:
                dy = np.array(list(map(convert_data, dy)))
            else:
                dy = np.array(dy)
            dy = np.append(dy, d)
            self.dy = np.resize(dy, (l))
        else:
            self.dy = d
            

    def show(self, sett=[1, 0, 0]):
        self.sett = sett
        
        if not self.test:
            y = self.masked(self.y)
        else:
            y = self.y
        
        if sett[1]:
            self.plot, = self.ax.plot(self.x, y, color=self.color, linestyle=self.line, linewidth=self.width, label=self.leg_label)
            
        if sett[0]:
            if np.isnan(self.dx).all() and np.isnan(self.dy).all():
                self.scatter = self.ax.scatter(self.x, y, color=self.color, marker=self.point, s=self.capsize, label=self.leg_label)
            elif not np.isnan(self.dx).all() and not np.isnan(self.dy).all():
                self.scatter = self.ax.errorbar(self.x, y, xerr=self.dx, yerr=self.dy, fmt=self.point, linewidth=self.width, capsize=self.capsize, color=self.color, label=self.leg_label)
            elif np.isnan(self.dx).all():
                self.scatter = self.ax.errorbar(self.x, y, yerr=self.dy, fmt=self.point, linewidth=self.width, capsize=self.capsize, color=self.color, label=self.leg_label)
            else:
                self.scatter = self.ax.errorbar(self.x, y, xerr=self.dx, fmt=self.point, linewidth=self.width, capsize=self.capsize, color=self.color, label=self.leg_label)
               
        if sett[2]:
            stair = np.append(self.x - self.d/2, self.d+self.x[-1])
            self.plot_h = self.ax.stairs(self.y, stair, fill=self.fill, color=self.color)

        if self.vis_ann and self.s != []:
            self.ann = []
            i = 0
            for s in self.s:
                self.ann.append(self.ax.annotate(s, (self.x[i], self.y[i] + (self.ax.set_ylim()[1] - self.ax.set_ylim()[0])/20), ha='center'))
                i += 1
        
        self.canvas.draw()
        

    def remove(self):
        if self.plot:
            self.plot.remove()
            self.plot = 0
            
        if self.scatter:
            self.scatter.remove()
            self.scatter = 0
            
        if self.plot_h:
            self.plot_h.remove()
            self.plot_h = 0
            
        if self.ann != []:
            for a in self.ann:
                a.remove()
            self.ann = []
            
        self.canvas.draw()
        
    def repaint(self, sett):
        self.remove()
        self.show(sett=sett)
        
    def hide(self, i):
        if self.plot:
            self.plot.set_visible(i)
        if self.scatter:
            self.scatter.set_visible(i)
        if self.plot_h:
            self.plot_h.set_visible(i)
        if self.ann != [] and self.vis_ann:
            for a in self.ann:
                a.set_visible(i)
        self.canvas.draw()
        
    def masked(self, y):
        y0, y1 = self.ax.get_ylim()[0], self.ax.get_ylim()[1]
        mx = max(y0, y1)
        mn = min(y0, y1)
        y = np.ma.masked_where(y>mx + abs(mx)*10, y)
        y = np.ma.masked_where(y<mn - abs(mn)*10, y)
        return y
    
    def save(self):
        return [self.leg_label, self.point, self.line, self.color, self.width, self.capsize, self.test, self.vis_ann, self.s, self.d, list(np.array(self.weight).data), self.fill, self.sett, list(np.array(self.x).data), list(np.array(self.y).data), list(np.array(self.dx).data), list(np.array(self.dy).data)]

class Cursor:
    def __init__(self, ax, x, vert=True, color="black", line="--", width=1.5, polar=False):
        self.ax = ax
        self.vert = vert
        self.color = color
        self.line = line
        self.width = width
        self.x = x
        self.active = 0
        self.polar = polar
        if vert:
            self.curs, = ax.plot([x, x], [ax.get_ylim()[0], ax.get_ylim()[1]], linestyle=line, linewidth=width, color=color)
        else:
            if polar:
                fi = np.linspace(0, 2*np.pi, 1000)
                r = fi.copy()
                r.fill(x)
                self.curs, = ax.plot(fi, r, linestyle=line, linewidth=width, color=color)
            else:
                self.curs, = ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [x, x], linestyle=line, linewidth=width, color=color)
            
    def step(self, x):
        if self.active:
            self.curs.remove()
            self.x = x
            if self.vert:
                self.curs, = self.ax.plot([x, x], [self.ax.get_ylim()[0], self.ax.get_ylim()[1]], linestyle=self.line, linewidth=self.width, color=self.color)
            else:
                if self.polar:
                    fi = np.linspace(0, 2*np.pi, 1000)
                    r = fi.copy()
                    r.fill(x)
                    self.curs, = self.ax.plot(fi, r, linestyle=self.line, linewidth=self.width, color=self.color)
                else:
                     self.curs, = self.ax.plot([self.ax.get_xlim()[0], self.ax.get_xlim()[1]], [x, x], linestyle=self.line, linewidth=self.width, color=self.color)
            
    def remove(self):
        self.curs.remove()
        
    def paint(self):
        if self.vert:
            self.curs, = self.ax.plot([self.x, self.x], [self.ax.get_ylim()[0], self.ax.get_ylim()[1]], linestyle=self.line, linewidth=self.width, color=self.color)
        else:
            if self.polar:
                fi = np.linspace(0, 2*np.pi, 1000)
                r = fi.copy()
                r.fill(self.x)
                self.curs, = self.ax.plot(fi, r, linestyle=self.line, linewidth=self.width, color=self.color)
            else:
                self.curs, = self.ax.plot([self.ax.get_xlim()[0], self.ax.get_xlim()[1]], [self.x, self.x], linestyle=self.line, linewidth=self.width, color=self.color)

    def save(self):
        return [self.vert, self.color, self.line, self.width, float(self.x), self.polar]



