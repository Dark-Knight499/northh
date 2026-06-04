PLAYER = (
    "       ██      ",
    "      ████     ",
    "     ██████    ",
    "   ██████████  ",
    " ██████████████",
    "██████ ██ █████",
    "████   ██  ████",
    " ███   ██   ███",
    "      ████     ",
)

PLAYER_THRUST = (
    "       ██      ",
    "      ████     ",
    "     ██████    ",
    "   ██████████  ",
    " ██████████████",
    "██████ ██ █████",
    "████   ██  ████",
    " ███   ██   ███",
    "    ████████   ",
)

PLAYER_THRUST2 = (
    "       ██      ",
    "      ████     ",
    "     ██████    ",
    "   ██████████  ",
    " ██████████████",
    "██████ ██ █████",
    "████   ██  ████",
    " ███   ██   ███",
    "   ▄██████▄   ",
)

ENEMY_SCOUT = (
    "  ▄▄██▄▄  ",
    " ████████ ",
    "██████████",
    "██████████",
    " ▀██████▀ ",
    "  ▀▀  ▀▀  ",
)

ENEMY_FIGHTER = (
    "   ▄▄██▄▄   ",
    "  ████████  ",
    " ██ ████ ██ ",
    "████████████",
    " ██████████ ",
    "   ██ ▄▄ ██ ",
    "      ▀▀    ",
)

ENEMY_HUNTER = (
    "  ▄██████▄  ",
    " ▄████████▄ ",
    "██ █▀▀▀█ ██ ",
    "████████████",
    " ▀████████▀ ",
    "  ▀██████▀  ",
    "   ██  ██   ",
)

ENEMY_KAMIKAZE = (
    "   ▄▄▄▄▄   ",
    "  ▄█████▄  ",
    " █████████ ",
    " █▀█ █ █▀█ ",
    " ▀███████▀ ",
    "  ▀█████▀  ",
    "   ▀▄▄▄▀   ",
)

ENEMY_ELITE = (
    "  ▄▄▄▄▄▄▄▄  ",
    " ▄████████▄ ",
    "██ █ ██ █ ██",
    "████████████",
    "██ █ ██ █ ██",
    " ▀████████▀ ",
    "  ▀▀▀▀▀▀▀▀  ",
)

BOSS_CORE = (
    " ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ",
    "▄▄████████████████████▄▄",
    "██ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ██",
    "██ ██████████████████ ██",
    "██ ██ ▄▄▄▄▄▄▄▄▄▄▄▄ ██ ██",
    "██ ██ ██████████████ ██ ██",
    "██ ██ ██ ████ ██████ ██ ██",
    "██ ██ ██ ████ ██████ ██ ██",
    "██ ██ ██ ████ ██████ ██ ██",
    "██ ██ ██ ████ ██████ ██ ██",
    "██ ██ ██ ████ ██████ ██ ██",
    "██ ██ ██████████████ ██ ██",
    "██ ██ ▀▀▀▀▀▀▀▀▀▀▀▀ ██ ██",
    "██ ██████████████████ ██",
    "██ ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀ ██",
    "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
)

BULLET = (
    "▄█▄",
    "███",
    "▀█▀",
)

ENEMY_BULLET = (
    "▄▄",
    "██",
    "▀▀",
)

PLAYER_WIDTH = 15
PLAYER_HEIGHT = 9
BOSS_WIDTH = 22
BOSS_HEIGHT = 16
SCOUT_WIDTH = 10
SCOUT_HEIGHT = 6
FIGHTER_WIDTH = 12
FIGHTER_HEIGHT = 7
HUNTER_WIDTH = 12
HUNTER_HEIGHT = 7
KAMIKAZE_WIDTH = 11
KAMIKAZE_HEIGHT = 7
ELITE_WIDTH = 12
ELITE_HEIGHT = 7

PLAYER_SPRITES = [PLAYER, PLAYER_THRUST, PLAYER_THRUST2]

EXPLOSION_PARTICLES = ["█", "▓", "▒", "░", "▄", "▀", "●", "◆", "✦", "✹"]

POWERUP_RAPID = (
    "▄██▄",
    "███",
    "▀██▀",
)

POWERUP_TRIPLE = (
    "▄▄▄",
    "███",
    "▀▀▀",
)

POWERUP_SHIELD = (
    "▄▄▄",
    "███",
    "▀▀▀",
)

POWERUP_LASER = (
    "▄▄▄",
    "███",
    "▀▀▀",
)

POWERUP_BOMB = (
    "▄▄▄",
    "███",
    "▀▀▀",
)


def get_sprite(name):
    sprites = {
        "player": PLAYER,
        "player_thrust": PLAYER_THRUST,
        "player_thrust2": PLAYER_THRUST2,
        "enemy_scout": ENEMY_SCOUT,
        "enemy_fighter": ENEMY_FIGHTER,
        "enemy_hunter": ENEMY_HUNTER,
        "enemy_kamikaze": ENEMY_KAMIKAZE,
        "enemy_elite": ENEMY_ELITE,
        "boss": BOSS_CORE,
        "bullet": BULLET,
        "enemy_bullet": ENEMY_BULLET,
        "powerup_rapid": POWERUP_RAPID,
        "powerup_triple": POWERUP_TRIPLE,
        "powerup_shield": POWERUP_SHIELD,
        "powerup_laser": POWERUP_LASER,
        "powerup_bomb": POWERUP_BOMB,
    }
    return sprites.get(name, ("?",))


def get_dimensions(name):
    dims = {
        "player": (PLAYER_WIDTH, PLAYER_HEIGHT),
        "enemy_scout": (SCOUT_WIDTH, SCOUT_HEIGHT),
        "enemy_fighter": (FIGHTER_WIDTH, FIGHTER_HEIGHT),
        "enemy_hunter": (HUNTER_WIDTH, HUNTER_HEIGHT),
        "enemy_kamikaze": (KAMIKAZE_WIDTH, KAMIKAZE_HEIGHT),
        "enemy_elite": (ELITE_WIDTH, ELITE_HEIGHT),
        "boss": (BOSS_WIDTH, BOSS_HEIGHT),
        "bullet": (3, 3),
        "enemy_bullet": (2, 3),
        "powerup_rapid": (5, 3),
        "powerup_triple": (3, 3),
        "powerup_shield": (3, 3),
        "powerup_laser": (3, 3),
        "powerup_bomb": (3, 3),
    }
    return dims.get(name, (1, 1))
