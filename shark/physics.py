import numpy as np



def create_waypoints(obj, cell):
    x, y = get_cell(obj)
    goal_x, goal_y = cell
    points = []
    while x != goal_x or y != goal_y:
        dx = goal_x - x
        dy = goal_y - y
        x_sign = -1 if dx < 0 else 1
        y_sign = -1 if dy < 0 else 1
        if dx:
            grad = abs(dy / dx)
            if grad <= 0.5:
                sx = 1
                sy = 0
            elif grad <= 2:
                sx = 1
                sy = 1
            else:
                sx = 0
                sy = 1
        else:
            sx = 0
            sy = 1
        x += sx * x_sign
        y += sy * y_sign
        points.append((x, y))
    points.reverse()
    return points


class O:
    def __init__(self):
        self.x = 5
        self.y = 5


print(get_block((5, 5)))
