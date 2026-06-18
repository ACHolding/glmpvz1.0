import pygame
import random
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 600, 400
FPS = 60
TITLE = "ac's pvz my take"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRASS_LIGHT = (100, 200, 80)
GRASS_DARK = (80, 180, 60)
HUD_GREEN = (50, 100, 30)
HUD_BROWN = (100, 70, 40)
SUN_YELLOW = (255, 230, 50)
SUN_ORANGE = (255, 150, 0)
PEA_GREEN = (50, 200, 50)
BROWN = (150, 100, 50)
DARK_BROWN = (100, 60, 30)
ZOMBIE_GREEN = (120, 150, 100)
ZOMBIE_DARK = (80, 110, 70)
GRAY = (200, 200, 200)
RED = (200, 50, 50)

# Grid Setup
GRID_COLS = 9
GRID_ROWS = 5
CELL_W = 60
CELL_H = 60
GRID_X = 30
GRID_Y = 70

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

class Sun:
    def __init__(self, x, y, target_y=None, value=25):
        self.x = x
        self.y = y
        self.target_y = target_y if target_y else y
        self.value = value
        self.radius = 15
        self.life = 600 # 10 seconds at 60fps
        self.collected = False

    def update(self):
        if self.y < self.target_y:
            self.y += 1
        else:
            self.life -= 1
        if self.life <= 0:
            self.collected = True # Will be removed

    def draw(self, surface):
        pygame.draw.circle(surface, SUN_ORANGE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, SUN_YELLOW, (int(self.x), int(self.y)), self.radius - 3)

class Plant:
    def __init__(self, x, y, plant_type):
        self.x = x
        self.y = y
        self.type = plant_type
        self.health = 100
        self.shoot_timer = 0
        self.sun_timer = random.randint(200, 400)
        
    def update(self, game):
        if self.type == "sunflower":
            self.sun_timer -= 1
            if self.sun_timer <= 0:
                self.sun_timer = 600 # 10 secs
                game.suns.append(Sun(self.x, self.y - 20, self.y + 10))
                
        elif self.type == "peashooter":
            self.shoot_timer -= 1
            # Check for zombies in this row
            row = (self.y - GRID_Y) // CELL_H
            has_zombie = any(z.row == row and z.x > self.x for z in game.zombies)
            if has_zombie and self.shoot_timer <= 0:
                self.shoot_timer = 90 # 1.5 secs
                game.peas.append(Pea(self.x + 20, self.y))
                
    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        if self.type == "peashooter":
            pygame.draw.rect(surface, DARK_BROWN, (cx-5, cy+5, 10, 20)) # Stem
            pygame.draw.circle(surface, PEA_GREEN, (cx, cy-5), 15)
            pygame.draw.circle(surface, (30, 150, 30), (cx, cy-5), 15, 2)
            pygame.draw.circle(surface, BLACK, (cx+15, cy-5), 5) # Hole
            pygame.draw.circle(surface, WHITE, (cx-5, cy-10), 3) # Eye
        elif self.type == "sunflower":
            pygame.draw.rect(surface, DARK_BROWN, (cx-5, cy+5, 10, 20)) # Stem
            pygame.draw.circle(surface, SUN_YELLOW, (cx, cy-5), 15)
            pygame.draw.circle(surface, SUN_ORANGE, (cx, cy-5), 8)
            pygame.draw.circle(surface, BLACK, (cx-4, cy-8), 2)
            pygame.draw.circle(surface, BLACK, (cx+4, cy-8), 2)
        elif self.type == "wallnut":
            pygame.draw.ellipse(surface, BROWN, (cx-20, cy-20, 40, 40))
            pygame.draw.ellipse(surface, DARK_BROWN, (cx-20, cy-20, 40, 40), 2)
            pygame.draw.circle(surface, BLACK, (cx-8, cy-5), 3)
            pygame.draw.circle(surface, BLACK, (cx+8, cy-5), 3)

class Pea:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 6
        self.damage = 20
        
    def update(self):
        self.x += self.speed
        
    def draw(self, surface):
        pygame.draw.circle(surface, PEA_GREEN, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(surface, (30, 150, 30), (int(self.x), int(self.y)), 6, 1)

class Zombie:
    def __init__(self, row):
        self.x = WIDTH + 20
        self.row = row
        self.y = GRID_Y + row * CELL_H + CELL_H // 2
        self.speed = 0.3
        self.health = 100
        self.eating = False
        
    def update(self, game):
        self.eating = False
        # Check collision with plants
        for p in game.plants:
            p_row = (p.y - GRID_Y) // CELL_H
            if p_row == self.row:
                if abs(p.x - self.x) < 25:
                    self.eating = True
                    p.health -= 0.2
                    return
                    
        if not self.eating:
            self.x -= self.speed
            
    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        # Legs
        pygame.draw.rect(surface, ZOMBIE_DARK, (cx-10, cy+5, 8, 15))
        pygame.draw.rect(surface, ZOMBIE_DARK, (cx+2, cy+5, 8, 15))
        # Body
        pygame.draw.rect(surface, ZOMBIE_GREEN, (cx-12, cy-10, 24, 20))
        # Head
        pygame.draw.circle(surface, ZOMBIE_GREEN, (cx, cy-15), 10)
        # Arms
        pygame.draw.rect(surface, ZOMBIE_GREEN, (cx-15, cy-5, 10, 5))
        pygame.draw.rect(surface, ZOMBIE_GREEN, (cx+5, cy-5, 10, 5))
        # Eyes
        pygame.draw.circle(surface, RED, (cx-3, cy-15), 2)
        pygame.draw.circle(surface, RED, (cx+3, cy-15), 2)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 16, bold=True)
        self.big_font = pygame.font.SysFont('arial', 40, bold=True)
        self.state = STATE_MENU
        self.reset_game()

    def reset_game(self):
        self.sun_count = 50
        self.plants = []
        self.zombies = []
        self.peas = []
        self.suns = []
        self.selected_plant = None
        self.shovel_active = False
        
        # Seed Packets
        self.seed_packets = [
            {"name": "peashooter", "cost": 100, "rect": pygame.Rect(80, 10, 50, 50), "cooldown": 0},
            {"name": "sunflower", "cost": 50, "rect": pygame.Rect(135, 10, 50, 50), "cooldown": 0},
            {"name": "wallnut", "cost": 50, "rect": pygame.Rect(190, 10, 50, 50), "cooldown": 0}
        ]
        
        self.shovel_rect = pygame.Rect(550, 15, 35, 40)
        self.sun_counter_rect = pygame.Rect(15, 15, 60, 40)
        
        self.sun_spawn_timer = 300
        self.zombie_spawn_timer = 600
        
    def update(self):
        if self.state != STATE_PLAYING: return
        
        # Sun Falling from sky
        self.sun_spawn_timer -= 1
        if self.sun_spawn_timer <= 0:
            self.sun_spawn_timer = 600
            self.suns.append(Sun(random.randint(50, WIDTH-50), -20, random.randint(100, 300)))
            
        # Zombie Spawning
        self.zombie_spawn_timer -= 1
        if self.zombie_spawn_timer <= 0:
            self.zombie_spawn_timer = random.randint(400, 800)
            self.zombies.append(Zombie(random.randint(0, 4)))
            
        # Update Entities
        for s in self.suns[:]:
            s.update()
            if s.collected:
                self.suns.remove(s)
                
        for p in self.plants[:]:
            p.update(self)
            if p.health <= 0:
                self.plants.remove(p)
                
        for pea in self.peas[:]:
            pea.update()
            if pea.x > WIDTH:
                self.peas.remove(pea)
            else:
                for z in self.zombies:
                    if abs(z.x - pea.x) < 20 and z.row == (pea.y - GRID_Y) // CELL_H:
                        z.health -= pea.damage
                        if pea in self.peas: self.peas.remove(pea)
                        break
                        
        for z in self.zombies[:]:
            z.update(self)
            if z.health <= 0:
                self.zombies.remove(z)
            if z.x < 0:
                self.state = STATE_GAME_OVER
                
        # Update Seed Cooldowns
        for sp in self.seed_packets:
            if sp["cooldown"] > 0:
                sp["cooldown"] -= 1

    def draw_grid(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                color = GRASS_LIGHT if (row + col) % 2 == 0 else GRASS_DARK
                rect = pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)
                pygame.draw.rect(self.screen, color, rect)

    def draw_hud(self):
        # Top Bar
        pygame.draw.rect(self.screen, HUD_BROWN, (0, 0, WIDTH, 60))
        pygame.draw.rect(self.screen, DARK_BROWN, (0, 0, WIDTH, 60), 3)
        
        # Sun Counter
        pygame.draw.rect(self.screen, HUD_GREEN, self.sun_counter_rect, border_radius=5)
        pygame.draw.circle(self.screen, SUN_YELLOW, (35, 35), 15)
        pygame.draw.circle(self.screen, SUN_ORANGE, (35, 35), 15, 2)
        sun_text = self.font.render(str(self.sun_count), True, WHITE)
        self.screen.blit(sun_text, (55, 25))
        
        # Seed Packets
        for sp in self.seed_packets:
            color = GRAY if self.sun_count >= sp["cost"] and sp["cooldown"] == 0 else (100, 100, 100)
            pygame.draw.rect(self.screen, color, sp["rect"], border_radius=5)
            pygame.draw.rect(self.screen, BLACK, sp["rect"], 2, border_radius=5)
            
            # Mini Plant Icon
            cx, cy = sp["rect"].centerx, sp["rect"].centery - 5
            if sp["name"] == "peashooter":
                pygame.draw.circle(self.screen, PEA_GREEN, (cx, cy), 10)
            elif sp["name"] == "sunflower":
                pygame.draw.circle(self.screen, SUN_YELLOW, (cx, cy), 10)
            elif sp["name"] == "wallnut":
                pygame.draw.ellipse(self.screen, BROWN, (cx-8, cy-8, 16, 16))
                
            cost_text = self.font.render(str(sp["cost"]), True, BLACK)
            self.screen.blit(cost_text, (sp["rect"].x + 5, sp["rect"].bottom - 15))
            
            # Selected Highlight
            if self.selected_plant == sp["name"]:
                pygame.draw.rect(self.screen, WHITE, sp["rect"], 3, border_radius=5)
                
            # Cooldown overlay
            if sp["cooldown"] > 0:
                cd_rect = pygame.Rect(sp["rect"].x, sp["rect"].y, sp["rect"].w, sp["rect"].h * (sp["cooldown"] / 300))
                s = pygame.Surface((cd_rect.w, cd_rect.h), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                self.screen.blit(s, cd_rect)
                
        # Shovel
        pygame.draw.rect(self.screen, GRAY, self.shovel_rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, self.shovel_rect, 2, border_radius=5)
        # Shovel Icon
        pygame.draw.rect(self.screen, HUD_BROWN, (self.shovel_rect.centerx-2, self.shovel_rect.y+5, 4, 20))
        pygame.draw.rect(self.screen, GRAY, (self.shovel_rect.centerx-8, self.shovel_rect.y+20, 16, 10))
        if self.shovel_active:
            pygame.draw.rect(self.screen, WHITE, self.shovel_rect, 3, border_radius=5)

    def draw_menu(self):
        self.screen.fill(BLACK)
        title = self.big_font.render(TITLE, True, WHITE)
        start_text = self.font.render("Click to Start", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 40))
        self.screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 20))

    def draw_game_over(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0,0))
        text = self.big_font.render("GAME OVER", True, RED)
        restart = self.font.render("Click to Restart", True, WHITE)
        self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 40))
        self.screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 20))

    def draw(self):
        self.screen.fill(BLACK)
        if self.state == STATE_MENU:
            self.draw_menu()
        else:
            self.draw_grid()
            self.draw_hud()
            
            # Draw Entities
            for p in self.plants: p.draw(self.screen)
            for z in self.zombies: z.draw(self.screen)
            for pea in self.peas: pea.draw(self.screen)
            for s in self.suns: s.draw(self.screen)
            
            # Cursor preview
            mx, my = pygame.mouse.get_pos()
            if self.selected_plant or self.shovel_active:
                col = (mx - GRID_X) // CELL_W
                row = (my - GRID_Y) // CELL_H
                if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                    hov_rect = pygame.Rect(GRID_X + col*CELL_W, GRID_Y + row*CELL_H, CELL_W, CELL_H)
                    pygame.draw.rect(self.screen, WHITE, hov_rect, 2)
            
            if self.state == STATE_GAME_OVER:
                self.draw_game_over()
                
        pygame.display.flip()

    def handle_click(self, mx, my):
        if self.state == STATE_MENU:
            self.state = STATE_PLAYING
            return
            
        if self.state == STATE_GAME_OVER:
            self.reset_game()
            self.state = STATE_PLAYING
            return
            
        # Check Shovel
        if self.shovel_rect.collidepoint(mx, my):
            self.shovel_active = not self.shovel_active
            self.selected_plant = None
            return
            
        # Check Seed Packets
        for sp in self.seed_packets:
            if sp["rect"].collidepoint(mx, my):
                if self.sun_count >= sp["cost"] and sp["cooldown"] == 0:
                    self.selected_plant = sp["name"]
                    self.shovel_active = False
                return
                
        # Check Suns
        for s in self.suns:
            if math.hypot(mx - s.x, my - s.y) < s.radius:
                self.sun_count += s.value
                s.collected = True
                return
                
        # Grid Placement
        col = (mx - GRID_X) // CELL_W
        row = (my - GRID_Y) // CELL_H
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            cell_x = GRID_X + col * CELL_W + CELL_W // 2
            cell_y = GRID_Y + row * CELL_H + CELL_H // 2
            
            # Check if plant exists
            existing = [p for p in self.plants if p.x == cell_x and p.y == cell_y]
            
            if self.shovel_active and existing:
                self.plants.remove(existing[0])
                self.shovel_active = False
            elif self.selected_plant and not existing:
                sp = next(s for s in self.seed_packets if s["name"] == self.selected_plant)
                if self.sun_count >= sp["cost"]:
                    self.plants.append(Plant(cell_x, cell_y, self.selected_plant))
                    self.sun_count -= sp["cost"]
                    sp["cooldown"] = 300 # 5 sec cooldown
                    self.selected_plant = None

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        self.handle_click(*event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == STATE_PLAYING:
                            self.state = STATE_MENU
                        else:
                            running = False
                            
            self.update()
            self.draw()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()