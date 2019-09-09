import matplotlib.pyplot as plt
import os
import sys
import numpy as np
from model import SimpleBrep

def display_brep(model):
    vertices = model.vertices
    lines = model.lines
    for _, (x, y) in vertices.items():
        plt.plot(x, y, 'bo')
    for _, (v0, v1, t) in lines.items():
        x0, y0 = vertices[v0]
        x1, y1 = vertices[v1]
        color = 'r' if t == 'v' else 'g'
        plt.plot([x0, x1], [y0, y1], color)
    plt.title('red: vertical lines; green: horizontal lines; blue: vertices')
    plt.show()

if __name__ == '__main__':
    model = SimpleBrep()
    model.load_brep(sys.argv[1])
    display_brep(model)
