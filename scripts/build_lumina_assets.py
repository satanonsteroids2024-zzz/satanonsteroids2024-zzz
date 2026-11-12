#!/usr/bin/env python3
"""
Generates the animated SVG assets for the GitHub profile README.

GitHub renders SVGs through <img>, so there is no JavaScript: every animation
here is plain CSS keyframes inside the SVG. The look combines two ideas:

  * kurage    - dark "ocean" UI, cyan/violet accents, flowing binary streams,
                a glass prompt composer with a rotating headline
  * lumina    - a full-bleed "interactive list": six slides, a circular glass
                reveal between them, six different title animations, a 01/06
                counter and a progress-line navigation, with a gold accent

Everything is original code and original artwork (no template source is copied).
Edit the CONFIG block below, run `python3 scripts/build_lumina_assets.py`, commit the assets/ folder.
"""
import html
import math
import pathlib
import random

# --------------------------------------------------------------------------
# CONFIG - change these and re-run
# --------------------------------------------------------------------------
NAME = "H S Bharath Surya"
ROLE = "Multi-agent systems  ·  LLM routing  ·  human-in-the-loop AI"
EYEBROW = "WHAT I BUILD"
HERO_HEAD = ("Sovereign", "by design.")   # white word + gradient italic word (the name lives in the intro)
HEADLINES = [  # words between *asterisks* get the accent colour
    "Ship *multi-agent* systems that stay accountable",
    "Route *LLMs* across Gemini, Groq & Ollama",
    "Automate the *boring* parts with n8n & Zapier",
    "Keep a *human* in the loop, always",
    "Run *local*. Stay sovereign.",
]
SLIDES = [  # (nav label, big title, description)
    ("HELLO", "Systems that think.",
     "AI Systems Architect and CS student in Bengaluru, building agentic software with a human in the loop."),
    ("ARES-X", "ARES-X Titan",
     "A sovereign AI intelligence OS: C4ISR-inspired, red-team aware, with human approval gates."),
    ("VOICE AI", "Voice, in 3D",
     "Real-time voice AI with a three-dimensional interface you can talk to."),
    ("AUTOMATION", "Quiet Automation",
     "End-to-end workflows on n8n, Zapier, webhooks and REST. The boring work, handled."),
    ("NIFTY", "Reading the Market",
     "A NIFTY futures research tool for the Indian market."),
    ("CONTACT", "Let's work together.",
     "Open to freelance, automation and technical writing. Say hello on LinkedIn."),
]
COMPOSER_PROMPT = "What are we building next?"
CHIPS = [  # (file, label)
    ("chip-ares", "→  Explore ARES-X"),
    ("chip-repos", "→  Browse all repositories"),
    ("chip-linkedin", "→  Connect on LinkedIn"),
]
CAPTION = "DRIFT GENTLY       SHIP CAREFULLY"   # the gold square sits in the gap

INTRO = dict(
    eyebrow="INTRO  ·  BENGALURU, IN",
    line1="Hi, I'm Bharath.",
    line2="I design AI systems.",
    para=[
        "CS student at Newton School of Technology in Bengaluru.",
        "I design AI systems that route work across models,",
        "call tools, and keep a human approving the decisions",
        "that matter: Python, FastAPI, LLM workflows and n8n.",
    ],
    pills=["90+ modules", "114/114 tests", "Open to freelance"],
    button="Say hello",
)

# --------------------------------------------------------------------------
# design tokens
# --------------------------------------------------------------------------
INK = "#04060a"
INK2 = "#0a0e15"
TEXT = "#f1f4f8"
MUTED = "#9aa4b4"
FAINT = "#808a9a"
CYAN = "#7ce8f2"
VIOLET = "#b9a6ff"
GOLD = "#d4af37"

MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "Geist,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
SERIF = "'Cormorant Garamond',Georgia,'Times New Roman',serif"

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"


def esc(s):
    return html.escape(s, quote=False)


def svg_open(w, h, title, desc):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d">\n<title id="t">{esc(title)}</title>\n'
        f'<desc id="d">{esc(desc)}</desc>\n'
    )


# binary stream geometry (monospace cells; textLength pins every row's width so all fonts line up)
CW = 7.8                                # cell width at 13px (also used by the footer wave)
BIN_BYTES = 12                          # bytes per repeating unit
BIN_FONTS = (9, 13, 18)                 # three depth layers: far, mid, near


def bin_period(fs):
    return BIN_BYTES * 9 * fs * 0.6     # px per unit = the scroll distance of one seamless loop


BIN_CSS = "".join(
    f"@keyframes bl{fs}{{{{to{{{{transform:translateX(-{bin_period(fs):.1f}px)}}}}}}}}"
    f"@keyframes br{fs}{{{{from{{{{transform:translateX(-{bin_period(fs):.1f}px)}}}}to{{{{transform:translateX(0)}}}}}}}}"
    f".bl{fs}{{{{animation:bl{fs} 30s linear infinite}}}} .br{fs}{{{{animation:br{fs} 30s linear infinite}}}}\n"
    for fs in BIN_FONTS)

BASE_CSS = f"""
.mono{{font-family:{MONO}}} .sans{{font-family:{SANS}}} .serif{{font-family:{SERIF}}}
@keyframes twinkle{{0%,100%{{opacity:.08}}50%{{opacity:.75}}}}
.tw{{animation:twinkle 4s ease-in-out infinite}}
{BIN_CSS}
@keyframes rp{{0%,100%{{opacity:.62}}50%{{opacity:1}}}}
.rp{{animation:rp 6s ease-in-out infinite}}
@keyframes pk{{0%{{transform:translateX(0);opacity:0}}12%,78%{{opacity:1}}100%{{transform:translateX(var(--pk));opacity:0}}}}
.pk{{opacity:0;animation:pk 3s cubic-bezier(.35,0,.25,1) infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes spinr{{to{{transform:rotate(-360deg)}}}}
.ring1{{transform-box:fill-box;transform-origin:center;animation:spin 70s linear infinite}}
.ring2{{transform-box:fill-box;transform-origin:center;animation:spinr 110s linear infinite}}
@keyframes scan{{0%{{transform:translateY(-60px);opacity:0}}15%,85%{{opacity:1}}100%{{transform:translateY(380px);opacity:0}}}}
.scan{{animation:scan 5.5s cubic-bezier(.4,0,.6,1) infinite}}
"""

# --------------------------------------------------------------------------
# flowing binary streams (replaces the old ASCII jellyfish)
# --------------------------------------------------------------------------
LAYERS = (  # fs, row gap, row offset, opacity range, seconds per loop, share of glowing bits, glow, blur
    dict(fs=9, gap=11, off=0, op=(0.14, 0.30), dur=(60, 110), hi=0.05, glow=0, blur=0.45),
    dict(fs=13, gap=17, off=5, op=(0.36, 0.66), dur=(22, 48), hi=0.11, glow=2.2, blur=0),
    dict(fs=18, gap=27, off=13, op=(0.45, 0.8), dur=(13, 26), hi=0.14, glow=3.5, blur=0),
)


def _bit_unit(rnd, hi_p):
    base, hi = [], []
    for _ in range(BIN_BYTES):
        byte = "".join(rnd.choice("01") for _ in range(8))
        base.append(byte + " ")
        hi.append("".join(ch if rnd.random() < hi_p else " " for ch in byte) + " ")
    return "".join(base), "".join(hi)


def binary_field(x, y, w, h, seed=1, color_a=CYAN, color_b=VIOLET, opacity=1.0, packets=7):
    """three depth layers of scrolling 0/1 rows (far = tiny, slow, blurred; near = large, fast, glowing),
    rows that breathe in a travelling wave, glowing bits, and short data packets racing along the rows"""
    rnd = random.Random(seed)
    out = [f'<g opacity="{opacity}" class="mono">',
           f'<defs><linearGradient id="pk{seed}"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
           f'<stop offset=".7" stop-color="{CYAN}" stop-opacity=".9"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>']
    mid_rows = []
    for L in LAYERS:
        fs, gap = L["fs"], L["gap"]
        period = bin_period(fs)
        reps = int((w + period) // period) + 2
        rows = int((h - L["off"]) // gap)
        style = []
        if L["blur"]:
            style.append(f"filter:blur({L['blur']}px)")
        elif L["glow"]:
            style.append(f"filter:drop-shadow(0 0 {L['glow']}px {CYAN}99)")
        out.append(f'<g font-size="{fs}" style="{";".join(style)}">')
        for r in range(rows):
            base, hi = _bit_unit(rnd, L["hi"])
            yy = y + L["off"] + r * gap
            if fs == 13:
                mid_rows.append(yy)
            col = _lerp_hex(color_a, color_b, r / max(rows - 1, 1))
            dur = rnd.uniform(*L["dur"])
            cls = f"bl{fs}" if r % 2 == 0 else f"br{fs}"
            tl = len(base) * reps * fs * 0.6
            pdur = rnd.uniform(4.5, 8)
            out.append(
                f'<g class="rp" style="animation-duration:{pdur:.1f}s;animation-delay:{-(r * 0.35) % pdur:.2f}s">'
                f'<g class="{cls}" style="animation-duration:{dur:.1f}s;animation-delay:{-rnd.uniform(0, dur):.1f}s">'
                f'<text x="{x}" y="{yy}" textLength="{tl:.1f}" lengthAdjust="spacing" xml:space="preserve" '
                f'fill="{col}" fill-opacity="{rnd.uniform(*L["op"]):.2f}">{base * reps}</text>'
                + (f'<text x="{x}" y="{yy}" textLength="{tl:.1f}" lengthAdjust="spacing" xml:space="preserve" '
                   f'fill="#ffffff" fill-opacity="1">{hi * reps}</text>' if L["hi"] else "")
                + '</g></g>')
        out.append("</g>")
    for _ in range(packets):                       # data packets: short bright streaks racing along a row
        yy = rnd.choice(mid_rows) - 4
        pw = rnd.uniform(60, 120)
        out.append(
            f'<rect class="pk" x="{x - 10}" y="{yy:.0f}" width="{pw:.0f}" height="1.6" rx=".8" fill="url(#pk{seed})" '
            f'style="--pk:{w * rnd.uniform(0.7, 1.0):.0f}px;animation-duration:{rnd.uniform(2.4, 4.2):.1f}s;'
            f'animation-delay:{-rnd.uniform(0, 4):.1f}s"/>')
    out.append("</g>")
    return "\n".join(out)


def hud_rings(cx, cy, r, opacity=1.0, labels=True):
    """slow counter-rotating dashed rings and tiny readouts around a stream"""
    o = [f'<g opacity="{opacity}" fill="none">',
         f'<circle class="ring1" cx="{cx}" cy="{cy}" r="{r}" stroke="{CYAN}" stroke-opacity=".22" stroke-dasharray="1.5 9"/>',
         f'<circle class="ring2" cx="{cx}" cy="{cy}" r="{r + 26}" stroke="{VIOLET}" stroke-opacity=".2" stroke-dasharray="46 16 6 16"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r - 24}" stroke="#fff" stroke-opacity=".05"/>']
    if labels:
        o.append(f'<text x="{cx}" y="{cy - r - 36}" text-anchor="middle" class="mono" font-size="10" letter-spacing="3" '
                 f'fill="{MUTED}" fill-opacity=".8" stroke="none">STREAM 01  ·  LIVE</text>')
        o.append(f'<text x="{cx}" y="{cy + r + 46}" text-anchor="middle" class="mono" font-size="10" letter-spacing="3" '
                 f'fill="{MUTED}" fill-opacity=".6" stroke="none">0x7F  ·  SYNC  OK</text>')
        o.append(f'<circle class="tw" cx="{cx - 62}" cy="{cy - r - 39}" r="2.4" fill="{CYAN}" stroke="none"/>')
    o.append("</g>")
    return "\n".join(o)


def plankton(n, x0, x1, y0, y1, seed=7):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.choice((1, 1, 1.4, 1.8))
        col = rnd.choice((CYAN, CYAN, VIOLET, TEXT))
        out.append(
            f'<circle class="tw" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{col}" '
            f'style="animation-delay:{rnd.uniform(0, 4):.2f}s;animation-duration:{rnd.uniform(3, 7):.1f}s"/>'
        )
    return "\n".join(out)


GRID_DEF = (
    '<pattern id="grid" width="10" height="15" patternUnits="userSpaceOnUse">'
    '<path d="M10 0V15M0 15H10" stroke="#fff" stroke-opacity=".035" fill="none"/></pattern>'
)


# --------------------------------------------------------------------------
# hero.svg
# --------------------------------------------------------------------------
def build_hero():
    W, H = 1200, 440
    n = len(HEADLINES)
    per = 3.0
    total = n * per
    pct = per / total * 100

    def hl_markup(s):
        parts = s.split("*")
        o = ""
        for i, p in enumerate(parts):
            if not p:
                continue
            o += f'<tspan fill="{CYAN}">{esc(p)}</tspan>' if i % 2 else esc(p)
        return o

    css = BASE_CSS + f"""
@keyframes hl{{0%{{opacity:0;transform:translateY(10px);filter:blur(8px)}}
  {pct*0.16:.2f}%{{opacity:1;transform:none;filter:blur(0)}}
  {pct*0.84:.2f}%{{opacity:1;transform:none;filter:blur(0)}}
  {pct:.2f}%{{opacity:0;transform:translateY(-8px);filter:blur(6px)}}100%{{opacity:0}}}}
.hl{{opacity:0;animation:hl {total}s cubic-bezier(.2,.7,.2,1) infinite both}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.rise{{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}} .hl0{{opacity:1}}}}
"""
    s = svg_open(W, H, f"{' '.join(HERO_HEAD)} — banner",
                 f"{' '.join(HERO_HEAD)} {ROLE.replace('  ', ' ')}. Rows of binary code stream across a dark grid "
                 f"while a prompt box rotates through what I build.")
    s += f"<style>{css}</style>\n<defs>{GRID_DEF}\n"
    s += (
        f'<radialGradient id="gC" cx="78%" cy="18%" r="55%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".20"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>\n'
        f'<radialGradient id="gV" cx="12%" cy="105%" r="60%"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>\n'
        f'<linearGradient id="gName" gradientUnits="userSpaceOnUse" x1="330" y1="0" x2="640" y2="0">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>\n'
        f'<linearGradient id="gStroke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".55"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity=".10"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".55"/></linearGradient>\n'
        f'<radialGradient id="bmg"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff" stop-opacity=".85"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>\n'
        f'<mask id="bm" maskUnits="userSpaceOnUse" x="660" y="14" width="540" height="410"><rect x="660" y="14" width="540" height="410" fill="url(#bmg)"/></mask>\n'
        f'<linearGradient id="scanG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{CYAN}" stop-opacity=".30"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>\n'
        f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>\n'
    )
    s += '<g clip-path="url(#clip)">\n'
    s += f'<rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>\n'
    s += f'<rect width="{W}" height="{H}" fill="url(#gC)"/><rect width="{W}" height="{H}" fill="url(#gV)"/>\n'
    s += plankton(34, 40, 1180, 20, 420) + "\n"

    # binary data stream, fading out toward the edges
    s += '<g mask="url(#bm)">\n'
    s += binary_field(670, 40, 530, 380, seed=3, opacity=0.85) + "\n"
    s += '<rect class="scan" x="660" y="14" width="540" height="60" fill="url(#scanG)"/>\n'
    s += "</g>\n"
    s += hud_rings(935, 230, 172, 0.95) + "\n"

    # copy
    s += f'<g class="rise" style="animation-delay:.05s"><rect x="64" y="86" width="8" height="8" rx="2" fill="{GOLD}"/>'
    s += f'<text x="84" y="95" class="mono" font-size="13" letter-spacing="3" fill="{MUTED}" xml:space="preserve">{esc(EYEBROW)}</text></g>\n'
    s += (f'<g class="rise" style="animation-delay:.2s"><text x="64" y="172" class="serif" font-size="70" font-weight="500" '
          f'fill="{TEXT}" letter-spacing="-1">{esc(HERO_HEAD[0])} <tspan fill="url(#gName)" font-style="italic">{esc(HERO_HEAD[1])}</tspan></text></g>\n')
    s += (f'<g class="rise" style="animation-delay:.35s"><text x="66" y="214" class="sans" font-size="19" fill="{MUTED}" '
          f'xml:space="preserve">{esc(ROLE)}</text></g>\n')

    # glass composer with rotating headline
    s += '<g class="rise" style="animation-delay:.5s">'
    s += (f'<rect x="64" y="250" width="640" height="78" rx="22" fill="{INK2}" fill-opacity=".82" '
          f'stroke="url(#gStroke)" stroke-width="1.2"/>')
    s += f'<text x="94" y="298" class="mono" font-size="22" fill="{CYAN}">›</text>'
    for i, line in enumerate(HEADLINES):
        s += (f'<text class="hl sans hl{i}" x="122" y="297" font-size="24" fill="{TEXT}" '
              f'style="animation-delay:{i * per}s">{hl_markup(line)}</text>')
    s += "</g>\n"
    s += (f'<text x="68" y="362" class="mono" font-size="12" letter-spacing="1.5" fill="{FAINT}">'
          f'python  ·  fastapi  ·  llm routing  ·  agents  ·  automation</text>\n')
    s += "</g>\n</svg>\n"
    return s


# --------------------------------------------------------------------------
# lumina.svg  - the interactive list
# --------------------------------------------------------------------------
LW, LHT = 1200, 560
CX, CY, RMAX = 600, 270, 700
SLIDE_T = 4.0                    # seconds per slide
N = len(SLIDES)
CYCLE = N * SLIDE_T              # 24 s
REVEAL = 1.2                     # seconds the glass circle takes to open

PALETTES = [  # (bg1, bg2, glow, accent)
    ("#04060a", "#0b1a26", CYAN, VIOLET),
    ("#03080c", "#06242c", "#4fe0d0", CYAN),
    ("#07050f", "#1b1036", VIOLET, "#ff9ad5"),
    ("#050a12", "#10203a", "#6fa8ff", CYAN),
    ("#040a07", "#0a2519", "#5be3a0", CYAN),
    ("#0a0705", "#2d2108", GOLD, "#ffd978"),
]


def motif(i):
    """low-contrast artwork that sets each slide's mood"""
    c = PALETTES[i][3]
    g = PALETTES[i][2]
    rnd = random.Random(100 + i)
    o = []
    if i == 0:  # drifting dots + faint rings
        for r in (120, 200, 290):
            o.append(f'<circle cx="930" cy="230" r="{r}" fill="none" stroke="{g}" stroke-opacity=".10" stroke-dasharray="2 8"/>')
        o.append(plankton(40, 560, 1180, 40, 440, seed=21))
    elif i == 1:  # radar
        for r in (70, 130, 190, 250, 310):
            o.append(f'<circle cx="900" cy="250" r="{r}" fill="none" stroke="{g}" stroke-opacity=".16"/>')
        o.append(f'<path d="M900 -80V580M540 250H1260" stroke="{g}" stroke-opacity=".14"/>')
        o.append(f'<g class="sweep"><path d="M900 250 L1210 250 A310 310 0 0 0 1119 31 Z" fill="url(#sweep)"/></g>')
        for _ in range(7):
            a, d = rnd.uniform(0, 6.28), rnd.uniform(60, 290)
            o.append(f'<circle class="tw" cx="{900 + d * math.cos(a):.0f}" cy="{250 + d * math.sin(a):.0f}" r="3.2" fill="{c}"'
                     f' style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>')
    elif i == 2:  # voice waveform
        for k in range(44):
            x = 600 + k * 13
            h = 14 + 120 * abs(math.sin(k * 0.37) * math.cos(k * 0.11 + 0.8))
            o.append(f'<rect class="bar" x="{x}" y="{250 - h / 2:.1f}" width="5" height="{h:.1f}" rx="2.5" fill="{g}" '
                     f'fill-opacity=".38" style="animation-delay:{-(k * 0.11):.2f}s"/>')
    elif i == 3:  # workflow graph
        pts = [(640, 120), (780, 200), (700, 330), (900, 120), (960, 280), (1090, 190), (1040, 380), (860, 400)]
        edges = [(0, 1), (1, 2), (1, 3), (3, 5), (1, 4), (4, 5), (4, 6), (2, 7), (7, 4)]
        for a, b in edges:
            o.append(f'<line class="flow" x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" y2="{pts[b][1]}" '
                     f'stroke="{g}" stroke-opacity=".5" stroke-dasharray="4 6"/>')
        for x, y in pts:
            o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{PALETTES[i][0]}" stroke="{g}" stroke-opacity=".8" stroke-width="1.5"/>'
                     f'<circle cx="{x}" cy="{y}" r="3" fill="{g}"/>')
    elif i == 4:  # candles
        y = 260.0
        line = []
        for k in range(30):
            x = 590 + k * 18.5
            op = y
            y += rnd.uniform(-26, 24)
            y = max(120, min(400, y))
            hi, lo = min(op, y) - rnd.uniform(6, 22), max(op, y) + rnd.uniform(6, 22)
            col = g if y < op else "#fca5a5"
            o.append(f'<line x1="{x:.1f}" y1="{hi:.1f}" x2="{x:.1f}" y2="{lo:.1f}" stroke="{col}" stroke-opacity=".5"/>'
                     f'<rect x="{x - 4:.1f}" y="{min(op, y):.1f}" width="8" height="{max(abs(y - op), 3):.1f}" fill="{col}" fill-opacity=".55"/>')
            line.append(f"{x:.1f},{(op + y) / 2:.1f}")
        o.append(f'<polyline points="{" ".join(line)}" fill="none" stroke="{CYAN}" stroke-opacity=".35" stroke-width="1.4"/>')
    else:  # golden hour
        for r in (90, 150, 215, 285, 360):
            o.append(f'<circle cx="900" cy="520" r="{r}" fill="none" stroke="{g}" stroke-opacity="{0.34 - r / 1500:.2f}"/>')
        o.append(f'<circle cx="900" cy="520" r="70" fill="url(#sun)"/>')
        o.append(plankton(26, 560, 1180, 40, 400, seed=55))
    return "\n".join(o)


def slide_bg(i):
    b1, b2, glow, _ = PALETTES[i]
    return (
        f'<rect width="{LW}" height="{LHT}" fill="url(#bg{i})"/>'
        f'<rect width="{LW}" height="{LHT}" fill="url(#glow{i})"/>' + motif(i)
    )


TITLE_ANIM = [  # (from, out) css for the six title animations, one per slide
    ("opacity:0;transform:translateY(26px)", "opacity:0;transform:translateY(-22px)"),             # rise
    ("opacity:0;transform:translateY(-30px)", "opacity:0;transform:translateY(22px)"),             # drop
    ("opacity:0;transform:scale(1.07);filter:blur(14px)", "opacity:0;transform:scale(.98);filter:blur(10px)"),  # blur reveal
    ("opacity:0;letter-spacing:.14em", "opacity:0;letter-spacing:.05em"),                          # tracking in
    ("opacity:0;transform:scale(1,0)", "opacity:0;transform:scale(1,0)"),                          # unfold
    ("opacity:0;transform:translateX(70px)", "opacity:0;transform:translateX(-46px)"),             # slide
]
TITLE_REST = "opacity:1;transform:none;filter:blur(0);letter-spacing:0"


def build_lumina():
    css = BASE_CSS
    # per-slide title keyframes: in 0-2.9%, hold to 13.75%, out by 15.8% of a 24 s cycle
    for i, (frm, out) in enumerate(TITLE_ANIM):
        css += (f"@keyframes ti{i}{{0%{{{frm}}}2.9%{{{TITLE_REST}}}13.75%{{{TITLE_REST}}}"
                f"15.8%{{{out}}}100%{{{out}}}}}\n")
    css += (f"@keyframes win{{0%{{opacity:0;transform:translateY(10px)}}2.9%{{opacity:1;transform:none}}"
            f"13.75%{{opacity:1;transform:none}}15.8%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:0}}}}\n")
    css += (f"@keyframes cnt{{0%{{opacity:0}}2.9%{{opacity:1}}13.75%{{opacity:1}}15.8%{{opacity:0}}100%{{opacity:0}}}}\n")
    css += (f"@keyframes fill{{0%{{transform:scaleX(0);opacity:1}}16.6%{{transform:scaleX(1);opacity:1}}"
            f"17.4%{{transform:scaleX(1);opacity:0}}100%{{transform:scaleX(0);opacity:0}}}}\n")
    css += (f"@keyframes act{{0%{{opacity:0}}1%{{opacity:1}}16.6%{{opacity:1}}17.6%{{opacity:0}}100%{{opacity:0}}}}\n")
    # circular glass reveal for layers 1..N (layer N repeats slide 0 so the loop is seamless)
    for j in range(1, N + 1):
        a = (SLIDE_T * j - REVEAL) / CYCLE * 100
        b = SLIDE_T * j / CYCLE * 100
        css += (f"@keyframes rv{j}{{0%,{a:.3f}%{{transform:scale(0)}}{b:.3f}%,100%{{transform:scale(1)}}}}\n"
                f"@keyframes rm{j}{{0%{{transform:scale(0);opacity:0}}{a:.3f}%{{transform:scale(0);opacity:.55}}"
                f"{b:.3f}%,100%{{transform:scale(1);opacity:0}}}}\n")
    css += f"""
.rv,.rm{{transform-box:view-box;transform-origin:{CX}px {CY}px;animation-duration:{CYCLE}s;animation-iteration-count:infinite;
  animation-timing-function:cubic-bezier(.45,0,.55,1);animation-fill-mode:both}}
.ti,.dsc,.cn,.fl,.ac{{opacity:0;animation-duration:{CYCLE}s;animation-iteration-count:infinite;animation-fill-mode:both}}
.ti{{animation-timing-function:cubic-bezier(.2,.7,.2,1)}} .dsc{{animation-name:win;animation-timing-function:cubic-bezier(.2,.7,.2,1)}}
.cn{{animation-name:cnt}} .ac{{animation-name:act}}
.fl{{animation-name:fill;transform-box:fill-box;transform-origin:0 50%;animation-timing-function:linear}}
@keyframes sweep{{to{{transform:rotate(360deg)}}}}
.sweep{{transform-box:view-box;transform-origin:900px 250px;animation:sweep 7s linear infinite}}
@keyframes bar{{0%,100%{{transform:scaleY(.55)}}50%{{transform:scaleY(1.2)}}}}
.bar{{transform-box:fill-box;transform-origin:50% 50%;animation:bar 1.6s ease-in-out infinite}}
@keyframes flow{{to{{stroke-dashoffset:-20}}}} .flow{{animation:flow 1.4s linear infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}} .s0{{opacity:1!important}}}}
"""
    s = svg_open(LW, LHT, "Interactive list — what I build",
                 "An animated slideshow that cycles through six sections: " +
                 "; ".join(f"{t} — {d}" for _, t, d in SLIDES))
    s += f"<style>{css}</style>\n<defs>{GRID_DEF}\n"
    for i, (b1, b2, glow, acc) in enumerate(PALETTES):
        s += (f'<linearGradient id="bg{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{b1}"/>'
              f'<stop offset="1" stop-color="{b2}"/></linearGradient>'
              f'<radialGradient id="glow{i}" cx="78%" cy="40%" r="55%"><stop offset="0" stop-color="{glow}" stop-opacity=".30"/>'
              f'<stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>\n')
    s += (f'<linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="900" y1="250" x2="1210" y2="140">'
          f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".45"/></linearGradient>\n'
          f'<radialGradient id="sun"><stop offset="0" stop-color="#ffe9a8"/><stop offset="1" stop-color="{GOLD}" stop-opacity=".1"/></radialGradient>\n'
          f'<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset=".35" stop-color="{INK}" stop-opacity="0"/>'
          f'<stop offset="1" stop-color="{INK}" stop-opacity=".92"/></linearGradient>\n'
          f'<linearGradient id="shadeL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{INK}" stop-opacity=".72"/>'
          f'<stop offset=".55" stop-color="{INK}" stop-opacity="0"/></linearGradient>\n')
    for j in range(1, N + 1):
        s += f'<mask id="m{j}"><circle class="rv" cx="{CX}" cy="{CY}" r="{RMAX}" fill="#fff" style="animation-name:rv{j}"/></mask>\n'
    s += (f'<radialGradient id="lmg"><stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#fff" stop-opacity=".8"/>'
          f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
          f'<mask id="lm" maskUnits="userSpaceOnUse" x="740" y="104" width="440" height="230"><rect x="740" y="104" width="440" height="230" fill="url(#lmg)"/></mask>\n')
    s += f'<clipPath id="clip"><rect width="{LW}" height="{LHT}" rx="18"/></clipPath></defs>\n'

    s += '<g clip-path="url(#clip)">\n'
    s += f'<rect width="{LW}" height="{LHT}" fill="{INK}"/>\n'
    s += f"<g>{slide_bg(0)}</g>\n"
    for j in range(1, N + 1):
        s += f'<g mask="url(#m{j})">{slide_bg(j % N)}</g>\n'
        s += (f'<circle class="rm" cx="{CX}" cy="{CY}" r="{RMAX}" fill="none" stroke="#fff" stroke-width="3" '
              f'style="animation-name:rm{j}"/>\n')
    s += f'<rect width="{LW}" height="{LHT}" fill="url(#grid)"/>\n'
    s += f'<rect width="{LW}" height="{LHT}" fill="url(#shade)"/><rect width="{LW}" height="{LHT}" fill="url(#shadeL)"/>\n'
    s += '<g mask="url(#lm)">\n' + binary_field(750, 116, 420, 210, seed=5, opacity=0.62) + "\n</g>\n"
    s += hud_rings(960, 222, 92, 0.55, labels=False) + "\n"

    # chrome
    s += (f'<text x="{LW - 64}" y="84" text-anchor="end" class="mono" font-size="12" letter-spacing="3" fill="{FAINT}">'
          f'INTERACTIVE LIST  ·  GLASS TRANSITION</text>\n')
    s += f'<text x="124" y="108" class="mono" font-size="16" fill="{FAINT}">/ {N:02d}</text>\n'
    for i, (nav, title, desc) in enumerate(SLIDES):
        d = SLIDE_T * i - 0.6
        first = ' s0' if i == 0 else ''
        s += (f'<text class="cn serif{first}" x="64" y="108" font-size="58" font-weight="500" fill="{GOLD}" '
              f'style="animation-delay:{d}s">{i + 1:02d}</text>\n')
        s += (f'<text class="ti serif{first}" x="64" y="392" font-size="88" font-weight="500" fill="{TEXT}" letter-spacing="0" '
              f'style="animation-name:ti{i};animation-delay:{d}s;transform-origin:64px 392px">{esc(title)}</text>\n')
        s += (f'<text class="dsc sans{first}" x="68" y="438" font-size="18" fill="{MUTED}" '
              f'style="animation-delay:{d + 0.25}s">{esc(desc)}</text>\n')

    # navigation
    gap = 16
    colw = (LW - 128 - gap * (N - 1)) / N
    for i, (nav, _, _) in enumerate(SLIDES):
        x = 64 + i * (colw + gap)
        d = SLIDE_T * i
        s += f'<rect x="{x:.1f}" y="494" width="{colw:.1f}" height="2" rx="1" fill="#fff" fill-opacity=".16"/>\n'
        s += (f'<rect class="fl" x="{x:.1f}" y="494" width="{colw:.1f}" height="2" rx="1" fill="{GOLD}" '
              f'style="animation-delay:{d}s"/>\n')
        s += (f'<text x="{x:.1f}" y="524" class="mono" font-size="11" letter-spacing="1.8" fill="{FAINT}">{esc(nav)}</text>\n')
        s += (f'<text class="ac mono" x="{x:.1f}" y="524" font-size="11" letter-spacing="1.8" fill="{TEXT}" '
              f'style="animation-delay:{d}s">{esc(nav)}</text>\n')
    s += "</g>\n</svg>\n"
    return s


# --------------------------------------------------------------------------
# composer.svg  - the glass prompt box
# --------------------------------------------------------------------------
def build_composer():
    W, H = 1200, 214
    n = len(COMPOSER_PROMPT)
    cw = 13.2
    tw = n * cw
    css = BASE_CSS + f"""
@keyframes type{{0%{{transform:scaleX(0)}}38%{{transform:scaleX(1)}}84%{{transform:scaleX(1)}}92%{{transform:scaleX(0)}}100%{{transform:scaleX(0)}}}}
@keyframes cur{{0%{{transform:translateX(0)}}38%{{transform:translateX({tw:.1f}px)}}84%{{transform:translateX({tw:.1f}px)}}92%{{transform:translateX(0)}}100%{{transform:translateX(0)}}}}
.ty{{transform-origin:104px 0;transform-box:view-box;animation:type 9s steps({n},end) infinite}}
.cu{{animation:cur 9s steps({n},end) infinite}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:.1}}}} .blink{{animation:blink 1s steps(1) infinite}}
@keyframes mode{{0%,28%{{transform:translateX(0)}}33.3%,61%{{transform:translateX(72px)}}66.6%,94%{{transform:translateX(144px)}}100%{{transform:translateX(0)}}}}
.mode{{animation:mode 9s cubic-bezier(.2,.7,.2,1) infinite}}
@keyframes glowp{{0%,100%{{opacity:.55}}50%{{opacity:1}}}} .gp{{animation:glowp 3s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""
    s = svg_open(W, H, "Prompt box",
                 f"A glass prompt box that types “{COMPOSER_PROMPT}”, with attach, web, voice and Auto / Fast / Think controls.")
    s += f"<style>{css}</style>\n<defs>{GRID_DEF}\n"
    s += (f'<radialGradient id="g1" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".16"/>'
          f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>\n'
          f'<linearGradient id="gs" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".6"/>'
          f'<stop offset=".5" stop-color="#fff" stop-opacity=".10"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".6"/></linearGradient>\n'
          f'<linearGradient id="gb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>\n'
          f'<clipPath id="tc"><rect class="ty" x="104" y="52" width="{tw:.1f}" height="44"/></clipPath>\n'
          f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>\n')
    s += '<g clip-path="url(#clip)">\n'
    s += f'<rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#grid)"/><rect width="{W}" height="{H}" fill="url(#g1)"/>\n'
    s += plankton(16, 40, 1160, 10, 200, seed=33) + "\n"
    s += f'<rect class="gp" x="64" y="22" width="1072" height="170" rx="26" fill="none" stroke="{CYAN}" stroke-opacity=".12" stroke-width="6"/>\n'
    s += f'<rect x="64" y="22" width="1072" height="170" rx="26" fill="{INK2}" fill-opacity=".9" stroke="url(#gs)" stroke-width="1.2"/>\n'
    # typed prompt
    s += (f'<g clip-path="url(#tc)"><text x="104" y="86" class="mono" font-size="22" textLength="{tw:.1f}" lengthAdjust="spacing" '
          f'xml:space="preserve" fill="{TEXT}">{esc(COMPOSER_PROMPT)}</text></g>\n')
    s += f'<g class="cu"><rect class="blink" x="104" y="62" width="2.5" height="30" rx="1" fill="{CYAN}"/></g>\n'
    s += '<path d="M96 120H1104" stroke="#fff" stroke-opacity=".08"/>\n'
    # tools: attach, web, voice
    st = f'fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
    s += f'<g {st}><circle cx="112" cy="156" r="17"/><path d="M112 148v16M104 156h16"/></g>\n'
    s += f'<g {st}><circle cx="158" cy="156" r="17"/><circle cx="158" cy="156" r="8"/><path d="M150 156h16M158 148c-3 4-3 12 0 16M158 148c3 4 3 12 0 16"/></g>\n'
    s += f'<g {st}><circle cx="204" cy="156" r="17"/><rect x="200" y="147" width="8" height="13" rx="4"/><path d="M196 156a8 8 0 0 0 16 0M204 164v4"/></g>\n'
    # mode pills
    s += f'<rect x="252" y="139" width="224" height="34" rx="17" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".08"/>\n'
    s += f'<g class="mode"><rect x="256" y="143" width="68" height="26" rx="13" fill="{CYAN}" fill-opacity=".16" stroke="{CYAN}" stroke-opacity=".5"/></g>\n'
    for k, m in enumerate(("Auto", "Fast", "Think")):
        s += (f'<text x="{290 + 72 * k}" y="161" text-anchor="middle" class="sans" font-size="14" fill="{TEXT if k == 0 else MUTED}">{m}</text>\n')
    # send
    s += f'<circle cx="1082" cy="156" r="22" fill="url(#gb)"/><path d="M1082 166V146M1073 154l9-9 9 9" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>\n'
    s += (f'<text x="1044" y="161" text-anchor="end" class="mono" font-size="12" letter-spacing="2" fill="{FAINT}">ENTER TO SHIP</text>\n')
    s += "</g>\n</svg>\n"
    return s


# --------------------------------------------------------------------------
# chips + footer
# --------------------------------------------------------------------------
def build_chip(label):
    W, H = 330, 60
    s = svg_open(W, H, label.replace("→", "").strip(), label.replace("→", "").strip())
    s += (f"<style>.sans{{font-family:{SANS}}}"
          f"@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>\n<defs>"
          f'<linearGradient id="gs" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".7"/>'
          f'<stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".7"/></linearGradient></defs>\n')
    s += f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="28" fill="{INK2}" stroke="url(#gs)" stroke-width="1.2"/>\n'
    s += f'<text x="{W / 2}" y="36" text-anchor="middle" class="sans" font-size="16" font-weight="500" fill="{TEXT}" xml:space="preserve">{esc(label)}</text>\n'
    s += "</svg>\n"
    return s


def build_footer():
    W, H = 1200, 130
    unit = "~-._.-~'"
    reps = 21
    tw = len(unit) * reps * CW
    period = len(unit) * CW
    css = BASE_CSS + "".join(
        f"@keyframes w{k}{{from{{transform:translateX(0)}}to{{transform:translateX(-{period:.1f}px)}}}}" for k in range(3)
    ) + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    s = svg_open(W, H, "Footer", "A slow ASCII wave drifting under a closing line.")
    s += f"<style>{css}</style>\n<defs>{GRID_DEF}"
    s += (f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
          f'<stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
          f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>'
          f'<linearGradient id="gc" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
          f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>\n')
    s += f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>\n'
    s += '<g mask="url(#m)" class="mono" font-size="14">\n'
    for k, (y, op, dur, x0) in enumerate(((30, .75, 22, -10), (50, .45, 31, -40), (70, .25, 44, -20))):
        s += (f'<g class="" style="animation:w{k} {dur}s linear infinite"><text x="{x0}" y="{y}" textLength="{tw:.1f}" '
              f'lengthAdjust="spacing" xml:space="preserve" fill="url(#gc)" fill-opacity="{op}">{unit * reps}</text></g>\n')
    s += "</g>\n"
    s += f'<text x="{W / 2}" y="108" text-anchor="middle" class="mono" font-size="12" letter-spacing="4" fill="{FAINT}" xml:space="preserve">{esc(CAPTION)}</text>\n'
    s += f'<rect x="{W / 2 - 2}" y="99" width="8" height="8" rx="2" fill="{GOLD}"/>\n'
    s += "</g></svg>\n"
    return s


# --------------------------------------------------------------------------
# intro.svg - particle portrait + text that burst into dust and reform
#   Needs numpy + Pillow and the photo:  python3 scripts/build_lumina_assets.py --photo /path/to/photo
#   The photo itself is never copied into the repo, only the dot positions.
# --------------------------------------------------------------------------
PW, PH = 370, 504                       # portrait working size (px)
PORTRAIT_CROP = (125, 415, 775, 1300)   # crop of the source photo that holds the picture
# hand-traced outline of the subject in the cropped/resized frame (keeps the background empty)
PORTRAIT_POLY = [(84,160),(84,125),(95,95),(112,68),(135,46),(165,28),(200,20),(240,22),(275,36),(305,58),(328,85),
                 (340,115),(338,150),(330,185),(322,222),(302,232),(298,250),(291,280),(293,310),(300,318),(310,322),
                 (340,335),(370,362),(370,504),(0,504),(0,315),(60,305),(112,298),(135,308),(128,290),(122,275),
                 (110,262),(107,247),(98,238),(82,228),(79,205),(82,185),(88,172)]
I_W, I_H = 1200, 640
I_CYCLE = 14.0
I_SCALE = 0.6                           # units (half pixels) -> canvas px  (1.2 * 0.5)
I_OX, I_OY = 70, 16                     # portrait origin on the canvas
CELL = 40                               # cell size in units
BTN = (560, 520, 190, 48)               # x, y, w, h of the "Say hello" pill
TB = 6.0                                # when the burst starts (seconds into the loop)
BC = (440, 300)                         # where it starts: between the portrait and the text
SERIF_TTF, SERIF_I_TTF, SANS_TTF = ("/System/Library/Fonts/Supplemental/Georgia.ttf",
                                    "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
                                    "/System/Library/Fonts/Supplemental/Arial.ttf")


def portrait_density(photo):
    """tone map of the portrait (0..1 per pixel) that decides where particles go and how bright they are.
    Built for likeness: faithful mid-tones, local contrast so hair/face structure survives, a floor so the
    dark hair is never empty, and a soft fade at the cut edges."""
    import numpy as np
    from PIL import Image, ImageFilter, ImageOps, ImageDraw
    g = Image.open(photo).convert("L").crop(PORTRAIT_CROP).resize((PW, PH), Image.LANCZOS)
    g = ImageOps.autocontrast(g, cutoff=0.5)
    mask = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(mask).polygon(PORTRAIT_POLY, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    f = lambda im: np.asarray(im, float) / 255
    m, a = f(mask), f(g)
    big, mid = f(g.filter(ImageFilter.GaussianBlur(18))), f(g.filter(ImageFilter.GaussianBlur(3)))
    local = np.clip(0.5 + (a - big) * 1.6, 0, 1)
    tone = np.clip(0.62 * a ** 0.65 + 0.38 * local, 0, 1)
    detail = np.clip((a - mid) * 2.2, -0.5, 0.5)
    d = np.clip(0.18 + 0.84 * tone + 1.15 * detail, 0, 1)
    rim = np.clip(m - f(mask.filter(ImageFilter.GaussianBlur(5))), 0, 1)
    d = np.clip(d + 0.25 * rim, 0, 1) * m
    yy, xx = np.mgrid[0:PH, 0:PW]
    fade = (np.clip((PH - yy) / 120, 0, 1) ** 0.8) * np.clip(xx / 45, 0, 1) * np.clip((PW - xx) / 45, 0, 1)
    return d * np.where(m > 0.5, fade, 1)


def portrait_dots(photo, step=2.2):
    d = portrait_density(photo)
    rnd = random.Random(5)
    dots = []
    for y0 in [k * step for k in range(int(PH / step) + 1)]:
        for x0 in [k * step for k in range(int(PW / step) + 1)]:
            x, y = x0 + rnd.uniform(0, step), y0 + rnd.uniform(0, step)
            if x >= PW or y >= PH:
                continue
            v = float(d[int(y), int(x)])
            if rnd.random() < v * 0.9:
                dots.append((x, y, v))
    return dots


def _lerp_hex(a, b, t):
    t = min(max(t, 0.0), 1.0)
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


AURORA = ("#7ce8f2", "#8fb4ff", "#b9a6ff", "#e79bff", "#ff8fc8")   # cyan > blue > violet > orchid > pink


def _aurora(x, y):
    """particle colour: a soft aurora sweeping diagonally across the portrait (quantised to keep paths few)"""
    t = min(max((x / PW * 0.65 + y / PH * 0.35 - 0.22) / 0.62, 0.0), 1.0)   # stretched so the face stays cyan-ish
    seg = t * (len(AURORA) - 1)
    k = min(int(seg), len(AURORA) - 2)
    return _lerp_hex(AURORA[k], AURORA[k + 1], seg - k)


def _text_dots(text, ttf, size, x, y, step, rnd):
    """rasterise a line of text and return jittered dots that sit on the glyphs, plus the text width"""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(ttf, size)
    width = font.getlength(text)
    mask = Image.new("L", (I_W, I_H), 0)
    ImageDraw.Draw(mask).text((x, y), text, font=font, anchor="ls", fill=255)
    m = np.asarray(mask, float) / 255
    ys, xs = np.nonzero(m[:, :] > 0.2)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pts = []
    gy = y0
    while gy <= y1:
        gx = x0
        while gx <= x1:
            px, py = gx + rnd.uniform(0, step), gy + rnd.uniform(0, step)
            if px < I_W and py < I_H and rnd.random() < m[int(py), int(px)] * 0.92:
                pts.append((px, py))
            gx += step
        gy += step
    return pts, width


def build_intro(photo):
    dots = portrait_dots(photo, 1.55)          # denser sampling than the avatar
    rnd = random.Random(9)
    CP = CELL * I_SCALE                              # cell size on the canvas (24 px)

    # ---- every particle: (canvas x, canvas y, colour, stroke width, kind) -----------------
    parts = []                                       # kind "p" = portrait, "t" = text
    for x, y, v in dots:
        cx, cy = I_OX + x * 2 * I_SCALE, I_OY + y * 2 * I_SCALE
        lvl = 0 if v < 0.4 else 1 if v < 0.7 else 2
        parts.append((cx, cy, lvl, (1.0, 1.5, 2.0)[lvl], "p"))
    crisp = []                                       # real text that is swapped for particles during the burst
    L1, L2 = INTRO["line1"], INTRO["line2"]
    for text, ttf, size, x, y, step, sw, colour, anim in (
            (L1, SERIF_TTF, 68, 558, 196, 1.75, 1.35, TEXT, "serif"),
            (L2, SERIF_I_TTF, 58, 558, 264, 1.7, 1.3, "grad", "serif-i")):
        pts, w = _text_dots(text, ttf, size, x, y, step, rnd)
        for px, py in pts:
            c = colour if colour != "grad" else _lerp_hex(CYAN, VIOLET, (px - 560) / 440)
            parts.append((px, py, c, sw, "t"))
        crisp.append((anim, text, x, y, size, w))
    for i, line in enumerate(INTRO["para"]):
        pts, w = _text_dots(line, SANS_TTF, 18, 560, 316 + i * 29, 1.15, rnd)
        for px, py in pts:
            parts.append((px, py, TEXT if i == 0 else MUTED, 0.95, "t"))
        crisp.append(("para", line, 560, 316 + i * 29, 18, w))

    # ---- group particles: spatial cell > speed bin (burst) --------------------------
    cells = {}
    for cx, cy, col, sw, kind in parts:
        cells.setdefault((kind, int(cx // CP), int(cy // CP)), []).append((cx, cy, col, sw))
    groups = {"p": [], "t": []}
    for (kind, gx, gy), pts in sorted(cells.items()):
        px, py = (gx + 0.5) * CP, (gy + 0.5) * CP
        base = _lerp_hex(_aurora((px - I_OX) / (2 * I_SCALE), (py - I_OY) / (2 * I_SCALE)), "#ffffff", 0.3) if kind == "p" else None
        # burst vectors: away from the burst centre, with a shockwave delay that grows with distance
        away = math.atan2(py - BC[1], px - BC[0])
        dist_bc = math.hypot(px - BC[0], py - BC[1])
        bins = {}
        for cx, cy, col, sw in pts:
            if base:                                    # portrait: aurora colour, dimmed by tone level
                col = _lerp_hex("#04060a", base, (0.55, 0.8, 1.0)[col])
            bins.setdefault(rnd.randrange(4), {}).setdefault((col, sw), []).append((round(cx * 2) / 2, round(cy * 2) / 2))
        inner = ""
        for b, paths in sorted(bins.items()):
            a = away + rnd.uniform(-0.2, 0.2)
            mag = (70, 170, 290, 430)[b] * rnd.uniform(0.8, 1.2)
            vx, vy = math.cos(a) * mag + 30, math.sin(a) * mag - 40
            wa = rnd.uniform(0, 6.283)
            delay = TB + min(dist_bc, 800) / 800 * 0.55 + rnd.uniform(0, 0.15)
            body = "".join(f'<path stroke="{col}" stroke-width="{sw}" d="' + "".join(f"M{x:g} {y:g}h0" for x, y in xy) + '"/>'
                           for (col, sw), xy in sorted(paths.items()))
            inner += (f'<g class="bp" style="--vx:{vx:.0f}px;--vy:{vy:.0f}px;--wx:{math.cos(wa) * 50:.0f}px;'
                      f'--wy:{math.sin(wa) * 50:.0f}px;animation-delay:{delay:.2f}s">{body}</g>')
        groups[kind].append(inner)

    # ---- loose particles that stream off the portrait toward the text ---------------------
    flow = []
    for _ in range(170):
        x, y, v = rnd.choice(dots)
        cxp, cyp = I_OX + x * 2 * I_SCALE, I_OY + y * 2 * I_SCALE
        if rnd.random() < 0.5:
            cxp, cyp = I_OX + rnd.uniform(40, 330) * 1.2, I_OY + rnd.uniform(380, 500) * 1.2
        col = rnd.choice((TEXT, "#7ce8f2", "#b9a6ff", "#e79bff", "#ff8fc8"))
        flow.append(
            f'<circle class="fl" cx="{cxp:.0f}" cy="{cyp:.0f}" r="{rnd.choice((1, 1.2, 1.6, 2)):.1f}" fill="{col}" '
            f'style="--fx:{rnd.uniform(120, 460):.0f}px;--fy:{rnd.uniform(-170, 70):.0f}px;'
            f'animation-duration:{rnd.uniform(6, 13):.1f}s;animation-delay:{-rnd.uniform(0, 13):.1f}s"/>')

    def dust(n, seed):
        r = random.Random(seed)
        return "".join(f"M{r.randrange(8, I_W - 8)} {r.randrange(8, I_H - 8)}h0" for _ in range(n))

    pc = lambda t: f"{t / I_CYCLE * 100:.2f}%"
    css = BASE_CSS + f"""
@keyframes burst{{
 0%{{transform:translate(0,0);opacity:1;animation-timing-function:cubic-bezier(.12,.75,.2,1)}}
 5.6%{{transform:translate(var(--vx),var(--vy));opacity:.9;animation-timing-function:ease-out}}
 14.4%{{transform:translate(calc(var(--vx)*1.3 + var(--wx)),calc(var(--vy)*1.3 + var(--wy)));opacity:.55;animation-timing-function:cubic-bezier(.55,0,.25,1)}}
 22%,100%{{transform:translate(0,0);opacity:1}}}}
.bp{{animation:burst {I_CYCLE}s infinite both}}
@keyframes crisp{{0%,{pc(TB - .02)}{{opacity:1}}{pc(TB + .35)},{pc(TB + 4.6)}{{opacity:0}}{pc(TB + 5.3)},100%{{opacity:1}}}}
.crisp{{animation:crisp {I_CYCLE}s linear infinite}}
@keyframes ptx{{0%,{pc(TB - .03)}{{opacity:0}}{pc(TB)},{pc(TB + 4.5)}{{opacity:1}}{pc(TB + 5.2)},100%{{opacity:0}}}}
.ptx{{opacity:0;animation:ptx {I_CYCLE}s linear infinite}}
@keyframes dust{{0%,{pc(TB - .1)}{{opacity:.15}}{pc(TB + .7)},{pc(TB + 3.4)}{{opacity:.85}}{pc(TB + 5.0)},100%{{opacity:.15}}}}
.dust{{animation:dust {I_CYCLE}s ease-in-out infinite}}
@keyframes ring{{0%{{transform:scale(.04);opacity:.55}}9%,100%{{transform:scale(1);opacity:0}}}}
.ring{{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring {I_CYCLE}s cubic-bezier(.2,.7,.2,1) infinite;animation-fill-mode:forwards}}
@keyframes bflash{{0%{{opacity:.7}}7%,100%{{opacity:0}}}}
.bflash{{opacity:0;animation:bflash {I_CYCLE}s ease-out infinite;animation-fill-mode:forwards}}
@keyframes flow{{0%{{opacity:0;transform:translate(0,0)}}12%{{opacity:.9}}70%{{opacity:.55}}100%{{opacity:0;transform:translate(var(--fx),var(--fy))}}}}
.fl{{opacity:0;animation:flow 9s ease-in-out infinite}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.rise{{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}}
"""
    css += "@media (prefers-reduced-motion:reduce){*{animation:none!important}}\n"

    s = svg_open(I_W, I_H, f"{NAME} — intro",
                 "Portrait and intro text drawn as thousands of particles that burst into dust and pull back together. "
                 + " ".join(INTRO["para"]))
    s += f"<style>{css}</style>\n<defs>{GRID_DEF}\n"
    s += (f'<radialGradient id="gC" cx="22%" cy="45%" r="50%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".13"/>'
          f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>\n'
          f'<radialGradient id="gV" cx="95%" cy="100%" r="60%"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".18"/>'
          f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>\n'
          f'<radialGradient id="curglow"><stop offset="0" stop-color="{CYAN}" stop-opacity=".30"/>'
          f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>\n'
          f'<radialGradient id="bfl"><stop offset="0" stop-color="#fff" stop-opacity=".55"/>'
          f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>\n'
          f'<linearGradient id="gName" gradientUnits="userSpaceOnUse" x1="560" y1="0" x2="1000" y2="0">'
          f'<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>\n'
          f'<linearGradient id="gStroke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".6"/>'
          f'<stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".6"/></linearGradient>\n'
          f'<linearGradient id="gBtn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>\n'
          f'<clipPath id="clip"><rect width="{I_W}" height="{I_H}" rx="18"/></clipPath></defs>\n')
    s += '<g clip-path="url(#clip)">\n'
    s += f'<rect width="{I_W}" height="{I_H}" fill="{INK}"/><rect width="{I_W}" height="{I_H}" fill="url(#grid)"/>\n'
    s += f'<rect width="{I_W}" height="{I_H}" fill="url(#gC)"/><rect width="{I_W}" height="{I_H}" fill="url(#gV)"/>\n'
    s += plankton(30, 30, 1170, 20, 620, seed=71) + "\n"
    s += (f'<path class="dust" stroke="#fff" stroke-opacity=".7" stroke-linecap="round" stroke-width="1.6" d="{dust(240, 301)}"/>\n'
          f'<path class="dust" stroke="#fff" stroke-opacity=".7" stroke-linecap="round" stroke-width="2.4" style="animation-delay:-1.7s" d="{dust(160, 302)}"/>\n')
    s += f'<g fill="none" stroke-linecap="round">\n' + "\n".join(groups["p"]) + "\n</g>\n"
    s += '<g>\n' + "\n".join(flow) + "\n</g>\n"

    # copy: eyebrow stays, headline + description are real text that swaps for particles during the burst
    s += (f'<g class="rise" style="animation-delay:.1s"><rect x="560" y="106" width="8" height="8" rx="2" fill="{GOLD}"/>'
          f'<text x="580" y="115" class="mono" font-size="13" letter-spacing="3" fill="{MUTED}" xml:space="preserve">{esc(INTRO["eyebrow"])}</text></g>\n')
    s += '<g class="ptx"><g fill="none" stroke-linecap="round">\n' + "\n".join(groups["t"]) + "\n</g></g>\n"
    for k, (anim, text, x, y, size, w) in enumerate(crisp):
        delay = 0.25 + k * 0.1
        if anim == "serif":
            attrs = f'class="serif" font-size="{size}" font-weight="500" fill="{TEXT}"'
        elif anim == "serif-i":
            attrs = f'class="serif" font-size="{size}" font-weight="500" font-style="italic" fill="url(#gName)"'
        else:
            attrs = f'class="sans" font-size="{size}" fill="{TEXT if text == INTRO["para"][0] else MUTED}"'
        s += (f'<g class="rise" style="animation-delay:{delay:.2f}s"><g class="crisp"><text x="{x}" y="{y}" {attrs} '
              f'textLength="{w:.1f}" lengthAdjust="spacing">{esc(text)}</text></g></g>\n')
    x = 560
    s += '<g class="rise" style="animation-delay:.95s">'
    for p in INTRO["pills"]:
        w = len(p) * 7.9 + 34
        s += (f'<rect x="{x}" y="442" width="{w:.0f}" height="34" rx="17" fill="{INK2}" stroke="url(#gStroke)" stroke-width="1"/>'
              f'<circle cx="{x + 16}" cy="459" r="3" fill="{CYAN}"/>'
              f'<text x="{x + 28}" y="463.5" class="mono" font-size="13" textLength="{len(p) * 7.9:.0f}" lengthAdjust="spacing" fill="{TEXT}">{esc(p)}</text>')
        x += w + 12
    s += "</g>\n"
    bx, by, bw, bh = BTN
    s += (f'<g class="rise" style="animation-delay:1.05s"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="url(#gBtn)"/>'
          f''
          f'<text x="{bx + bw / 2 - 8}" y="{by + 30}" text-anchor="middle" class="sans" font-size="17" font-weight="600" fill="{INK}">{esc(INTRO["button"])}</text>'
          f'<path d="M{bx + bw - 46} {by + 24}h14m-5 -5l5 5l-5 5" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>\n')
    s += f'<circle class="bflash" cx="{BC[0]}" cy="{BC[1]}" r="230" fill="url(#bfl)" style="animation-delay:{TB}s"/>\n'
    s += (f'<circle class="ring" cx="{BC[0]}" cy="{BC[1]}" r="760" fill="none" stroke="#fff" stroke-width="1.5" '
          f'style="animation-delay:{TB}s"/>\n')

    s += "</g>\n</svg>\n"
    return s


# --------------------------------------------------------------------------
# avatar - square PNG + looping GIF of the particle portrait (for the GitHub profile picture)
#   python3 scripts/build_lumina_assets.py --photo photo.webp --avatar        -> avatar/avatar.png, avatar/avatar.gif
#   GitHub has no API for avatars: upload the file at Settings > Public profile > Profile picture.
# --------------------------------------------------------------------------
AV_WIN = (5, 0, 365, 360)              # square window of the portrait (x0, y0, x1, y1)


def build_avatar(photo, outdir):
    import numpy as np
    from PIL import Image, ImageDraw
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    x0, y0, x1, y1 = AV_WIN
    side = x1 - x0
    dots = [(x, y, v) for x, y, v in portrait_dots(photo) if x0 <= x < x1 and y0 <= y < y1]
    P = np.array([(x - x0, y - y0) for x, y, _ in dots], float)
    V = np.array([v for *_, v in dots], float)
    n = len(P)
    rnd = np.random.default_rng(7)
    # colour: white on the left, gold rim on the right (same idea as the intro)
    t = np.clip(P[:, 0] / side, 0, 1)
    white, gold, orange = np.array([241, 244, 248]), np.array([255, 217, 120]), np.array([255, 176, 87])
    cols = np.where((t < .55)[:, None], white,
                    np.where((t < .8)[:, None], white + (gold - white) * ((t - .55) / .25)[:, None],
                             gold + (orange - gold) * (np.clip((t - .8) / .2, 0, 1))[:, None]))
    center = np.array([(210 - x0), (230 - y0)], float)
    d = P - center
    dist = np.hypot(d[:, 0], d[:, 1]) + 1e-6
    unit = d / dist[:, None]
    speed = rnd.uniform(25, 150, n)[:, None]
    wind = np.array([14.0, -12.0])
    swirl = rnd.normal(0, 18, (n, 2))
    burst = unit * speed + wind + swirl
    delay = rnd.uniform(0, 0.08, n)

    def bg(size):
        yy, xx = np.mgrid[0:size, 0:size] / size
        glow = np.exp(-(((xx - .78) ** 2 + (yy - .45) ** 2) / .09)) * 38
        vig = np.exp(-(((xx - .5) ** 2 + (yy - .5) ** 2) / .35))
        base = np.stack([4 + 16 * vig + glow, 6 + 18 * vig + glow * .8, 10 + 22 * vig + glow * .25], -1)
        return Image.fromarray(np.clip(base, 0, 255).astype("uint8"), "RGB")

    def render(size, off=None, alpha=None, shimmer=None, ss=2):
        big = size * ss
        img = bg(big)
        dr = ImageDraw.Draw(img)
        sc = big / side
        pos = P if off is None else P + off
        for i in range(n):
            a = 1.0 if alpha is None else alpha[i]
            if a <= 0.02:
                continue
            k = a * (1.0 if shimmer is None else shimmer[i])
            r = (0.75 + 0.8 * V[i]) * sc * 0.62
            c = tuple(int(c * min(k, 1.0) + bgc * (1 - min(k, 1.0))) for c, bgc in zip(cols[i], (6, 8, 12)))
            cx, cy = pos[i, 0] * sc, pos[i, 1] * sc
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        return img.resize((size, size), Image.LANCZOS)

    render(1024).save(outdir / "avatar.png", optimize=True)

    # looping GIF: shimmer -> burst -> drift -> reform
    frames, N = [], 26
    ease_out = lambda u: 1 - (1 - u) ** 3
    ease_io = lambda u: 0.5 - 0.5 * np.cos(np.pi * u)
    for f in range(N):
        u = f / N
        shimmer = 0.82 + 0.18 * np.sin(u * 2 * np.pi * 2 + P[:, 0] * 0.09 + P[:, 1] * 0.05)
        loc = np.clip(u - delay, 0, 1)
        off = np.zeros((n, 2))
        alpha = np.ones(n)
        out_u = np.clip((loc - 0.42) / 0.14, 0, 1)
        drift_u = np.clip((loc - 0.56) / 0.18, 0, 1)
        back_u = np.clip((loc - 0.74) / 0.2, 0, 1)
        pos_f = burst * ease_out(out_u)[:, None] + burst * 0.45 * drift_u[:, None] + swirl * 0.8 * drift_u[:, None]
        k = 1 - ease_io(back_u)
        off = pos_f * k[:, None]
        alpha = 1 - 0.55 * ease_out(out_u) * k
        frames.append(render(256, off, alpha, shimmer, ss=2).quantize(colors=56, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    frames[0].save(outdir / "avatar.gif", save_all=True, append_images=frames[1:], duration=115, loop=0,
                   optimize=True, disposal=1)
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {"hero.svg": build_hero(), "lumina.svg": build_lumina(),
             "composer.svg": build_composer(), "footer.svg": build_footer()}
    for name, label in CHIPS:
        files[f"{name}.svg"] = build_chip(label)
    import sys
    if "--photo" in sys.argv and "--avatar" in sys.argv:
        n = build_avatar(sys.argv[sys.argv.index("--photo") + 1], OUT.parent / "avatar")
        print(f"avatar: {n} particles")
        return
    if "--photo" in sys.argv:
        photo = sys.argv[sys.argv.index("--photo") + 1]
        files["intro.svg"] = build_intro(photo)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}  ({len(content) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
