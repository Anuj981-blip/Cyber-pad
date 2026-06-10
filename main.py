import board
import busio
import displayio
import terminalio
import time
import supervisor

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC, make_key
from kmk.scanners import DiodeOrientation
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.holdtap import HoldTap
from kmk.modules.combos import Combos, Chord
from kmk.modules import Module
from adafruit_display_text import label

try:
    import adafruit_displayio_ssd1306
    OLED_AVAILABLE = True
except ImportError:
    OLED_AVAILABLE = False

BITMAP_PRODUCTIVITY = bytearray([
    0x00, 0x00, 0x00, 0x00,
    0x7F, 0xFF, 0xFF, 0xFE,
    0x40, 0x00, 0x00, 0x02,
    0x5B, 0x6D, 0xB6, 0xD2,
    0x5B, 0x6D, 0xB6, 0xD2,
    0x40, 0x00, 0x00, 0x02,
    0x4F, 0xFF, 0xFF, 0xF2,
    0x40, 0x00, 0x00, 0x02,
    0x7F, 0xFF, 0xFF, 0xFE,
    0x00, 0x00, 0x00, 0x00,
    *([0x00] * 88),
])

BITMAP_GAMING = bytearray([
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x0F, 0xF0, 0x00,
    0x00, 0x08, 0x10, 0x00,
    0x00, 0x0F, 0xF0, 0x00,
    0x00, 0x08, 0x10, 0x00,
    0x00, 0x0F, 0xF0, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x3F, 0xFF, 0xFF, 0xFC,
    0x40, 0x00, 0x00, 0x02,
    0x4E, 0x00, 0x00, 0x72,
    0x4E, 0x00, 0x00, 0x72,
    0x4E, 0x00, 0x00, 0x72,
    0x40, 0x00, 0x00, 0x02,
    0x3F, 0xFF, 0xFF, 0xFC,
    0x00, 0x00, 0x00, 0x00,
    *([0x00] * 68),
])

BITMAP_MEDIA = bytearray([
    *([0x00] * 8),
    0x01, 0xFF, 0xFE, 0x00,
    0x01, 0x00, 0x10, 0x00,
    0x01, 0x00, 0x10, 0x00,
    0x01, 0xFF, 0xF0, 0x00,
    0x01, 0x00, 0x10, 0x00,
    0x01, 0x00, 0x10, 0x00,
    0x00, 0x00, 0x30, 0x00,
    0x00, 0x01, 0xF0, 0x00,
    0x00, 0x03, 0xF0, 0x00,
    0x00, 0x01, 0xF0, 0x00,
    0x00, 0x00, 0x00, 0x00,
    *([0x00] * 84),
])

BITMAPS = [BITMAP_PRODUCTIVITY, BITMAP_GAMING, BITMAP_MEDIA]
PROFILE_NAMES = ["PRODUCTIVITY", "  GAMING  ", "   MEDIA   "]
PROFILE_COUNT = 3


class OLEDManager:
    WIDTH  = 128
    HEIGHT = 32
    ICON_W = 32
    ICON_H = 32

    def __init__(self):
        self.display = None
        self.splash  = None
        self.profile_label = None
        self.layer_label   = None
        self.anim_frame    = 0
        self.last_anim_ms  = 0
        self.current_profile = -1
        self._last_oled_ms   = 0
        self._init_display()

    def _init_display(self):
        if not OLED_AVAILABLE:
            return
        try:
            displayio.release_displays()
            i2c = busio.I2C(board.D5, board.D4)
            bus = displayio.I2CDisplay(i2c, device_address=0x3C)
            self.display = adafruit_displayio_ssd1306.SSD1306(
                bus, width=self.WIDTH, height=self.HEIGHT
            )
            self._build_layout()
            self._boot_animation()
        except Exception as e:
            print("OLED init failed:", e)
            self.display = None

    def _build_layout(self):
        if not self.display:
            return

        self.splash = displayio.Group()

        bg_bmp = displayio.Bitmap(self.WIDTH, self.HEIGHT, 2)
        bg_pal = displayio.Palette(2)
        bg_pal[0] = 0x000000
        bg_pal[1] = 0xFFFFFF
        self.splash.append(displayio.TileGrid(bg_bmp, pixel_shader=bg_pal, x=0, y=0))

        self.icon_bmp = displayio.Bitmap(self.ICON_W, self.ICON_H, 2)
        self.icon_pal = displayio.Palette(2)
        self.icon_pal[0] = 0x000000
        self.icon_pal[1] = 0xFFFFFF
        self.splash.append(
            displayio.TileGrid(self.icon_bmp, pixel_shader=self.icon_pal, x=0, y=0)
        )

        div_bmp = displayio.Bitmap(1, self.HEIGHT, 2)
        div_pal = displayio.Palette(2)
        div_pal[0] = 0x000000
        div_pal[1] = 0xFFFFFF
        for y in range(self.HEIGHT):
            div_bmp[0, y] = 1
        self.splash.append(displayio.TileGrid(div_bmp, pixel_shader=div_pal, x=34, y=0))

        self.profile_label = label.Label(
            terminalio.FONT, text="            ",
            color=0xFFFFFF, x=38, y=8, scale=1
        )
        self.splash.append(self.profile_label)

        self.layer_label = label.Label(
            terminalio.FONT, text="LYR: 0",
            color=0xFFFFFF, x=38, y=22, scale=1
        )
        self.splash.append(self.layer_label)

        self.display.root_group = self.splash

    def _load_icon(self, profile_idx):
        if not self.display:
            return
        raw = BITMAPS[profile_idx % PROFILE_COUNT]
        for y in range(self.ICON_H):
            for xbyte in range(4):
                idx = y * 4 + xbyte
                byte = raw[idx] if idx < len(raw) else 0
                for bit in range(8):
                    x = xbyte * 8 + bit
                    self.icon_bmp[x, y] = (byte >> (7 - bit)) & 1

    def _boot_animation(self):
        if not self.display:
            return

        boot_group = displayio.Group()
        bg = displayio.Bitmap(self.WIDTH, self.HEIGHT, 2)
        pal = displayio.Palette(2)
        pal[0] = 0x000000
        pal[1] = 0xFFFFFF
        boot_group.append(displayio.TileGrid(bg, pixel_shader=pal))
        boot_group.append(
            label.Label(terminalio.FONT, text=">> MACROPAD <<",
                        color=0xFFFFFF, x=10, y=10)
        )

        bar_bmp = displayio.Bitmap(self.WIDTH, 6, 2)
        bar_pal = displayio.Palette(2)
        bar_pal[0] = 0x000000
        bar_pal[1] = 0xFFFFFF
        boot_group.append(displayio.TileGrid(bar_bmp, pixel_shader=bar_pal, x=0, y=24))
        self.display.root_group = boot_group

        for w in range(0, self.WIDTH, 4):
            for x in range(w, min(w + 4, self.WIDTH)):
                for y in range(6):
                    bar_bmp[x, y] = 1
            time.sleep(0.015)

        time.sleep(0.3)
        self.display.root_group = self.splash

    def update(self, profile_idx, layer_idx, tick_ms):
        if not self.display:
            return

        if profile_idx != self.current_profile:
            self.current_profile = profile_idx
            self._load_icon(profile_idx)
            self.profile_label.text = PROFILE_NAMES[profile_idx]
            self._run_profile_transition()

        self.layer_label.text = "LYR: {}".format(layer_idx)

        if profile_idx == 1:
            if tick_ms - self.last_anim_ms > 500:
                self.last_anim_ms = tick_ms
                self.anim_frame ^= 1
                self.icon_pal[0] = 0xFFFFFF if self.anim_frame else 0x000000
                self.icon_pal[1] = 0x000000 if self.anim_frame else 0xFFFFFF
        else:
            self.icon_pal[0] = 0x000000
            self.icon_pal[1] = 0xFFFFFF

    def _run_profile_transition(self):
        if not self.display:
            return
        for _ in range(2):
            self.display.contrast(0)
            time.sleep(0.05)
            self.display.contrast(255)
            time.sleep(0.05)


keyboard = KMKKeyboard()

keyboard.col_pins = (board.D0, board.D1, board.D2)
keyboard.row_pins = (board.D3, board.D6, board.D7)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

keyboard.extensions.append(MediaKeys())
keyboard.modules.append(HoldTap())

combos = Combos()
keyboard.modules.append(combos)

encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)

encoder_handler.pins = ((board.D9, board.D10, board.D8, False),)

_state = {"profile": 0}


def get_profile():
    return _state["profile"]


def next_profile():
    _state["profile"] = (_state["profile"] + 1) % PROFILE_COUNT
    print("Profile -> {}".format(PROFILE_NAMES[_state["profile"]]))


def _prof_press(key, keyboard, *args):
    next_profile()
    return False


PROF_KEY = make_key(names=("PROF_NEXT",), on_press=_prof_press)

combos.combos = [
    Chord((KC.NO, KC.NO, KC.NO), PROF_KEY),
]

KEYMAPS = {
    0: [
        [
            KC.LCTL(KC.C), KC.LCTL(KC.V), KC.LCTL(KC.Z),
            KC.LCTL(KC.S), KC.LCTL(KC.F), KC.LCTL(KC.A),
            KC.LCTL(KC.W), KC.TAB,        KC.LCTL(KC.T),
            KC.MUTE,
        ],
        [
            KC.LCTL(KC.LSFT(KC.Z)), KC.LCTL(KC.X), KC.LCTL(KC.D),
            KC.LCTL(KC.P),          KC.LCTL(KC.O), KC.LCTL(KC.N),
            KC.LCTL(KC.Q),          KC.LCTL(KC.H), KC.F5,
            KC.LCTL(KC.LSFT(KC.S)),
        ],
    ],
    1: [
        [
            KC.ESC,  KC.N1, KC.N2,
            KC.N3,   KC.N4, KC.N5,
            KC.R,    KC.B,  KC.G,
            KC.MUTE,
        ],
        [
            KC.F1, KC.F2, KC.F3,
            KC.F4, KC.F5, KC.F6,
            KC.F7, KC.F8, KC.F9,
            KC.F10,
        ],
    ],
    2: [
        [
            KC.MPLY, KC.MPRV, KC.MNXT,
            KC.VOLD, KC.MUTE, KC.VOLU,
            KC.MRWD, KC.MSTP, KC.MFFD,
            KC.MPLY,
        ],
        [
            KC.PSCR,         KC.LSFT(KC.LGUI(KC.N4)), KC.LCTL(KC.LGUI(KC.N4)),
            KC.LGUI(KC.LEFT),KC.LGUI(KC.UP),           KC.LGUI(KC.RIGHT),
            KC.LGUI(KC.DOWN),KC.LCTL(KC.LGUI(KC.LEFT)),KC.LCTL(KC.LGUI(KC.RIGHT)),
            KC.LSFT(KC.F11),
        ],
    ],
}

ENCODER_MAPS = {
    0: [
        (KC.LCTL(KC.Z), KC.LCTL(KC.LSFT(KC.Z))),
        (KC.LCTL(KC.RBRC), KC.LCTL(KC.LBRC)),
    ],
    1: [
        (KC.PGUP, KC.PGDN),
        (KC.VOLU, KC.VOLD),
    ],
    2: [
        (KC.VOLU, KC.VOLD),
        (KC.BRIU, KC.BRID),
    ],
}


def apply_profile(p):
    keyboard.keymap = KEYMAPS[p]
    encoder_handler.map = [tuple(tuple(e) for e in ENCODER_MAPS[p])]


apply_profile(0)

oled = OLEDManager()
oled.update(0, 0, supervisor.ticks_ms())


class OLEDRefreshModule(Module):

    def __init__(self, oled_mgr, state):
        self.oled = oled_mgr
        self.state = state
        self._last_profile = -1
        self._last_oled_ms = 0

    def during_bootup(self, keyboard):
        pass

    def before_matrix_scan(self, keyboard):
        p = self.state["profile"]
        if p != self._last_profile:
            apply_profile(p)
            self._last_profile = p
        return keyboard

    def after_matrix_scan(self, keyboard):
        return keyboard

    def before_hid_send(self, keyboard):
        return keyboard

    def after_hid_send(self, keyboard):
        now = supervisor.ticks_ms()
        if (now - self._last_oled_ms) > 100:
            self._last_oled_ms = now
            layer = keyboard.active_layers[0] if keyboard.active_layers else 0
            self.oled.update(self.state["profile"], layer, now)
        return keyboard

    def on_powersave_enable(self, keyboard):
        return keyboard

    def on_powersave_disable(self, keyboard):
        return keyboard


keyboard.modules.append(OLEDRefreshModule(oled, _state))

if __name__ == "__main__":
    keyboard.go()
