import pygame
import sys
import random
import math

pygame.init()
pygame.mixer.init()

W, H = 400, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
FPS = 60

SKY_TOP      = (100, 180, 255)
SKY_BOT      = (200, 235, 255)
CLOUD_COLOR  = (255, 255, 255)
GROUND_COLOR = (80, 160, 60)
GROUND_DARK  = (55, 120, 40)
PIPE_GREEN   = (60, 175, 60)
PIPE_DARK    = (40, 130, 40)
PIPE_LIGHT   = (100, 210, 100)
BIRD_YELLOW  = (255, 210, 0)
BIRD_DARK    = (200, 160, 0)
BIRD_ORANGE  = (255, 120, 40)
WHITE        = (255, 255, 255)
BLACK        = (0, 0, 0)
RED          = (220, 60, 60)
GOLD         = (255, 215, 0)

GRAVITY      = 0.45
FLAP_FORCE   = -9.0
PIPE_SPEED   = 3.0
PIPE_GAP     = 140
PIPE_FREQ    = 90
GROUND_H     = 50
PIPE_W       = 55

try:
    font_big   = pygame.font.SysFont("Arial", 42, bold=True)
    font_med   = pygame.font.SysFont("Arial", 26, bold=True)
    font_small = pygame.font.SysFont("Arial", 18)
except Exception:
    font_big   = pygame.font.Font(None, 48)
    font_med   = pygame.font.Font(None, 30)
    font_small = pygame.font.Font(None, 22)


class Bird:
    R = 16

    def __init__(self):
        self.x   = 90
        self.y   = H // 2
        self.vy  = 0.0
        self.angle = 0.0
        self.wing_frame = 0
        self.alive = True

    def flap(self):
        self.vy = FLAP_FORCE

    def update(self):
        self.vy    += GRAVITY
        self.y     += self.vy
        self.angle  = max(-30, min(90, self.vy * 5))
        self.wing_frame += 1

    def draw(self, surf):
        bird_surf = pygame.Surface((50, 40), pygame.SRCALPHA)
        cx, cy = 22, 20

        wing_offset = int(math.sin(self.wing_frame * 0.35) * 5)
        pygame.draw.ellipse(bird_surf, BIRD_DARK,
                            (cx - 14, cy + 4 + wing_offset, 18, 10))
        pygame.draw.ellipse(bird_surf, BIRD_YELLOW,
                            (cx - 12, cy + 2 + wing_offset, 16, 8))

        pygame.draw.ellipse(bird_surf, BIRD_YELLOW, (cx - 16, cy - 12, 34, 24))
        pygame.draw.ellipse(bird_surf, BIRD_DARK,   (cx - 16, cy - 12, 34, 24), 2)

        pygame.draw.ellipse(bird_surf, (255, 230, 100),
                            (cx - 6, cy - 4, 18, 14))

        pygame.draw.ellipse(bird_surf, WHITE,  (cx + 4, cy - 10, 12, 10))
        pygame.draw.circle(bird_surf, BLACK,   (cx + 10, cy - 6), 4)
        pygame.draw.circle(bird_surf, WHITE,   (cx + 11, cy - 7), 1)

        pts = [(cx + 16, cy - 2), (cx + 24, cy + 1), (cx + 16, cy + 4)]
        pygame.draw.polygon(bird_surf, BIRD_ORANGE, pts)
        pygame.draw.polygon(bird_surf, (180, 80, 20), pts, 1)

        rotated = pygame.transform.rotate(bird_surf, -self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.R + 4,
                           self.y - self.R + 4,
                           (self.R - 4) * 2,
                           (self.R - 4) * 2)

class Pipe:
    CAP_H = 24
    CAP_W = PIPE_W + 12

    def __init__(self):
        min_top = 60
        max_top = H - GROUND_H - PIPE_GAP - 60
        self.top_h = random.randint(min_top, max_top)
        self.x     = W + 20
        self.scored = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, surf):
        x, tw = self.x, PIPE_W
        cap_x = x - (self.CAP_W - tw) // 2

        body_rect_top = pygame.Rect(x, 0, tw, self.top_h)
        pygame.draw.rect(surf, PIPE_GREEN, body_rect_top)
        pygame.draw.rect(surf, PIPE_LIGHT,
                         pygame.Rect(x + tw * 0.15, 0, tw * 0.15, self.top_h))

        cap_top = pygame.Rect(cap_x, self.top_h - self.CAP_H,
                              self.CAP_W, self.CAP_H)
        pygame.draw.rect(surf, PIPE_GREEN, cap_top, border_bottom_left_radius=5,
                         border_bottom_right_radius=5)
        pygame.draw.rect(surf, PIPE_DARK, cap_top, 2,
                         border_bottom_left_radius=5,
                         border_bottom_right_radius=5)

        bot_y = self.top_h + PIPE_GAP
        body_rect_bot = pygame.Rect(x, bot_y, tw, H - bot_y)
        pygame.draw.rect(surf, PIPE_GREEN, body_rect_bot)
        pygame.draw.rect(surf, PIPE_LIGHT,
                         pygame.Rect(x + tw * 0.15, bot_y, tw * 0.15, H - bot_y))

        cap_bot = pygame.Rect(cap_x, bot_y, self.CAP_W, self.CAP_H)
        pygame.draw.rect(surf, PIPE_GREEN, cap_bot, border_top_left_radius=5,
                         border_top_right_radius=5)
        pygame.draw.rect(surf, PIPE_DARK, cap_bot, 2,
                         border_top_left_radius=5,
                         border_top_right_radius=5)

    def get_rects(self):
        cap_x = self.x - (self.CAP_W - PIPE_W) // 2
        top_rect = pygame.Rect(cap_x, 0, self.CAP_W, self.top_h)
        bot_rect = pygame.Rect(cap_x, self.top_h + PIPE_GAP,
                               self.CAP_W, H)
        return top_rect, bot_rect

    def off_screen(self):
        return self.x + PIPE_W + 20 < 0

class Particle:
    def __init__(self, x, y, burst=False):
        self.x  = x + random.uniform(-6, 6)
        self.y  = y + random.uniform(-6, 6)
        speed   = random.uniform(2, 6) if burst else random.uniform(1, 3)
        angle   = random.uniform(0, math.tau) if burst else \
                  random.uniform(math.pi, math.tau)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - (2 if burst else 0)
        self.life    = 1.0
        self.decay   = random.uniform(0.04, 0.08)
        self.r       = random.randint(2, 5)
        self.color   = random.choice([BIRD_YELLOW, GOLD, BIRD_ORANGE, WHITE])

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.15
        self.life -= self.decay

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        r = max(1, int(self.r * self.life))
        col = (*self.color[:3],)
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, alpha), (r, r), r)
        surf.blit(s, (int(self.x) - r, int(self.y) - r))

clouds = [
    {"x": 50,  "y": 70,  "r": 28, "spd": 0.3},
    {"x": 160, "y": 50,  "r": 22, "spd": 0.2},
    {"x": 290, "y": 90,  "r": 32, "spd": 0.25},
    {"x": 370, "y": 55,  "r": 20, "spd": 0.35},
]

def draw_background(surf, scroll):
    for y in range(H - GROUND_H):
        t = y / (H - GROUND_H)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))

    # Awan
    for c in clouds:
        cx = (c["x"] - scroll * c["spd"]) % (W + 100) - 50
        for ox, oy, rr in [(0, 0, c["r"]), (-c["r"]*0.7, c["r"]*0.4, c["r"]*0.65),
                           (c["r"]*0.7, c["r"]*0.4, c["r"]*0.6)]:
            pygame.draw.ellipse(surf, CLOUD_COLOR,
                                (int(cx + ox - rr), int(c["y"] + oy - rr * 0.65),
                                 int(rr * 2), int(rr * 1.3)))

    ground_y = H - GROUND_H
    pygame.draw.rect(surf, GROUND_COLOR, (0, ground_y, W, GROUND_H))
    pygame.draw.rect(surf, GROUND_DARK,  (0, ground_y, W, 6))

    step = 18
    offset = int(scroll * 1.5) % step
    for gx in range(-step + offset, W + step, step):
        pts = [(gx, ground_y),
               (gx + step // 2, ground_y - 14),
               (gx + step, ground_y)]
        pygame.draw.polygon(surf, (95, 185, 65), pts)


def draw_text_shadow(surf, text, font, color, x, y, center=True):
    shadow = font.render(text, True, (0, 0, 0, 180))
    main   = font.render(text, True, color)
    if center:
        sr = shadow.get_rect(center=(x + 2, y + 2))
        mr = main.get_rect(center=(x, y))
    else:
        sr = shadow.get_rect(topleft=(x + 2, y + 2))
        mr = main.get_rect(topleft=(x, y))
    surf.blit(shadow, sr)
    surf.blit(main, mr)


def reset():
    return Bird(), [], [], 0, 0, 0

def main():
    bird, pipes, particles, score, frame, scroll = reset()
    best  = 0
    state = "idle"

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if state == "idle":
                    state = "playing"
                    bird, pipes, particles, score, frame, scroll = reset()
                    bird.flap()

                elif state == "playing":
                    bird.flap()
                    for _ in range(5):
                        particles.append(Particle(bird.x - 10, bird.y + 5))

                elif state == "dead":
                    state = "idle"

        if state == "playing":
            scroll += PIPE_SPEED * 0.5
            frame  += 1
            bird.update()

            if frame % PIPE_FREQ == 0:
                pipes.append(Pipe())

            for p in pipes:
                p.update()
                if not p.scored and p.x + PIPE_W < bird.x:
                    p.scored = True
                    score   += 1
                    best     = max(best, score)

            pipes = [p for p in pipes if not p.off_screen()]

            for pt in particles:
                pt.update()
            particles = [pt for pt in particles if pt.life > 0]

            bird_rect = bird.get_rect()
            hit = False

            if bird.y + Bird.R >= H - GROUND_H or bird.y - Bird.R <= 0:
                hit = True

            for p in pipes:
                tr, br = p.get_rects()
                if bird_rect.colliderect(tr) or bird_rect.colliderect(br):
                    hit = True

            if hit:
                state = "dead"
                for _ in range(20):
                    particles.append(Particle(bird.x, bird.y, burst=True))

        draw_background(screen, scroll)

        for p in pipes:
            p.draw(screen)

        for pt in particles:
            pt.draw(screen)

        bird.draw(screen)

        if state == "playing":
            draw_text_shadow(screen, str(score), font_big, WHITE, W // 2, 60)

        if state == "idle":
            panel = pygame.Surface((260, 130), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 140))
            pygame.draw.rect(panel, (255,255,255,60), panel.get_rect(), 2, border_radius=12)
            screen.blit(panel, (W//2 - 130, H//2 - 80))

            draw_text_shadow(screen, "🐦  FLAPPY BIRD", font_med, GOLD, W//2, H//2 - 48)
            draw_text_shadow(screen, "Tekan SPASI / Klik", font_small, WHITE, W//2, H//2 - 12)
            draw_text_shadow(screen, "untuk mulai terbang!", font_small, WHITE, W//2, H//2 + 14)
            if best > 0:
                draw_text_shadow(screen, f"Rekor: {best}", font_small, GOLD, W//2, H//2 + 42)

        elif state == "dead":
            panel = pygame.Surface((260, 160), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 160))
            pygame.draw.rect(panel, (255,255,255,60), panel.get_rect(), 2, border_radius=12)
            screen.blit(panel, (W//2 - 130, H//2 - 90))

            draw_text_shadow(screen, "GAME OVER", font_med, RED,   W//2, H//2 - 60)
            draw_text_shadow(screen, f"Skor: {score}",    font_med, WHITE, W//2, H//2 - 22)
            draw_text_shadow(screen, f"Rekor: {best}",    font_med, GOLD,  W//2, H//2 + 12)
            draw_text_shadow(screen, "Klik untuk main lagi", font_small,
                             (200, 200, 200), W//2, H//2 + 50)

        pygame.display.flip()


if __name__ == "__main__":
    main()
