"""Gamepad support.

Pads known to SDL (Xbox, PlayStation, Switch Pro...) go through the SDL game
controller API, which names buttons the same way whatever the brand. Anything else,
and pads in the browser, fall back to the raw joystick API read with the W3C
"standard gamepad" layout that browsers expose.

Fixed layout: left stick or d-pad to move, A / X / RB / RT to fire, A to confirm,
B to go back, Start to pause.
"""

import logging

import pygame

from spaceshooter.controls import Command, PlayerInput

try:
    from pygame._sdl2 import controller as sdl_controller
except ImportError:  # not every pygame build ships it
    sdl_controller = None

log = logging.getLogger(__name__)

DEADZONE = 0.35  # stick share ignored around the centre when playing
MENU_THRESHOLD = 0.6  # stick share that counts as one step in a menu
TRIGGER_THRESHOLD = 0.5

if sdl_controller is not None:
    CONTROLLER_COMMANDS = {
        pygame.CONTROLLER_BUTTON_A: Command.CONFIRM,
        pygame.CONTROLLER_BUTTON_B: Command.BACK,
        pygame.CONTROLLER_BUTTON_START: Command.PAUSE,
        pygame.CONTROLLER_BUTTON_DPAD_UP: Command.UP,
        pygame.CONTROLLER_BUTTON_DPAD_DOWN: Command.DOWN,
        pygame.CONTROLLER_BUTTON_DPAD_LEFT: Command.LEFT,
        pygame.CONTROLLER_BUTTON_DPAD_RIGHT: Command.RIGHT,
    }
    CONTROLLER_FIRE = (
        pygame.CONTROLLER_BUTTON_A,
        pygame.CONTROLLER_BUTTON_X,
        pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
    )

# W3C standard gamepad layout (https://w3c.github.io/gamepad/#remapping).
STANDARD_COMMANDS = {
    0: Command.CONFIRM,
    1: Command.BACK,
    9: Command.PAUSE,
    12: Command.UP,
    13: Command.DOWN,
    14: Command.LEFT,
    15: Command.RIGHT,
}
STANDARD_FIRE = (0, 2, 5, 7)  # A, X, RB, RT
STANDARD_DPAD = (12, 13, 14, 15)  # up, down, left, right


def axis_zone(value: float, threshold: float) -> int:
    """-1, 0 or 1 depending on which side of the dead zone `value` (-1..1) is."""
    if value <= -threshold:
        return -1
    if value >= threshold:
        return 1
    return 0


class Pad:
    """One connected device, read as player intent."""

    def __init__(self, device: object, is_controller: bool) -> None:
        self.device = device
        self.is_controller = is_controller

    def read(self) -> PlayerInput:
        if self.is_controller:
            return self.read_controller()
        return self.read_joystick()

    def read_controller(self) -> PlayerInput:
        pad = self.device
        x = pad.get_axis(pygame.CONTROLLER_AXIS_LEFTX) / 32767
        y = pad.get_axis(pygame.CONTROLLER_AXIS_LEFTY) / 32767
        dx = axis_zone(x, DEADZONE) or (
            pad.get_button(pygame.CONTROLLER_BUTTON_DPAD_RIGHT)
            - pad.get_button(pygame.CONTROLLER_BUTTON_DPAD_LEFT)
        )
        dy = axis_zone(y, DEADZONE) or (
            pad.get_button(pygame.CONTROLLER_BUTTON_DPAD_DOWN)
            - pad.get_button(pygame.CONTROLLER_BUTTON_DPAD_UP)
        )
        trigger = pad.get_axis(pygame.CONTROLLER_AXIS_TRIGGERRIGHT) / 32767
        fire = any(pad.get_button(b) for b in CONTROLLER_FIRE) or trigger > TRIGGER_THRESHOLD
        return PlayerInput(int(dx), int(dy), bool(fire))

    def read_joystick(self) -> PlayerInput:
        stick = self.device
        buttons = stick.get_numbuttons()

        def button(index: int) -> bool:
            return index < buttons and stick.get_button(index)

        dx = dy = 0
        if stick.get_numaxes() >= 2:
            dx = axis_zone(stick.get_axis(0), DEADZONE)
            dy = axis_zone(stick.get_axis(1), DEADZONE)
        if stick.get_numhats():
            hat_x, hat_y = stick.get_hat(0)
            dx, dy = dx or hat_x, dy or -hat_y  # hats point up with +1
        up, down, left, right = (button(i) for i in STANDARD_DPAD)
        dx = dx or int(right) - int(left)
        dy = dy or int(down) - int(up)
        return PlayerInput(dx, dy, any(button(i) for i in STANDARD_FIRE))


class Gamepads:
    def __init__(self) -> None:
        self.pads: dict[int, Pad] = {}  # by joystick instance id
        self.zones: dict[tuple[int, int], int] = {}  # last menu zone of each stick axis
        self.last_event: pygame.event.Event | None = None
        self.last_command: Command | None = None

    def init(self) -> None:
        pygame.joystick.init()
        if sdl_controller is not None:
            try:
                sdl_controller.init()
            except pygame.error as error:
                log.info("No game controller API: %s", error)
        # Devices already plugged in are announced by JOYDEVICEADDED events.

    @property
    def count(self) -> int:
        return len(self.pads)

    def connect(self, device_index: int) -> None:
        if self.has_controller_api() and sdl_controller.is_controller(device_index):
            pad = sdl_controller.Controller(device_index)
            instance_id = pad.as_joystick().get_instance_id()
            self.pads[instance_id] = Pad(pad, is_controller=True)
        else:
            stick = pygame.joystick.Joystick(device_index)
            self.pads[stick.get_instance_id()] = Pad(stick, is_controller=False)

    @staticmethod
    def has_controller_api() -> bool:
        return sdl_controller is not None and sdl_controller.get_init()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Track devices being plugged in and out."""
        if event.type == pygame.JOYDEVICEADDED:
            try:
                self.connect(event.device_index)
            except pygame.error as error:
                log.warning("Could not open gamepad %s: %s", event.device_index, error)
        elif event.type == pygame.JOYDEVICEREMOVED:
            self.pads.pop(event.instance_id, None)

    def read(self) -> PlayerInput:
        result = PlayerInput()
        for pad in self.pads.values():
            result |= pad.read()
        return result

    def command(self, event: pygame.event.Event) -> Command | None:
        """Menu meaning of a gamepad event, or None.

        Memoised on the event so several handlers can ask about the same event
        without the stick edge detection firing only for the first one.
        """
        if event is not self.last_event:
            self.last_event = event
            self.last_command = self.translate(event)
        return self.last_command

    def translate(self, event: pygame.event.Event) -> Command | None:
        if event.type == pygame.CONTROLLERBUTTONDOWN:
            return CONTROLLER_COMMANDS.get(event.button) if sdl_controller else None
        if event.type == pygame.CONTROLLERAXISMOTION:
            if event.axis in (pygame.CONTROLLER_AXIS_LEFTX, pygame.CONTROLLER_AXIS_LEFTY):
                return self.stick_step(event.instance_id, event.axis, event.value / 32767)
            return None

        # Raw joystick events, only for pads not handled as game controllers
        # (SDL sends both kinds for those).
        pad = self.pads.get(getattr(event, "instance_id", -1))
        if pad is None or pad.is_controller:
            return None
        if event.type == pygame.JOYBUTTONDOWN:
            return STANDARD_COMMANDS.get(event.button)
        if event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            return {
                (0, 1): Command.UP,
                (0, -1): Command.DOWN,
                (-1, 0): Command.LEFT,
                (1, 0): Command.RIGHT,
            }.get((hat_x, hat_y))
        if event.type == pygame.JOYAXISMOTION and event.axis in (0, 1):
            return self.stick_step(event.instance_id, event.axis, event.value)
        return None

    def stick_step(self, instance_id: int, axis: int, value: float) -> Command | None:
        """A stick pushed past the threshold counts once, until it comes back."""
        zone = axis_zone(value, MENU_THRESHOLD)
        previous = self.zones.get((instance_id, axis), 0)
        self.zones[(instance_id, axis)] = zone
        if zone == 0 or zone == previous:
            return None
        horizontal = axis == 0  # LEFTX is axis 0 in both APIs
        if horizontal:
            return Command.RIGHT if zone > 0 else Command.LEFT
        return Command.DOWN if zone > 0 else Command.UP


gamepads = Gamepads()
