import sys
import numpy as np
import matplotlib.pyplot as plt
from display import display_brep
from model import SimpleBrep, same_model

def print_error(*message):
    print('\033[91m', 'ERROR ', *message, '\033[0m')

def print_ok(*message):
    print('\033[92m', *message, '\033[0m')

def print_warning(*message):
    print('\033[93m', *message, '\033[0m')

def display(current_model, target_model, name='haha.png'):
    fig, (axes_current, axes_target) = plt.subplots(1, 2)
    def display_model(ax, model, title):
        vertices = model.vertices
        lines = model.lines
        for _, (x, y) in vertices.items():
            ax.plot(x, y, 'bo')
        for _, (v0, v1, t) in lines.items():
            x0, y0 = vertices[v0]
            x1, y1 = vertices[v1]
            color = 'r' if t == 'v' else 'g'
            ax.plot([x0, x1], [y0, y1], color)
        ax.set_title(title)
    display_model(axes_current, current_model, 'current')
    display_model(axes_target, target_model, 'target')
    plt.savefig(name)
    plt.clf()

def run(target_file):
    target_model = SimpleBrep()
    target_model.load_brep(target_file)

    # Start playing interactively.
    current_model = SimpleBrep()
    print('all vertices in the target model:')
    for v, (x, y) in enumerate(target_model.vertices.items()):
        print('name:', v, 'val:', x, y)
    print('you can use them to replicate the target model.')
    print('to create a new vertex from numerical values, type the following command:')
    print_ok('v0 <name> <x> <y>')
    print('to create a new vertex by referencing existing lines or vertices, type the following command:')
    print_ok('v1 <name> <vertex or line name> <vertex or line name>')
    print('to create a new vertex by mixing numerical values and references, type the following command:')
    print_ok('v2 <name> <x> <vertex or line name>')
    print_ok('v3 <name> <vertex or line name> <y>')
    print('to create a new line from numerical values, type the following command:')
    print_ok('l0 <name> <v|h> <x> <y> <length>')
    print('to create a new line by referencing existing entities, type the following command:')
    print_ok('l1 <name> <v|h> <vertex name> <vertex or line name>')
    print('to create a new line by mixing numerical values and references, type the following command:')
    print_ok('l2 <name> <v|h> <x> <y> <vertex or line name>')
    print_ok('l3 <name> <v|h> <vertex name> <length>')
    print('your goal is to replicate the target model while minimizing the number of commands you type')

    print_ok('sample solution for square.brep')
    print('l0 left v 0 0 1')
    print('l3 top h n1 1')
    print('l3 right v n2 -1')
    print('l1 bottom h n0 n3')

    print_ok('sample solution for flag.brep')
    print('l1 left v 0 0 2')
    print('l3 top h n1 1')
    print('l3 right v n2 -1')
    print('l3 bottom h n3 left')

    while True:
        # Show the current progress.
        print('displaying the current progress. press alt + f4 to continue...')
        display(current_model, target_model)

        # Enumerate all vertices and lines.
        print('all vertices:')
        for v, (x, y) in current_model.vertices.items():
            print('name:', v, 'val:', x, y)
        print('all lines:')
        for l, (v0, v1, t) in current_model.lines.items():
            print('name:', l, 'end points:', v0, v1, 'type:', t)
        print('type in your command:')
        s = input()
        #TODO use parse_command here
        tokens = s.strip().split()
        try:
            if tokens[0] in ['v0', 'v1', 'v2', 'v3']:
                command = ' '.join(tokens[1:])
            else:
                command = ' '.join(tokens[1:3] + ['start'] + tokens[3:-1] + ['end', tokens[-1]])
            current_model.execute_command(command)
        except:
            print_error('invalid command, please retry.')
        if same_model(current_model, target_model):
            print('you have solved the problem!')
            break

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python play.py square.brep')
        sys.exit(0)
    target_file = sys.argv[1]
    run(target_file)
