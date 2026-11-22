import pygame
import pytest

from spaceshooter.controls import (
    DEFAULT_KEYS,
    Action,
    Bindings,
    Command,
    PlayerInput,
    command,
    read_input,
)
from spaceshooter.gamepad import Gamepads, Pad
from spaceshooter.save import SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.controls import ControlsScene
from spaceshooter.scenes.title import TitleScene


class Keys(dict):
    def __missing__(self, key):
        return False


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class FakeJoystick:
    """Stand-in for pygame.joystick.Joystick with the W3C standard layout."""

    def __init__(self, buttons=(), axes=(0.0, 0.0), hat=(0, 0)):
        self.buttons = set(buttons)
        self.axes = axes
        self.hat = hat

    def get_numbuttons(self):
        return 17

    def get_button(self, index):
        return index in self.buttons

    def get_numaxes(self):
        return len(self.axes)

    def get_axis(self, index):
        return self.axes[index]

    def get_numhats(self):
        return 1

    def get_hat(self, index):
        return self.hat


# --- keyboard bindings -------------------------------------------------------


def test_rebound_key_moves_and_old_one_does_not():
    bindings = Bindings()
    assert bindings.bind(Action.LEFT, pygame.K_j)
    assert read_input(Keys({pygame.K_j: True}), bindings) == PlayerInput(dx=-1)
    assert read_input(Keys({pygame.K_q: True}), bindings) == PlayerInput()
    assert read_input(Keys({pygame.K_LEFT: True}), bindings) == PlayerInput(dx=-1)  # fixed


def test_a_key_drives_a_single_action():
    bindings = Bindings()
    bindings.bind(Action.FIRE, pygame.K_q)
    assert pygame.K_q not in bindings.custom[Action.LEFT]
    assert read_input(Keys({pygame.K_q: True}), bindings) == PlayerInput(fire=True)


@pytest.mark.parametrize("reserved", [pygame.K_ESCAPE, pygame.K_p, pygame.K_m, pygame.K_UP])
def test_reserved_keys_cannot_be_bound(reserved):
    bindings = Bindings()
    assert not bindings.bind(Action.FIRE, reserved)
    assert bindings.is_default


def test_bindings_survive_a_save(tmp_path):
    save = SaveData(tmp_path / "save.json")
    save.bindings.bind(Action.UP, pygame.K_i)
    save.save()
    again = SaveData(tmp_path / "save.json")
    assert again.bindings.custom[Action.UP] == (pygame.K_i,)
    assert again.bindings.custom[Action.LEFT] == DEFAULT_KEYS[Action.LEFT]


@pytest.mark.parametrize("data", [None, "x", {"left": "a"}, {"left": [1.5]}])
def test_odd_saved_bindings_fall_back_to_defaults(data):
    assert Bindings.from_json(data).is_default


def test_reset_restores_defaults():
    bindings = Bindings()
    bindings.bind(Action.DOWN, pygame.K_k)
    bindings.reset()
    assert bindings.is_default


def test_inputs_combine():
    combined = PlayerInput(dx=1) | PlayerInput(dx=1, dy=-1, fire=True)
    assert combined == PlayerInput(dx=1, dy=-1, fire=True)
    assert (PlayerInput(dx=-1) | PlayerInput(dx=1)).dx == 0


@pytest.mark.parametrize(
    ("k", "expected"),
    [
        (pygame.K_UP, Command.UP),
        (pygame.K_s, Command.DOWN),
        (pygame.K_RETURN, Command.CONFIRM),
        (pygame.K_ESCAPE, Command.BACK),
        (pygame.K_p, Command.PAUSE),
        (pygame.K_x, None),
    ],
)
def test_key_commands(k, expected):
    assert command(key(k)) is expected


# --- gamepad -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("device", "expected"),
    [
        (FakeJoystick(), PlayerInput()),
        (FakeJoystick(axes=(-0.9, 0.1)), PlayerInput(dx=-1)),
        (FakeJoystick(axes=(0.2, 0.2)), PlayerInput()),  # inside the dead zone
        (FakeJoystick(hat=(1, 1)), PlayerInput(dx=1, dy=-1)),
        (FakeJoystick(buttons={13}), PlayerInput(dy=1)),  # d-pad down
        (FakeJoystick(buttons={0}), PlayerInput(fire=True)),  # A
        (FakeJoystick(buttons={7}), PlayerInput(fire=True)),  # RT
    ],
)
def test_standard_joystick_reading(device, expected):
    assert Pad(device, is_controller=False).read() == expected


@pytest.fixture
def pads():
    gamepads = Gamepads()
    gamepads.pads[3] = Pad(FakeJoystick(), is_controller=False)
    return gamepads


def joy(event_type, **attributes):
    return pygame.event.Event(event_type, instance_id=3, **attributes)


def test_joystick_buttons_become_commands(pads):
    assert pads.command(joy(pygame.JOYBUTTONDOWN, button=0)) is Command.CONFIRM
    assert pads.command(joy(pygame.JOYBUTTONDOWN, button=1)) is Command.BACK
    assert pads.command(joy(pygame.JOYBUTTONDOWN, button=9)) is Command.PAUSE
    assert pads.command(joy(pygame.JOYHATMOTION, hat=0, value=(0, 1))) is Command.UP


def test_unknown_device_is_ignored(pads):
    event = pygame.event.Event(pygame.JOYBUTTONDOWN, instance_id=99, button=0)
    assert pads.command(event) is None


def test_stick_counts_one_step_until_released(pads):
    def tilt(value):
        return pads.command(joy(pygame.JOYAXISMOTION, axis=1, value=value))

    assert tilt(0.9) is Command.DOWN
    assert tilt(1.0) is None  # still held
    assert tilt(0.1) is None  # back to centre
    assert tilt(-0.8) is Command.UP


def test_same_event_asked_twice_gives_the_same_answer(pads):
    event = joy(pygame.JOYAXISMOTION, axis=0, value=-1.0)
    assert pads.command(event) is Command.LEFT
    assert pads.command(event) is Command.LEFT


def test_unplugging_forgets_the_pad(pads):
    pads.handle_event(pygame.event.Event(pygame.JOYDEVICEREMOVED, instance_id=3))
    assert pads.count == 0


# --- controls screen ---------------------------------------------------------


@pytest.fixture
def screen(display, tmp_path):
    manager = SceneManager()
    save = SaveData(tmp_path / "save.json")
    manager.push(TitleScene(manager, save))
    manager.handle_event(key(pygame.K_DOWN))
    manager.handle_event(key(pygame.K_RETURN))
    assert isinstance(manager.top, ControlsScene)
    return manager, save


def test_rebinding_from_the_controls_screen(screen):
    manager, save = screen
    manager.handle_event(key(pygame.K_RETURN))  # first row: Gauche
    assert manager.top.waiting is Action.LEFT
    manager.handle_event(key(pygame.K_j))
    assert manager.top.waiting is None
    assert SaveData(save.path).bindings.custom[Action.LEFT] == (pygame.K_j,)
    assert manager.top.menu.items[0][0] == "Gauche : J"


def test_reserved_key_keeps_waiting(screen):
    manager, save = screen
    manager.handle_event(key(pygame.K_RETURN))
    manager.handle_event(key(pygame.K_p))
    assert manager.top.waiting is Action.LEFT
    assert manager.top.message == "Touche réservée"
    manager.handle_event(key(pygame.K_ESCAPE))  # cancel
    assert manager.top.waiting is None
    assert save.bindings.is_default


def test_back_returns_to_title_and_hint_follows_bindings(screen):
    manager, save = screen
    save.bindings.bind(Action.FIRE, pygame.K_x)
    manager.handle_event(key(pygame.K_ESCAPE))
    assert isinstance(manager.top, TitleScene)
    assert "Espace / X : tirer" in manager.top.keys_hint()
    manager.draw(pygame.display.get_surface())
