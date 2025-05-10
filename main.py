import pygame
import random
import os

pygame.init()

# cONFIGURAÇÕES DE JANELA
clock = pygame.time.Clock()
fps = 60
screen_width, screen_height = 500, 300
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle")

# FONTES E CORES
font = pygame.font.Font(".\\font\\final_fantasy_36_font.ttf", 20)
RED, GREEN, WHITE = (255, 0, 0), (0, 255, 0), (255, 255, 255)

# CARREGAMENTO DE IMAGENS
background_image = pygame.image.load("background.png").convert_alpha()
panel_image = pygame.image.load("panel.png").convert_alpha()

# FUNÇÕES DE DESENHO
def draw_text(text, font, color, x, y):
    """Renderiza e desenha texto na tela."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_background():
    """Desenha o fundo da batalha."""
    screen.blit(background_image, (0, 0))

def draw_panel(fighters):
    """Desenha o painel de status dos lutadores."""
    screen.blit(panel_image, (0, 200))
    for index, fighter in enumerate(fighters):
        x = 10 if index == 0 else 300
        draw_text(f"{fighter.name} HP: {fighter.hp}/{fighter.max_hp}", font, WHITE, x, 210)

# CLASSE DE LUTA
class Fighter:
    def __init__(self, x, y, name, max_hp, strength, potions, flip):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potions = potions
        self.alive = True
        self.flip = flip

        self.animations = self.load_animations()
        self.action = "idle"
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def load_animations(self):
        """Carrega todas as animações disponíveis do lutador."""
        animations = {}
        animation_types = ["idle", "attack", "hurt", "death"]

        for animation_type in animation_types:
            frames = []
            folder = f".\\sprites\\{self.name}\\{animation_type}"
            if not os.path.exists(folder):
                continue
            for file_name in sorted(os.listdir(folder), key=lambda x: int(x.split(".")[0])):
                path = os.path.join(folder, file_name)
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                if self.flip:
                    img = pygame.transform.flip(img, True, False)
                frames.append(img)
            animations[animation_type] = frames

        return animations
    
    def set_action(self, action_name):
        """Troca para uma nova animação se diferente da atual."""
        if action_name != self.action:
            self.action = action_name
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update(self):
        """Atualiza a animação atual do lutador."""
        animation_cooldown = 100
        frames = self.animations.get(self.action, [])

        if not frames:
            return
        
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

            if self.frame_index >= len(frames):
                if self.action in ("attack", "hurt"):
                    self.set_action("idle")
                    frames = self.animations.get(self.action, [])
                    self.frame_index = 0
                elif self.action == "death":
                    self.frame_index = len(frames) - 1
                else:
                    self.frame_index = 0

        if self.frame_index < len(frames):
            self.image = frames[self.frame_index]

    def idle(self):
        """Volta a animação para idle."""
        self.set_action("idle")

    def attack(self, target):
        """Realiza um ataque contra um alvo."""
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        target.hp = max(target.hp - damage, 0)
        if target.hp == 0:
            target.alive = False
            target.set_action("death")
        else:
            target.set_action("hurt")
        self.set_action("attack")

    def draw(self):
        """Desenha o lutador na tela."""
        screen.blit(self.image, self.rect)

# CLASSE DE BARRA DE VIDA
class HealthBar:
    def __init__(self, x, y, max_hp):
        self.x, self.y = x, y
        self.max_hp = max_hp

    def draw(self, current_hp):
        ratio = current_hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class BattleMenu:
    def __init__(self, options, font, x, y, spacing=30):
        self.options = options
        self.font = font
        self.selected_index = 0
        self.x = x
        self.y = y
        self.spacing = spacing

    def draw(self):
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_index else WHITE
            draw_text(option, self.font, color, self.x, self.y + i * self.spacing)

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % len(self.options)

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % len(self.options)

    def get_selected_option(self):
        return self.options[self.selected_index]

# INSTANCIAMENTO DOS LUTADORES
fighters = [
    Fighter(87, 145, "Hero", 30, 10, 5, False),
    Fighter(412, 150, "Bandit", 30, 10, 5, False)
]
health_bars = [
    HealthBar(10, 30, fighters[0].max_hp),
    HealthBar(screen_width - 160, 30, fighters[1].max_hp)
]

# VARIÁVEIS DE CONTROLE
current_fighter = 0
action_cooldown = 0
action_wait_time = 90

# CONTROLE DE ESTADO
player_turn = True # True para o jogador, False para o inimigo
state_stack = ["menu"]

# MENU DE BATALHA
battle_menu = BattleMenu(["Atacar", "Defender"], font, 10, 240)

# LOOP PRINCIPAL DA BATALHA
run = True
while run:
    clock.tick(fps)

    # DESENHO
    draw_background()
    draw_panel(fighters)
    for i, fighter in enumerate(fighters):
        fighter.update()
        fighter.draw()
        health_bars[i].draw(fighter.hp)

    # VERIFICA ESTADO ATUAL DO JOGO
    current_state = state_stack[-1]

    # TURNO DO JOGADOR
    if player_turn and current_state == "menu":
        battle_menu.draw()

    # TURNO DO INIMIGO
    elif not player_turn:
        action_cooldown += 1
        if action_cooldown >= action_wait_time:
            if fighters[1].alive:
                fighters[1].attack(fighters[0])
            current_fighter = 0
            action_cooldown = 0
            player_turn = True
            state_stack = ["menu"]

    # EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        # Navegação de menu
        if player_turn and current_state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    battle_menu.move_down()
                elif event.key == pygame.K_UP:
                    battle_menu.move_up()
                elif event.key == pygame.K_x: # CONFIRMAR
                    selected = battle_menu.get_selected_option()
                    if selected == "Atacar":
                        fighters[0].attack(fighters[1])
                        player_turn = False
                        action_cooldown = 0
                        state_stack = ["battle"]
                    elif selected == "Defender":
                        print(f"{fighters[0].name} está defendendo!")
                        player_turn = False
                        action_cooldown = 0
                        state_stack = ["battle"]
                elif event.key == pygame.K_z: # VOLTAR
                    pass

    pygame.display.update()

pygame.quit()
