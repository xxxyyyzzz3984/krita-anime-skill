"""Render high-detail anime demos through a running Krita MCP Bridge.

All artwork is authored as deterministic Bezier/vector geometry, rendered by
Krita's embedded Qt SVG engine, and written into layered Krita paint documents.
No image-generation model or external bitmap asset is used.
"""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from krita_client import KritaClient
from krita_client.config import ClientConfig

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "demos"
WIDTH = 1600
HEIGHT = 1000


def svg_document(body: str, defs: str = "") -> str:
    document = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}"><defs>{defs}</defs>{body}</svg>'
    )
    ET.fromstring(document)  # noqa: S314 - validates our bounded, local SVG before sending it to Krita
    return document


COMMON_DEFS = """
<linearGradient id="night" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#101827"/><stop offset="0.55" stop-color="#26364a"/>
  <stop offset="1" stop-color="#496073"/>
</linearGradient>
<linearGradient id="platform" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#34495a"/><stop offset="1" stop-color="#111a25"/>
</linearGradient>
<linearGradient id="coat" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffd858"/><stop offset="0.55" stop-color="#f1b832"/>
  <stop offset="1" stop-color="#d89025"/>
</linearGradient>
<radialGradient id="lamp" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#fffbd2" stop-opacity=".9"/><stop offset="1" stop-color="#ffe47a" stop-opacity="0"/>
</radialGradient>
<pattern id="tone" width="10" height="10" patternUnits="userSpaceOnUse">
  <circle cx="2" cy="2" r="1.45" fill="#20232a"/>
</pattern>
<pattern id="fineTone" width="7" height="7" patternUnits="userSpaceOnUse">
  <circle cx="1.5" cy="1.5" r=".9" fill="#3b3b3b"/>
</pattern>
"""


def mika_character(
    x: float,
    y: float,
    scale: float,
    *,
    outfit: str = "raincoat",
    pose: str = "calm",
    expression: str = "focused",
    monochrome: bool = False,
) -> str:
    """Return the locked Mika design as detailed, reusable SVG geometry."""
    ink = "#20242c"
    skin = "#f5c8aa" if not monochrome else "#fffdf8"
    skin_shadow = "#dd927e" if not monochrome else "#d9d9d9"
    hair = "#c84f51" if not monochrome else "#f7f7f4"
    hair_shadow = "#7f3342" if not monochrome else "#b8b8b8"
    hair_light = "#f28b72" if not monochrome else "#ffffff"
    eye = "#d98c31" if not monochrome else "#3d3d3d"
    clip = "#ffd85b" if not monochrome else "#ffffff"
    if outfit == "uniform":
        cloth, cloth_shadow, accent = "#314f72", "#20354e", "#cf5260"
    elif outfit == "winter":
        cloth, cloth_shadow, accent = "#7ca5b8", "#4d778d", "#f4eee4"
    else:
        cloth, cloth_shadow, accent = ("#f1be39", "#c78428", "#fff1b3") if not monochrome else (
            "#f7f7f4",
            "#bdbdbd",
            "#ffffff",
        )
    mouth = {
        "smile": "M204 247 Q224 261 244 245",
        "surprised": "M215 246 Q224 238 233 247 Q224 259 215 246",
    }.get(expression, "M209 249 Q224 256 239 247")
    brow_left = "M154 181 Q178 167 199 178" if expression != "worried" else "M154 178 Q178 169 199 184"
    brow_right = "M249 177 Q272 166 295 179" if expression != "worried" else "M249 183 Q272 170 295 177"
    if pose == "run":
        left_arm = "M112 405 C55 430 24 488 5 548 L53 570 C82 524 111 493 150 472"
        right_arm = "M331 405 C389 359 423 311 451 257 L490 290 C467 363 423 432 359 477"
        hand_detail = f"""
        <path d="M448 263 C460 239 468 216 478 198 C485 185 497 190 492 207 L484 235
                 C496 216 507 220 500 239 L489 266 C481 284 472 294 461 299 Z"
              fill="{skin}" stroke="{ink}" stroke-width="6"/>
        <path d="M476 238 Q488 248 489 266 M466 227 Q478 238 481 252" fill="none" stroke="{skin_shadow}" stroke-width="3"/>
        """
        body_transform = "rotate(-4 225 420)"
    elif pose == "reach":
        left_arm = "M111 410 C66 442 42 499 31 556 L80 567 C96 518 119 486 153 470"
        right_arm = "M333 411 C386 372 421 320 452 265 L492 297 C466 371 423 437 359 477"
        hand_detail = f"""
        <path d="M449 270 C463 245 471 220 482 202 C490 190 501 197 496 213 L488 240
                 C501 222 510 228 503 247 L491 274 C483 291 474 302 463 305 Z"
              fill="{skin}" stroke="{ink}" stroke-width="6"/>
        <path d="M480 242 Q491 253 491 274 M470 231 Q481 241 484 257" fill="none" stroke="{skin_shadow}" stroke-width="3"/>
        """
        body_transform = "rotate(2 225 420)"
    else:
        left_arm = "M112 409 C79 454 69 516 77 586 L126 583 C126 522 139 486 159 459"
        right_arm = "M334 409 C368 453 380 515 373 586 L324 583 C324 523 311 486 291 459"
        hand_detail = ""
        body_transform = ""
    return f"""
<g transform="translate({x:g} {y:g}) scale({scale:g})" stroke-linecap="round" stroke-linejoin="round">
  <g transform="{body_transform}">
    <path d="{left_arm}" fill="{cloth}" stroke="{ink}" stroke-width="7"/>
    <path d="{right_arm}" fill="{cloth}" stroke="{ink}" stroke-width="7"/>
    {hand_detail}
    <path d="M76 598 C82 472 115 390 165 368 C193 355 255 355 284 369 C337 395 366 477 374 612 Z"
          fill="{cloth}" stroke="{ink}" stroke-width="8"/>
    <path d="M85 565 C113 532 136 510 164 496 M365 565 C338 531 314 511 288 496"
          fill="none" stroke="{cloth_shadow}" stroke-width="13" opacity=".8"/>
    <path d="M173 331 L169 390 Q224 426 280 389 L275 329 Z" fill="{skin}" stroke="{ink}" stroke-width="7"/>
    <path d="M174 346 Q224 382 275 345 L276 372 Q224 405 170 370 Z" fill="{skin_shadow}" opacity=".42"/>
    <path d="M115 137 C109 52 170 8 230 12 C317 9 358 74 342 166 L325 289
             C318 325 302 351 278 381 L258 349 L225 394 L194 349 L167 382
             C143 351 126 326 118 289 Z"
          fill="{hair_shadow}" stroke="{ink}" stroke-width="8"/>
    <path d="M132 160 C132 91 171 55 225 52 C287 49 323 92 318 166 L307 252
             C299 302 269 335 224 350 C178 338 146 306 136 253 Z"
          fill="{skin}" stroke="{ink}" stroke-width="7"/>
    <path d="M136 252 C145 300 179 334 223 339 C267 336 296 302 307 252
             C289 284 263 295 224 297 C184 295 154 283 136 252 Z" fill="{skin_shadow}" opacity=".2"/>
    <path d="M111 155 C101 69 159 22 226 24 C302 19 351 68 340 164
             C321 115 299 91 264 78 C219 61 167 82 134 139 Z"
          fill="{hair}" stroke="{ink}" stroke-width="8"/>
    <path d="M128 132 C143 74 197 51 246 61 C210 74 188 107 181 166
             C165 144 149 134 128 132 Z" fill="{hair_light}" opacity=".62"/>
    <path d="M170 71 C137 94 124 139 132 201 C146 177 163 158 184 143
             C194 128 203 103 207 74 Z" fill="{hair}" stroke="{ink}" stroke-width="6"/>
    <path d="M207 65 C190 105 194 148 210 184 C229 155 239 116 239 68 Z"
          fill="{hair}" stroke="{ink}" stroke-width="6"/>
    <path d="M239 66 C237 112 252 148 276 174 C284 138 280 104 268 75 Z"
          fill="{hair}" stroke="{ink}" stroke-width="6"/>
    <path d="M270 73 C285 109 303 139 324 157 C318 108 299 82 270 73 Z"
          fill="{hair}" stroke="{ink}" stroke-width="6"/>
    <path d="M121 177 C91 211 102 292 137 321 L148 250 L146 174 Z"
          fill="{hair}" stroke="{ink}" stroke-width="7"/>
    <path d="M319 164 L306 252 L307 322 C349 288 356 215 319 164 Z"
          fill="{hair}" stroke="{ink}" stroke-width="7"/>
    <path d="M122 283 Q101 263 105 233 Q110 211 131 224" fill="{skin}" stroke="{ink}" stroke-width="6"/>
    <path d="M321 222 Q343 211 348 234 Q351 264 325 283" fill="{skin}" stroke="{ink}" stroke-width="6"/>
    <path d="{brow_left}" fill="none" stroke="{hair_shadow}" stroke-width="6"/>
    <path d="{brow_right}" fill="none" stroke="{hair_shadow}" stroke-width="6"/>
    <path d="M151 203 Q177 183 203 202 Q181 228 153 207 Z" fill="#fffdf8" stroke="{ink}" stroke-width="6"/>
    <ellipse cx="179" cy="205" rx="13" ry="18" fill="{eye}" stroke="{ink}" stroke-width="4"/>
    <ellipse cx="180" cy="208" rx="6" ry="10" fill="#332621"/>
    <circle cx="174" cy="199" r="4.5" fill="white"/><circle cx="184" cy="211" r="2.5" fill="white"/>
    <path d="M247 202 Q273 182 299 203 Q275 228 249 207 Z" fill="#fffdf8" stroke="{ink}" stroke-width="6"/>
    <ellipse cx="273" cy="205" rx="13" ry="18" fill="{eye}" stroke="{ink}" stroke-width="4"/>
    <ellipse cx="272" cy="208" rx="6" ry="10" fill="#332621"/>
    <circle cx="267" cy="198" r="4.5" fill="white"/><circle cx="277" cy="211" r="2.5" fill="white"/>
    <path d="M147 197 Q174 174 204 196 M246 196 Q276 174 303 198" fill="none" stroke="{ink}" stroke-width="4"/>
    <path d="M224 207 Q217 228 221 235 Q226 239 233 235" fill="none" stroke="{skin_shadow}" stroke-width="4"/>
    <path d="{mouth}" fill="none" stroke="#a44550" stroke-width="5"/>
    <path d="M143 242 Q162 252 182 244 M267 244 Q288 253 307 242" fill="none" stroke="#e68e91" stroke-width="6" opacity=".5"/>
    <path d="M290 96 L324 108 L304 134 L272 118 Z" fill="{clip}" stroke="{ink}" stroke-width="5"/>
    <path d="M132 139 C151 87 189 65 229 61 M315 139 C298 95 272 73 238 65"
          fill="none" stroke="{hair_light}" stroke-width="8" opacity=".55"/>
    <path d="M116 177 Q132 239 122 301 M334 175 Q319 235 326 300 M153 113 Q141 170 146 226
             M300 105 Q315 167 306 222" fill="none" stroke="{hair_light}" stroke-width="3" opacity=".55"/>
    <path d="M171 392 L224 438 L278 391" fill="{accent}" stroke="{ink}" stroke-width="7"/>
    <path d="M171 392 L148 451 L207 430 L224 438 L243 430 L301 451 L278 391"
          fill="none" stroke="{ink}" stroke-width="7"/>
    <path d="M224 438 L224 590" fill="none" stroke="{cloth_shadow}" stroke-width="8"/>
    <path d="M151 470 Q171 514 165 570 M298 470 Q278 514 286 570"
          fill="none" stroke="{cloth_shadow}" stroke-width="6" opacity=".8"/>
    <path d="M104 538 Q121 551 137 550 M313 550 Q330 552 347 538" fill="none" stroke="{ink}" stroke-width="6"/>
    <circle cx="224" cy="482" r="6" fill="{ink}"/><circle cx="224" cy="526" r="6" fill="{ink}"/>
  </g>
</g>"""


def main_illustration_layers() -> list[tuple[str, str]]:
    atmosphere = svg_document(
        """
<rect width="1600" height="1000" fill="url(#night)"/>
<circle cx="1260" cy="160" r="260" fill="url(#lamp)"/><circle cx="280" cy="300" r="190" fill="url(#lamp)" opacity=".28"/>
<path d="M0 690 L1600 610 L1600 1000 L0 1000 Z" fill="url(#platform)"/>
<path d="M0 780 L1600 675" stroke="#97a8b1" stroke-width="6" opacity=".7"/>
<path d="M0 840 L1600 720" stroke="#f2c847" stroke-width="13" opacity=".8"/>
<path d="M0 863 L1600 743" stroke="#111823" stroke-width="5" opacity=".8"/>
""",
        COMMON_DEFS,
    )
    architecture = svg_document(
        """
<g fill="none" stroke-linejoin="round">
  <path d="M0 0 L470 310 L1600 188" stroke="#7690a2" stroke-width="9" opacity=".45"/>
  <path d="M210 0 L520 300 M550 0 L580 292 M900 0 L660 285 M1260 0 L740 278 M1600 20 L820 270"
        stroke="#41576a" stroke-width="10"/>
  <path d="M0 114 L1600 62 M0 210 L1600 126" stroke="#2a3b4d" stroke-width="16"/>
</g>
<g transform="translate(70 205) skewY(-4)">
  <rect x="0" y="0" width="560" height="305" rx="8" fill="#263847" stroke="#8ca4ae" stroke-width="8"/>
  <rect x="28" y="28" width="145" height="215" fill="#8eb6c5" stroke="#162433" stroke-width="8"/>
  <rect x="190" y="28" width="145" height="215" fill="#7198a9" stroke="#162433" stroke-width="8"/>
  <rect x="352" y="28" width="178" height="215" fill="#9abcc5" stroke="#162433" stroke-width="8"/>
  <path d="M44 224 L140 76 M206 226 L309 65 M371 226 L493 59" stroke="#dce8e7" stroke-width="5" opacity=".45"/>
  <rect x="184" y="259" width="165" height="21" rx="10" fill="#dc5d57"/>
</g>
<g transform="translate(1120 170)">
  <rect width="350" height="116" rx="8" fill="#f5d65b" stroke="#172331" stroke-width="9"/>
  <path d="M38 58 H300 M255 31 L304 58 L255 85" fill="none" stroke="#172331" stroke-width="13"/>
</g>
<g stroke="#1a2836" stroke-width="15"><path d="M1025 80 L1010 690"/><path d="M1450 45 L1410 646"/></g>
<g fill="#f8f4d4"><rect x="977" y="118" width="91" height="28" rx="8"/><rect x="1360" y="94" width="138" height="30" rx="8"/></g>
<g stroke="#8ca6b0" stroke-width="3" opacity=".45">
  <path d="M30 975 L824 558 M280 1000 L850 555 M640 1000 L880 550 M1510 1000 L935 544"/>
</g>
""",
        COMMON_DEFS,
    )
    character = svg_document(
        mika_character(555, 75, 1.42, outfit="raincoat", pose="run", expression="focused"), COMMON_DEFS
    )
    lighting = svg_document(
        """
<path d="M0 680 C380 655 810 660 1600 580" fill="none" stroke="#d7f5ff" stroke-width="4" opacity=".22"/>
<g stroke="#d7eff5" stroke-linecap="round">
  <path d="M80 70 l-70 150 M190 30 l-58 128 M320 108 l-55 130 M450 26 l-78 173 M590 80 l-47 111
           M720 17 l-70 167 M850 70 l-69 154 M1000 20 l-63 143 M1150 80 l-73 168 M1320 17 l-60 151 M1510 70 l-78 177"
        stroke-width="6" opacity=".52"/>
  <path d="M40 320 l-42 98 M245 360 l-52 120 M420 300 l-39 90 M980 350 l-55 132 M1210 330 l-44 104 M1480 300 l-62 143"
        stroke-width="3" opacity=".72"/>
</g>
<g fill="none" stroke="#b7e4ef" opacity=".5">
  <ellipse cx="235" cy="867" rx="178" ry="19" stroke-width="5"/><ellipse cx="1090" cy="790" rx="122" ry="13" stroke-width="4"/>
  <path d="M77 907 Q235 872 395 905 M980 822 Q1090 797 1205 821" stroke-width="3"/>
</g>
<path d="M1100 720 C1240 690 1400 650 1600 640" stroke="#f6cd58" stroke-width="18" opacity=".22"/>
<path d="M615 878 Q824 845 1035 861" stroke="#fff3c2" stroke-width="8" opacity=".36"/>
""",
        COMMON_DEFS,
    )
    return [
        ("01 Atmosphere / color script", atmosphere),
        ("02 Station / perspective", architecture),
        ("03 Mika / cel + lineart", character),
        ("04 Rain / rim light", lighting),
    ]


def consistency_layers() -> list[tuple[str, str]]:
    paper = svg_document(
        """
<rect width="1600" height="1000" fill="#f4f1ea"/>
<path d="M0 96 H1600" stroke="#252d37" stroke-width="7"/>
<text x="55" y="66" font-family="sans-serif" font-size="28" font-weight="700" fill="#252d37">MIKA / IDENTITY-LOCKED CHARACTER SHEET</text>
<text x="1520" y="65" text-anchor="end" font-family="sans-serif" font-size="18" fill="#68737c">MODEL 01</text>
"""
    )
    panels = svg_document(
        """
<g fill="#fffdfa" stroke="#26323c" stroke-width="5">
  <rect x="42" y="132" width="480" height="700"/><rect x="560" y="132" width="480" height="700"/><rect x="1078" y="132" width="480" height="700"/>
</g>
<g stroke="#9ca7ad" stroke-width="2" stroke-dasharray="8 8" opacity=".65">
  <path d="M282 150 V812 M800 150 V812 M1318 150 V812"/>
  <path d="M55 334 H510 M573 334 H1028 M1091 334 H1546"/>
</g>
<g font-family="sans-serif" font-weight="700" fill="#26323c">
  <text x="67" y="174" font-size="20">A / SCHOOL UNIFORM</text><text x="585" y="174" font-size="20">B / WINTER LAYER</text>
  <text x="1103" y="174" font-size="20">C / RAIN ACTION</text>
</g>
<g fill="#26323c" font-family="sans-serif" font-size="15">
  <text x="67" y="807">NEUTRAL / 3-4 VIEW</text><text x="585" y="807">REACH / SOFT SMILE</text><text x="1103" y="807">RUN / FOCUSED</text>
</g>
"""
    )
    characters = svg_document(
        mika_character(92, 172, 0.89, outfit="uniform", pose="calm", expression="focused")
        + mika_character(610, 172, 0.89, outfit="winter", pose="reach", expression="smile")
        + mika_character(1128, 172, 0.89, outfit="raincoat", pose="run", expression="focused"),
        COMMON_DEFS,
    )
    notes = svg_document(
        """
<g fill="none" stroke="#cf5660" stroke-width="3">
  <path d="M1405 226 L1498 190"/><path d="M1238 347 L1128 304"/><path d="M708 340 L600 300"/>
</g>
<g fill="#fffdfa" stroke="#cf5660" stroke-width="3">
  <circle cx="1510" cy="185" r="20"/><circle cx="1115" cy="299" r="20"/><circle cx="587" cy="295" r="20"/>
</g>
<g fill="#cf5660" font-family="sans-serif" font-size="14" font-weight="700" text-anchor="middle">
  <text x="1510" y="190">01</text><text x="1115" y="304">02</text><text x="587" y="300">03</text>
</g>
<g transform="translate(55 875)">
  <text x="0" y="-14" font-family="sans-serif" font-size="16" font-weight="700" fill="#26323c">LOCKED PALETTE</text>
  <rect x="0" y="0" width="88" height="55" fill="#c84f51"/><rect x="88" y="0" width="88" height="55" fill="#7f3342"/>
  <rect x="176" y="0" width="88" height="55" fill="#f5c8aa"/><rect x="264" y="0" width="88" height="55" fill="#d98c31"/>
  <rect x="352" y="0" width="88" height="55" fill="#ffd85b"/><rect x="440" y="0" width="88" height="55" fill="#20242c"/>
</g>
<g transform="translate(720 866)" fill="#26323c" font-family="sans-serif">
  <text font-size="17" font-weight="700">CONSISTENCY KEYS</text>
  <text y="31" font-size="15">01 diamond clip · 02 double-highlight iris · 03 four-lock fringe</text>
  <text y="58" font-size="15">soft V jaw · coral bob · costume and gesture may change; silhouette anchors do not</text>
</g>
"""
    )
    return [
        ("01 Sheet / paper", paper),
        ("02 Guides / labels", panels),
        ("03 Mika / three variants", characters),
        ("04 Anchors / palette", notes),
    ]


def storyboard_layers() -> list[tuple[str, str]]:
    clip_defs = COMMON_DEFS + """
<clipPath id="p1"><rect x="45" y="80" width="355" height="830"/></clipPath>
<clipPath id="p2"><rect x="430" y="80" width="355" height="830"/></clipPath>
<clipPath id="p3"><rect x="815" y="80" width="355" height="830"/></clipPath>
<clipPath id="p4"><rect x="1200" y="80" width="355" height="830"/></clipPath>
"""
    paper = svg_document(
        """
<rect width="1600" height="1000" fill="#dedbd4"/>
<rect x="22" y="24" width="1556" height="940" fill="#fffef9" stroke="#202329" stroke-width="5"/>
<text x="48" y="61" font-family="sans-serif" font-size="18" font-weight="700" fill="#202329">SEQUENCE 07 / THE LAST PAPER CRANE</text>
"""
    )
    tones = svg_document(
        """
<g clip-path="url(#p1)"><rect x="45" y="80" width="355" height="830" fill="#f9f9f6"/>
  <path d="M45 80 H400 V470 Q250 420 45 525 Z" fill="url(#fineTone)" opacity=".72"/>
  <path d="M45 720 L400 590 V910 H45 Z" fill="url(#tone)" opacity=".42"/></g>
<g clip-path="url(#p2)"><rect x="430" y="80" width="355" height="830" fill="#fffef9"/>
  <path d="M430 80 H785 V400 Q610 330 430 410 Z" fill="url(#fineTone)" opacity=".32"/>
  <path d="M430 650 Q620 570 785 650 V910 H430 Z" fill="url(#tone)" opacity=".3"/></g>
<g clip-path="url(#p3)"><rect x="815" y="80" width="355" height="830" fill="#fffef9"/>
  <path d="M815 80 H1170 V910 H815 Z" fill="url(#fineTone)" opacity=".22"/>
  <path d="M815 740 L1170 570 V910 H815 Z" fill="url(#tone)" opacity=".46"/></g>
<g clip-path="url(#p4)"><rect x="1200" y="80" width="355" height="830" fill="#fffef9"/>
  <circle cx="1378" cy="455" r="225" fill="url(#fineTone)" opacity=".3"/>
  <rect x="1200" y="730" width="355" height="180" fill="url(#tone)" opacity=".32"/></g>
""",
        clip_defs,
    )
    inks = svg_document(
        """
<g clip-path="url(#p1)" stroke="#202329" stroke-linejoin="round">
  <path d="M20 568 L430 408 M20 640 L430 489 M20 742 L430 590" fill="none" stroke-width="7"/>
  <path d="M92 80 L148 525 M318 80 L283 475" fill="none" stroke-width="12"/>
  <rect x="78" y="205" width="236" height="160" fill="#fffef9" stroke-width="7"/>
  <path d="M98 336 L290 230 M157 365 L307 280" fill="none" stroke-width="4"/>
</g>
"""
        + mika_character(96, 405, 0.62, outfit="raincoat", pose="calm", expression="worried", monochrome=True)
        + f'<g clip-path="url(#p2)">{mika_character(374, 95, 1.02, outfit="raincoat", expression="surprised", monochrome=True)}</g>'
        + f'<g clip-path="url(#p3)">{mika_character(786, 280, 0.79, outfit="raincoat", pose="run", expression="focused", monochrome=True)}</g>'
        + f'<g clip-path="url(#p4)">{mika_character(1144, 315, 0.72, outfit="raincoat", pose="calm", expression="smile", monochrome=True)}</g>'
        + """
<g clip-path="url(#p4)" fill="none" stroke="#202329" stroke-linejoin="round">
  <path d="M1200 742 H1555 M1250 742 L1230 910 M1510 742 L1535 910" stroke-width="10"/>
  <path d="M1430 705 l45 -31 l40 34 l-45 18 z M1475 674 l8 -38 l32 72" fill="#fffef9" stroke-width="5"/>
</g>
""",
        clip_defs,
    )
    effects = svg_document(
        """
<g fill="#fffef9" stroke="#202329" stroke-width="5">
  <path d="M78 116 Q180 72 315 121 Q338 187 290 230 Q195 246 101 211 Q64 175 78 116 Z"/>
  <path d="M476 112 Q590 77 712 121 Q746 168 711 217 Q604 244 497 214 Q458 174 476 112 Z"/>
  <path d="M1235 116 Q1355 78 1498 119 Q1537 175 1494 227 Q1369 250 1251 216 Q1212 174 1235 116 Z"/>
</g>
<g fill="#202329" font-family="sans-serif" font-size="19" font-weight="700">
  <text x="104" y="150">THE TRAIN IS ALREADY HERE.</text><text x="504" y="150">THE CRANE...</text>
  <text x="1262" y="151">YOU KEPT YOUR PROMISE.</text>
</g>
<g clip-path="url(#p3)" fill="none" stroke="#202329" stroke-linecap="round">
  <path d="M790 202 L948 446 M804 151 L982 422 M855 118 L1010 402 M1166 105 L1048 405 M1172 210 L1078 430"
        stroke-width="6"/>
  <path d="M849 770 Q968 708 1120 704" stroke-width="10"/>
</g>
<text x="843" y="285" font-family="sans-serif" font-size="47" font-weight="900" fill="#202329" transform="rotate(-12 843 285)">RUN</text>
<g fill="#202329"><circle cx="104" cy="280" r="4"/><circle cx="130" cy="265" r="3"/><circle cx="150" cy="254" r="2"/></g>
<g fill="none" stroke="#202329" stroke-width="6">
  <rect x="45" y="80" width="355" height="830"/><rect x="430" y="80" width="355" height="830"/>
  <rect x="815" y="80" width="355" height="830"/><rect x="1200" y="80" width="355" height="830"/>
</g>
<g fill="#202329" font-family="sans-serif" font-size="15" font-weight="700">
  <text x="55" y="940">01 / ESTABLISHING</text><text x="440" y="940">02 / EXTREME CLOSE-UP</text>
  <text x="825" y="940">03 / TRACKING ACTION</text><text x="1210" y="940">04 / QUIET RESOLUTION</text>
</g>
""",
        clip_defs,
    )
    return [
        ("01 Manga paper", paper),
        ("02 Screen tones", tones),
        ("03 Character + environment inks", inks),
        ("04 Balloons + speed lines", effects),
    ]


def render_document(client: KritaClient, name: str, stem: str, layers: list[tuple[str, str]]) -> None:
    client.call("new_canvas", {"width": WIDTH, "height": HEIGHT, "name": name, "background": "#ffffff"})
    for layer_name, layer_svg in layers:
        result = client.render_svg_paint_layer(name=layer_name, svg=layer_svg)
        if result.get("status") != "ok":
            message = f"Krita SVG layer render failed: {result}"
            raise RuntimeError(message)
    client.call("save", {"path": str((OUTPUT / f"{stem}.kra").resolve())})
    client.call("save", {"path": str((OUTPUT / f"{stem}.png").resolve())})
    print(f"Rendered {name} with {len(layers)} detailed layers")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    config = ClientConfig(default_timeout=120.0, export_timeout=120.0, max_batch_size=50)
    with KritaClient(config) as client:
        client.health()
        render_document(client, "Rain Platform Key Visual", "fine-lineart-scene", main_illustration_layers())
        render_document(client, "Mika Character Consistency", "character-consistency-sheet", consistency_layers())
        render_document(client, "The Last Paper Crane", "four-panel-storyboard", storyboard_layers())


if __name__ == "__main__":
    main()
