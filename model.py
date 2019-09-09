import sys
import os
import numpy as np

class TaoExcept(Exception):
    pass

np_type = np.float64

def is_number(value):
    try:
        v = float(value)
    except:
        return False
    return True

def is_valid_name(value):
    for c in value:
        if not ('0' <= c <= '9' or 'a' <= c <= 'z' or 'A' <= c <= 'Z'): return False
    return True

def same_model(model1, model2):
    # First, check if they have the same set of vertices.
    v2_names = set([v for v in model2.vertices])
    v1to2 = {}
    for v1, (x, y) in model1.vertices.items():
        found = False
        for v2 in v2_names:
            x2, y2 = model2.vertices[v2]
            if x == x2 and y == y2:
                v1to2[v1] = v2
                v2_names.remove(v2)
                found = True
                break
        if not found: return False
    if v2_names: return False
    # Now we are sure all the vertices are the same. Check the lines.
    l2_names = set([l for l in model2.lines])
    for l1, (v1, v2, _) in model1.lines.items():
        v1 = v1to2[v1]
        v2 = v1to2[v2]
        found = False
        for l2 in l2_names:
            s2, t2, _ = model2.lines[l2]
            if (v1 == s2 and v2 == t2) or (v1 == t2 and v2 == s2):
                found = True
                l2_names.remove(l2)
                break
        if not found: return False
    return not l2_names

class SimpleBrep(object):
    def __init__(self):
        self.vertices = {}
        self.lines = {}
        self.used_names = set()
    
    @staticmethod
    def parse_command(some_string):
        """
        Input a string
        Output an AST object
        """
        assert type(some_string) == type(""), "you crazy"
        # TODO: write this
        raise NotImplementedError

    def check_brep(self):
        # First, all names must be valid and unique.
        for n in self.vertices:
            if not is_valid_name(n):
                #print('invalid vertex name:', n)
                raise TaoExcept()
        for n in self.lines:
            if not is_valid_name(n):
                #print('invalid line name:', n)
                raise TaoExcept()
        for n in self.vertices:
            if n in self.lines:
                #print('duplicated vertex and line names:', n)
                raise TaoExcept()
        for n in self.lines:
            if n in self.vertices:
                #print('duplicated vertex and line names:', n)
                raise TaoExcept()
        # For vertices, all positions must be unique.
        for n1, (x1, y1) in self.vertices.items():
            for n2, (x2, y2) in self.vertices.items():
                if n1 >= n2: continue
                if x1 == x2 and y1 == y2:
                    #print('two same vertices:', n1, n2)
                    raise TaoExcept()
        # Now all vertices are valid.

        # Now check lines. First, check if they are either horizontal or vertical.
        new_lines = {}
        for l, (v0, v1, t) in self.lines.items():
            if v0 == v1:
                #print('degenerated lines:', l)
                raise TaoExcept()
            if v0 not in self.vertices or v1 not in self.vertices:
                #print('line uses undefined vertex:', v0, v1)
                raise TaoExcept()
            x0, y0 = self.vertices[v0]
            x1, y1 = self.vertices[v1]
            if t == 'h':
                if y0 != y1:
                    #print('line', l, 'is not horizontal.')
                    raise TaoExcept()
                if x0 > x1:
                    # Swap.
                    v0, v1 = v1, v0
                new_lines[l] = (v0, v1, t)
            elif t == 'v':
                if x0 != x1:
                    #print('line', l, 'is not vertical.')
                    raise TaoExcept()
                if y0 > y1:
                    v0, v1 = v1, v0
                new_lines[l] = (v0, v1, t)
            elif t == 'u':
                # Determine the type now.
                if x0 == x1:
                    if y0 > y1:
                        v0, v1 = v1, v0
                    new_lines[l] = (v0, v1, 'v')
                elif y0 == y1:
                    if x0 > x1:
                        v0, v1 = v1, v0
                    new_lines[l] = (v0, v1, 'h')
                else:
                    #print('cannot process lines that are not horizontal or vertical:', l)
                    raise TaoExcept()
            else:
                #print('undefined type:', t)
                raise TaoExcept()
        self.lines = new_lines
        # Now we know:
        # Each line uses two different vertices.
        # Each line is either vertical or horizontal.
        # Each line either goes from left to right or bottom to top.

        # Next, we will check if two lines are the same.
        for l1, (s1, e1, _) in self.lines.items():
            for l2, (s2, e2, _) in self.lines.items():
                if l1 >= l2: continue
                if s1 == s2 and e1 == e2:
                    #print('duplicated lines:', l1, l2)
                    raise TaoExcept()

        # Next, we check if a line crosses a vertex.
        for l, (v0, v1, t) in self.lines.items():
            fixed_idx = 1 if t == 'h' else 0
            x0 = self.vertices[v0][1 - fixed_idx]
            x1 = self.vertices[v1][1 - fixed_idx]
            for vn, v in self.vertices.items():
                if v[fixed_idx] == self.vertices[v0][fixed_idx] and x0 < v[1 - fixed_idx] < x1:
                    #print('should have splitted line', l, 'with vertex', vn)
                    raise TaoExcept()

        # Finally, check if two lines cross each other.
        for l1, (s1, e1, t1) in self.lines.items():
            for l2, (s2, e2, t2) in self.lines.items():
                if l1 >= l2 or t1 == t2: continue
                if t1 == 'v':
                    s1, s2 = s2, s1
                    e1, e2 = e2, e1
                # Now (s1, e1) is horizontal and (s2, e2) is vertical.
                x1 = self.vertices[s1][0]
                x2 = self.vertices[e1][0]
                x0 = self.vertices[s2][0]
                y1 = self.vertices[s2][1]
                y2 = self.vertices[e2][1]
                y0 = self.vertices[s1][1]
                if x1 < x0 < x2 and y1 < y0 < y2:
                    #print('line', l1, 'and', l2, 'cross.')
                    raise TaoExcept()

    def load_brep(self, brep_file_name):
        vertices = {}
        lines = {}
        with open(brep_file_name, 'r') as f:
            while True:
                line = f.readline()
                if not line: break
                line = line.strip()
    
                # Ignore comments.
                if '#' in line:
                    line = line[:line.find('#')].strip()
    
                # Ignore empty lines.
                if not line: continue
                tokens = line.split()
                if not tokens: continue
    
                # Ignore invalid number of tokens.
                if len(tokens) != 3:
                    #print('invalid syntax:', line)
                    raise TaoExcept()
    
                # Check if it is a vertex or a line.
                if is_number(tokens[1]):
                    # Parse a vertex.
                    v_name = tokens[0]
                    x, y = float(tokens[1]), float(tokens[2])
                    vertices[v_name] = np.array([x, y], dtype=np_type)
                else:
                    # Parse a line.
                    l_name = tokens[0]
                    v0_name, v1_name = tokens[1:]
                    # 'u' stands for undefined. It will be determined in check_brep.
                    lines[l_name] = (v0_name, v1_name, 'u')
        self.vertices = vertices
        self.lines = lines
        self.check_brep()
        self.used_names = set()
        for n in self.vertices:
            self.used_names.add(n)
        for n in self.lines:
            self.used_names.add(n)

    def save_brep(self, brep_file_name):
        with open(brep_file_name, 'w') as f:
            for v, (x, y) in self.vertices.items():
                f.write('{} {} {}\n'.format(v, x, y))

            for l, (v0, v1, _) in self.lines.items():
                f.write('{} {} {}\n'.format(l, v0, v1))

    def new_name(self):
        cnt = 0
        while True:
            name = 'n' + str(cnt)
            if name not in self.used_names:
                self.used_names.add(name)
                return name
            cnt += 1

    def execute_vertex_command(self, tokens):
        name = tokens[0]
        def extract_coord(token, idx):
            if is_number(token):
                return float(token)
            if token in self.vertices:
                return self.vertices[token][idx]
            if token in self.lines:
                v1, v2, t = self.lines[token]
                if (idx == 0 and t == 'h') or (idx == 1 and t == 'v'):
                    #print('you cannot extract x (y) from a horizontal (vertical) line:', token)
                    raise TaoExcept()
                return self.vertices[v1][idx]
            if '_' in token:
                line, flag = token.split('_')
                if line not in self.lines:
                    #print('invalid lines:', line)
                    raise TaoExcept()
                v1, v2, t = self.lines[line]
                if (t == 'h' and flag not in ['left', 'right']) or (t == 'v' and flag not in ['top', 'bottom']):
                    #print('invalid orientation flag:', token)
                    raise TaoExcept()
                if flag == 'left' or flag == 'bottom':
                    return self.vertices[v1][idx]
                elif flag == 'right' or flag == 'top':
                    return self.vertices[v2][idx]
                else:
                    #print('unknown flag:', flag)
                    raise TaoExcept()
            #print('invalid token:', token)
            raise TaoExcept()

        # Grab x.
        vx = extract_coord(tokens[1], 0)
        vy = extract_coord(tokens[2], 1)

        # First, check if this vertex is new.
        if not is_valid_name(name) or name in self.vertices or name in self.lines:
            #print('invalid or duplicated name:', name)
            raise TaoExcept()
        for n, (x, y) in self.vertices.items():
            if vx == x and vy == y:
                #print('duplicated vertices:', name, n)
                raise TaoExcept() 
        self.vertices[name] = np.array([vx, vy], dtype=np_type)
        self.used_names.add(name)
        # Check if we need to further segment any lines.
        new_lines = {}
        for l, (v0, v1, t) in self.lines.items():
            v0x, v0y = self.vertices[v0]
            v1x, v1y = self.vertices[v1]
            if t == 'h' and v0y == vy and v0x < vx < v1x:
                # Split it into two horizontal lines.
                l1 = self.new_name()
                new_lines[l1] = (v0, name, 'h')
                l2 = self.new_name()
                new_lines[l2] = (name, v1, 'h')
            elif t == 'v' and v0x == vx and v0y < vy < v1y:
                # Split it into two vertical lines.
                l1 = self.new_name()
                new_lines[l1] = (v0, name, 'v')
                l2 = self.new_name()
                new_lines[l2] = (name, v1, 'v')
            else:
                new_lines[l] = (v0, v1, t)
        self.lines = new_lines
        self.check_brep()

    def execute_line_command(self, tokens):
        name = tokens[0]
        if not is_valid_name(name) or name in self.vertices or name in self.lines:
            #print('invalid or duplicated names:', name)
            raise TaoExcept()
        if tokens[1] not in ['v', 'h']:
            #print('invalid line type:', tokens[1])
            raise TaoExcept() 
        new_t = tokens[1]
        if tokens[2] != 'start':
            #print('invalid token, expect to see start:', tokens[2])
            raise TaoExcept()

        def try_new_vertex(x, y):
            for n, (vx, vy) in self.vertices.items():
                if x == vx and y == vy:
                    return n
            n = self.new_name()
            self.execute_vertex_command([n, x, y])
            return n

        def parse_line_endpoints(token):
            line, flag = token.split('_')
            if line not in self.lines:
                #print('invalid line:', line)
                raise TaoExcept()
            v1, v2, t = self.lines[line]
            if (t == 'h' and flag not in ['left', 'right']) or (t == 'v' and flag not in ['top', 'bottom']):
                #print('invalid orientation flag:', flag)
                raise TaoExcept()
            if flag == 'left' or flag == 'bottom':
                return v1
            elif flag == 'right' or flag == 'top':
                return v2
            else:
                #print('unknown flag:', flag)
                raise TaoExcept()

        # Get the starting vertex.
        if is_number(tokens[3]):
            start_v = try_new_vertex(float(tokens[3]), float(tokens[4]))
        else:
            # It must be an existing vertex.
            if tokens[3] in self.vertices:
                start_v = tokens[3]
            elif '_' in tokens[3]:
                start_v = parse_line_endpoints(tokens[3])
            else:
                #print('invalid vertex name:', tokens[3])
                raise TaoExcept()

        sx, sy = self.vertices[start_v]
        ex, ey = sx, sy
        end_v = ''
        # Now get the ending point.
        if tokens[-2] != 'end':
            #print('invalid token. expect to see end:', tokens[-2])
            raise TaoExcept()
        if is_number(tokens[-1]):
            length = float(tokens[-1])
            if new_t == 'h':
                ex += length
            else:
                ey += length
            end_v = try_new_vertex(ex, ey)
        elif tokens[-1] in self.vertices:
            end_v = tokens[-1]
        elif '_' in tokens[-1]:
            end_v = parse_line_endpoints(tokens[-1])
        elif tokens[-1] in self.lines:
            v1, _, t = self.lines[tokens[-1]]
            if new_t == t:
                #print('cannot use the same type of lines to define the endpoint:', tokens[-1])
                raise TaoExcept()
            if new_t == 'h':
                ex = self.vertices[v1][0]
            else:
                ey = self.vertices[v1][1]
            end_v = try_new_vertex(ex, ey)
        else:
            #print('invalid token:', tokens[-1])
            raise TaoExcept()

        # Now we have start_v and end_v. 
        sx, sy = self.vertices[start_v]
        ex, ey = self.vertices[end_v]
        if (new_t == 'h' and sy != ey) or (new_t == 'v' and sx != ex):
            #print('inconsistent endpoints and line type:', sx, sy, ex, ey, new_t)
            raise TaoExcept()
        if (new_t == 'h' and sx > ex) or (new_t == 'v' and sy > ey):
            start_v, end_v = end_v, start_v
        self.lines[name] = (start_v, end_v, new_t)
        self.used_names.add(name)
        self.resolve_overlap_lines()
        self.resolve_cross_lines()
        self.check_brep()

    def resolve_overlap_lines(self):
        new_lines = {}
        new_segmented_lines = {}
        for l, (v1, v2, t) in self.lines.items():
            fixed_idx = 1 if t == 'h' else 0
            x0 = self.vertices[v1][1 - fixed_idx]
            x1 = self.vertices[v2][1 - fixed_idx]
            y = self.vertices[v1][fixed_idx]
            middle = []
            for vn, v in self.vertices.items():
                vx = v[1 - fixed_idx]
                vy = v[fixed_idx]
                if vy == y and x0 < vx < x1:
                    middle.append((vx, vn))
            if middle:
                middle = sorted(middle, key=lambda v : v[0])
                middle = [(x0, v1)] + middle + [(x1, v2)]
                for i in range(len(middle) - 1):
                    new_ln = self.new_name()
                    new_segmented_lines[new_ln] = (middle[i][1], middle[i + 1][1], t)
            else:
                new_lines[l] = (v1, v2, t)
        # If a new segmented lines have not been seen before, add it.
        for l, (s, e, t) in new_segmented_lines.items():
            skip = False
            for l2, (s2, e2, _) in new_lines.items():
                if s == s2 and e == e2:
                    skip = True
                    break
            if not skip:
                new_lines[l] = (s, e, t)
        self.lines = new_lines

    def resolve_cross_lines(self):
        intersections = {}
        for l1, (s1, e1, t1) in self.lines.items():
            fixed_idx = 1 if t1 == 'h' else 0
            x0 = self.vertices[s1][1 - fixed_idx]
            x1 = self.vertices[e1][1 - fixed_idx]
            y = self.vertices[s1][fixed_idx]
            for l2, (s2, e2, t2) in self.lines.items():
                if l1 >= l2 or t1 == t2: continue
                y0 = self.vertices[s2][fixed_idx]
                y1 = self.vertices[e2][fixed_idx]
                x = self.vertices[s2][1 - fixed_idx]
                if x0 < x < x1 and y0 < y < y1:
                    n_v = self.new_name()
                    intersections[n_v] = (x, y) if t1 == 'h' else (y, x)
        for n, (x, y) in intersections.items():
            self.execute_vertex_command([n, x, y])

    def execute_command(self, command):
        #TODO: use parse_command here
        tokens = command.split()
        if len(tokens) == 3:
            # Vertex.
            self.execute_vertex_command(tokens)
        elif len(tokens) == 6 or len(tokens) == 7:
            # Line.
            self.execute_line_command(tokens)
        else:
            #print('invalid command:', command)
            raise TaoExcept() 

    def execute_command_file(self, command_file_name):
        with open(command_file_name, 'r') as f:
            while True:
                line = f.readline()
                if not line: break
                line = line.strip()
    
                # Ignore comments.
                if '#' in line:
                    line = line[:line.find('#')].strip()
    
                # Ignore empty lines.
                if not line: continue
                tokens = line.split()
                if not tokens: continue

                self.execute_command(line)

def run(command_file_name, brep_name):
    model = SimpleBrep()
    model.execute_command_file(command_file_name)
    model.save_brep(brep_name)

if __name__ == '__main__':
    command_file_name = sys.argv[1]
    name, ext = command_file_name.split('.')
    brep_name = name + '.brep'
    run(command_file_name, brep_name)
