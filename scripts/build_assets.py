"""Generate the animated SVG sections for the GitHub profile README.

Usage: python3 scripts/build_assets.py <github-graphql-dump.json>
"""
import json
import math
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 1200

FONT = "Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

BG, SURF, SURF2, BORDER = "#0B1220", "#121B2D", "#16213A", "#243251"
INK, MUTED, DIM = "#E8EDF7", "#8A97B4", "#5B6884"
RED, RED2, GOLD = "#E10600", "#FF3B30", "#F5B14C"
OK, TEAL, VIOLET, BLUE = "#4CC38A", "#4FD1C5", "#A78BFA", "#5C8DFF"
DARK_SLOT = "#1A2236"

BASE_CSS = f"""
.f{{font-family:{FONT}}} .m{{font-family:{MONO}}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.r{{animation:rise .7s cubic-bezier(.2,.7,.2,1) backwards}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.pulse{{animation:pulse 1.6s ease-in-out infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin .45s linear infinite}}
.spin-slow{{transform-box:fill-box;transform-origin:center;animation:spin 6s linear infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}} .r{{opacity:1}}}}
"""


def t(s):
    return escape(str(s))


def text_w(s, size, k=0.58):
    return len(s) * size * k


def svg(h, body, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" fill="none">\n'
        f"<style>{BASE_CSS}{css}</style>\n"
        f'<defs><clipPath id="clip"><rect width="{W}" height="{h}" rx="16"/></clipPath>{defs}</defs>\n'
        f'<g clip-path="url(#clip)">\n{body}\n</g>\n'
        f'<rect x=".5" y=".5" width="{W-1}" height="{h-1}" rx="16" stroke="{BORDER}"/>\n'
        "</svg>\n"
    )


def card_bg(h, fill=SURF):
    return f'<rect width="{W}" height="{h}" fill="{fill}"/>'


def eyebrow(x, y, label, right=None, color=RED):
    out = (
        f'<rect x="{x}" y="{y-11}" width="10" height="10" rx="2" fill="{color}"/>'
        f'<text x="{x+20}" y="{y}" class="m" font-size="14" letter-spacing="3" fill="{MUTED}">{t(label)}</text>'
    )
    if right:
        out += f'<text x="{W-x}" y="{y}" text-anchor="end" class="m" font-size="14" letter-spacing="2" fill="{GOLD}">{t(right)}</text>'
    return out


def chip(x, y, label, color, size=15, delay=None, h=32):
    w = text_w(label, size) + 30
    cls = ' class="r"' if delay is not None else ""
    style = f' style="animation-delay:{delay:.2f}s"' if delay is not None else ""
    g = (
        f"<g{cls}{style}>"
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity=".13" stroke="{color}" stroke-opacity=".45"/>'
        f'<text x="{x + w/2:.0f}" y="{y + h/2 + size*0.36:.1f}" text-anchor="middle" class="f" font-size="{size}" font-weight="600" fill="{color}">{t(label)}</text>'
        "</g>"
    )
    return g, w


def checker_strip(y, h=16, sq=8, anim=True):
    pid = f"chk{y}"
    move = (
        f'<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="{sq*2} 0" dur="0.8s" repeatCount="indefinite"/>'
        if anim
        else ""
    )
    defs = (
        f'<pattern id="{pid}" width="{sq*2}" height="{sq*2}" patternUnits="userSpaceOnUse">'
        f'<rect width="{sq*2}" height="{sq*2}" fill="#0A0A0A"/>'
        f'<rect width="{sq}" height="{sq}" fill="#F2F2F2"/><rect x="{sq}" y="{sq}" width="{sq}" height="{sq}" fill="#F2F2F2"/>'
        f"{move}</pattern>"
    )
    return defs, f'<rect y="{y}" width="{W}" height="{h}" fill="url(#{pid})"/>'


def f1_car(x, y, s, cls="", wheel_cls="spin"):
    """Side-profile open-wheel car facing right; local box ~362x104, ground at y=104."""

    def wheel(cx, cy, r):
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#07090D"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r-6}" stroke="{RED2}" stroke-width="2.5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="8" fill="#2A3550"/>'
            f'<g class="{wheel_cls}"><path d="M{cx-11} {cy}H{cx+11}M{cx} {cy-11}V{cy+11}" stroke="#7F8BA6" stroke-width="2.4"/></g>'
        )

    return (
        f'<g class="{cls}" transform="translate({x} {y}) scale({s})">'
        f'<ellipse cx="185" cy="104" rx="175" ry="5" fill="#000" opacity=".45"/>'
        # rear wing
        f'<rect x="6" y="16" width="9" height="56" rx="2" fill="#0A0A0A"/>'
        f'<rect x="2" y="16" width="50" height="10" rx="2" fill="{RED}"/>'
        f'<rect x="10" y="42" width="32" height="5" fill="#0A0A0A"/>'
        # floor
        f'<rect x="30" y="86" width="300" height="6" rx="2" fill="#0A0A0A"/>'
        # body
        f'<path d="M40 86 L44 60 L95 54 L128 32 L150 28 L168 32 L176 50 L214 52 L250 60 L300 70 L338 78 L348 86 Z" fill="{RED}"/>'
        f'<path d="M100 86 L104 64 L170 60 L230 64 L252 86 Z" fill="#A80400"/>'
        f'<path d="M150 57 L302 74 L302 79 L150 63 Z" fill="#F2F2F2" opacity=".92"/>'
        f'<path d="M128 32 L150 28 L168 32 L160 40 L134 40 Z" fill="#0A0A0A"/>'
        f'<text x="118" y="80" class="m" font-size="13" font-weight="700" fill="#F2F2F2">01</text>'
        # driver + halo
        f'<circle cx="196" cy="45" r="9" fill="{GOLD}"/>'
        f'<rect x="196" y="41" width="10" height="5" rx="2" fill="#0A0A0A"/>'
        f'<path d="M180 51 Q196 32 216 51" stroke="#0A0A0A" stroke-width="4" stroke-linecap="round"/>'
        # front wing
        f'<rect x="318" y="88" width="42" height="6" rx="2" fill="#0A0A0A"/>'
        f'<rect x="354" y="78" width="6" height="16" rx="1" fill="{RED}"/>'
        f"{wheel(78, 82, 22)}{wheel(282, 85, 19)}"
        "</g>"
    )


def speed_lines(x0, x1, ys, color=MUTED, dur=0.9):
    out = []
    for i, y in enumerate(ys):
        ln = 60 + (i * 37) % 90
        delay = (i * 0.17) % dur
        out.append(
            f'<line x1="{x1}" y1="{y}" x2="{x1+ln}" y2="{y}" stroke="{color}" stroke-opacity=".55" stroke-width="2" stroke-linecap="round">'
            f'<animate attributeName="x1" values="{x1};{x0}" dur="{dur}s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="x2" values="{x1+ln};{x0+ln}" dur="{dur}s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke-opacity" values="0;.6;0" dur="{dur}s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            "</line>"
        )
    return "".join(out)


# ---------------------------------------------------------------- hero
def hero():
    h = 430
    cycle = 8.0
    out_at = 4.6
    off_pct = out_at / cycle * 100
    css = ""
    for i in range(5):
        on = (0.5 + i * 0.7) / cycle * 100
        css += (
            f"@keyframes L{i}{{0%,{on-0.2:.2f}%{{fill:{DARK_SLOT}}}{on:.2f}%,{off_pct-0.3:.2f}%{{fill:#FF2A1F}}{off_pct:.2f}%,100%{{fill:{DARK_SLOT}}}}}"
            f".l{i}{{fill:{DARK_SLOT};animation:L{i} {cycle}s linear infinite}}"
        )
    css += (
        f"@keyframes go{{0%,{off_pct:.1f}%{{opacity:0}}{off_pct+1:.1f}%,92%{{opacity:1}}96%,100%{{opacity:0}}}}"
        f".go{{opacity:0;animation:go {cycle}s linear infinite}}"
        f"@keyframes drive{{0%,{off_pct:.1f}%{{transform:translateX(0)}}86%{{transform:translateX(1300px)}}86.01%{{transform:translateX(-420px)}}100%{{transform:translateX(0)}}}}"
        f".drive{{animation:drive {cycle}s cubic-bezier(.55,0,.75,.6) infinite}}"
        f"@keyframes sweep{{from{{transform:translateX(-400px)}}to{{transform:translateX(1400px)}}}}"
        f".sweep{{animation:sweep 5s linear infinite}}"
    )
    chk_defs, chk = checker_strip(h - 16)
    defs = (
        chk_defs
        + f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" stroke="#131D33"/></pattern>'
        + f'<radialGradient id="glow" cx="78%" cy="35%" r="45%"><stop offset="0" stop-color="{RED}" stop-opacity=".32"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        + f'<linearGradient id="title" x1="0" x2="1"><stop offset="0" stop-color="{RED2}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
        + '<linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        + '<filter id="lg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        + f'<pattern id="kerb" width="48" height="8" patternUnits="userSpaceOnUse"><rect width="24" height="8" fill="{RED}"/><rect x="24" width="24" height="8" fill="#F2F2F2"/></pattern>'
    )
    b = [f'<rect width="{W}" height="{h}" fill="{BG}"/>', f'<rect width="{W}" height="{h}" fill="url(#grid)"/>', f'<rect width="{W}" height="{h}" fill="url(#glow)"/>']
    b.append(f'<rect class="sweep" x="0" y="0" width="300" height="{h}" fill="url(#sheen)"/>')

    b.append(f'<circle cx="62" cy="66" r="5" fill="{RED2}" class="pulse"/>')
    b.append(f'<text x="78" y="71" class="m r" font-size="15" letter-spacing="2.5" fill="{MUTED}">LIVE  ·  BENGALURU, IN  ·  NEWTON SCHOOL OF TECHNOLOGY</text>')
    b.append(f'<text x="54" y="150" class="f r" style="animation-delay:.1s" font-size="66" font-weight="800" letter-spacing="-1.5" fill="{INK}">H S Bharath Surya</text>')
    b.append(f'<text x="56" y="200" class="f r" style="animation-delay:.2s" font-size="34" font-weight="700" fill="url(#title)">AI Systems Architect</text>')
    b.append(f'<text x="56" y="240" class="f r" style="animation-delay:.3s" font-size="19" fill="{MUTED}">I design the system and set the strategy. AI runs the laps.</text>')

    x = 56
    colors = [BLUE, RED2, VIOLET, GOLD, TEAL]
    for i, label in enumerate(["Python", "LLM Workflows", "Multi-agent Systems", "Automation", "Prompt Engineering"]):
        g, w = chip(x, 266, label, colors[i], size=14, delay=0.4 + i * 0.08, h=30)
        b.append(g)
        x += w + 10

    # start-light gantry
    gx, gy = 772, 44
    b.append(f'<rect x="{gx-16}" y="{gy}" width="{5*76+12}" height="14" rx="4" fill="#05080F" stroke="#1E2A44"/>')
    for i in range(5):
        px = gx + i * 76
        b.append(f'<rect x="{px}" y="{gy+14}" width="56" height="112" rx="12" fill="#05080F" stroke="#1E2A44"/>')
        for cy in (gy + 46, gy + 94):
            b.append(f'<circle cx="{px+28}" cy="{cy}" r="17" class="l{i}" filter="url(#lg)"/>')
    b.append(f'<text x="{gx+178}" y="{gy+168}" text-anchor="middle" class="m go" font-size="16" letter-spacing="3" font-weight="700" fill="{GOLD}">LIGHTS OUT AND AWAY WE GO</text>')

    # track
    b.append(f'<rect y="322" width="{W}" height="{h-322-16}" fill="#0E1626"/>')
    b.append(f'<rect y="322" width="{W}" height="8" fill="url(#kerb)" opacity=".85"/>')
    b.append(f'<line x1="0" y1="370" x2="{W}" y2="370" stroke="#2A3550" stroke-width="2" stroke-dasharray="34 22"/>')
    b.append(speed_lines(-200, 1200, [346, 360, 382, 396], dur=1.1))
    b.append(f'<g class="drive">{f1_car(70, 334, 0.6)}</g>')
    b.append(chk)
    return svg(h, "\n".join(b), css, defs)


# ---------------------------------------------------------------- about
def about():
    h = 420
    b = [card_bg(h)]
    b.append(eyebrow(40, 56, "DRIVER PROFILE", "CAR No. 01"))
    rows = [
        ("TEAM", "CS @ Newton School of Technology", INK),
        ("ROLE", "AI Systems Architect & Builder", INK),
        ("BASE", "Bengaluru, India", INK),
        ("POWER UNIT", "Python · FastAPI · LLM APIs · n8n · Zapier", INK),
        ("RACECRAFT", "Multi-agent routing · Prompting · Automation", INK),
        ("STATUS", "Open to freelance, automation & writing work", OK),
    ]
    y = 104
    for i, (k, v, c) in enumerate(rows):
        d = 0.15 + i * 0.09
        dot = f'<circle cx="236" cy="{y-6}" r="5" fill="{OK}" class="pulse"/>' if k == "STATUS" else ""
        vx = 250 if k == "STATUS" else 230
        b.append(
            f'<g class="r" style="animation-delay:{d:.2f}s">'
            f'<text x="40" y="{y}" class="m" font-size="13" letter-spacing="2" fill="{DIM}">{t(k)}</text>'
            f'{dot}<text x="{vx}" y="{y}" class="f" font-size="18" font-weight="500" fill="{c}">{t(v)}</text>'
            f'<line x1="40" y1="{y+20}" x2="720" y2="{y+20}" stroke="{BORDER}"/>'
            "</g>"
        )
        y += 50

    px, py, pw, ph = 760, 84, 400, 296
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{SURF2}" stroke="{BORDER}"/>')
    b.append(f'<text x="{px+20}" y="{py+32}" class="m" font-size="12" letter-spacing="2" fill="{DIM}">ON TRACK</text>')
    b.append(f'<text x="{px+pw-20}" y="{py+32}" text-anchor="end" class="m pulse" font-size="12" letter-spacing="2" fill="{RED2}">● P1</text>')
    b.append(f'<rect x="{px}" y="{py+170}" width="{pw}" height="3" fill="url(#kerbA)"/>')
    b.append(f'<g clip-path="url(#pclip)">{speed_lines(px - 120, px + pw, [py + 112, py + 132, py + 150, py + 160], dur=0.8)}</g>')
    b.append(f'<g class="bob">{f1_car(px + 34, py + 70, 0.92)}</g>')
    b.append(f'<text x="{px+20}" y="{py+218}" class="f" font-size="16" font-style="italic" fill="{MUTED}">“I design the system, set the strategy,</text>')
    b.append(f'<text x="{px+20}" y="{py+244}" class="f" font-size="16" font-style="italic" fill="{MUTED}">and let AI handle the pit work.”</text>')
    css = "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.5px)}} .bob{animation:bob .35s ease-in-out infinite}"
    defs = (
        f'<pattern id="kerbA" width="32" height="3" patternUnits="userSpaceOnUse"><rect width="16" height="3" fill="{RED}"/><rect x="16" width="16" height="3" fill="#F2F2F2"/></pattern>'
        f'<clipPath id="pclip"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12"/></clipPath>'
    )
    return svg(h, "\n".join(b), css, defs)


# ---------------------------------------------------------------- stack
def stack():
    groups = [
        ("CORE", BLUE, ["Python", "FastAPI", "SQLite", "Git", "Linux"]),
        ("AI / LLM", RED2, ["Gemini", "Groq", "Ollama", "OpenRouter", "RAG", "Function calling", "Prompt engineering"]),
        ("AUTOMATION", GOLD, ["n8n", "Zapier", "REST APIs", "Webhooks", "systemd"]),
        ("SECURITY", TEAL, ["Kali Linux", "OSINT", "liboqs (post-quantum)"]),
    ]
    h = 120 + len(groups) * 58
    b = [card_bg(h), eyebrow(40, 56, "PIT GARAGE  ·  TECH STACK", "SETUP SHEET")]
    y = 92
    n = 0
    for label, color, items in groups:
        b.append(f'<text x="40" y="{y+21}" class="m r" font-size="13" letter-spacing="2" fill="{DIM}">{t(label)}</text>')
        b.append(f'<rect x="200" y="{y+4}" width="3" height="24" rx="1.5" fill="{color}"/>')
        x = 222
        for it in items:
            g, w = chip(x, y, it, color, size=15, delay=0.1 + n * 0.04)
            b.append(g)
            x += w + 10
            n += 1
        y += 58
    return svg(h, "\n".join(b))


# ---------------------------------------------------------------- ares x
def ares():
    h = 640
    css = (
        "@keyframes fill{from{width:0}to{width:var(--w)}}"
        ".bar{animation:fill 1.6s cubic-bezier(.2,.7,.2,1) .6s both}"
        "@keyframes glow{0%,100%{stroke-opacity:.35}50%{stroke-opacity:1}}"
        ".glow{animation:glow 2.4s ease-in-out infinite}"
    )
    b = [card_bg(h)]
    b.append(eyebrow(40, 56, "POLE POSITION  ·  FLAGSHIP BUILD"))
    sw = text_w("IN ACTIVE DEVELOPMENT", 13, 0.75) + 46
    b.append(f'<rect x="{W-40-sw:.0f}" y="36" width="{sw:.0f}" height="30" rx="15" fill="{GOLD}" fill-opacity=".12" stroke="{GOLD}" stroke-opacity=".5"/>')
    b.append(f'<circle cx="{W-40-sw+18:.0f}" cy="51" r="4.5" fill="{GOLD}" class="pulse"/>')
    b.append(f'<text x="{W-40-sw+30:.0f}" y="56" class="m" font-size="13" letter-spacing="1.5" font-weight="700" fill="{GOLD}">IN ACTIVE DEVELOPMENT</text>')

    b.append(f'<text x="40" y="112" class="f r" font-size="42" font-weight="800" letter-spacing="-1" fill="{INK}">ARES X <tspan fill="{RED2}">—</tspan> Titan</text>')
    b.append(f'<text x="40" y="148" class="f r" style="animation-delay:.1s" font-size="18" fill="{MUTED}">Sovereign AI intelligence OS — C4ISR-inspired threat intel, decision support &amp; red-team operations.</text>')
    b.append(f'<text x="40" y="180" class="m r" style="animation-delay:.15s" font-size="13" letter-spacing="1.5" fill="{DIM}">ARCHITECT &amp; PROJECT LEAD  ·  MAR 2025 – PRESENT  ·  AI-ASSISTED BUILD (CLAUDE OPUS)</text>')

    # pipeline
    py = 204
    b.append(f'<rect x="40" y="{py}" width="{W-80}" height="150" rx="12" fill="{SURF2}" stroke="{BORDER}"/>')
    b.append(f'<text x="60" y="{py+30}" class="m" font-size="12" letter-spacing="2" fill="{DIM}">INFERENCE PIPELINE</text>')
    nodes = [
        (60, 170, "Signals", "OSINT · threat feeds", BLUE),
        (260, 200, "Dispatcher", "Gemini function-calling", VIOLET),
        (490, 290, "Multi-agent router", "Gemini → Groq → Ollama → OpenRouter", RED2),
        (810, 160, "Approval gate", "human sign-off", GOLD),
        (1000, 140, "Recommend", "never auto-acts", OK),
    ]
    ny, nh = py + 50, 66
    cy = ny + nh / 2
    for i in range(len(nodes) - 1):
        x1 = nodes[i][0] + nodes[i][1]
        x2 = nodes[i + 1][0]
        b.append(f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="{BORDER}" stroke-width="2"/>')
        for k in range(2):
            b.append(
                f'<circle cy="{cy}" r="3.5" fill="{nodes[i+1][4]}">'
                f'<animate attributeName="cx" values="{x1};{x2}" dur="1.2s" begin="{k*0.6 + i*0.15:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" dur="1.2s" begin="{k*0.6 + i*0.15:.2f}s" repeatCount="indefinite"/>'
                "</circle>"
            )
    for i, (x, w, title, sub, c) in enumerate(nodes):
        cls = "glow" if i == 2 else ""
        b.append(
            f'<g class="r" style="animation-delay:{0.2 + i*0.1:.2f}s">'
            f'<rect x="{x}" y="{ny}" width="{w}" height="{nh}" rx="10" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".55" class="{cls}"/>'
            f'<rect x="{x}" y="{ny+14}" width="3" height="{nh-28}" rx="1.5" fill="{c}"/>'
            f'<text x="{x+16}" y="{ny+28}" class="f" font-size="16" font-weight="700" fill="{INK}">{t(title)}</text>'
            f'<text x="{x+16}" y="{ny+50}" class="m" font-size="12" fill="{MUTED}">{t(sub)}</text>'
            "</g>"
        )
    b.append(f'<text x="60" y="{py+138}" class="m" font-size="12" fill="{DIM}">Falls back down the chain on rate limits or outages · runs fully local via Ollama when needed</text>')

    # stat tiles
    ty, th = 378, 108
    tw = (W - 80 - 3 * 20) / 4
    tiles = [("235", "FILES", INK, None), ("90+", "MODULES", INK, None), ("114/114", "TESTS PASSING", OK, 1.0), ("12+", "INTEGRATED PHASES", INK, None)]
    for i, (num, label, c, bar) in enumerate(tiles):
        x = 40 + i * (tw + 20)
        b.append(f'<g class="r" style="animation-delay:{0.5 + i*0.1:.2f}s">')
        b.append(f'<rect x="{x:.0f}" y="{ty}" width="{tw:.0f}" height="{th}" rx="12" fill="{SURF2}" stroke="{BORDER}"/>')
        b.append(f'<text x="{x+22:.0f}" y="{ty+54}" class="f" font-size="40" font-weight="800" letter-spacing="-1" fill="{c}">{t(num)}</text>')
        b.append(f'<text x="{x+22:.0f}" y="{ty+82}" class="m" font-size="12" letter-spacing="2" fill="{DIM}">{t(label)}</text>')
        if bar:
            bw = tw - 44
            b.append(f'<rect x="{x+22:.0f}" y="{ty+92}" width="{bw:.0f}" height="4" rx="2" fill="{BORDER}"/>')
            b.append(f'<rect x="{x+22:.0f}" y="{ty+92}" height="4" rx="2" fill="{OK}" class="bar" style="--w:{bw:.0f}px" width="{bw:.0f}"/>')
        b.append("</g>")

    # features
    feats = [
        ("Native Kali Linux app — systemd + GTK/pywebview on FastAPI", BLUE, "live"),
        ("Hard human-approval gates: detects, investigates, recommends", GOLD, "live"),
        ("Post-quantum cryptography with liboqs", VIOLET, "in progress"),
        ("Enterprise RAG + federated search", TEAL, "in progress"),
    ]
    for i, (f, c, st) in enumerate(feats):
        col, row = i % 2, i // 2
        x = 40 + col * 570
        y = 528 + row * 36
        stc = OK if st == "live" else DIM
        b.append(
            f'<g class="r" style="animation-delay:{0.7 + i*0.08:.2f}s">'
            f'<rect x="{x}" y="{y-11}" width="8" height="8" rx="2" fill="{c}"/>'
            f'<text x="{x+20}" y="{y-2}" class="f" font-size="16" fill="{INK}">{t(f)}</text>'
            f'<text x="{x+540}" y="{y-2}" text-anchor="end" class="m" font-size="11" letter-spacing="1" fill="{stc}">{t(st.upper())}</text>'
            "</g>"
        )
    b.append(f'<line x1="40" y1="584" x2="{W-40}" y2="584" stroke="{BORDER}"/>')
    b.append(f'<text x="40" y="614" class="m" font-size="13" letter-spacing="1" fill="{GOLD}">VISION →</text>')
    b.append(f'<text x="122" y="614" class="f" font-size="15" fill="{MUTED}">a Palantir / Recorded Future / Maltego-class platform, pitched through iDEX &amp; DRDO</text>')
    return svg(h, "\n".join(b), css)


# ---------------------------------------------------------------- garage
def gear_path(cx, cy, r_out, r_in, teeth):
    pts = []
    for i in range(teeth * 4):
        a = i * math.pi * 2 / (teeth * 4)
        r = r_out if (i % 4) in (1, 2) else r_in
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def garage():
    h = 300
    css = (
        "@keyframes eq{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}"
        ".eq{transform-box:fill-box;transform-origin:bottom;animation:eq .9s ease-in-out infinite}"
        "@keyframes candle{0%{transform:scaleY(.2);opacity:0}30%,100%{transform:scaleY(1);opacity:1}}"
        ".cd{transform-box:fill-box;transform-origin:bottom;animation:candle 3s ease-out infinite}"
    )
    b = [card_bg(h), eyebrow(40, 56, "ALSO IN THE GARAGE", "3 BUILDS")]
    cw = (W - 80 - 2 * 20) / 3
    cards = [
        ("Voice AI · 3D interface", ["Real-time voice assistant", "wrapped in a full 3D front end"], RED2, "eq"),
        ("Automation engine", ["Runs tasks from trigger to done", "n8n / Zapier + API integrations"], GOLD, "gear"),
        ("NIFTY futures research", ["Trading research tool for", "NIFTY futures analysis"], TEAL, "candle"),
    ]
    for i, (title, lines, c, icon) in enumerate(cards):
        x = 40 + i * (cw + 20)
        y = 84
        b.append(f'<g class="r" style="animation-delay:{0.1 + i*0.12:.2f}s">')
        b.append(f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="180" rx="12" fill="{SURF2}" stroke="{BORDER}"/>')
        b.append(f'<rect x="{x+22:.0f}" y="{y+22}" width="52" height="52" rx="12" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".4"/>')
        ix, iy = x + 22, y + 22
        if icon == "eq":
            for k in range(5):
                bh = [18, 30, 24, 34, 16][k]
                b.append(f'<rect x="{ix+10+k*7:.0f}" y="{iy+42-bh}" width="4" height="{bh}" rx="2" fill="{c}" class="eq" style="animation-delay:{k*0.12:.2f}s"/>')
        elif icon == "gear":
            b.append(f'<g class="spin-slow"><path d="{gear_path(ix+26, iy+26, 17, 12.5, 8)}" fill="{c}"/><circle cx="{ix+26:.1f}" cy="{iy+26}" r="5.5" fill="{SURF2}"/></g>')
        else:
            data = [(14, 24, OK), (20, 18, RED2), (12, 30, OK), (22, 14, RED2), (8, 34, OK)]
            for k, (top, hh, cc) in enumerate(data):
                cx = ix + 11 + k * 7.5
                b.append(f'<line x1="{cx+2:.1f}" y1="{iy+top-4}" x2="{cx+2:.1f}" y2="{iy+top+hh+3}" stroke="{cc}" stroke-width="1.2"/>')
                b.append(f'<rect x="{cx:.1f}" y="{iy+top}" width="4" height="{hh}" rx="1" fill="{cc}" class="cd" style="animation-delay:{k*0.2:.2f}s"/>')
        b.append(f'<text x="{x+22:.0f}" y="{y+108}" class="f" font-size="19" font-weight="700" fill="{INK}">{t(title)}</text>')
        for j, ln in enumerate(lines):
            b.append(f'<text x="{x+22:.0f}" y="{y+136+j*24}" class="f" font-size="15" fill="{MUTED}">{t(ln)}</text>')
        b.append("</g>")
    return svg(h, "\n".join(b), css)


# ---------------------------------------------------------------- telemetry
def telemetry(data):
    v = data["data"]["viewer"]
    cc = v["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    created = date.fromisoformat(v["createdAt"][:10])
    months = OrderedDict()
    y, m = created.year, created.month
    last = date.fromisoformat(days[-1]["date"])
    while (y, m) <= (last.year, last.month):
        months[(y, m)] = 0
        m += 1
        if m == 13:
            y, m = y + 1, 1
    for d in days:
        dd = date.fromisoformat(d["date"])
        if (dd.year, dd.month) in months:
            months[(dd.year, dd.month)] += d["contributionCount"]

    h = 250
    css = ".gb{transform-box:fill-box;transform-origin:bottom;animation:grow 1.2s cubic-bezier(.2,.7,.2,1) both}@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
    b = [card_bg(h), eyebrow(40, 56, "SEASON TELEMETRY  ·  GITHUB", f"ROOKIE SEASON · SINCE {created.strftime('%b %Y').upper()}")]
    tiles = [
        (str(cc["contributionCalendar"]["totalContributions"]), "CONTRIBUTIONS"),
        (str(v["pullRequests"]["totalCount"]), "PULL REQUESTS"),
        (str(cc["totalCommitContributions"]), "COMMITS"),
        (last.strftime("%d %b"), "LATEST LAP"),
    ]
    tw = 164
    for i, (num, label) in enumerate(tiles):
        x = 40 + i * (tw + 16)
        b.append(
            f'<g class="r" style="animation-delay:{0.1 + i*0.08:.2f}s">'
            f'<rect x="{x}" y="86" width="{tw}" height="124" rx="12" fill="{SURF2}" stroke="{BORDER}"/>'
            f'<text x="{x+20}" y="146" class="f" font-size="38" font-weight="800" letter-spacing="-1" fill="{INK}">{t(num)}</text>'
            f'<text x="{x+20}" y="176" class="m" font-size="12" letter-spacing="2" fill="{DIM}">{t(label)}</text>'
            "</g>"
        )
    px, pw = 40 + 4 * (tw + 16), W - 40 - (40 + 4 * (tw + 16))
    b.append(f'<rect x="{px}" y="86" width="{pw}" height="124" rx="12" fill="{SURF2}" stroke="{BORDER}"/>')
    b.append(f'<text x="{px+20}" y="110" class="m" font-size="12" letter-spacing="2" fill="{DIM}">PACE BY MONTH</text>')
    mx = max(months.values()) or 1
    n = len(months)
    slot = (pw - 40) / n
    bw = min(34, slot * 0.55)
    base = 186
    for i, ((yy, mm), val) in enumerate(months.items()):
        cx = px + 20 + slot * i + slot / 2
        bh = max(3, 58 * val / mx)
        b.append(f'<rect x="{cx-bw/2:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{RED2 if val == mx else BLUE}" fill-opacity="{1 if val else .35}" class="gb" style="animation-delay:{0.3 + i*0.1:.2f}s"/>')
        b.append(f'<text x="{cx:.1f}" y="{base+18}" text-anchor="middle" class="m" font-size="11" fill="{DIM}">{date(yy, mm, 1).strftime("%b").upper()}</text>')
    return svg(h, "\n".join(b), css)


# ---------------------------------------------------------------- footer
def footer():
    h = 130
    chk_defs, chk = checker_strip(0, h=24, sq=12)
    b = [card_bg(h, BG), chk]
    b.append(f'<text x="{W/2}" y="80" text-anchor="middle" class="f" font-size="24" font-weight="700" font-style="italic" fill="{INK}">Lights out and away we go.</text>')
    b.append(f'<text x="{W/2}" y="110" text-anchor="middle" class="m" font-size="12" letter-spacing="3" fill="{DIM}">H S BHARATH SURYA  ·  AI SYSTEMS ARCHITECT  ·  BENGALURU</text>')
    return svg(h, "\n".join(b), "", chk_defs)


# ---------------------------------------------------------------- buttons
LINKEDIN = "M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"
GITHUB = "M12 .3a12 12 0 0 0-3.8 23.38c.6.12.83-.26.83-.57L9 21.07c-3.34.72-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.08-.74.09-.73.09-.73 1.2.09 1.83 1.24 1.83 1.24 1.07 1.83 2.81 1.3 3.5 1 .1-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.14-.3-.54-1.52.1-3.18 0 0 1-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.28-1.55 3.29-1.23 3.29-1.23.64 1.66.24 2.88.12 3.18a4.65 4.65 0 0 1 1.23 3.22c0 4.61-2.8 5.63-5.48 5.92.42.36.81 1.1.81 2.22l-.01 3.29c0 .31.2.69.82.57A12 12 0 0 0 12 .3"


def button(label, sub, icon_path, color):
    bw, bh = 300, 64
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}" fill="none">'
        f"<style>{BASE_CSS}</style>"
        f'<rect x=".5" y=".5" width="{bw-1}" height="{bh-1}" rx="12" fill="{SURF}" stroke="{BORDER}"/>'
        f'<rect x="12" y="12" width="40" height="40" rx="10" fill="{color}" fill-opacity=".15"/>'
        f'<g transform="translate(22 22) scale(.83)"><path d="{icon_path}" fill="{color}"/></g>'
        f'<text x="66" y="29" class="f" font-size="16" font-weight="700" fill="{INK}">{t(label)}</text>'
        f'<text x="66" y="48" class="m" font-size="11" letter-spacing="1" fill="{DIM}">{t(sub)}</text>'
        f'<path d="M272 26l7 6-7 6" stroke="{MUTED}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>\n"
    )


def main():
    data = json.loads(Path(sys.argv[1]).read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "hero.svg": hero(),
        "about.svg": about(),
        "stack.svg": stack(),
        "ares-x.svg": ares(),
        "garage.svg": garage(),
        "telemetry.svg": telemetry(data),
        "footer.svg": footer(),
        "btn-linkedin.svg": button("LinkedIn", "H S BHARATH SURYA", LINKEDIN, "#3B8BEB"),
        "btn-github.svg": button("GitHub", "@SATANONSTEROIDS2024-ZZZ", GITHUB, INK),
    }
    for name, content in files.items():
        (OUT / name).write_text(content)
        print(f"{name:20s} {len(content):>7,d} bytes")


if __name__ == "__main__":
    main()
