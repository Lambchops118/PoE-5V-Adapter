"""Generate the reusable TPS23753A PoE power sheet.

The electrical values follow TI PMP7355 Rev B (SLVRB20/SLVRB21). This is a
schematic starting point, not a substitute for layout and hardware validation.
"""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


PROJECT_DIR = Path(__file__).resolve().parents[1] / "adapter"
OUT = PROJECT_DIR / "power_module.kicad_sch"
ROOT_UUID = "abba7e16-9e2d-492b-8263-437add6fbe59"
SHEET_UUID = "717f8bb2-4b5f-48e6-a460-a833c491042a"
FONT = '(effects (font (size 1.27 1.27)))'
HIDDEN = '(effects (font (size 1.27 1.27)) (hide yes))'


_uid_number = 0


def uid():
    global _uid_number
    _uid_number += 1
    return str(uuid5(NAMESPACE_URL, f"poe-5v-adapter/{_uid_number}"))


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def xy(x, y):
    return f"{x:g} {y:g}"


def pin(name, number, x, y, angle, kind="passive"):
    return (f'(pin {kind} line (at {xy(x,y)} {angle}) (length 5.08) '
            f'(name {q(name)} {FONT}) (number {q(number)} {FONT}))')


def box(x1, y1, x2, y2):
    return (f'(rectangle (start {xy(x1,y1)}) (end {xy(x2,y2)}) '
            '(stroke (width 0.254) (type default)) (fill (type background)))')


def symbol_def(name, prefix, value, pins, bounds, description=""):
    x1, y1, x2, y2 = bounds
    body = box(*bounds)
    pp = "\n".join(pin(*p) for p in pins)
    return (f'(symbol "PoEAdapter:{name}" (pin_names (offset 0.508)) '
            f'(in_bom yes) (on_board yes) '
            f'(property "Reference" {q(prefix)} (at 0 {y2+4:g} 0) {FONT}) '
            f'(property "Value" {q(value)} (at 0 {y1-4:g} 0) {FONT}) '
            f'(property "Footprint" "" (at 0 0 0) {HIDDEN}) '
            f'(property "Datasheet" "" (at 0 0 0) {HIDDEN}) '
            f'(property "Description" {q(description)} (at 0 0 0) {HIDDEN}) '
            f'(symbol "{name}_0_1" {body}) '
            f'(symbol "{name}_1_1" {pp}))')


DEFS = {
    "RJ45_Power": ("J", "RJ45 power only",
        [(str(n), str(n), -15.24, 17.78 - (n-1)*5.08, 0, "passive") for n in range(1,9)],
        (-10.16,-21.59,10.16,21.59), "Eight-position modular jack; no Ethernet data path"),
    "Bridge": ("BR", "HD01",
        [("AC1","3",-12.7,3.81,0,"passive"), ("AC2","4",-12.7,-3.81,0,"passive"),
         ("+","1",12.7,3.81,180,"passive"), ("-","2",12.7,-3.81,180,"passive")],
        (-7.62,-7.62,7.62,7.62), "100 V 0.8 A bridge rectifier"),
    "TPS23753A": ("U", "TPS23753APW",
        [(name,str(num),-20.32,15.24-(num-1)*5.08,0,"input" if name in ("CTL","CS","APD") else "passive")
         for num,name in enumerate(["CTL","VB","CS","VC","GATE","RTN","VSS"],1)] +
        [(name,str(num),20.32,15.24-(num-8)*5.08,180,"passive")
         for num,name in enumerate(["VDD1","VDD","DEN","CLS","APD","BLNK","FRS"],8)],
        (-15.24,-18,15.24,18), "IEEE 802.3at Type 1 PD and isolated flyback controller"),
    "R": ("R", "R", [("~","1",0,5.08,270,"passive"),("~","2",0,-5.08,90,"passive")],
          (-1.27,-2.54,1.27,2.54), "Resistor"),
    "C": ("C", "C", [("~","1",0,5.08,270,"passive"),("~","2",0,-5.08,90,"passive")],
          (-2.54,-1.27,2.54,1.27), "Capacitor"),
    "L": ("L", "L", [("~","1",0,5.08,270,"passive"),("~","2",0,-5.08,90,"passive")],
          (-2.54,-2.54,2.54,2.54), "Inductor"),
    "D": ("D", "D", [("K","1",0,5.08,270,"passive"),("A","2",0,-5.08,90,"passive")],
          (-2.54,-2.54,2.54,2.54), "Diode; pin 1 cathode, pin 2 anode"),
    "NMOS": ("Q", "FDS2582",
        [("D",str(n),0,10.16,270,"passive") for n in range(5,9)] +
        [("G","4",-10.16,0,0,"input")] +
        [("S",str(n),0,-10.16,90,"passive") for n in range(1,4)],
        (-5.08,-5.08,5.08,5.08), "150 V primary switching MOSFET; parallel pins per footprint"),
    "Flyback": ("T", "POE13P-50L",
        [("PRI+","3",-15.24,12.7,0,"passive"),("PRI-","4",-15.24,5.08,0,"passive"),
         ("BIAS+","1",-15.24,-5.08,0,"passive"),("BIAS-","2",-15.24,-12.7,0,"passive"),
         ("SEC_TOP_A","8",15.24,10.16,180,"passive"),("SEC_TOP_B","7",15.24,10.16,180,"passive"),
         ("SEC_BOT_A","10",15.24,-10.16,180,"passive"),("SEC_BOT_B","9",15.24,-10.16,180,"passive")],
        (-10.16,-17.78,10.16,17.78), "Coilcraft 5 V PoE flyback transformer"),
    "Opto": ("U", "TCMT1107",
        [("C","4",-12.7,5.08,0,"passive"),("E","3",-12.7,-5.08,0,"passive"),
         ("LED_A","1",12.7,5.08,180,"passive"),("LED_K","2",12.7,-5.08,180,"passive")],
        (-7.62,-8.89,7.62,8.89), "Feedback optocoupler; isolation barrier"),
    "TLV431": ("U", "TLV431ACDBVR",
        [("K","3",0,10.16,270,"passive"),("REF","4",-10.16,0,0,"input"),
         ("A","5",0,-10.16,90,"passive"),
         ("NC","1",10.16,2.54,180,"no_connect"),
         ("SUB","2",10.16,-2.54,180,"passive")],
        (-5.08,-5.08,5.08,5.08), "1.24 V adjustable shunt reference"),
    "Output": ("J", "5V_2A_Output",
        [("+5V","1",-10.16,2.54,0,"passive"),("GND","2",-10.16,-2.54,0,"passive")],
        (-5.08,-5.08,5.08,5.08), "Optional two-pin output connector; use sheet pins in host design"),
}

parts = []
labels = []
notes = []


def part(kind, ref, value, x, y, nets, footprint="", datasheet=""):
    x = round(x / 1.27) * 1.27
    y = round(y / 1.27) * 1.27
    spec = DEFS[kind]
    pins = spec[2]
    assert len(pins) == len(nets), (ref, pins, nets)
    for p, net in zip(pins, nets):
        if p[5] == "no_connect":
            continue
        px, py = p[2], p[3]
        item = (net, x+px, y-py)
        if item not in labels:
            labels.append(item)
    parts.append((kind, ref, value, x, y, pins, footprint, datasheet))


def passive(kind, ref, value, x, y, top, bottom, footprint=""):
    part(kind,ref,value,x,y,[top,bottom],footprint)


# Power-only RJ45: each pair is bussed because no Ethernet PHY is present.
part("RJ45_Power","J1","RJ45_Power_Only",35,58,
     ["PAIR_12","PAIR_12","PAIR_36","PAIR_45","PAIR_45","PAIR_36","PAIR_78","PAIR_78"])
part("Bridge","BR1","HD01",85,49,["PAIR_12","PAIR_36","VDD","VSS"])
part("Bridge","BR2","HD01",85,83,["PAIR_45","PAIR_78","VDD","VSS"])
passive("D","D1","SMAJ58A",125,51,"VDD","VSS")
passive("C","C23","0.1uF_100V",145,51,"VDD","VSS")

# PD detection, classification, startup and PWM controller.
part("TPS23753A","U1","TPS23753APW",105,167,
     ["CTL","VB","CS","VC","GATE","RTN","VSS",
      "VDD","VDD","DEN","CLS","RTN","BLNK","FRS"],
     "Package_SO:TSSOP-14_4.4x5mm_P0.65mm")
passive("R","R7","24.9k_1%",35,124,"VDD","DEN")
passive("R","R12","90.9R_1%_Class3",57,124,"CLS","VSS")
passive("R","R10","59k_250kHz",35,167,"FRS","RTN")
passive("R","R11","80.6k",57,167,"BLNK","RTN")
passive("C","C20","0.1uF_16V",35,210,"VB","RTN")
passive("C","C15","0.22uF_25V",57,210,"VC","RTN")
passive("C","C16","10uF_25V",79,210,"VC","RTN")

# Input bulk capacitor, EMI filter and flyback power stage.
passive("C","C8","22uF_100V",170,51,"VDD","RTN")
passive("L","L1","10uH_750mA",190,51,"VDD","VPRI")
passive("C","C9","2.2uF_100V",215,51,"VPRI","RTN")
passive("C","C10","2.2uF_100V",240,51,"VPRI","RTN")
part("Flyback","T1","POE13P-50L",265,135,
     ["VPRI","DRAIN","AUX_RECT","RTN",
      "SEC_RETURN","SEC_RETURN","VOUT_RAW","VOUT_RAW"])
part("NMOS","Q1","FDS2582",208,170,["DRAIN"]*4+["GATE_R"]+["SENSE"]*3,
     "Package_SO:SO-8_3.9x4.9mm_P1.27mm")
passive("R","R13","10R",170,170,"GATE","GATE_R")
passive("R","R18","0.39R_0.5W",207,207,"SENSE","RTN")
passive("R","R20","1k",185,207,"CS","SENSE")
passive("R","R6","39k_0.1W",228,87,"VPRI","SNUB")
passive("C","C11","0.1uF_100V",250,87,"VPRI","SNUB")
passive("D","D8","MURA120",239,114,"SNUB","DRAIN")
passive("R","R9","10R",211,240,"AUX_RECT","AUX_DIODE")
passive("D","D10","BAS16",235,240,"VC","AUX_DIODE")

# Isolated secondary rectification and filtered 5 V output.
passive("D","D4","B540_5A_40V",320,125,"SEC_RETURN","ISO_GND")
passive("R","R5","20R_0.5W",343,107,"SEC_RETURN","SEC_SNUB")
passive("C","C7","680pF_50V",343,130,"SEC_SNUB","ISO_GND")
passive("C","C12","47uF_10V",320,165,"VOUT_RAW","ISO_GND")
passive("C","C13","47uF_10V",343,165,"VOUT_RAW","ISO_GND")
passive("L","L2","1uH_2.4A",370,165,"VOUT_RAW","POE_5V")
passive("C","C14","100uF_6.3V",395,165,"POE_5V","ISO_GND")
passive("C","C28","1uF_10V",418,165,"POE_5V","ISO_GND")
part("Output","J2","5V_2A_Output",453,165,["POE_5V","ISO_GND"])

# Isolated feedback: TLV431 and optocoupler preserve the power isolation.
passive("R","R22","1k",330,230,"POE_5V","LED_A")
part("Opto","U2","TCMT1107",277,267,["CTL","RTN","LED_A","VKAT"])
passive("R","R23","2k",205,269,"VB","CTL")
passive("C","C21","47nF",225,269,"VB","CTL_RC")
passive("R","R28","402R",245,269,"CTL_RC","CTL")
passive("R","R16","10k",350,230,"POE_5V","VKAT")
part("TLV431","U3","TLV431ACDBVR",390,269,["VKAT","FB","ISO_GND","NC","ISO_GND"],
     "Package_TO_SOT_SMD:SOT-23-5")
passive("R","R19","44.2k_1%",415,230,"POE_5V","FB")
passive("R","R24","14.3k_1%",415,299,"FB","ISO_GND")
passive("C","C18","100pF",346,300,"VKAT","FB")
passive("R","R21","10k",369,300,"VKAT","COMP_RC")
passive("C","C19","6.8nF",390,300,"COMP_RC","FB")
passive("C","C22","1uF_10V",438,268,"VKAT","ISO_GND")


def instance(p):
    kind, ref, value, x, y, pins, footprint, datasheet = p
    if kind in ("R", "C", "L", "D"):
        rx, ry, vx, vy = x+7.62, y-2.54, x+7.62, y+2.54
    elif kind == "RJ45_Power":
        rx, ry, vx, vy = x, y-27.94, x, y+27.94
    elif kind in ("TPS23753A", "Flyback", "NMOS"):
        rx, ry, vx, vy = x, y-25.4, x, y+25.4
    else:
        rx, ry, vx, vy = x, y-13.97, x, y+13.97
    props = [
        f'(property "Reference" {q(ref)} (at {xy(rx,ry)} 0) {FONT})',
        f'(property "Value" {q(value)} (at {xy(vx,vy)} 0) {FONT})',
        f'(property "Footprint" {q(footprint)} (at {xy(x,y)} 0) {HIDDEN})',
        f'(property "Datasheet" {q(datasheet)} (at {xy(x,y)} 0) {HIDDEN})',
    ]
    pin_uuids = ' '.join(f'(pin {q(pp[1])} (uuid {q(uid())}))' for pp in pins)
    return (f'(symbol (lib_id "PoEAdapter:{kind}") (at {xy(x,y)} 0) (unit 1) '
            f'(in_bom yes) (on_board yes) (dnp no) (uuid {q(uid())}) '
            + ' '.join(props) + ' ' + pin_uuids +
            f'(instances (project "adapter" (path "/{ROOT_UUID}/{SHEET_UUID}" '
            f'(reference {q(ref)}) (unit 1)))))')


def label(net, x, y):
    return f'(label {q(net)} (at {xy(x,y)} 0) {FONT} (uuid {q(uid())}))'


def text_note(s, x, y, size=1.5):
    return (f'(text {q(s)} (at {xy(x,y)} 0) '
            f'(effects (font (size {size:g} {size:g}))) (uuid {q(uid())}))')


notes += [
    text_note("POWER-ONLY PoE | IEEE 802.3at Type 1 / Class 3 | 5 V, 2 A maximum",235,24,2.0),
    text_note("INPUT: all four cable pairs accepted; no Ethernet data path",65,106),
    text_note("PRIMARY: VSS and RTN are separate across the TPS23753A hot-swap switch",125,230),
    text_note("ISOLATION BARRIER: do not join RTN or VSS to ISO_GND",306,61),
    text_note("T1, U2: maintain creepage and clearance in PCB layout",350,77),
    text_note("Reference: TI PMP7355 Rev B, SLVRB20 / SLVRB21. Validate on hardware.",250,339),
]

hlabels = [
    f'(hierarchical_label "POE_5V" (shape output) (at 480.06 157.48 0) {FONT} (uuid {q(uid())}))',
    f'(hierarchical_label "ISO_GND" (shape output) (at 480.06 167.64 0) {FONT} (uuid {q(uid())}))',
]
labels.extend([("POE_5V",480.06,157.48),("ISO_GND",480.06,167.64)])

defs = '\n'.join(symbol_def(k,*v) for k,v in DEFS.items())
libdefs = '\n'.join(symbol_def(k,*v).replace(f'"PoEAdapter:{k}"',q(k),1)
                    for k,v in DEFS.items())
lib = f'(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") {libdefs})'
(PROJECT_DIR / 'PoEAdapter.kicad_sym').write_text(lib)
(PROJECT_DIR / 'sym-lib-table').write_text(
    '(sym_lib_table (lib (name "PoEAdapter") (type "KiCad") '
    '(uri "${KIPRJMOD}/PoEAdapter.kicad_sym") (options "") (descr "")))\n')
sheet = f'''(kicad_sch
 (version 20260306)
 (generator "eeschema")
 (generator_version "10.0")
 (uuid {q(SHEET_UUID)})
 (paper "A2")
 (title_block (title "Power-only isolated PoE to 5 V / 2 A") (rev "A"))
 (lib_symbols {defs})
 {chr(10).join(instance(p) for p in parts)}
 {chr(10).join(label(n,x,y) for n,x,y in labels)}
 {chr(10).join(hlabels)}
 {chr(10).join(notes)}
 (sheet_instances (path "/" (page "1")))
 (embedded_fonts no)
)'''
OUT.write_text(sheet)
root = f'''(kicad_sch
 (version 20260306)
 (generator "eeschema")
 (generator_version "10.0")
 (uuid {q(ROOT_UUID)})
 (paper "A4")
 (title_block (title "Reusable isolated PoE to 5 V / 2 A") (rev "A"))
 (lib_symbols)
 (sheet (at 50.8 50.8) (size 88.9 45.72)
   (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0))
   (uuid {q(SHEET_UUID)})
   (property "Sheetname" "PoE_5V_2A" (at 50.8 49.53 0) {FONT})
   (property "Sheetfile" "power_module.kicad_sch" (at 50.8 97.79 0) {FONT})
   (pin "POE_5V" output (at 139.7 63.5 0) {FONT} (uuid {q(uid())}))
   (pin "ISO_GND" output (at 139.7 76.2 0) {FONT} (uuid {q(uid())}))
   (instances (project "adapter" (path "/{ROOT_UUID}" (page "2")))))
 (no_connect (at 139.7 63.5) (uuid {q(uid())}))
 (no_connect (at 139.7 76.2) (uuid {q(uid())}))
 (text "Add power_module.kicad_sch as a hierarchical sheet in a host board."
   (at 120.65 115.57 0) {FONT} (uuid {q(uid())}))
 (sheet_instances (path "/" (page "1")))
 (embedded_fonts no)
)'''
(PROJECT_DIR / 'adapter.kicad_sch').write_text(root)
print(f"Wrote {OUT} with {len(parts)} parts and parent sheet")
