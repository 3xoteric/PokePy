# Pokepy

import time
from engine import Screen, Color, make_battle_screen

PIKACHU_SPRITE = [
    "   /\\_/\\  ",
    "  ( o.o ) ",
    "  > ^ <   ",
    " /|   |\\ ",
]

CHARMANDER_SPRITE = [
    "    _   ",
    "   (o)  ",
    "  /|=|\\",
    " / | | \\",
]


def demo_battle():
    screen = Screen()
    try:
        player_hp = 35
        enemy_hp  = 39

        make_battle_screen(
            screen,
            player_name="PIKACHU",  player_hp=player_hp, player_max_hp=35,
            enemy_name="CHARMANDER", enemy_hp=enemy_hp,  enemy_max_hp=39,
            message="Um CHARMANDER selvagem apareceu!",
        )

        screen.draw_sprite(10, 20, CHARMANDER_SPRITE, Color.RED)
        screen.draw_sprite(60, 40, PIKACHU_SPRITE,    Color.YELLOW)

        screen.render()
        time.sleep(3)

    finally:
        screen.close()


if __name__ == "__main__":
    demo_battle()