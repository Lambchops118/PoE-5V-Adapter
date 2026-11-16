# Reusable isolated PoE power sheet

This KiCad 10 project is a power-only PoE powered device (PD). It accepts a
Cat5e/Cat6 cable at J1 and targets **5 V at up to 2 A** at the isolated output.
It does not carry Ethernet data. The power stage is based on TI's tested
[PMP7355 5 V / 2 A reference design](https://www.ti.com/tool/PMP7355), using
the [TPS23753A](https://www.ti.com/product/TPS23753A).

## Use in another board

1. Copy `power_module.kicad_sch` and `PoEAdapter.kicad_sym` into the host
   project's directory. Add the `PoEAdapter` library entry from this project's
   `sym-lib-table` to the host project's `sym-lib-table`.
2. In the host schematic, add a hierarchical sheet and choose the existing
   `power_module.kicad_sch` file. Import its two hierarchical pins.
3. Connect `POE_5V` and `ISO_GND` to the IoT board's 5 V rail and return.
   Keep `ISO_GND` separate from the PoE primary-side `VSS` and `RTN` nets.
4. Use J1 as the cable input. J2 is an optional two-pin output connector and
   can be omitted if the sheet is integrated onto the same PCB. The parent
   `adapter.kicad_sch` is a standalone wrapper; its output pins intentionally
   have no-connect flags until a host board connects them.

`tools/generate_schematic.py` rebuilds both schematics and the local symbol
library. KiCad embeds the symbol definitions in the schematic; copying the
library alongside it keeps the symbols editable without warnings.

## Architecture

- RJ45 pins 1+2, 3+6, 4+5, and 7+8 are bussed into four power pairs. BR1 and
  BR2 rectify the two pair sets and accept either PoE polarity. This connection
  is **only suitable for a power-only port**; it cannot share the jack with an
  Ethernet PHY.
- U1 provides Type 1 PD detection, Class 3 classification, hot-swap control,
  and flyback PWM. `VSS` is the cable-side return; `RTN` is the controlled
  converter return. R7 is the 24.9 kΩ detection signature and R12 is the
  90.9 Ω Class 3 classification resistor.
- T1 (Coilcraft POE13P-50L) and U2 (TCMT1107) cross the isolation barrier.
  D4 rectifies the secondary, L2 and the output capacitors filter it, and
  U3 (TLV431A) regulates the output through U2.
- The input TVS, filter, primary MOSFET, current sense, auxiliary bias, and
  snubbers follow the functional blocks in [TI's schematic](https://www.ti.com/lit/pdf/SLVRB20)
  and [BOM](https://www.ti.com/lit/pdf/SLVRB21). Adapter ORing, Ethernet
  magnetics, and data termination were omitted for this power-only version.

## Before making hardware

KiCad ERC and netlist export pass, but this is **a schematic design, not a
tested board**. The PCB file is still blank. Select an RJ45 jack and finish
component footprints and current/voltage ratings against the exact purchased
parts. Preserve the transformer and optocoupler isolation barrier in copper,
creepage, and clearance. Follow TI's layout guidance for the hot-swap return,
switching loop, sense resistor, TVS, and output filter. Verify PoE detection,
classification, output regulation, startup, load transients, thermals, and
isolation on a prototype before reusing it in production.

The TPS23753A is a Type 1, approximately 13 W input PD. TI rates its
PMP7355 reference design for 5 V / 2 A. **5 V / 2.5 A is not claimed** for
this design because converter losses leave inadequate input power margin.
