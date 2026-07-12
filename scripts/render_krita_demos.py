"""Render the README demos through a running Krita MCP Bridge."""

from __future__ import annotations

from pathlib import Path

from krita_client import KritaClient
from krita_client.config import ClientConfig

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "demos"
INK = "#172331"
SKIN = "#F3BF9B"
HAIR = "#E8664C"
YELLOW = "#F1BD39"
CORAL = "#D9554E"
BLUE = "#294F70"


def command(action: str, **params: object) -> dict[str, object]:
    return {"action": action, "params": params}


class Scene:
    def __init__(self, width: int, height: int, name: str, background: str) -> None:
        self.width = width
        self.height = height
        self.commands: list[dict[str, object]] = [
            command("new_canvas", width=width, height=height, name=name, background=background)
        ]
        self._color = ""

    def layer(self, name: str) -> None:
        self.commands.append(command("create_layer", name=name, layer_type="paintlayer"))
        self.commands.append(command("select_layer", name=name))

    def color(self, value: str) -> None:
        if value != self._color:
            self.commands.append(command("set_color", color=value))
            self._color = value

    def rectangle(self, x: int, y: int, width: int, height: int, color: str) -> None:
        self.color(color)
        self.commands.append(
            command("draw_shape", shape="rectangle", x=x, y=y, width=width, height=height, fill=True, stroke=False)
        )

    def ellipse(self, x: int, y: int, width: int, height: int, color: str) -> None:
        self.color(color)
        self.commands.append(
            command("draw_shape", shape="ellipse", x=x, y=y, width=width, height=height, fill=True, stroke=False)
        )

    def line(self, x1: int, y1: int, x2: int, y2: int, color: str, width: int = 3) -> None:
        self.color(color)
        self.commands.append(
            command(
                "draw_shape",
                shape="line",
                x=x1,
                y=y1,
                width=abs(x2 - x1),
                height=abs(y2 - y1),
                fill=True,
                stroke=False,
                x2=x2,
                y2=y2,
                line_width=width,
            )
        )

    def outlined_rectangle(self, x: int, y: int, width: int, height: int, fill: str, border: int = 4) -> None:
        self.rectangle(x, y, width, height, INK)
        self.rectangle(x + border, y + border, width - border * 2, height - border * 2, fill)

    def outlined_ellipse(self, x: int, y: int, width: int, height: int, fill: str, border: int = 4) -> None:
        self.ellipse(x, y, width, height, INK)
        self.ellipse(x + border, y + border, width - border * 2, height - border * 2, fill)

    def outlined_line(self, x1: int, y1: int, x2: int, y2: int, fill: str, width: int) -> None:
        self.line(x1, y1, x2, y2, INK, width + 5)
        self.line(x1, y1, x2, y2, fill, width)

    def save(self, stem: str) -> None:
        self.commands.append(command("save", path=str((OUTPUT / f"{stem}.kra").resolve())))
        self.commands.append(command("save", path=str((OUTPUT / f"{stem}.png").resolve())))


def face(scene: Scene, center_x: int, top: int, scale: float) -> None:
    def value(number: int) -> int:
        return round(number * scale)

    scene.outlined_ellipse(center_x - value(62), top + value(24), value(124), value(145), HAIR, value(4))
    scene.outlined_ellipse(center_x - value(51), top + value(50), value(102), value(120), SKIN, value(4))
    scene.outlined_line(center_x - value(42), top + value(82), center_x - value(8), top + value(48), HAIR, value(14))
    scene.outlined_line(center_x - value(8), top + value(48), center_x + value(18), top + value(86), HAIR, value(14))
    scene.outlined_line(center_x + value(18), top + value(86), center_x + value(43), top + value(57), HAIR, value(14))
    scene.ellipse(center_x - value(30), top + value(100), value(13), value(17), "#FFFDF4")
    scene.ellipse(center_x + value(17), top + value(100), value(13), value(17), "#FFFDF4")
    scene.ellipse(center_x - value(26), top + value(104), value(6), value(9), INK)
    scene.ellipse(center_x + value(21), top + value(104), value(6), value(9), INK)
    scene.line(center_x - value(10), top + value(144), center_x + value(10), top + value(144), "#B74751", value(3))
    scene.outlined_rectangle(center_x + value(34), top + value(42), value(20), value(15), "#FFD15D", value(2))


def full_character(scene: Scene, center_x: int, top: int, scale: float, outfit: str, pose: str) -> None:
    def value(number: int) -> int:
        return round(number * scale)

    outfit_color = {"raincoat": YELLOW, "uniform": "#506F91", "winter": "#80A3B5"}[outfit]
    scene.outlined_rectangle(center_x - value(58), top + value(190), value(116), value(142), outfit_color, value(5))
    if pose == "run":
        scene.outlined_line(
            center_x - value(48), top + value(215), center_x - value(112), top + value(280), outfit_color, value(20)
        )
        scene.outlined_line(
            center_x + value(48), top + value(215), center_x + value(107), top + value(155), outfit_color, value(20)
        )
        scene.outlined_line(
            center_x - value(35), top + value(330), center_x - value(92), top + value(440), BLUE, value(25)
        )
        scene.outlined_line(
            center_x + value(35), top + value(330), center_x + value(105), top + value(422), BLUE, value(25)
        )
    elif pose == "reach":
        scene.outlined_line(
            center_x - value(48), top + value(215), center_x - value(78), top + value(292), outfit_color, value(20)
        )
        scene.outlined_line(
            center_x + value(48), top + value(215), center_x + value(112), top + value(135), outfit_color, value(20)
        )
        scene.outlined_line(
            center_x - value(35), top + value(330), center_x - value(42), top + value(435), BLUE, value(25)
        )
        scene.outlined_line(
            center_x + value(35), top + value(330), center_x + value(50), top + value(435), BLUE, value(25)
        )
    else:
        scene.outlined_line(
            center_x - value(48), top + value(215), center_x - value(75), top + value(290), outfit_color, value(20)
        )
        scene.outlined_line(
            center_x + value(48), top + value(215), center_x + value(75), top + value(290), outfit_color, value(20)
        )
        scene.outlined_line(
            center_x - value(35), top + value(330), center_x - value(42), top + value(435), BLUE, value(25)
        )
        scene.outlined_line(
            center_x + value(35), top + value(330), center_x + value(42), top + value(435), BLUE, value(25)
        )
    face(scene, center_x, top, scale)
    if outfit == "uniform":
        scene.outlined_line(center_x - value(34), top + value(205), center_x, top + value(245), "#F5EFE2", value(10))
        scene.outlined_line(center_x + value(34), top + value(205), center_x, top + value(245), "#F5EFE2", value(10))
        scene.outlined_line(center_x, top + value(238), center_x, top + value(300), CORAL, value(8))
    elif outfit == "winter":
        scene.outlined_line(
            center_x - value(35), top + value(205), center_x + value(35), top + value(205), "#F5EFE2", value(12)
        )
    else:
        scene.outlined_line(center_x, top + value(215), center_x, top + value(315), "#F7E8BD", value(8))


def fine_scene() -> Scene:
    scene = Scene(1200, 800, "Fine Lineart Scene", "#101D2E")
    scene.layer("Station / Perspective")
    for x in range(-160, 1280, 130):
        scene.line(x, 90, x + 420, 660, "#29445D", 2)
    scene.line(0, 650, 1200, 650, "#6CA4B8", 4)
    scene.line(80, 800, 535, 470, "#F7CF66", 6)
    scene.line(470, 800, 580, 470, "#F7CF66", 6)
    scene.line(1080, 800, 630, 470, "#F7CF66", 6)
    scene.outlined_rectangle(790, 145, 300, 78, CORAL, 5)
    scene.layer("Hero / Stabilized Lineart")
    full_character(scene, 570, 135, 1.12, "raincoat", "run")
    scene.layer("Rain / Motion")
    for y in (280, 330, 380, 430):
        scene.line(780, y, 1110, y - 20, "#EEF4F3", 2)
    scene.save("fine-lineart-scene")
    return scene


def consistency_scene() -> Scene:
    scene = Scene(1200, 800, "Character Consistency Sheet", "#F5EFE2")
    scene.layer("Reference Panels")
    scene.outlined_rectangle(35, 125, 330, 575, "#E7F0F6", 5)
    scene.outlined_rectangle(435, 125, 330, 575, "#DCE8F0", 5)
    scene.outlined_rectangle(835, 125, 330, 575, "#F6D4B0", 5)
    scene.layer("Mika / Identity Locked")
    full_character(scene, 200, 180, 0.82, "uniform", "stand")
    full_character(scene, 600, 180, 0.82, "winter", "reach")
    full_character(scene, 1000, 180, 0.82, "raincoat", "run")
    scene.layer("Palette Anchors")
    for index, color in enumerate((SKIN, HAIR, INK, "#FFD15D")):
        scene.outlined_rectangle(45 + index * 58, 735, 38, 38, color, 2)
    scene.save("character-consistency-sheet")
    return scene


def crane(scene: Scene, center_x: int, center_y: int, scale: float) -> None:
    width = round(42 * scale)
    scene.outlined_line(center_x - width, center_y, center_x, center_y - round(28 * scale), "#FFFDF4", round(5 * scale))
    scene.outlined_line(center_x, center_y - round(28 * scale), center_x + width, center_y, "#FFFDF4", round(5 * scale))
    scene.outlined_line(
        center_x - width,
        center_y,
        center_x + round(10 * scale),
        center_y + round(25 * scale),
        "#FFFDF4",
        round(5 * scale),
    )
    scene.outlined_line(
        center_x + width,
        center_y,
        center_x + round(10 * scale),
        center_y + round(25 * scale),
        "#FFFDF4",
        round(5 * scale),
    )


def storyboard_scene() -> Scene:
    scene = Scene(1400, 800, "Four Panel Storyboard", "#E8DFCF")
    scene.layer("Storyboard Panels")
    for index in range(4):
        scene.outlined_rectangle(35 + index * 340, 92, 310, 560, "#F7F1E6", 5)
    scene.layer("Character + Crane Poses")
    full_character(scene, 155, 260, 0.48, "raincoat", "stand")
    crane(scene, 290, 220, 0.55)
    face(scene, 530, 180, 0.82)
    crane(scene, 650, 190, 0.48)
    full_character(scene, 850, 235, 0.55, "raincoat", "run")
    crane(scene, 985, 190, 0.42)
    full_character(scene, 1150, 290, 0.42, "raincoat", "stand")
    scene.line(1090, 520, 1355, 520, INK, 8)
    crane(scene, 1300, 465, 0.52)
    scene.layer("Vector-style Motion Notes")
    scene.outlined_line(790, 450, 1010, 290, CORAL, 5)
    scene.save("four-panel-storyboard")
    return scene


def execute(scene: Scene, client: KritaClient) -> None:
    pending: list[dict[str, object]] = []

    def flush() -> None:
        if not pending:
            return
        chunk = list(pending)
        pending.clear()
        result = client.batch(chunk, stop_on_error=True)
        if result.get("status") != "ok":
            message = f"Krita demo batch failed: {result}"
            raise RuntimeError(message)

    barriers = {"new_canvas", "create_layer", "select_layer", "save"}
    for item in scene.commands:
        if item["action"] in barriers:
            flush()
            client.call(str(item["action"]), dict(item["params"]))
            continue
        pending.append(item)
        if len(pending) == 45:
            flush()
    flush()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    config = ClientConfig(default_timeout=120.0, export_timeout=120.0, max_batch_size=50)
    with KritaClient(config) as client:
        client.health()
        for scene in (fine_scene(), consistency_scene(), storyboard_scene()):
            execute(scene, client)
            print(f"Rendered {scene.commands[0]['params']['name']}")


if __name__ == "__main__":
    main()
