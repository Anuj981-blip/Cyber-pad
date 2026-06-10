Here's the updated README with the project renamed to **CyberPad**:

---

# CyberPad — 3×3 Macropad

A compact 9-key macropad with rotary encoder, OLED display, and three switchable profiles (Productivity, Gaming, Media). Built around the Seeed XIAO RP2040 and powered by KMK firmware.

---

## Features

- **9 MX-style switches** in a 3×3 matrix
- **Rotary encoder** with push-button for layer-aware actions
- **128×32 SSD1306 OLED** showing active profile icon, profile name, and current layer
- **3 profiles** (Productivity / Gaming / Media), each with 2 layers
- **Profile switching** via top-row chord (hold keys 1+2+3 simultaneously)
- **Per-profile boot animation** and profile transition flash on the OLED
- 3D-printed enclosure with heat-set inserts

---

## Screenshots & Renders

### Macropad Render
> `CAD/assembled-model.STEP` — open in FreeCAD, Fusion 360, or any STEP viewer.

![Macropad render placeholder](https://placehold.co/800x450/1a1a2e/ffffff?text=CyberPad+3D+Render)

---

### Schematic
> `PCB/cyberpad.kicad_sch`

![Schematic placeholder](https://placehold.co/800x550/1a1a2e/ffffff?text=CyberPad+Schematic)

**Pin mapping (Seeed XIAO RP2040):**

| Signal  | XIAO Pin | GPIO  | Notes                |
|---------|----------|-------|----------------------|
| Col 0   | D0       | GP26  | SW1 / SW4 / SW7      |
| Col 1   | D1       | GP27  | SW2 / SW5 / SW8      |
| Col 2   | D2       | GP28  | SW3 / SW6 / SW9      |
| Row 0   | D3       | GP29  | SW1 / SW2 / SW3      |
| Row 1   | D6       | GP0   | SW4 / SW5 / SW6      |
| Row 2   | D7       | GP1   | SW7 / SW8 / SW9      |
| SDA     | D4       | GP6   | OLED SDA             |
| SCL     | D5       | GP7   | OLED SCL             |
| Enc CLK | D9       | GP3   | Encoder A            |
| Enc DT  | D10      | GP4   | Encoder B            |
| Enc SW  | D8       | GP2   | Encoder push-button  |

---

### PCB Layout
> `PCB/cyberpad.kicad_pcb`

![PCB layout placeholder](https://placehold.co/800x550/1a1a2e/ffffff?text=CyberPad+PCB+Layout)

- 2-layer PCB, 80 × 80 mm
- MX switch footprints with 1N4148 through-hole diode per switch (COL2ROW)
- EC11 rotary encoder footprint
- 4× M3 mounting holes (corner, 4 mm from edge)
- JST connector for optional battery

---

### Case (3D)
> `CAD/Top.STEP` · `CAD/Bottom.STEP`

![Case render placeholder](https://placehold.co/800x450/1a1a2e/ffffff?text=CyberPad+Case+3D)

- Two-part snap/screw enclosure
- Top shell: switch plate integrated, 1.6 mm switch travel clearance
- Bottom shell: 4× M3×5×4 mm heat-set insert bosses
- OLED window cut-out, encoder knob cutout, USB-C access port
- Designed in Fusion 360, exported as STEP

---

## Bill of Materials

A fully itemized list of all components required to build a CyberPad.

| Qty | Item                              | Notes                                  |
|-----|-----------------------------------|----------------------------------------|
| ×1  | Custom PCB                        | See `PCB/` and `production/gerbers.zip`|
| ×1  | 3D-Printed Case (Top + Bottom)    | See `CAD/Top.STEP` & `CAD/Bottom.STEP` |
| ×1  | Seeed XIAO RP2040                 | Main microcontroller                   |
| ×1  | 0.91" OLED Display (SSD1306 I2C)  | 128×32, I2C address 0x3C               |
| ×1  | EC11 Rotary Encoder               | With push-button, 20 detents           |
| ×9  | MX-Style Switches                 | 5-pin or 3-pin (PCB-mount)             |
| ×9  | White Blank DSA Keycaps           | 1U                                     |
| ×9  | Through-hole 1N4148 Diodes        | SOD-27 / DO-35 glass                   |
| ×4  | M3×16 mm Screws                   | Phillips or hex socket                 |
| ×4  | M3×5×4 mm Heat-set Inserts        | For bottom shell bosses                |

---

## Firmware

**Runtime:** CircuitPython 9.x + KMK

**Required libraries (copy to `CIRCUITPY/lib/`):**

```
kmk/
adafruit_displayio_ssd1306.mpy
adafruit_display_text/
```

**Flash instructions:**

1. Download CircuitPython `.uf2` for XIAO RP2040 from [circuitpython.org](https://circuitpython.org/board/seeeduino_xiao_rp2040/)
2. Hold BOOT, plug in USB → drag `.uf2` to the `RPI-RP2` drive
3. Copy the `lib/` folder and `main.py` to `CIRCUITPY/`
4. Device reboots automatically — OLED shows boot animation

**Profiles:**

| Profile      | Layer 0                     | Layer 1                    | Encoder CW/CCW        |
|--------------|-----------------------------|----------------------------|-----------------------|
| Productivity | Copy/Paste/Undo, Save/Find  | Redo/Cut/Dup, Print/Open   | Undo / Redo           |
| Gaming       | ESC, 1–5, R/B/G             | F1–F10                     | Page Up / Page Down   |
| Media        | Play/Prev/Next, Vol±        | Screenshots, Window snap   | Vol+ / Vol−           |

Switch profiles by holding the entire top row (keys 1+2+3) simultaneously.

---

## Repository Structure

```
CyberPad/
├── README.md
├── CAD/
│   ├── assembled-model.STEP
│   ├── Top.STEP
│   └── Bottom.STEP
├── PCB/
│   ├── cyberpad.kicad_pro
│   ├── cyberpad.kicad_sch
│   └── cyberpad.kicad_pcb
├── Firmware/
│   └── main.py
└── production/
    ├── gerbers.zip
    ├── Top.STEP
    ├── Bottom.STEP
    └── main.py
```

---

## License

Hardware (PCB + CAD): [CERN-OHL-P v2](https://ohwr.org/cern_ohl_p_v2.txt)
Firmware: [MIT](https://opensource.org/licenses/MIT)

---
