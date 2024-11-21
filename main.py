import pygame
import random

# Dimensiuni ale ferestrei
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 15
CELL_SIZE = WIDTH // GRID_SIZE
# Maximul de gunoaie 60
# Culori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREY = (105,105,105)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Tipuri de celule
EMPTY = 0
WALL = 1
GARBAGE = 2
COLLECTOR = 3

# Inițializare Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RoboClean")
clock = pygame.time.Clock()

# Încărcare imagini
wall_img = pygame.image.load("images/wall-white.jpg")
wall_img = pygame.transform.scale(wall_img, (CELL_SIZE, CELL_SIZE))

robot_img = pygame.image.load("images/robot.jpg")
robot_img = pygame.transform.scale(robot_img, (CELL_SIZE, CELL_SIZE))

garbage_images = [
    pygame.image.load("images/organic-garbage.jpg"),
    pygame.image.load("images/fishbone-garbage.jpg"),
    pygame.image.load("images/insecte-moarte-garbage.jpg")
]
garbage_images = [pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE)) for img in garbage_images]
collector_img = pygame.image.load("images/collector.jpg")
collector_img = pygame.transform.scale(collector_img, (CELL_SIZE, CELL_SIZE))

# Creare matrice pentru apartament
def create_apartment(garbage_count):
    grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    garbage_positions = {}  # Dictionar pentru asocierea gunoiului cu imaginile
    # Adăugăm pereți
    for i in range(GRID_SIZE):
        grid[0][i] = WALL
        grid[GRID_SIZE-1][i] = WALL
        grid[i][0] = WALL
        grid[i][GRID_SIZE-1] = WALL

        # Calculăm linia de mijloc
    middle = GRID_SIZE // 2

        # Adăugăm pereții orizontali pe linia de mijloc
    for i in range(1,GRID_SIZE-1):
        if i != middle-1 and i != middle+1:  # Verificăm dacă nu este centrul
            grid[middle][i] = WALL  # Peretele orizontal

        # Adăugăm pereții verticali pe coloana de mijloc
    for i in range(1,GRID_SIZE-1):
        if i != middle-1 and i != middle+1:  # Verificăm dacă nu este centrul
            grid[i][middle] = WALL  # Peretele vertical

    # Adăugăm gunoi în locații random
    for _ in range(garbage_count):
        x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
        while grid[y][x] != EMPTY:  # Evită suprapunerea gunoiului
            x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
        grid[y][x] = GARBAGE
        garbage_positions[(x, y)] = random.choice(garbage_images)  # Asociem imaginea
    # Zona de colectare
    grid[GRID_SIZE-2][GRID_SIZE-2] = COLLECTOR
    return grid,garbage_positions

# Desenarea grilei
def draw_grid(grid,garbage_positions):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[y][x] == WALL:
                screen.blit(wall_img, rect.topleft)
            elif grid[y][x] == GARBAGE:
                garbage_img = garbage_positions[(x, y)]
                screen.blit(garbage_img, rect.topleft)
            elif grid[y][x] == COLLECTOR:
                screen.blit(collector_img, rect.topleft)
            else:
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, GRAY, rect, 1)  # Grilă

def draw_labels():
    font = pygame.font.Font(None, 36)
    labels = {
        "Dormitor": (3 * CELL_SIZE, 4 * CELL_SIZE),
        "Baie": (10 * CELL_SIZE, 4 * CELL_SIZE),
        "Living": (3 * CELL_SIZE, 10 * CELL_SIZE),
        "Bucătărie": (10 * CELL_SIZE, 10 * CELL_SIZE),
    }
    for label, position in labels.items():
        text = font.render(label, True, BLACK)
        screen.blit(text, position)


# Robotul
class Robot:
    def __init__(self, x, y, global_score):
        self.x = x
        self.y = y
        self.inventory = 0
        self.max_capacity = 10
        self.score = 0  # Inițializăm scorul la 0
        self.global_score = global_score

    def move(self, dx, dy, grid):
        # Încercăm să curățăm înainte de a ne mișca
        self.collect_garbage(grid)

        new_x, new_y = self.x + dx, self.y + dy
        if grid[new_y][new_x] != WALL:
            self.x, self.y = new_x, new_y

    def collect_garbage(self, grid):
        if grid[self.y][self.x] == GARBAGE and self.inventory < self.max_capacity:
            grid[self.y][self.x] = EMPTY
            self.inventory += 1
            self.score += 1  # Incrementăm scorul robotului când curățăm un gunoi
            self.global_score[0] += 1  # Actualizăm scorul global
            print(f"Scorul global este acum: {self.global_score[0]}")  # Opțional pentru debug

    def drop_off(self, grid):
        if grid[self.y][self.x] == COLLECTOR:
            self.inventory = 0

# Funcții pentru AI
def ai_clean(robot, grid):
    """Algoritm simplu pentru AI: se deplasează aleator pentru curățare."""
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(directions)  # Alege o direcție aleator
    for dx, dy in directions:
        new_x, new_y = robot.x + dx, robot.y + dy
        if grid[new_y][new_x] != WALL:
            robot.move(dx, dy, grid)
            robot.collect_garbage(grid)
            robot.drop_off(grid)
            break

def is_clean(grid):
    """Verifică dacă mediul este complet curat."""
    for row in grid:
        if GARBAGE in row:
            return False
    return True

def show_instructions():
    running = True
    font = pygame.font.Font(None, 24)
    instructions_text = [
        "Instrucțiuni:",
        "* Folosește tastele săgeată pentru a muta robotul.",
        "* Apasă tasta '1' pentru a seta cantitatea de gunoi.",
        "* Apasă tasta '2' pentru a schimba modul de joc între manual și AI.",
        "* Apasă tasta '3' pentru a seta nr. robitilor(AI).",
        "* Apasă tasta '4' pentru a începe jocul.",
        "* Apasă tasta '5' pentru a ieși.",
        "* Apasă tasta '6' pentru instructiuni.",
        "* Robotul colectează gunoiul din apartament.",
        "* Scopul este de a curăța întregul apartament.",
        "Apasă orice tastă pentru a reveni la meniu."
    ]
    while running:
        screen.fill(GREY)
        y_offset = 50
        for line in instructions_text:
            text = font.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 50

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False  # Închidem fereastra de instrucțiuni la apăsarea oricărei taste

def menu():
    running = True
    garbage_count = 20
    mode = "manual"
    num_robots = 1
    active_input = False
    user_input = ""

    while running:
        screen.fill(GREY)
        font = pygame.font.Font(None, 36)
        font_instructions = pygame.font.Font(None, 24)

        # Textul meniului
        title = font.render("Meniu Principal", True, WHITE)
        option1 = font.render(f"1. Setează gunoi: {garbage_count}", True, WHITE if not active_input else GRAY)
        option2 = font.render(f"2. Mod: {mode}", True, WHITE)
        option3 = font.render(f"3. Număr roboți (AI): {num_robots}", True, WHITE if active_input != "robots" else GRAY)
        start = font.render("4. Start", True, WHITE)
        quit_game = font.render("5. Ieșire", True, WHITE)
        instructions = font.render("6. Instructions", True, WHITE)

        # Afișare text
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        screen.blit(option1, (WIDTH // 2 - option1.get_width() // 2, 150))
        screen.blit(option2, (WIDTH // 2 - option2.get_width() // 2, 225))
        screen.blit(option3, (WIDTH // 2 - option3.get_width() // 2, 300))
        screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 375))
        screen.blit(quit_game, (WIDTH // 2 - quit_game.get_width() // 2, 450))
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 525))

        # Afișăm inputul dacă este activ
        if active_input:
            if active_input == "robots":
                input_box = pygame.Rect(410, 295, 50, 36)  # Cutie pentru input
                pygame.draw.rect(screen, GRAY, input_box)
                input_text = font.render(user_input, True, BLACK)
                screen.blit(input_text, (input_box.x + 5, input_box.y + 5))
            elif active_input == "garbage":
                input_box = pygame.Rect(385, 145, 50, 36)  # Cutie pentru input
                pygame.draw.rect(screen, GRAY, input_box)
                input_text = font.render(user_input, True, BLACK)
                screen.blit(input_text, (input_box.x + 5, input_box.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None
            if event.type == pygame.KEYDOWN:
                if active_input:
                    if event.key == pygame.K_RETURN:  # Finalizăm inputul
                        if user_input.isdigit():
                            if active_input == "garbage":
                                garbage_count = int(user_input)
                            elif active_input == "robots" and mode == "ai":
                                num_robots = max(1, int(user_input))  # Minimul 1 robot
                        user_input = ""
                        active_input = False
                    elif event.key == pygame.K_BACKSPACE:  # Ștergere caracter
                        user_input = user_input[:-1]
                    elif event.unicode.isdigit():  # Acceptăm doar cifre
                        user_input += event.unicode
                else:
                    if event.key == pygame.K_1:  # Activăm inputul
                        active_input = "garbage"
                    elif event.key == pygame.K_2:
                        mode = "ai" if mode == "manual" else "manual"  # Schimbă modul
                    elif event.key == pygame.K_3:
                        if mode == "ai":
                           active_input = "robots"
                    elif event.key == pygame.K_4:
                        return garbage_count, mode, num_robots
                    elif event.key == pygame.K_5:
                        running = False
                        return None, None ,None
                    elif event.key == pygame.K_6:
                        show_instructions()

# Main
def main():
    garbage_count, mode, num_robots = menu()
    if garbage_count is None:
        return

    grid,garbage_positions = create_apartment(garbage_count)

    # Scor global (lista pentru referință)
    global_score = [0]  # Folosim o listă pentru a putea modifica valoarea în mai multe locuri
    # Creăm un singur robot pentru modul manual, sau mai mulți pentru modul AI
    robots = []
    if mode == "manual":
        robots.append(Robot(1, 1, global_score))  # Adăugăm un singur robot
    else:
        for i in range(num_robots):
            x, y = random.randint(1, GRID_SIZE - 2), random.randint(1, GRID_SIZE - 2)
            while grid[y][x] != EMPTY:  # Evităm suprapunerea
                x, y = random.randint(1, GRID_SIZE - 2), random.randint(1, GRID_SIZE - 2)
            robots.append(Robot(x, y, global_score))  # Adăugăm mai mulți roboți pentru AI

    running = True
    # Timer
    start_ticks = pygame.time.get_ticks()  # Start time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Modul AI: fiecare robot își folosește AI-ul
        if mode == "ai":
           for robot in robots:
               ai_clean(robot, grid)
        # Modul de operare
        elif mode == "manual":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                robots[0].move(0, -1, grid)
            if keys[pygame.K_DOWN]:
                robots[0].move(0, 1, grid)
            if keys[pygame.K_LEFT]:
                robots[0].move(-1, 0, grid)
            if keys[pygame.K_RIGHT]:
                robots[0].move(1, 0, grid)

        # Verificăm dacă mediul este curățat
        if is_clean(grid):
            final_time = (pygame.time.get_ticks() - start_ticks) // 1000
            print("Mediul este complet curat! Simulare finalizată.")
            print(f"Durata totală: {final_time} secunde")
            running = False

        # Desenare
        screen.fill(GRAY)
        draw_grid(grid,garbage_positions)
        draw_labels()
        for robot in robots:
            rect = pygame.Rect(robot.x * CELL_SIZE, robot.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            screen.blit(robot_img, rect.topleft)
            # Curăță gunoiul și depune gunoiul
            robot.collect_garbage(grid)
            robot.drop_off(grid)

        # Afișăm scorul
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Scor: {global_score[0]}", True, BLACK)
        screen.blit(score_text, (50, 10))

        # Afișăm timpul
        elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        timer_text = font.render(f"Timp: {elapsed_seconds}s", True, BLACK)
        screen.blit(timer_text, (WIDTH - 150, 10))

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
