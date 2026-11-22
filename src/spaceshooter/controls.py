"""Player controls: rebindable keyboard keys, gamepad, and menu commands.

The arrow keys and Space always work. On top of them each action has custom keys,
WASD and ZQSD by default (so both QWERTY and AZERTY play out of the box), which the
player can change from the "Commandes" screen.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, StrEnum

import pygame


class Action(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    FIRE = "fire"


ACTION_LABELS = {
    Action.LEFT: "Gauche",
    Action.RIGHT: "Droite",
    Action.UP: "Haut",
    Action.DOWN: "Bas",
    Action.FIRE: "Tirer",
}
FIXED_KEYS = {
    Action.LEFT: pygame.K_LEFT,
    Action.RIGHT: pygame.K_RIGHT,
    Action.UP: pygame.K_UP,
    Action.DOWN: pygame.K_DOWN,
    Action.FIRE: pygame.K_SPACE,
}
DEFAULT_KEYS = {
    Action.LEFT: (pygame.K_a, pygame.K_q),
    Action.RIGHT: (pygame.K_d,),
    Action.UP: (pygame.K_w, pygame.K_z),
    Action.DOWN: (pygame.K_s,),
    Action.FIRE: (),
}
# Keys with a global meaning (pause, mute, fullscreen) or already fixed to an action.
RESERVED_KEYS = frozenset(
    {pygame.K_ESCAPE, pygame.K_p, pygame.K_m, pygame.K_F11, *FIXED_KEYS.values()}
)
KEY_NAMES = {pygame.K_SPACE: "Espace", pygame.K_RETURN: "Entrée", pygame.K_TAB: "Tab"}


def key_name(key: int) -> str:
    return KEY_NAMES.get(key) or pygame.key.name(key).upper() or f"#{key}"


class Bindings:
    """Custom keys of each action (the fixed keys are always added)."""

    def __init__(self, keys: Mapping[Action, Sequence[int]] | None = None) -> None:
        source = DEFAULT_KEYS if keys is None else keys
        self.custom = {action: tuple(source.get(action, ())) for action in Action}

    def keys_for(self, action: Action) -> tuple[int, ...]:
        return (FIXED_KEYS[action], *self.custom[action])

    def bind(self, action: Action, key: int) -> bool:
        """Make `key` the only custom key of `action`. Returns False for a reserved key."""
        if key in RESERVED_KEYS:
            return False
        for other in Action:  # a key drives a single action
            self.custom[other] = tuple(k for k in self.custom[other] if k != key)
        self.custom[action] = (key,)
        return True

    def reset(self) -> None:
        self.custom = dict(DEFAULT_KEYS)

    @property
    def is_default(self) -> bool:
        return self.custom == DEFAULT_KEYS

    def label(self, action: Action) -> str:
        return " / ".join(key_name(key) for key in self.custom[action]) or "aucune"

    def to_json(self) -> dict[str, list[int]]:
        return {action.value: list(keys) for action, keys in self.custom.items()}

    @classmethod
    def from_json(cls, data: object) -> "Bindings":
        """Rebuild saved bindings, falling back to the defaults for anything odd."""
        bindings = cls()
        if not isinstance(data, dict):
            return bindings
        for action in Action:
            keys = data.get(action.value)
            if isinstance(keys, list) and all(isinstance(k, int) for k in keys):
                bindings.custom[action] = tuple(k for k in keys if k not in RESERVED_KEYS)
        return bindings


@dataclass(frozen=True)
class PlayerInput:
    dx: int = 0  # -1 left, 0 none, +1 right
    dy: int = 0  # -1 up, 0 none, +1 down
    fire: bool = False

    def __or__(self, other: "PlayerInput") -> "PlayerInput":
        """Combine two sources (keyboard and gamepad): directions add up, fire is either."""
        return PlayerInput(
            dx=max(-1, min(1, self.dx + other.dx)),
            dy=max(-1, min(1, self.dy + other.dy)),
            fire=self.fire or other.fire,
        )


def read_input(pressed: Sequence[bool], bindings: Bindings | None = None) -> PlayerInput:
    """Translate the state from pygame.key.get_pressed() into player intent."""
    bindings = bindings or Bindings()

    def held(action: Action) -> bool:
        return any(pressed[key] for key in bindings.keys_for(action))

    return PlayerInput(
        dx=int(held(Action.RIGHT)) - int(held(Action.LEFT)),
        dy=int(held(Action.DOWN)) - int(held(Action.UP)),
        fire=held(Action.FIRE),
    )


class Command(Enum):
    """What an event means for menus and scenes, whatever device it came from."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    CONFIRM = "confirm"
    BACK = "back"
    PAUSE = "pause"


KEY_COMMANDS = {
    pygame.K_UP: Command.UP,
    pygame.K_w: Command.UP,
    pygame.K_z: Command.UP,
    pygame.K_DOWN: Command.DOWN,
    pygame.K_s: Command.DOWN,
    pygame.K_LEFT: Command.LEFT,
    pygame.K_RIGHT: Command.RIGHT,
    pygame.K_RETURN: Command.CONFIRM,
    pygame.K_KP_ENTER: Command.CONFIRM,
    pygame.K_SPACE: Command.CONFIRM,
    pygame.K_ESCAPE: Command.BACK,
    pygame.K_p: Command.PAUSE,
}


def command(event: pygame.event.Event) -> Command | None:
    if event.type == pygame.KEYDOWN:
        return KEY_COMMANDS.get(event.key)
    from spaceshooter.gamepad import gamepads  # local import: gamepad needs Command

    return gamepads.command(event)
