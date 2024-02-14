import tkinter as tk
from tkinter import ttk
from shapely.geometry import LineString, Point, MultiPoint, Polygon
import math

class DrawingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Zeichen-App")
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Datei", menu=self.file_menu)
        self.file_menu.add_command(label="Drucken", command=self.print_canvas)
        self.canvas = tk.Canvas(self.master, width=500, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.directions = ['Rechts', 'Links', 'Oben', 'Unten']
        self.direction = tk.StringVar()
        self.dropdown = ttk.Combobox(self.master, textvariable=self.direction)
        self.dropdown['values'] = self.directions
        self.dropdown.current(0)
        self.dropdown.pack(side='bottom')
        self.entry = tk.Entry(self.master)
        self.entry.pack(side='bottom')
        self.button = tk.Button(self.master, text="Fertig", command=self.draw_line)
        self.button.pack(side='bottom')
        self.back_button = tk.Button(self.master, text="Zurück", command=self.delete_last_line)
        self.back_button.pack(side='bottom')
        self.clear_button = tk.Button(self.master, text="Löschen", command=self.clear_all)
        self.clear_button.pack(side='bottom')
        self.connect_button = tk.Button(self.master, text="Verbinden", command=self.connect_points)
        self.connect_button.pack(side='bottom')
        self.point_entry1 = tk.Entry(self.master)
        self.point_entry1.pack(side='bottom')
        self.point_entry2 = tk.Entry(self.master)
        self.point_entry2.pack(side='bottom')
        self.x, self.y = 250, 250
        self.lines = []
        self.intersections = []
        self.selected_points = []
        self.polygons = []
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<Button-2>", self.select_point)
    def calculate_area(self):
    # Hier können Sie den Code hinzufügen, der benötigt wird, um die Fläche zu berechnen.
        pass
    def draw_line(self):
        direction = self.direction.get()
        distance = float(self.entry.get().replace(',', '.'))
        old_x, old_y = self.x, self.y
        if direction == 'Rechts':
            self.x += distance
        elif direction == 'Links':
            self.x -= distance
        elif direction == 'Oben':
            self.y -= distance
        elif direction == 'Unten':
            self.y += distance
        line_id = self.canvas.create_line(old_x, old_y, self.x, self.y)
        text_id = self.canvas.create_text((old_x + self.x)/2, (old_y + self.y)/2 - 10, text=str(distance))
        line = LineString([(old_x, old_y), (self.x, self.y)])
        self.lines.append((line, line_id, text_id))
        if len(self.lines) == 1 or not Point(old_x, old_y).equals(self.intersections[-1][0]):
            oval_id = self.canvas.create_oval(old_x - 5, old_y - 5, old_x + 5, old_y + 5, fill='red')
            self.intersections.append((Point(old_x, old_y), oval_id))
        oval_id = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill='red')
        self.intersections.append((Point(self.x, self.y), oval_id))
        for i in range(len(self.lines) - 1):
            if self.lines[i][0].intersects(line):
                intersection = self.lines[i][0].intersection(line)
                if isinstance(intersection, Point):
                    oval_id = self.canvas.create_oval(intersection.x - 5, intersection.y - 5, intersection.x + 5, intersection.y + 5, fill='red')
                    self.intersections.append((intersection, oval_id))
                elif isinstance(intersection, MultiPoint):
                    for point in intersection:
                        oval_id = self.canvas.create_oval(point.x - 5, point.y - 5, point.x + 5, point.y + 5, fill='red')
                        self.intersections.append((point, oval_id))
        if self.x < 0 or self.y < 0 or self.x > self.canvas.winfo_width() or self.y > self.canvas.winfo_height():
            dx = max(0, -self.x) + min(0, self.canvas.winfo_width() - self.x)
            dy = max(0, -self.y) + min(0, self.canvas.winfo_height() - self.y)
            self.canvas.move(tk.ALL, dx, dy)
            self.x += dx
            self.y += dy
        for i, (point, oval_id) in enumerate(self.intersections, start=1):
            self.canvas.create_text(point.x, point.y - 10, text=f'#{i}', fill='red')
        self.calculate_area()

    def delete_last_line(self):
        if self.lines:
            _, line_id, text_id = self.lines.pop()
            self.canvas.delete(line_id)
            self.canvas.delete(text_id)
            if self.lines:
                line, _, _ = self.lines[-1]
                self.x, self.y = line.coords[-1]
            else:
                self.x, self.y = 250, 250
            for _, oval_id in self.intersections:
                self.canvas.delete(oval_id)
            self.intersections = []
            for line, line_id, text_id in self.lines:
                old_x, old_y = line.coords[0]
                oval_id = self.canvas.create_oval(old_x - 5, old_y - 5, old_x + 5, old_y + 5, fill='red')
                self.intersections.append((Point(old_x, old_y), oval_id))
                self.x, self.y = line.coords[-1]
                oval_id = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill='red')
                self.intersections.append((Point(self.x, self.y), oval_id))
            for i, (point, oval_id) in enumerate(self.intersections, start=1):
                self.canvas.create_text(point.x, point.y - 10, text=f'#{i}', fill='red')

    def clear_all(self):
        self.canvas.delete("all")
        self.lines = []
        self.intersections = []
        self.selected_points = []
        self.x, self.y = 250, 250

    def start_move(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def stop_move(self, event):
        pass

    def select_point(self, event):
        click_point = Point(event.x, event.y)
        for intersection, oval_id in self.intersections:
            if intersection.distance(click_point) < 5:
                self.canvas.itemconfig(oval_id, fill='green')
                if len(self.selected_points) == 2:
                    self.canvas.delete(self.selected_points.pop(0)[2])
                x, y = intersection.x, intersection.y
                line_id = self.canvas.create_line(self.selected_points[0][0] if self.selected_points else x, self.selected_points[0][1] if self.selected_points else y, x, y, fill='blue')
                self.selected_points.append((x, y, line_id))
                if len(self.selected_points) == 2:
                    distance = math.sqrt((self.selected_points[0][0] - self.selected_points[1][0])**2 + (self.selected_points[0][1] - self.selected_points[1][1])**2)
                    self.canvas.create_text((self.selected_points[0][0] + self.selected_points[1][0])/2, (self.selected_points[0][1] + self.selected_points[1][1])/2 - 10, text="{:.2f}".format(distance), fill='blue')
                break

    def connect_points(self):
        point1 = int(self.point_entry1.get().replace('#', ''))
        point2 = int(self.point_entry2.get().replace('#', ''))
        if 1 <= point1 <= len(self.intersections) and 1 <= point2 <= len(self.intersections):
            intersection1, oval_id1 = self.intersections[point1 - 1]
            intersection2, oval_id2 = self.intersections[point2 - 1]
            self.canvas.itemconfig(oval_id1, fill='green')
            self.canvas.itemconfig(oval_id2, fill='green')
            x1, y1 = intersection1.x, intersection1.y
            x2, y2 = intersection2.x, intersection2.y
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill='blue')
            distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2 - 10, text="{:.2f}".format(distance), fill='blue')

    def print_canvas(self):
    # Hier können Sie den Code hinzufügen, der benötigt wird, um das Canvas zu drucken.
        pass

root = tk.Tk()
app = DrawingApp(root)
root.mainloop()





