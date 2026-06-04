import random

import pytest
from rich.text import Text

from src.easter.engine import (
    ArcadeEngine,
    Bullet,
    Enemy,
    Particle,
    PowerUp,
    rects_overlap,
)
from src.easter.sprites import (
    BULLET,
    ELITE_HEIGHT,
    ELITE_WIDTH,
    ENEMY_ELITE,
    ENEMY_FIGHTER,
    ENEMY_HUNTER,
    ENEMY_KAMIKAZE,
    ENEMY_SCOUT,
    FIGHTER_HEIGHT,
    FIGHTER_WIDTH,
    HUNTER_HEIGHT,
    HUNTER_WIDTH,
    KAMIKAZE_HEIGHT,
    KAMIKAZE_WIDTH,
    PLAYER,
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
    get_dimensions,
    get_sprite,
)


class TestRectOverlap:
    def test_overlapping_rects(self):
        assert rects_overlap(0, 0, 5, 5, 2, 2, 5, 5) is True

    def test_non_overlapping_rects(self):
        assert rects_overlap(0, 0, 5, 5, 10, 10, 5, 5) is False

    def test_touching_edges(self):
        assert rects_overlap(0, 0, 5, 5, 5, 5, 5, 5) is False

    def test_contained(self):
        assert rects_overlap(2, 2, 1, 1, 0, 0, 5, 5) is True

    def test_zero_size(self):
        assert rects_overlap(0, 0, 0, 0, 0, 0, 5, 5) is False


class TestSprites:
    def test_get_sprite_player(self):
        sprite = get_sprite("player")
        assert len(sprite) == PLAYER_HEIGHT
        assert all(len(row) == PLAYER_WIDTH for row in sprite)

    def test_player_sprites_count(self):
        assert len(PLAYER_SPRITES) == 3

    def test_get_sprite_enemy_scout(self):
        sprite = get_sprite("enemy_scout")
        assert len(sprite) == SCOUT_HEIGHT
        assert all(len(row) == SCOUT_WIDTH for row in sprite)

    def test_get_sprite_enemy_fighter(self):
        sprite = get_sprite("enemy_fighter")
        assert len(sprite) == FIGHTER_HEIGHT
        assert all(len(row) == FIGHTER_WIDTH for row in sprite)

    def test_get_sprite_enemy_hunter(self):
        sprite = get_sprite("enemy_hunter")
        assert len(sprite) == HUNTER_HEIGHT
        assert all(len(row) == HUNTER_WIDTH for row in sprite)

    def test_get_sprite_enemy_kamikaze(self):
        sprite = get_sprite("enemy_kamikaze")
        assert len(sprite) == KAMIKAZE_HEIGHT
        assert all(len(row) == KAMIKAZE_WIDTH for row in sprite)

    def test_get_sprite_enemy_elite(self):
        sprite = get_sprite("enemy_elite")
        assert len(sprite) == ELITE_HEIGHT
        assert all(len(row) == ELITE_WIDTH for row in sprite)

    def test_get_sprite_bullet(self):
        sprite = get_sprite("bullet")
        assert len(sprite) == 3
        assert all(len(row) == 3 for row in sprite)

    def test_get_dimensions(self):
        assert get_dimensions("player") == (PLAYER_WIDTH, PLAYER_HEIGHT)
        assert get_dimensions("enemy_scout") == (10, 6)
        assert get_dimensions("enemy_fighter") == (12, 7)
        assert get_dimensions("enemy_hunter") == (12, 7)
        assert get_dimensions("enemy_kamikaze") == (11, 7)
        assert get_dimensions("enemy_elite") == (12, 7)

    def test_get_sprite_unknown(self):
        sprite = get_sprite("nonexistent")
        assert sprite == ("?",)

    def test_get_dimensions_unknown(self):
        assert get_dimensions("nonexistent") == (1, 1)


class TestEngineInit:
    def test_engine_initializes(self):
        eng = ArcadeEngine(width=120, height=40)
        assert eng.player.lives == 3
        assert eng.score == 0
        assert eng.wave == 1
        assert eng.game_over is False
        assert eng.frame == 0
        assert len(eng.bullets) == 0
        assert len(eng.enemies) == 0
        assert len(eng.particles) == 0
        assert len(eng.powerups) == 0
        assert len(eng.stars) > 0

    def test_engine_default_dimensions(self):
        eng = ArcadeEngine()
        assert eng.WIDTH == 120
        assert eng.HEIGHT == 40

    def test_engine_custom_dimensions(self):
        eng = ArcadeEngine(width=80, height=30)
        assert eng.WIDTH == 80
        assert eng.HEIGHT == 30

    def test_engine_reset_restores_defaults(self):
        eng = ArcadeEngine()
        eng.score = 999
        eng.wave = 10
        eng.player.lives = 1
        eng.reset()
        assert eng.score == 0
        assert eng.wave == 1
        assert eng.player.lives == 3
        assert len(eng.bullets) == 0

    def test_player_start_position_bottom(self):
        eng = ArcadeEngine(width=120, height=40)
        assert eng.player.y == 40 - PLAYER_HEIGHT - 2
        assert eng.player.x == 120 // 2 - PLAYER_WIDTH // 2

    def test_engine_attract_mode_off_by_default(self):
        eng = ArcadeEngine()
        assert eng.is_attract() is False

    def test_engine_set_attract(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        assert eng.is_attract() is True

    def test_engine_stars_have_four_layers(self):
        eng = ArcadeEngine()
        chars = [s.char for s in eng.stars]
        assert "." in chars
        assert "*" in chars
        assert "✦" in chars
        assert "✹" in chars


class TestEngineMovement:
    def test_move_left(self):
        eng = ArcadeEngine()
        start_x = eng.player.x
        eng.move_left()
        assert eng.player.x == start_x - 4

    def test_move_left_clamps(self):
        eng = ArcadeEngine()
        eng.player.x = 1
        eng.move_left()
        assert eng.player.x == 0
        eng.move_left()
        assert eng.player.x == 0

    def test_move_right(self):
        eng = ArcadeEngine()
        start_x = eng.player.x
        eng.move_right()
        assert eng.player.x == start_x + 4

    def test_move_right_clamps(self):
        eng = ArcadeEngine()
        eng.player.x = eng.WIDTH - PLAYER_WIDTH
        eng.move_right()
        assert eng.player.x == eng.WIDTH - PLAYER_WIDTH

    def test_no_movement_when_game_over(self):
        eng = ArcadeEngine()
        eng.game_over = True
        start_x = eng.player.x
        eng.move_left()
        assert eng.player.x == start_x

    def test_no_movement_in_attract_mode(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        start_x = eng.player.x
        eng.move_left()
        assert eng.player.x == start_x


class TestEngineShooting:
    def test_shoot_creates_bullet(self):
        eng = ArcadeEngine()
        eng.shoot()
        assert len(eng.bullets) == 1
        bx = eng.player.x + PLAYER_WIDTH // 2 - 1
        assert eng.bullets[0].x == bx
        assert eng.bullets[0].y == eng.player.y - 3

    def test_shoot_cooldown(self):
        eng = ArcadeEngine()
        eng.shoot()
        eng.shoot()
        assert len(eng.bullets) == 1

    def test_shoot_after_cooldown(self):
        eng = ArcadeEngine()
        eng.shoot()
        eng.player.shoot_cooldown = 0
        eng.shoot()
        assert len(eng.bullets) == 2

    def test_rapid_fire_faster_cooldown(self):
        eng = ArcadeEngine()
        eng.player.rapid_fire = 100
        eng.shoot()
        eng.shoot()
        assert len(eng.bullets) == 1
        eng.player.shoot_cooldown = 0
        eng.shoot()
        assert len(eng.bullets) == 2

    def test_triple_shot_three_bullets(self):
        eng = ArcadeEngine()
        eng.player.triple_shot = 100
        eng.shoot()
        assert len(eng.bullets) == 3

    def test_no_shoot_when_game_over(self):
        eng = ArcadeEngine()
        eng.game_over = True
        eng.shoot()
        assert len(eng.bullets) == 0

    def test_no_shoot_in_attract_mode(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        eng.shoot()
        assert len(eng.bullets) == 0


class TestEngineBulletMovement:
    def test_bullet_moves_up(self):
        eng = ArcadeEngine()
        eng.shoot()
        by = eng.bullets[0].y
        eng.tick()
        assert eng.bullets[0].y == by - 8

    def test_bullet_removed_when_off_screen(self):
        eng = ArcadeEngine()
        eng.bullets.append(Bullet(10, 2))
        eng.tick()
        assert len(eng.bullets) == 0


class TestEngineCollision:
    def test_bullet_hits_enemy(self):
        eng = ArcadeEngine()
        eng.bullets.append(Bullet(50, 30))
        eng.enemies.append(
            Enemy(48, 23, "scout", 10, 6, 1, points=100, entry_done=True)
        )
        eng.tick()
        assert len(eng.bullets) == 0

    def test_hit_enemy_adds_score(self):
        eng = ArcadeEngine()
        eng.bullets.append(Bullet(50, 30))
        eng.enemies.append(
            Enemy(48, 23, "scout", 10, 6, 1, points=100, entry_done=True)
        )
        eng.tick()
        assert eng.score == 100

    def test_hit_enemy_creates_particles(self):
        eng = ArcadeEngine()
        eng.bullets.append(Bullet(50, 30))
        eng.enemies.append(
            Enemy(48, 23, "scout", 10, 6, 1, points=100, entry_done=True)
        )
        eng.tick()
        assert len(eng.particles) > 0

    def test_tank_enemy_survives_hit(self):
        eng = ArcadeEngine()
        eng.bullets.append(Bullet(50, 30))
        eng.enemies.append(
            Enemy(48, 23, "fighter", 12, 7, 2, points=250, entry_done=True)
        )
        eng.tick()
        fighter = [e for e in eng.enemies if e.active]
        assert len(fighter) > 0
        assert fighter[0].hp == 1

    def test_enemy_hits_player(self):
        eng = ArcadeEngine()
        eng.player.invincible = 0
        e = Enemy(eng.player.x, eng.player.y, "scout", 10, 6, 1)
        e.entry_done = True
        eng.enemies.append(e)
        eng.tick()
        assert eng.player.lives == 2

    def test_player_invincibility_prevents_damage(self):
        eng = ArcadeEngine()
        eng.player.invincible = 60
        e = Enemy(eng.player.x, eng.player.y, "scout", 10, 6, 1)
        e.entry_done = True
        eng.enemies.append(e)
        eng.tick()
        assert eng.player.lives == 3

    def test_shield_absorbs_hit(self):
        eng = ArcadeEngine()
        eng.player.invincible = 0
        eng.player.shield = 100
        e = Enemy(eng.player.x, eng.player.y, "scout", 10, 6, 1)
        e.entry_done = True
        eng.enemies.append(e)
        eng.tick()
        assert eng.player.lives == 3
        assert eng.player.shield == 0


class TestEngineParticles:
    def test_spawn_explosion_creates_particles(self):
        eng = ArcadeEngine()
        eng._spawn_explosion(50, 30, 20)
        assert len(eng.particles) == 20

    def test_particles_move_and_fade(self):
        eng = ArcadeEngine()
        eng._spawn_explosion(50, 30, 5)
        eng.tick()
        assert all(p.x != 50 or p.y != 30 for p in eng.particles)

    def test_particles_removed_when_expired(self):
        eng = ArcadeEngine()
        eng.particles.append(Particle(50, 30, 0, 0, "*", life=1, max_life=10))
        eng.tick()
        assert len(eng.particles) == 0


class TestEnginePowerUp:
    def test_collect_rapid_fire(self):
        eng = ArcadeEngine()
        eng._apply_powerup("rapid")
        assert eng.player.rapid_fire > 0

    def test_collect_triple_shot(self):
        eng = ArcadeEngine()
        eng._apply_powerup("triple")
        assert eng.player.triple_shot > 0

    def test_collect_shield(self):
        eng = ArcadeEngine()
        eng._apply_powerup("shield")
        assert eng.player.shield > 0

    def test_smart_bomb_kills_all_enemies(self):
        eng = ArcadeEngine()
        eng.enemies.append(Enemy(50, 20, "scout", 10, 6, 1))
        eng._apply_powerup("bomb")
        assert len(eng.enemies) == 0

    def test_powerup_moves_down(self):
        eng = ArcadeEngine()
        eng.powerups.append(PowerUp(50, 0, "rapid"))
        eng.tick()
        assert eng.powerups[0].y > 0

    def test_powerup_removed_off_screen(self):
        eng = ArcadeEngine()
        eng.powerups.append(PowerUp(50, eng.HEIGHT + 5, "rapid"))
        eng.tick()
        assert len(eng.powerups) == 0


class TestEngineScreenShake:
    def test_trigger_shake_sets_timer(self):
        eng = ArcadeEngine()
        eng.trigger_shake(5)
        assert eng.shake_timer == 5

    def test_shake_decays(self):
        eng = ArcadeEngine()
        eng.trigger_shake(3)
        assert eng.shake_x == 0
        eng.tick()
        assert eng.shake_timer == 2


class TestEngineRender:
    def test_render_returns_list_of_strings(self):
        eng = ArcadeEngine(width=80, height=30)
        result = eng.render()
        assert isinstance(result, list)
        assert len(result) == 30
        assert all(len(row) == 80 for row in result)

    def test_render_styled_returns_text(self):
        eng = ArcadeEngine()
        result = eng.render_styled()
        assert isinstance(result, Text)

    def test_render_styled_matches_render(self):
        eng = ArcadeEngine(width=80, height=30)
        eng.player.invincible = 0
        styled = eng.render_styled()
        plain = eng.render()
        assert styled.plain.rstrip("\n") == "\n".join(plain).rstrip("\n")


class TestEngineHUD:
    def test_hud_styled_returns_text(self):
        eng = ArcadeEngine()
        result = eng.get_hud_styled()
        assert isinstance(result, Text)

    def test_hud_contains_score(self):
        eng = ArcadeEngine()
        eng.score = 42
        result = eng.get_hud_styled()
        assert "0000042" in result.plain

    def test_hud_contains_high_score(self):
        eng = ArcadeEngine()
        eng.high_score = 9999
        result = eng.get_hud_styled()
        assert "0009999" in result.plain

    def test_hud_contains_wave(self):
        eng = ArcadeEngine()
        eng.wave = 7
        result = eng.get_hud_styled()
        assert "07" in result.plain

    def test_hud_lives(self):
        eng = ArcadeEngine()
        result = eng.get_hud_styled()
        assert "♥" in result.plain

    def test_hud_rapid_indicator(self):
        eng = ArcadeEngine()
        eng.player.rapid_fire = 100
        result = eng.get_hud_styled()
        assert "RAPID" in result.plain

    def test_hud_triple_indicator(self):
        eng = ArcadeEngine()
        eng.player.triple_shot = 100
        result = eng.get_hud_styled()
        assert "TRIPLE" in result.plain

    def test_hud_shield_indicator(self):
        eng = ArcadeEngine()
        eng.player.shield = 100
        result = eng.get_hud_styled()
        assert "SHIELD" in result.plain

    def test_hud_no_indicators_by_default(self):
        eng = ArcadeEngine()
        result = eng.get_hud_styled()
        assert "RAPID" not in result.plain
        assert "TRIPLE" not in result.plain
        assert "SHIELD" not in result.plain

    def test_hud_boss_bar(self):
        from src.easter.engine import Boss

        eng = ArcadeEngine()
        eng.boss = Boss(x=10, y=10)
        result = eng.get_hud_styled()
        assert "BOSS" in result.plain


class TestEngineEdgeCases:
    def test_tick_with_game_over_does_nothing(self):
        eng = ArcadeEngine()
        eng.game_over = True
        eng.tick()
        assert eng.frame == 0

    def test_tick_increments_frame(self):
        eng = ArcadeEngine()
        eng.tick()
        assert eng.frame == 1

    def test_attract_mode_skips_tick(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        eng.tick()
        assert eng.frame == 0

    def test_resize_updates_dimensions(self):
        eng = ArcadeEngine(width=120, height=40)
        eng.resize(160, 50)
        assert eng.WIDTH == 160
        assert eng.HEIGHT == 50

    def test_start_game_clears_attract(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        eng.start_game()
        assert eng.is_attract() is False
        assert eng.frame == 0

    def test_rescore_updates_high_score(self):
        eng = ArcadeEngine()
        eng.score = 5000
        eng.rescore()
        assert eng.high_score == 5000

    def test_rescore_does_not_lower_high_score(self):
        eng = ArcadeEngine()
        eng.high_score = 10000
        eng.score = 5000
        eng.rescore()
        assert eng.high_score == 10000

    def test_survive_many_ticks(self):
        eng = ArcadeEngine(width=80, height=30)
        ticks = 0
        for _ in range(50):
            eng.tick()
            if not eng.game_over:
                ticks += 1
        assert eng.score >= 0
        assert ticks > 0

    def test_player_death_triggers_game_over(self):
        eng = ArcadeEngine()
        eng.player.lives = 1
        eng.player.invincible = 0
        e = Enemy(eng.player.x, eng.player.y, "scout", 10, 6, 1)
        e.entry_done = True
        eng.enemies.append(e)
        eng.tick()
        assert eng.game_over is True or eng.player.lives == 0


class TestAttractMode:
    def test_attract_display_returns_text(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        result = eng.get_attract_display()
        assert isinstance(result, Text)

    def test_attract_display_contains_title(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        result = eng.get_attract_display()
        assert "N O R T H H" in result.plain

    def test_attract_display_contains_insert_coin(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        result = eng.get_attract_display()
        assert "INSERT COIN" in result.plain

    def test_attract_display_contains_controls(self):
        eng = ArcadeEngine()
        eng.set_attract(True)
        result = eng.get_attract_display()
        assert "SPACE" in result.plain
        assert "ESC" in result.plain


class TestBoss:
    def test_boss_spawns_at_correct_wave(self):
        eng = ArcadeEngine()
        eng.boss_wave = 5
        eng._spawn_boss()
        assert eng.boss is not None
        assert eng.boss.active is True
        assert eng.boss.hp > 0

    def test_boss_enters_from_top(self):
        eng = ArcadeEngine()
        eng._spawn_boss()
        assert eng.boss.y < 0

    def test_boss_kill_gives_score(self):
        eng = ArcadeEngine()
        eng._spawn_boss()
        eng.boss.y = 5
        eng.score = 0
        eng._kill_boss()
        assert eng.score > 0

    def test_boss_kill_creates_particles(self):
        eng = ArcadeEngine()
        eng._spawn_boss()
        eng._kill_boss()
        assert len(eng.particles) > 0


class TestStarfield:
    def test_stars_move_down(self):
        eng = ArcadeEngine()
        y_positions = [(s.y, s.speed) for s in eng.stars[:10]]
        eng.tick()
        for (old_y, speed), s in zip(y_positions, eng.stars[:10]):
            expected = old_y + speed
            actual = s.y
            if expected >= eng.HEIGHT:
                assert actual == 0
            else:
                assert actual == pytest.approx(expected, abs=0.01)

    def test_stars_wrap_around(self):
        eng = ArcadeEngine()
        for s in eng.stars:
            s.y = eng.HEIGHT - 0.5
        eng.tick()
        assert any(s.y == 0 for s in eng.stars)

    def test_stars_have_varied_chars(self):
        eng = ArcadeEngine()
        chars = set(s.char for s in eng.stars)
        assert len(chars) >= 3


class TestSpaceshipScreen:
    def test_screen_importable(self):
        from src.easter.screen import SpaceshipScreen

        assert SpaceshipScreen is not None

    def test_screen_has_bindings(self):
        from src.easter.screen import SpaceshipScreen

        assert len(SpaceshipScreen.BINDINGS) > 0

    def test_screen_compose(self):
        from src.easter.screen import SpaceshipScreen

        screen = SpaceshipScreen()
        widgets = list(screen.compose())
        assert len(widgets) > 0

    def test_screen_has_engine(self):
        from src.easter.screen import SpaceshipScreen

        screen = SpaceshipScreen()
        assert screen.engine is not None
        assert screen.engine.player.lives == 3

    def test_old_import_still_works(self):
        from src.ui.screens.spaceship import Spaceship

        assert Spaceship is not None

    def test_screen_starts_in_attract(self):
        from src.easter.screen import SpaceshipScreen

        screen = SpaceshipScreen()
        assert screen.engine.is_attract() is True
