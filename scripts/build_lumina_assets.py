#!/usr/bin/env python3
"""
Generates the animated SVG assets for the GitHub profile README.

GitHub renders SVGs through <img>, so there is no JavaScript: every animation
here is plain CSS keyframes inside the SVG. The look combines two ideas:

  * kurage    - dark "ocean" UI, cyan/violet accents, ASCII jellyfish,
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
ROLE = "AI Systems Architect  ·  CS @ Newton School of Technology"
EYEBROW = "BENGALURU  ·  OPEN TO WORK"
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


BASE_CSS = f"""
.mono{{font-family:{MONO}}} .sans{{font-family:{SANS}}} .serif{{font-family:{SERIF}}}
@keyframes pulse{{0%,100%{{transform:scale(1,1)}}45%{{transform:scale(.93,1.06)}}}}
@keyframes fa{{0%,33.3%{{opacity:1}}33.4%,100%{{opacity:0}}}}
@keyframes fb{{0%,33.3%{{opacity:0}}33.4%,66.6%{{opacity:1}}66.7%,100%{{opacity:0}}}}
@keyframes fc{{0%,66.6%{{opacity:0}}66.7%,100%{{opacity:1}}}}
@keyframes driftA{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(16px,-24px)}}}}
@keyframes driftB{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-18px,-16px)}}}}
@keyframes twinkle{{0%,100%{{opacity:.08}}50%{{opacity:.75}}}}
.bell{{transform-box:fill-box;transform-origin:50% 0;animation:pulse 3.6s ease-in-out infinite}}
.fa{{animation:fa 1.8s steps(1) infinite}} .fb{{animation:fb 1.8s steps(1) infinite}} .fc{{animation:fc 1.8s steps(1) infinite}}
.dA{{animation:driftA 9s ease-in-out infinite}} .dB{{animation:driftB 11s ease-in-out infinite}}
.tw{{animation:twinkle 4s ease-in-out infinite}}
"""

# --------------------------------------------------------------------------
# ASCII jellyfish (original design)
# --------------------------------------------------------------------------
CW, LH, FS = 8.4, 15, 14          # cell width, line height, font size
COLS = 17
BELL = [
    '.-"""""-.',
    ".'  . : .  '.",
    "/  . : : : .  \\",
    "|  : : : : : :  |",
    "|.'  : : : :  '.|",
    "'-.__~~~~~~~__.-'",
]
BELL_OP = [0.95, 0.9, 0.85, 0.8, 0.75, 0.7]
TENT_OP = [0.6, 0.5, 0.4, 0.3, 0.2]
TENT_COLS = (3, 6, 8, 10, 13)


def tentacle_frames():
    frames = []
    for ph in (0.0, 2.1, 4.2):
        rows = []
        for k in range(len(TENT_OP)):
            line = [" "] * COLS
            for ci, c in enumerate(TENT_COLS):
                v = math.sin(k * 0.9 + ci * 1.3 + ph)
                ch = "(" if v > 0.35 else ")" if v < -0.35 else "|"
                if k == len(TENT_OP) - 1:
                    ch = "."
                line[c] = ch
            rows.append("".join(line))
        frames.append(rows)
    return frames


FRAMES = tentacle_frames()


def _row(y, s, op, color):
    return (
        f'<text x="0" y="{y}" textLength="{COLS * CW:.1f}" lengthAdjust="spacing" '
        f'xml:space="preserve" fill="{color}" fill-opacity="{op}">{esc(s)}</text>'
    )


def jelly(x, y, scale, color, drift="dA", delay=0.0, dur=None, opacity=1.0):
    out = [f'<g transform="translate({x} {y}) scale({scale})" opacity="{opacity}">']
    style = f"animation-delay:{delay}s;" + (f"animation-duration:{dur}s;" if dur else "")
    out.append(
        f'<g class="{drift}" style="{style}filter:drop-shadow(0 0 7px {color}66)">'
    )
    out.append(f'<g class="mono bell" font-size="{FS}">')
    for i, line in enumerate(BELL):
        out.append(_row((i + 1) * LH, line.center(COLS), BELL_OP[i], color))
    out.append("</g>")
    base = (len(BELL) + 1) * LH
    for f, cls in zip(FRAMES, ("fa", "fb", "fc")):
        out.append(f'<g class="mono {cls}" font-size="{FS}">')
        for k, line in enumerate(f):
            out.append(_row(base + k * LH, line, TENT_OP[k], color))
        out.append("</g>")
    out.append("</g></g>")
    return "\n".join(out)


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
    s = svg_open(W, H, f"{NAME} — profile banner",
                 f"{NAME}, {ROLE.replace('  ', ' ')}. Animated ASCII jellyfish drift over a dark ocean grid "
                 f"while a prompt box rotates through what I build.")
    s += f"<style>{css}</style>\n<defs>{GRID_DEF}\n"
    s += (
        f'<radialGradient id="gC" cx="78%" cy="18%" r="55%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".20"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>\n'
        f'<radialGradient id="gV" cx="12%" cy="105%" r="60%"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>\n'
        f'<linearGradient id="gName" gradientUnits="userSpaceOnUse" x1="170" y1="0" x2="560" y2="0">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>\n'
        f'<linearGradient id="gStroke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".55"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity=".10"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".55"/></linearGradient>\n'
        f'<mask id="fadeR"><linearGradient id="fr" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".18" stop-color="#fff"/></linearGradient><rect width="{W}" height="{H}" fill="url(#fr)"/></mask>\n'
        f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>\n'
    )
    s += '<g clip-path="url(#clip)">\n'
    s += f'<rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>\n'
    s += f'<rect width="{W}" height="{H}" fill="url(#gC)"/><rect width="{W}" height="{H}" fill="url(#gV)"/>\n'
    s += plankton(34, 40, 1180, 20, 420) + "\n"

    # jellyfish field
    s += '<g mask="url(#fadeR)">\n'
    s += jelly(770, 58, 1.7, CYAN, "dA", 0, 10, .95) + "\n"
    s += jelly(1048, 196, 1.0, VIOLET, "dB", -3, 12, .9) + "\n"
    s += jelly(1086, 50, 0.7, CYAN, "dB", -5, 8, .7) + "\n"
    s += jelly(716, 318, 0.62, VIOLET, "dA", -2, 13, .65) + "\n"
    s += "</g>\n"

    # copy
    s += f'<g class="rise" style="animation-delay:.05s"><rect x="64" y="86" width="8" height="8" rx="2" fill="{GOLD}"/>'
    s += f'<text x="84" y="95" class="mono" font-size="13" letter-spacing="3" fill="{MUTED}" xml:space="preserve">{esc(EYEBROW)}</text></g>\n'
    first, rest = NAME.split(" ", 2)[0:2], NAME.split(" ", 2)[2]
    s += (f'<g class="rise" style="animation-delay:.2s"><text x="64" y="172" class="serif" font-size="70" font-weight="500" '
          f'fill="{TEXT}" letter-spacing="-1">{esc(" ".join(first))} <tspan fill="url(#gName)" font-style="italic">{esc(rest)}</tspan></text></g>\n')
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
    s += jelly(1010, 36, 1.15, CYAN, "dB", -2, 10, .55) + "\n"
    s += jelly(560, 150, 0.6, VIOLET, "dA", -4, 12, .4) + "\n"

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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {"hero.svg": build_hero(), "lumina.svg": build_lumina(),
             "composer.svg": build_composer(), "footer.svg": build_footer()}
    for name, label in CHIPS:
        files[f"{name}.svg"] = build_chip(label)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"wrote assets/{name}  ({len(content) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
