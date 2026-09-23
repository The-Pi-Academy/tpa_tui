from __future__ import annotations

from dataclasses import dataclass, field


ORG = "The-Pi-Academy"
WORKSPACE_NAME = "thepiacademy"
THEME_ORANGE = "#d17914"
THEME_DARK = "#1f1408"
THEME_CREAM = "#fff8ed"


@dataclass(frozen=True)
class Repository:
    name: str
    url: str
    kind: str
    description: str
    requirements: tuple[str, ...] = ()
    apt_packages: tuple[str, ...] = ()
    setup_commands: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    heavy: bool = False


REPOSITORIES: tuple[Repository, ...] = (
    Repository(
        "simple-website",
        "https://github.com/The-Pi-Academy/simple-website.git",
        "HTML",
        "Beginner static website project.",
    ),
    Repository(
        "pizza-delivery-game",
        "https://github.com/The-Pi-Academy/pizza-delivery-game.git",
        "Python/Pygame",
        "Platform game teaching loops, events, movement, and collision.",
        requirements=("game/requirements.txt",),
        apt_packages=("python3-venv", "python3-pip"),
    ),
    Repository(
        "sort-algo-visualizer",
        "https://github.com/The-Pi-Academy/sort-algo-visualizer.git",
        "C++/Rust",
        "Sorting algorithm visualization with SDL2, Macroquad, and audio.",
        apt_packages=(
            "build-essential",
            "cmake",
            "pkg-config",
            "libsdl2-dev",
            "libsdl2-mixer-dev",
            "libsdl2-ttf-dev",
            "libasound2-dev",
        ),
        setup_commands=(("cargo", "fetch"),),
        heavy=True,
    ),
    Repository(
        "database-dashboard",
        "https://github.com/The-Pi-Academy/database-dashboard.git",
        "Java/Maven",
        "SQL learning API and dashboard.",
        apt_packages=("openjdk-17-jdk", "maven"),
        setup_commands=(("mvn", "-q", "dependency:go-offline"),),
    ),
    Repository(
        "digital-kiosk",
        "https://github.com/The-Pi-Academy/digital-kiosk.git",
        "Python/Tkinter",
        "Full-screen Raspberry Pi welcome kiosk.",
        apt_packages=("python3-tk",),
    ),
    Repository(
        "turtle-race",
        "https://github.com/The-Pi-Academy/turtle-race.git",
        "Python/Turtle",
        "Python turtle race lessons and exercises.",
        apt_packages=("python3-tk",),
    ),
    Repository(
        "SenseHAT-dice",
        "https://github.com/The-Pi-Academy/SenseHAT-dice.git",
        "Python/Sense HAT",
        "Shake-to-roll Sense HAT dice project.",
        apt_packages=("sense-hat",),
    ),
    Repository(
        "gpio-led-api",
        "https://github.com/The-Pi-Academy/gpio-led-api.git",
        "Python/Flask/GPIO",
        "Flask API for controlling a Raspberry Pi LED.",
        requirements=("app/requirements.txt",),
        apt_packages=("python3-venv", "python3-pip", "python3-rpi.gpio"),
    ),
    Repository(
        "gpio-buttons",
        "https://github.com/The-Pi-Academy/gpio-buttons.git",
        "Python/GPIO",
        "GPIO button and LED exercises.",
        apt_packages=("python3-rpi.gpio",),
    ),
    Repository(
        "less-simple-website",
        "https://github.com/The-Pi-Academy/less-simple-website.git",
        "HTML/CSS/JS",
        "Intermediate static website project.",
    ),
)

OPTIONAL_REPOSITORIES: tuple[Repository, ...] = (
    Repository(
        "object_detection_demo",
        "https://github.com/The-Pi-Academy/object_detection_demo.git",
        "Python/YOLO",
        "Optional Raspberry Pi 5 object detection station.",
        requirements=("requirements.txt",),
        apt_packages=("python3-venv", "python3-pip", "python3-opencv"),
        heavy=True,
    ),
)

ALL_REPOSITORIES: tuple[Repository, ...] = REPOSITORIES + OPTIONAL_REPOSITORIES


BASE_APT_PACKAGES: tuple[str, ...] = (
    "ca-certificates",
    "curl",
    "gpg",
    "git",
    "python3",
    "python3-pip",
    "python3-venv",
)

EDITOR_APT_PACKAGES: tuple[str, ...] = (
    "code",
    "thonny",
    "geany",
    "mousepad",
    "nano",
)
