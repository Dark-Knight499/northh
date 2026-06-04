import math
import random
from dataclasses import dataclass, field
from typing import Optional

from rich.text import Text

from src.easter.sprites import (
    BOSS_CORE,
    BOSS_HEIGHT,
    BOSS_WIDTH,
    BULLET,
    ELITE_WIDTH,
    ELITE_HEIGHT,
    ENEMY_BULLET,
    ENEMY_ELITE,
    ENEMY_FIGHTER,
    ENEMY_HUNTER,
    ENEMY_KAMIKAZE,
    ENEMY_SCOUT,
    EXPLOSION_PARTICLES,
    FIGHTER_HEIGHT,
    FIGHTER_WIDTH,
    HUNTER_HEIGHT,
    HUNTER_WIDTH,
    KAMIKAZE_HEIGHT,
    KAMIKAZE_WIDTH,
    PLAYER_HEIGHT,
    PLAYER_SPRITES,
    PLAYER_WIDTH,
    POWERUP_BOMB,
    POWERUP_LASER,
    POWERUP_RAPID,
    POWERUP_SHIELD,
    POWERUP_TRIPLE,
    SCOUT_HEIGHT,
    SCOUT_WIDTH,
)


@dataclass
class Player:
    x: float
    y: float
    w: int = PLAYER_WIDTH
    h: int = PLAYER_HEIGHT
    lives: int = 3
    invincible: int = 0
    anim_frame: int = 0
    shoot_cooldown: int = 0
    rapid_fire: int = 0
    triple_shot: int = 0
    shield: int = 0
    active: bool = True


@dataclass
class Bullet:
    x: float
    y: float
    w: int = 3
    h: int = 3
    speed: float = -8.0
    is_enemy: bool = False
    active: bool = True


@dataclass
class Enemy:
    x: float
    y: float
    kind: str
    w: int
    h: int
    hp: int
    speed_x: float = 0.0
    speed_y: float = 1.0
    points: int = 100
    shoot_timer: int = 0
    active: bool = True
    entry_done: bool = False
    entry_progress: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    char: str
    life: int
    max_life: int
    active: bool = True


@dataclass
class PowerUp:
    x: float
    y: float
    kind: str
    w: int = 5
    h: int = 3
    speed: float = 1.5
    active: bool = True


@dataclass
class Star:
    x: float
    y: float
    char: str
    speed: float
    brightness: int = 0


@dataclass
class Boss:
    x: float
    y: float
    w: int = BOSS_WIDTH
    h: int = BOSS_HEIGHT
    hp: int = 50
    max_hp: int = 50
    phase: int = 0
    attack_timer: int = 0
    move_dir: float = 1.0
    active: bool = True
    flash: int = 0


STYLES = {
    "player": "bold cyan",
    "player_shield": "bold blue on #0000aa",
    "enemy_scout": "bold green",
    "enemy_fighter": "bold red",
    "enemy_hunter": "bold magenta",
    "enemy_kamikaze": "bold yellow",
    "enemy_elite": "bold blue",
    "boss": "bold red on #330000",
    "boss_weak": "bold white on #660000",
    "bullet": "bold white on #0088ff",
    "enemy_bullet": "bold yellow on #ff4400",
    "particle": "orange1",
    "powerup_rapid": "bold yellow",
    "powerup_triple": "bold green",
    "powerup_shield": "bold blue",
    "powerup_laser": "bold magenta",
    "powerup_bomb": "bold red",
    "star1": "bright_black",
    "star2": "grey62",
    "star3": "bright_white",
    "star4": "bold bright_white",
    "hud_label": "grey50",
    "hud_value": "bold yellow",
    "hud_high": "bold yellow on #330000",
    "hud_wave": "bold cyan",
    "hud_lives": "bold red",
    "hud_lives_empty": "bright_black",
    "hud_spread": "bold green",
    "game_over_title": "bold white on #880000",
    "game_over_sub": "bold yellow",
    "wave_announce": "bold cyan on #000033",
    "crt_scanline": "dim",
    "insert_coin": "bold yellow blink",
}

FORMATION_PATTERNS = {
    "v": lambda w, count: [
        (w // 2 + (i - count // 2) * 8, -20 - i * 6) for i in range(count)
    ],
    "wave": lambda w, count: [
        (w // 2 + int(math.sin(i * 0.8) * 30), -20 - i * 5) for i in range(count)
    ],
    "diamond": lambda w, count: [
        (w // 2 + int(math.cos(i * 0.7) * 25), -20 - i * 4) for i in range(count)
    ],
    "arrow": lambda w, count: [
        (w // 2 + (abs(i - count // 2) - count // 2) * 5, -20 - i * 5)
        for i in range(count)
    ],
    "line": lambda w, count: [
        (w // 2 + (i - count // 2) * 10, -20) for i in range(count)
    ],
}

ENEMY_FORMATIONS = [
    {"kind": "scout", "pattern": "v", "count": 5, "hp": 1, "points": 100, "speed": 0.8},
    {
        "kind": "scout",
        "pattern": "wave",
        "count": 6,
        "hp": 1,
        "points": 100,
        "speed": 0.8,
    },
    {
        "kind": "fighter",
        "pattern": "arrow",
        "count": 4,
        "hp": 2,
        "points": 250,
        "speed": 0.6,
    },
    {
        "kind": "scout",
        "pattern": "diamond",
        "count": 7,
        "hp": 1,
        "points": 100,
        "speed": 0.9,
    },
    {
        "kind": "fighter",
        "pattern": "v",
        "count": 5,
        "hp": 2,
        "points": 250,
        "speed": 0.7,
    },
    {
        "kind": "hunter",
        "pattern": "line",
        "count": 3,
        "hp": 3,
        "points": 500,
        "speed": 0.5,
    },
    {
        "kind": "scout",
        "pattern": "wave",
        "count": 8,
        "hp": 1,
        "points": 100,
        "speed": 1.0,
    },
    {
        "kind": "fighter",
        "pattern": "diamond",
        "count": 6,
        "hp": 2,
        "points": 250,
        "speed": 0.7,
    },
    {
        "kind": "kamikaze",
        "pattern": "arrow",
        "count": 4,
        "hp": 1,
        "points": 700,
        "speed": 1.5,
    },
    {
        "kind": "elite",
        "pattern": "line",
        "count": 3,
        "hp": 4,
        "points": 1000,
        "speed": 0.4,
    },
]


def rects_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


class ArcadeEngine:
    FORMATION_WAVE_SIZE = 10

    def __init__(self, width: int = 120, height: int = 40):
        self.WIDTH = width
        self.HEIGHT = height
        self.reset()

    def reset(self):
        self.player = Player(
            x=self.WIDTH // 2 - PLAYER_WIDTH // 2,
            y=self.HEIGHT - PLAYER_HEIGHT - 2,
        )
        self.bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []
        self.particles: list[Particle] = []
        self.powerups: list[PowerUp] = []
        self.score = 0
        self.high_score = 0
        self.wave = 1
        self.subwave = 0
        self.frame = 0
        self.game_over = False
        self.attract_mode = False
        self.shake_x = 0.0
        self.shake_y = 0.0
        self.shake_timer = 0
        self.wave_announce_timer = 0
        self.boss: Optional[Boss] = None
        self.boss_wave = 5
        self._formation_queue: list[dict] = []
        self._formation_delay = 0
        self._enemies_in_formation = 0
        self._total_killed = 0
        self._flash_timer = 0
        self._init_stars()

    def _init_stars(self):
        self.stars = []
        layers = [
            (".", 0.2, 150, "star1"),
            ("*", 0.5, 100, "star2"),
            ("✦", 1.0, 50, "star3"),
            ("✹", 2.0, 25, "star4"),
        ]
        for char, speed, count, style in layers:
            for _ in range(count):
                self.stars.append(
                    Star(
                        x=random.uniform(0, self.WIDTH),
                        y=random.uniform(0, self.HEIGHT),
                        char=char,
                        speed=speed,
                        brightness=random.randint(0, 3),
                    )
                )

    def resize(self, width: int, height: int):
        ratio_x = width / self.WIDTH
        ratio_y = height / self.HEIGHT
        self.WIDTH = width
        self.HEIGHT = height
        self.player.x = min(self.player.x * ratio_x, self.WIDTH - PLAYER_WIDTH)
        self.player.y = self.HEIGHT - PLAYER_HEIGHT - 2
        for s in self.stars:
            s.x *= ratio_x
            s.y *= ratio_y
        for e in self.enemies:
            e.x *= ratio_x
            e.y *= ratio_y
        for b in self.bullets:
            b.x *= ratio_x
            b.y *= ratio_y
        for p in self.particles:
            p.x *= ratio_x
            p.y *= ratio_y
        for p in self.powerups:
            p.x *= ratio_x
            p.y *= ratio_y
        if self.boss:
            self.boss.x *= ratio_x
            self.boss.y *= ratio_y

    def tick(self):
        if self.game_over or self.attract_mode:
            return
        self.frame += 1
        self._update_stars()
        self._handle_shake()
        self._update_player()
        self._update_bullets()
        self._update_enemies()
        self._check_collisions()
        self.bullets = [b for b in self.bullets if b.active]
        self._update_particles()
        self._update_powerups()
        self._update_boss()
        self._handle_formation_spawning()
        self._handle_wave_announce()

    def _update_stars(self):
        for s in self.stars:
            s.y += s.speed
            if s.y >= self.HEIGHT:
                s.y = 0
                s.x = random.uniform(0, self.WIDTH)
                s.brightness = random.randint(0, 3)

    def _handle_shake(self):
        if self.shake_timer > 0:
            self.shake_x = random.uniform(-2, 2)
            self.shake_y = random.uniform(-1, 1)
            self.shake_timer -= 1
        else:
            self.shake_x = 0
            self.shake_y = 0

    def trigger_shake(self, duration: int = 5):
        self.shake_timer = max(self.shake_timer, duration)

    def _update_player(self):
        p = self.player
        if not p.active:
            return
        p.anim_frame = (p.anim_frame + 1) % (len(PLAYER_SPRITES) * 4)
        if p.shoot_cooldown > 0:
            p.shoot_cooldown -= 1
        if p.invincible > 0:
            p.invincible -= 1
        if p.rapid_fire > 0:
            p.rapid_fire -= 1
        if p.triple_shot > 0:
            p.triple_shot -= 1
        if p.shield > 0:
            p.shield -= 1

    def move_left(self):
        if self.game_over or self.attract_mode or not self.player.active:
            return
        self.player.x = max(0, self.player.x - 4)

    def move_right(self):
        if self.game_over or self.attract_mode or not self.player.active:
            return
        self.player.x = min(self.WIDTH - self.player.w, self.player.x + 4)

    def shoot(self):
        if self.game_over or self.attract_mode or not self.player.active:
            return
        p = self.player
        if p.shoot_cooldown > 0:
            return
        cd = 4 if p.rapid_fire > 0 else 8
        p.shoot_cooldown = cd
        bx = p.x + p.w // 2 - 1
        by = p.y - 3
        self.bullets.append(Bullet(bx, by))
        if p.triple_shot > 0:
            self.bullets.append(Bullet(bx - 5, by + 2))
            self.bullets.append(Bullet(bx + 5, by + 2))
        self._flash_timer = 3

    def _update_bullets(self):
        for b in self.bullets:
            b.y += b.speed
            if b.y + b.h < 0 or b.y > self.HEIGHT:
                b.active = False
        self.bullets = [b for b in self.bullets if b.active]

    def _update_enemies(self):
        for e in self.enemies:
            if not e.entry_done:
                e.entry_progress += 0.03
                if e.entry_progress >= 1.0:
                    e.entry_done = True
                    e.x = e.target_x
                    e.y = e.target_y
                    continue
                t = e.entry_progress
                e.x += (e.target_x - e.x) * 0.08
                e.y = e.y + (e.target_y - e.y) * 0.05 + 0.3
            else:
                e.x += e.speed_x
                e.y += e.speed_y
                if e.kind == "kamikaze" and e.y < self.HEIGHT * 0.6:
                    e.speed_y = 3.0
                    e.speed_x = (
                        self.player.x + self.player.w / 2 - e.x - e.w / 2
                    ) * 0.03
                if e.kind == "hunter":
                    dx = self.player.x + self.player.w / 2 - e.x - e.w / 2
                    e.speed_x += dx * 0.005
                    e.speed_x = max(-2, min(2, e.speed_x))
                if e.kind == "elite":
                    e.shoot_timer -= 1
                    if e.shoot_timer <= 0 and e.y > 0:
                        self.bullets.append(
                            Bullet(
                                e.x + e.w // 2,
                                e.y + e.h,
                                speed=3.0,
                                is_enemy=True,
                                w=2,
                                h=3,
                            )
                        )
                        e.shoot_timer = random.randint(30, 90)
            if e.y > self.HEIGHT + 10:
                e.active = False
        self.enemies = [e for e in self.enemies if e.active]

    def _check_collisions(self):
        p = self.player
        if not p.active or p.invincible > 0:
            return
        px, py, pw, ph = p.x, p.y, p.w, p.h
        for e in self.enemies:
            if not e.active:
                continue
            if rects_overlap(px, py, pw, ph, e.x, e.y, e.w, e.h):
                if p.shield > 0:
                    p.shield = 0
                    e.active = False
                    self._spawn_explosion(e.x + e.w // 2, e.y + e.h // 2, 30)
                    self.trigger_shake(4)
                else:
                    self._hit_player()
                break
        for b in self.bullets:
            if not b.active or b.is_enemy:
                continue
            if self.boss and self.boss.active:
                if rects_overlap(
                    b.x,
                    b.y,
                    b.w,
                    b.h,
                    self.boss.x,
                    self.boss.y,
                    self.boss.w,
                    self.boss.h,
                ):
                    self.boss.hp -= 1
                    b.active = False
                    self.boss.flash = 3
                    self.trigger_shake(3)
                    self._spawn_explosion(b.x, b.y, 5)
                    if self.boss.hp <= 0:
                        self._kill_boss()
                    continue
            for e in self.enemies:
                if not e.active:
                    continue
                if rects_overlap(b.x, b.y, b.w, b.h, e.x, e.y, e.w, e.h):
                    b.active = False
                    e.hp -= 1
                    if e.hp <= 0:
                        e.active = False
                        self.score += e.points * self.wave
                        self._total_killed += 1
                        self._spawn_explosion(e.x + e.w // 2, e.y + e.h // 2, 40)
                        self.trigger_shake(2)
                        if random.random() < 0.08:
                            self._drop_powerup(e.x, e.y)
                    break
        for b in self.bullets:
            if not b.active or not b.is_enemy:
                continue
            if rects_overlap(b.x, b.y, b.w, b.h, px, py, pw, ph):
                b.active = False
                if p.shield > 0:
                    p.shield = max(0, p.shield - 30)
                else:
                    self._hit_player()

    def _hit_player(self):
        p = self.player
        p.lives -= 1
        self._spawn_explosion(p.x + p.w // 2, p.y + p.h // 2, 50)
        self.trigger_shake(6)
        if p.lives <= 0:
            p.active = False
            self.game_over = True
            self.high_score = max(self.high_score, self.score)
        else:
            p.invincible = 60
            p.x = self.WIDTH // 2 - PLAYER_WIDTH // 2
            p.y = self.HEIGHT - PLAYER_HEIGHT - 2

    def _spawn_explosion(self, cx: float, cy: float, count: int = 40):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1, 6)
            self.particles.append(
                Particle(
                    x=cx,
                    y=cy,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    char=random.choice(EXPLOSION_PARTICLES),
                    life=random.randint(15, 40),
                    max_life=40,
                )
            )

    def _update_particles(self):
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.08
            p.vx *= 0.98
            p.life -= 1
            if p.life <= 0:
                p.active = False
        self.particles = [p for p in self.particles if p.active]

    def _drop_powerup(self, x: float, y: float):
        kind = random.choice(["rapid", "triple", "shield", "bomb"])
        w = {"rapid": 5, "triple": 3, "shield": 3, "laser": 3, "bomb": 3}[kind]
        self.powerups.append(PowerUp(x, y, kind, w=w))

    def _update_powerups(self):
        for p in self.powerups:
            p.y += p.speed
            if p.y > self.HEIGHT:
                p.active = False
            if rects_overlap(
                p.x,
                p.y,
                p.w,
                p.h,
                self.player.x,
                self.player.y,
                self.player.w,
                self.player.h,
            ):
                p.active = False
                self._apply_powerup(p.kind)
        self.powerups = [p for p in self.powerups if p.active]

    def _apply_powerup(self, kind: str):
        p = self.player
        if kind == "rapid":
            p.rapid_fire = 300
        elif kind == "triple":
            p.triple_shot = 300
        elif kind == "shield":
            p.shield = 300
        elif kind == "bomb":
            self._smart_bomb()

    def _smart_bomb(self):
        for e in self.enemies:
            if e.active:
                e.active = False
                self.score += e.points * self.wave
                self._spawn_explosion(e.x + e.w // 2, e.y + e.h // 2, 20)
        if self.boss and self.boss.active:
            self.boss.hp -= 10
            self.trigger_shake(8)
            if self.boss.hp <= 0:
                self._kill_boss()
        self.enemies = [e for e in self.enemies if e.active]
        self.trigger_shake(6)

    def _handle_formation_spawning(self):
        if self._formation_queue:
            if self._formation_delay <= 0:
                formation = self._formation_queue.pop(0)
                self._spawn_formation(formation)
                self._formation_delay = 60
            else:
                self._formation_delay -= 1
        elif len(self.enemies) == 0 and self.boss is None:
            self.subwave += 1
            if self.wave % self.boss_wave == 0 and self.subwave == 1:
                self._spawn_boss()
            else:
                self._queue_next_formations()

    def _queue_next_formations(self):
        for i in range(3):
            idx = (self.subwave - 1) * 3 + i
            if idx < len(ENEMY_FORMATIONS):
                entry = ENEMY_FORMATIONS[idx]
                if entry["kind"] == "kamikaze" and self.wave < 3:
                    entry = dict(entry, kind="scout", hp=1, points=100, speed=0.8)
                elif entry["kind"] == "elite" and self.wave < 5:
                    entry = dict(entry, kind="fighter", hp=2, points=250, speed=0.7)
                scaled = dict(entry)
                scaled["hp"] = max(1, entry["hp"] + self.wave // 3)
                scaled["speed"] = entry["speed"] + self.wave * 0.05
                self._formation_queue.append(scaled)

    def _spawn_formation(self, formation: dict):
        kind = formation["kind"]
        pattern = formation["pattern"]
        count = formation["count"]
        hp = formation["hp"]
        points = formation["points"]
        speed = formation["speed"]
        positions = FORMATION_PATTERNS[pattern](self.WIDTH, count)
        w = {
            "scout": SCOUT_WIDTH,
            "fighter": FIGHTER_WIDTH,
            "hunter": HUNTER_WIDTH,
            "kamikaze": KAMIKAZE_WIDTH,
            "elite": ELITE_WIDTH,
        }[kind]
        h = {
            "scout": SCOUT_HEIGHT,
            "fighter": FIGHTER_HEIGHT,
            "hunter": HUNTER_HEIGHT,
            "kamikaze": KAMIKAZE_HEIGHT,
            "elite": ELITE_HEIGHT,
        }[kind]
        for i, (tx, ty) in enumerate(positions):
            self.enemies.append(
                Enemy(
                    x=tx,
                    y=ty,
                    kind=kind,
                    w=w,
                    h=h,
                    hp=hp + (1 if kind == "elite" and i == 0 else 0),
                    speed_y=speed,
                    points=points,
                    target_x=max(5, min(self.WIDTH - w - 5, tx)),
                    target_y=max(3, min(self.HEIGHT * 0.4, abs(ty) + 5)),
                )
            )

    def _spawn_boss(self):
        self.boss = Boss(
            x=self.WIDTH // 2 - BOSS_WIDTH // 2,
            y=-BOSS_HEIGHT,
            hp=30 + self.wave * 10,
            max_hp=30 + self.wave * 10,
        )
        self.wave_announce_timer = 60
        self._spawn_explosion(self.WIDTH // 2, 0, 60)
        self.trigger_shake(8)

    def _update_boss(self):
        if not self.boss or not self.boss.active:
            return
        b = self.boss
        if b.flash > 0:
            b.flash -= 1
        if b.y < 3:
            b.y += 0.5
            return
        b.x += b.move_dir * 0.8
        if b.x <= 2 or b.x >= self.WIDTH - b.w - 2:
            b.move_dir *= -1
        b.attack_timer -= 1
        if b.attack_timer <= 0:
            b.attack_timer = max(20, 60 - self.wave * 2)
            attack = random.choice(["sweep", "missile", "spread", "summon"])
            if attack == "sweep":
                by = b.y + b.h
                for bx in range(int(b.x), int(b.x + b.w), 3):
                    self.bullets.append(
                        Bullet(bx, by, speed=4.0, is_enemy=True, w=2, h=3)
                    )
            elif attack == "missile":
                for _ in range(5 + self.wave):
                    bx = b.x + random.uniform(0, b.w)
                    self.bullets.append(
                        Bullet(
                            bx,
                            b.y + b.h,
                            speed=random.uniform(2, 5),
                            is_enemy=True,
                            w=2,
                            h=3,
                        )
                    )
            elif attack == "spread":
                cx = b.x + b.w / 2
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    bx = cx + math.cos(rad) * 15
                    by = b.y + b.h + math.sin(rad) * 15
                    self.bullets.append(
                        Bullet(
                            bx,
                            b.y + b.h,
                            speed=random.uniform(2, 4),
                            is_enemy=True,
                            w=2,
                            h=3,
                        )
                    )
            elif attack == "summon":
                for _ in range(3):
                    sx = random.uniform(0, self.WIDTH - FIGHTER_WIDTH)
                    self.enemies.append(
                        Enemy(
                            x=sx,
                            y=-20,
                            kind="fighter",
                            w=FIGHTER_WIDTH,
                            h=FIGHTER_HEIGHT,
                            hp=2,
                            speed_y=0.8,
                            points=250,
                            target_x=sx,
                            target_y=random.uniform(3, self.HEIGHT * 0.3),
                        )
                    )

    def _kill_boss(self):
        if not self.boss:
            return
        self._spawn_explosion(
            self.boss.x + self.boss.w // 2, self.boss.y + self.boss.h // 2, 120
        )
        self.trigger_shake(12)
        self.score += 5000 * self.wave
        self.boss = None
        self.subwave = 0
        self.wave += 1
        self._formation_queue.clear()
        self._formation_delay = 90
        self._total_killed = 0

    def _handle_wave_announce(self):
        if self.wave_announce_timer > 0:
            self.wave_announce_timer -= 1

    def player_shoot_action(self):
        if self.boss and self.boss.active:
            self.boss.hp -= 5
            self.boss.flash = 5
            self.trigger_shake(6)
            self._spawn_explosion(
                self.boss.x + random.uniform(0, self.boss.w),
                self.boss.y + random.uniform(0, self.boss.h),
                20,
            )
            if self.boss.hp <= 0:
                self._kill_boss()

    def _build_frame(self):
        sw = self.WIDTH
        sh = self.HEIGHT
        sx = int(self.shake_x)
        sy = int(self.shake_y)
        grid = [[(" ", None) for _ in range(sw)] for _ in range(sh)]

        def set_cell(x, y, ch, style):
            gx, gy = int(x) + sx, int(y) + sy
            if 0 <= gy < sh and 0 <= gx < sw:
                grid[gy][gx] = (ch, style)

        def blit_sprite(x, y, sprite, style, w=None):
            for dy, row in enumerate(sprite):
                for dx, ch in enumerate(row):
                    if ch != " ":
                        set_cell(x + dx, y + dy, ch, style)

        for s in self.stars:
            gx, gy = int(s.x) + sx, int(s.y) + sy
            if 0 <= gy < sh and 0 <= gx < sw and grid[gy][gx] == (" ", None):
                blink = s.brightness == 0 and (self.frame + id(s)) % 60 < 2
                style_key = f"star{min(s.brightness + 1, 4) if not blink else 4}"
                grid[gy][gx] = (s.char, style_key)

        p = self.player
        if p.active and not (p.invincible > 0 and self.frame % 6 < 3):
            frame_idx = (p.anim_frame // 4) % len(PLAYER_SPRITES)
            sprite = PLAYER_SPRITES[frame_idx]
            base_style = "player_shield" if p.shield > 0 else "player"
            blit_sprite(p.x, p.y, sprite, base_style)

        for b in self.bullets:
            if b.is_enemy:
                blit_sprite(b.x, b.y, ENEMY_BULLET, "enemy_bullet", w=b.w)
            else:
                blit_sprite(b.x, b.y, BULLET, "bullet", w=b.w)

        for e in self.enemies:
            sprites = {
                "scout": ENEMY_SCOUT,
                "fighter": ENEMY_FIGHTER,
                "hunter": ENEMY_HUNTER,
                "kamikaze": ENEMY_KAMIKAZE,
                "elite": ENEMY_ELITE,
            }
            sprite = sprites.get(e.kind, ENEMY_SCOUT)
            style = f"enemy_{e.kind}"
            blit_sprite(e.x, e.y, sprite, style)

        if self.boss and self.boss.active:
            style = "boss_weak" if self.boss.flash > 0 else "boss"
            blit_sprite(self.boss.x, self.boss.y, BOSS_CORE, style)

        for pt in self.particles:
            alpha = pt.life / pt.max_life
            if alpha > 0.1:
                set_cell(pt.x, pt.y, pt.char, STYLES["particle"])

        for pw in self.powerups:
            sprites = {
                "rapid": POWERUP_RAPID,
                "triple": POWERUP_TRIPLE,
                "shield": POWERUP_SHIELD,
                "laser": POWERUP_LASER,
                "bomb": POWERUP_BOMB,
            }
            sprite = sprites.get(pw.kind, POWERUP_RAPID)
            style = f"powerup_{pw.kind}"
            blit_sprite(pw.x, pw.y, sprite, style)

        if self.game_over:
            msg = "GAME OVER"
            mx = (sw - len(msg)) // 2
            my = sh // 2 - 2
            for i, ch in enumerate(msg):
                if 0 <= my < sh and 0 <= mx + i < sw:
                    grid[my][mx + i] = (ch, "game_over_title")
            sub = f"SCORE: {self.score:07d}"
            sx2 = (sw - len(sub)) // 2
            sy2 = sh // 2 + 1
            for i, ch in enumerate(sub):
                if 0 <= sy2 < sh and 0 <= sx2 + i < sw:
                    grid[sy2][sx2 + i] = (ch, "game_over_sub")
            restart = "PRESS R TO RESTART"
            rx = (sw - len(restart)) // 2
            ry = sh // 2 + 3
            for i, ch in enumerate(restart):
                if 0 <= ry < sh and 0 <= rx + i < sw:
                    grid[ry][rx + i] = (ch, "game_over_sub")

        if self.wave_announce_timer > 0:
            is_boss = self.wave % self.boss_wave == 0
            if is_boss:
                msg = f"⚠ BOSS WAVE {self.wave} ⚠"
            else:
                msg = f"── WAVE {self.wave} ──"
            mx = (sw - len(msg)) // 2
            my = sh // 2 - 4
            for i, ch in enumerate(msg):
                if 0 <= my < sh and 0 <= mx + i < sw:
                    grid[my][mx + i] = (ch, "wave_announce")

        return grid

    def render(self) -> list[str]:
        grid = self._build_frame()
        return ["".join(ch for ch, _ in row) for row in grid]

    def render_styled(self) -> Text:
        grid = self._build_frame()
        text = Text()
        for y, row in enumerate(grid):
            scanline = y % 2 == 1
            current_style = None
            buf = []
            for ch, style_name in row:
                base = STYLES.get(style_name)
                if scanline and base:
                    combined = base + " " + STYLES["crt_scanline"]
                elif scanline:
                    combined = STYLES["crt_scanline"]
                else:
                    combined = base
                if combined != current_style and buf:
                    text.append("".join(buf), style=current_style)
                    buf = []
                current_style = combined
                buf.append(ch)
            if buf:
                text.append("".join(buf), style=current_style)
            text.append("\n")
        return text

    def get_hud_styled(self) -> Text:
        text = Text()
        high = f"HIGH SCORE {self.high_score:07d}"
        score = f"SCORE      {self.score:07d}"
        wave = f"WAVE       {self.wave:02d}"
        lives = "♥ " * self.player.lives if self.player.active else ""
        text.append(f"  {high}", style=STYLES["hud_high"])
        text.append("   ")
        text.append(score, style=STYLES["hud_value"])
        text.append("   ")
        text.append(wave, style=STYLES["hud_wave"])
        text.append("   ")
        text.append(f"LIVES {lives}", style=STYLES["hud_lives"])
        if self.player.rapid_fire > 0:
            text.append("  [RAPID]", style=STYLES["hud_spread"])
        if self.player.triple_shot > 0:
            text.append("  [TRIPLE]", style=STYLES["hud_spread"])
        if self.player.shield > 0:
            text.append("  [SHIELD]", style=STYLES["hud_spread"])
        text.append("\n")
        if self.boss and self.boss.active:
            pct = self.boss.hp / self.boss.max_hp
            bar_len = 30
            filled = int(bar_len * pct)
            text.append("  BOSS  ", style="bold red")
            text.append("█" * filled, style="bold red")
            text.append("░" * (bar_len - filled), style="bright_black")
            text.append("\n")
        return text

    def get_attract_display(self) -> Text:
        text = Text()
        sh = self.HEIGHT
        sw = self.WIDTH
        title = "✦  N O R T H H   I N V A D E R S  ✦"
        tx = (sw - len(title)) // 2
        ty = sh // 2 - 6
        for _ in range(ty):
            text.append("\n")
        text.append(" " * tx)
        text.append(title, style="bold cyan")
        text.append("\n\n")
        sub = "A LOST 1 9 8 2  ARCADE CABINET"
        stx = (sw - len(sub)) // 2
        text.append(" " * stx)
        text.append(sub, style="bold yellow")
        text.append("\n\n\n")
        coin = "INSERT COIN"
        cx2 = (sw - len(coin)) // 2
        text.append(" " * cx2)
        flash = self.frame % 40 < 20
        coin_style = "bold yellow blink" if flash else "bright_black"
        text.append(coin, style=coin_style)
        text.append("\n\n")
        controls = "← →  MOVE   SPACE  FIRE   R  RESTART   ESC  QUIT"
        ctrl_x = (sw - len(controls)) // 2
        text.append(" " * ctrl_x)
        text.append(controls, style="grey50")
        text.append("\n\n")
        hs = f"HIGH SCORE  {self.high_score:07d}"
        hs_x = (sw - len(hs)) // 2
        text.append(" " * hs_x)
        text.append(hs, style="bold yellow")
        text.append("\n")
        return text

    def rescore(self):
        self.high_score = max(self.high_score, self.score)

    def start_game(self):
        self.attract_mode = False
        self.reset()

    def is_attract(self) -> bool:
        return self.attract_mode

    def set_attract(self, val: bool):
        self.attract_mode = val
