from util import *
from PIL import Image, ImageDraw, ImageFont
import random, math
from math import cos, sin


class Cube:
    #clockwis
    face_dict = {'U':0, 'L':1, 'F':2, 'R':3, 'B':4, 'D': 5}
    rot = {'x': (3, 1),'y': (0, 5), 'z': (2, 4)}
    net = [[4, 3, 2, 1], [0, 2, 5, 4], [0, 3, 5, 1], [0, 4, 5, 2], [1, 5, 3, 0], [1, 2, 3, 4]]
    touching = [[0]*4, [3, 3, 3, 1], [2, 3, 0, 1], [1, 3, 1, 1], [3, 2, 1, 0], [2]*4]
    orientation = [[1]*4, [1, 1, 1, 0], [1, 1, 0, 0], [1, 0, 1, 1], [1, 1, 0, 0], [1]*4]
    def __init__(self, size):
        self.sides = [Face(size, i) for i in range(6)]
        self.size = size
        for s, n, t, o in zip(self.sides, self.net, self.touching, self.orientation):
            s.neighbors = [self.sides[i] for i in n]
            s.touching = t[:]
            s.orientation = o
    def do(self, moves):
        moves = moves.split(' ')
        for move in moves:
            self.step(move)
    def get_num(self, s1, s2):
        if s1 == "'":
            return -1
        if s1 == "2":
            return 2
        if s1 == s2:
            return 1
        return None
    def step(self, move):
        if move[0] in self.rot:
            if len(move) == 1:
                turns = 1
            elif len(move) == 2:
                turns = self.get_num(move[1], move[0])
                if turns is None:
                    raise ValueError(f"Invalid move {move}")
            else:
                raise ValueError(f"Invalid move {move}")
            f1, f2 = self.rot[move[0]]
            f1, f2 = self.sides[f1], self.sides[f2]
            f1.turn(turns, self.size-1)
            if abs(turns) == 1:
                turns *= -1
            f2.turn(turns, 1)
        elif (move[0].islower() or len(move) > 1 and move[1] == 'w') and move[0].upper() in self.face_dict:
            face = self.sides[self.face_dict[move[0].upper()]]
            x = 2 if len(move) > 1 and move[1] == 'w' else 1
            if len(move) == x:
                turns = 1
            elif len(move) == x+1:
                turns = self.get_num(move[-1], move[-2])
                if turns is None:
                    raise ValueError(f"Invalid move {move}")
            else:
                raise ValueError(f"Invalid move {move}")
            face.turn(turns, 2)
        elif move[0].isdigit():
            layers = int(move[0])
            if layers <2 or layers >= self.size:
                raise ValueError(f"Invalid move {move}")
            if move[1] not in self.face_dict:
                raise ValueError(f"Invalid move {move}")
            face = self.sides[self.face_dict[move[1]]]
            narrow = False
            if len(move) >= 3 and move[2] == 'w':
                if len(move) == 3:
                    turns = 1
                elif len(move) == 4:
                    turns = self.get_num(move[-1], move[-2])
                    if turns is None:
                        raise ValueError(f"Invalid move {move}")
                else:
                    raise ValueError(f"Invalid move {move}")
            else:
                narrow = True
                if len(move) == 2:
                    turns = 1
                elif len(move) == 3:
                    turns = self.get_num(move[-1], move[-2])
                    if turns is None:
                        raise ValueError(f"Invalid move {move}")
                else:
                    raise ValueError(f"Invalid move {move}")
            face.turn(turns, layers)
            if narrow:
                if abs(turns) == 1:
                    turns *= -1
                face.turn(turns, layers-1)
        elif move[0] in self.face_dict:
            face = self.sides[self.face_dict[move[0]]]
            if len(move) == 1:
                turns = 1
            elif len(move) == 2:
                turns = self.get_num(move[-1], move[-2])
                if turns is None:
                    raise ValueError(f"Invalid move {move}")
            else:
                raise ValueError(f"Invalid move {move}")
            face.turn(turns, 1)
        else:
            raise ValueError(f"Invalid move {move}")



    def to_net(self):
        size = 260
        scale = 400
        cell = size/self.size
        gap = 15
        total = size+gap
        img = Image.new("RGB", (4*size+5*gap+2*scale, 3*size+4*gap))
        draw = ImageDraw.Draw(img)
        coords = [(total, 0), (0, total), (total, total), (2*total, total), (3*total, total), (total, 2*total)]
        for (sx, sy), side in zip(coords, self.sides):
            sx += gap
            sy += gap
            for i in range(self.size):
                for j in range(self.size):
                    draw.rectangle([sx+j*cell, sy+i*cell, sx+(1+j)*cell, sy+(1+i)*cell], fill=colors[side.grid[i][j]], outline='black', width=2)
        return img, draw
    def solved(self):
        for s in self.sides:
            for i in s.grid:
                for j in i:
                    if j != s.grid[0][0]:
                        return False
        return True
    @classmethod
    def scramble(cls, size=3):
        length = 10 if size == 2 else 20 if size == 3 else 45 if size == 4 else 20 * size - 40
        scramble_list = []
        prev = None
        faces = [('U', 'D'), ('F', 'B'), ('L', 'R')]
        turns = ['', '2', "'"]
        while len(scramble_list) < length:
            axis = prev
            while axis == prev:
                axis = random.randint(0, 2)
            prev = axis
            num = random.randint(1, size // 2)
            slices = random.sample(range((size - 1) if size % 2 else size), k=num)
            for i in slices:
                f, slice = divmod(i, size // 2)
                face = faces[axis][f]
                if slice == 0:
                    text = face
                elif slice == 1:
                    text = face + 'w'
                else:
                    text = f"{slice + 1}{face}w"
                text += random.choice(turns)
                scramble_list.append(text)
        return ' '.join(scramble_list)
    def to_3d(self, x, y, z, radians=False):
        img, draw = self.to_net()
        scale = 400
        deg = '' if radians else '°'
        font = ImageFont.truetype("Arial", 35)
        draw.text([1115+scale, 5], f"Rotation ({'rad' if radians else 'deg'}): {x}{deg}, {y}{deg}, {z}{deg}", "white", font, "mt")
        x, y, z = -x, -y, -z
        if not radians:
            x = math.radians(x)
            y = math.radians(y)
            z = math.radians(z)
        rotation_matrix = [
            [cos(y)*cos(z), sin(x)*sin(y)*cos(z)-cos(x)*sin(z), cos(x)*sin(y)*cos(z)+sin(x)*sin(z)],
            [cos(y) * sin(z), sin(x) * sin(y) * sin(z) + cos(x) * cos(z), cos(x) * sin(y) * sin(z) - sin(x) * cos(z)],
            [-sin(y), sin(x)*cos(y), cos(x)*cos(y)]
        ]
        start = [[-1, 1, -1], [-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1], [-1, -1, 1]]
        diff = 2/self.size
        direction = [(2, 0), (1, 2), (1, 0), (1, 2), (1, 0), (2, 0)]
        to_draw = []
        pad = .1
        for s, d, side in zip(start, direction, self.sides):
            for i in range(self.size):
                for j in range(self.size):
                    pos = s[:]
                    sign = (-s[d[0]], -s[d[1]])
                    pos[d[0]] += (i+pad)*diff*sign[0]
                    pos[d[1]] += (j+pad)*diff*sign[1]
                    exey, sxey, exsy = pos[:], pos[:], pos[:]
                    exey[d[0]] += (1-2*pad)*diff*sign[0]
                    exey[d[1]] += (1-2*pad)*diff*sign[1]
                    sxey[d[0]] += (1-2*pad)*diff*sign[0]
                    exsy[d[1]] += (1-2*pad)*diff*sign[1]
                    coords = []
                    for p in [pos, sxey, exey, exsy]:
                        rotated = matrix_multiply(rotation_matrix, wrap(p))
                        x = rotated[0][0] * scale * .57 + scale + 1115
                        y = 40 + scale - rotated[1][0] * scale * .57
                        z = rotated[2][0]
                        coords.append(x)
                        coords.append(y)
                    to_draw.append((coords, colors[side.grid[i][j]], z))
        to_draw.sort(key=lambda p: p[2])
        for coords, color, _ in to_draw:
            draw.polygon(coords, color, 'black')

        return img, draw

    def __repr__(self):
        ret = ""
        for i in range(self.size):
            ret += " "*(self.size*2+1) + list_to_emoji(self.sides[0].grid[i])+'\n'
        ret += '\n'
        for i in range(self.size):
            ret += f'{list_to_emoji(self.sides[1].grid[i])} {list_to_emoji(self.sides[2].grid[i])} {list_to_emoji(self.sides[3].grid[i])} {list_to_emoji(self.sides[4].grid[i])}\n'
        ret += '\n'
        for i in range(self.size):
            ret += " "*(self.size*2+1) + list_to_emoji(self.sides[5].grid[i]) +'\n'
        return ret
class Face:
    def __init__(self, size, color):
        self.size = size
        self.grid = [[color]*size for _ in range(size)]
        self.neighbors, self.touching, self.orientation = [None]*3
    def clockwise(self, layers=1):
        self.turn(1, layers)
    def counter_clockwise(self, layers=1):
        self.turn(-1, layers)
    def double(self, layers=1):
        self.turn(2, layers)
    def turn(self, d, layers):
        new = [[None]*self.size for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                if d == 1:
                    new[j][self.size-i-1] = self.grid[i][j]
                elif d == 2:
                    new[self.size - i - 1][self.size-j-1] = self.grid[i][j]
                else:
                    new[self.size - j - 1][i] = self.grid[i][j]
        self.grid = new
        for layer in range(layers):
            new_faces = [None]*4
            for i, side in enumerate(self.neighbors):
                new_faces[(i+d)%4] = side.getLayer(self.touching[i], layer)
                if self.orientation[i] != self.orientation[(i+d)%4]:
                    new_faces[(i + d) % 4].reverse()
            for i, side in enumerate(self.neighbors):
                side.setLayer(new_faces[i], self.touching[i], layer)
    def setLayer(self, layer, direction, i):
        if direction == 0:
            self.grid[i] = layer
        elif direction == 1:
            self.setCol(layer, self.size - i - 1)
        elif direction == 2:
            self.grid[self.size - i - 1] = layer
        elif direction == 3:
            self.setCol(layer, i)
    def getLayer(self, direction, i):
        if direction == 0:
            return self.grid[i]
        elif direction == 1:
            return self.getCol(self.size-i-1)
        elif direction == 2:
            return self.grid[self.size-i-1]
        elif direction == 3:
            return self.getCol(i)
        else:
            raise ValueError("direction not in [0, 4]")
    def getCol(self, col):
        return [row[col] for row in self.grid]
    def setCol(self, col, i):
        for row, cell in zip(self.grid, col):
            row[i] = cell
    def __repr__(self):
        ret = ""
        for i in range(self.size):
            ret += list_to_emoji(self.grid[i]) + '\n'
        return ret