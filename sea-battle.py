from random import randint, choice


SHIP_SET = [3, 2, 2, 1, 1, 1, 1]
COORDINATE_DICT = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5}


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x 
            cur_y = self.bow.y     
            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot):
        return shot in self.dots


class Filed:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [ ['~']*size for _ in range(size) ]
        self.busy = []
        self.ships = []
    
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "+"
                    self.busy.append(cur)
    
    def __str__(self):
        res = ""
        res += f"  | {' | '.join(COORDINATE_DICT.keys())} |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | {' | '.join(row)} |"
        
        if self.hid:
            res = res.replace("■", "~")
        return res
    
    def out(self, d):
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        
        if d in self.busy:
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    return False, False
                else:
                    print("Корабль ранен!")
                    return True, True
        
        self.field[d.x][d.y] = "+"
        print("Мимо!")
        return False, True
    
    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat[0]
            except BoardException as e:
                print(e)

class AI(Player):
    last_lucky_move = None
    next_shots = []
    not_shots = []

    def ask(self):
        while True:
            d = Dot(randint(0,5), randint(0, 5))
            if d not in self.enemy.busy:
                break
        print(f"Ход компьютера: {list(COORDINATE_DICT)[d.y]}{d.x+1}")
        return d
    
    def move(self):
        while True:
            if self.last_lucky_move is None:
                try:
                    target = self.ask()
                    repeat, near = self.enemy.shot(target)
                    if repeat is True and near is True:
                        self.last_lucky_move = target
                    return repeat
                except BoardException as e:
                    print(e)
            else:
                try:
                    target = self.shotAfterLuckyShot()
                    repeat, near = self.enemy.shot(target)
                    if repeat is True and near is True:
                        self.last_lucky_move = target
                    elif repeat is False and near is False:
                        self.last_lucky_move = None
                        self.next_shots = []
                        self.not_shots = []
                    return repeat
                except BoardException as e:
                    print(e)

    def shotAfterLuckyShot(self):
        '''Выбор клетки для выстрела после попадания'''
        near_shot = ((-1,0), (0, -1), (0,1), (1,0))
        not_shot = ((-1,-1), (-1,1), (1,-1), (1,1))
        for dx, dy in near_shot:
            shot = Dot(self.last_lucky_move.x + dx, self.last_lucky_move.y + dy)
            if all([not(self.enemy.out(shot)),
                    shot not in self.enemy.busy,
                    shot not in self.next_shots]):
                        self.next_shots.append(shot)
        for dx, dy in not_shot:
            shot = Dot(self.last_lucky_move.x + dx, self.last_lucky_move.y + dy)
            if all([not(self.enemy.out(shot)),
                    shot not in self.enemy.busy]):
                        self.not_shots.append(shot)
        for x in self.not_shots:
            if x in self.next_shots:
                self.next_shots.remove(x)
        next_shot = choice(self.next_shots)
        self.next_shots.remove(next_shot)
        print(f"Ход компьютера: {list(COORDINATE_DICT)[next_shot.y]}{next_shot.x+1}")
        return next_shot


class User(Player):
    def ask(self):
        while True:
            help_str = f'Введите букву столбца и цифру строки (Например: {choice(list(COORDINATE_DICT.keys()))}{randint(1,6)}) : '
            user_input = input(help_str).strip()[:2]
            try:
                x, y = user_input[0].lower(), user_input[1]
                x = COORDINATE_DICT[x]
                y = int(y) - 1
            except (TypeError, ValueError, KeyError):
                print('!!! Ошибка при вводе координат !!!')
                continue
            return Dot(y, x)

class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)
    
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board
    
    def random_place(self):
        board = Filed(size = self.size)
        attempts = 0
        for l in SHIP_SET:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @property
    def fields_print(self):
        left = str(self.us.board).split("\n")
        right = str(self.ai.board).split("\n")
        print(f"{'Доска игрока:'.center(30)}  {'Доска компьютера:'.center(30)}")
        for i in range(len(left)):
            print(f'{left[i]}\t {right[i]}')    
    
    def game(self):
        print("  Приветсвуем вас в игре морской бой ")
        num = 0
        while True:
            self.fields_print
            if num % 2 == 0:
                print("-"*60)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-"*60)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num += 1
            
            if self.ai.board.count == 7:
                print("-"*60)
                self.fields_print
                print("Пользователь выиграл!")
                break
            
            if self.us.board.count == 7:
                print("-"*60)
                self.fields_print
                print("Компьютер выиграл!")
                break
            num += 1

            
g = Game()
g.game()