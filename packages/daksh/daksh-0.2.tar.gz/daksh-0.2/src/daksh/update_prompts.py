import shutil, json, os
from datetime import datetime
from pathlib import Path as P
from .__pre_init__ import cli


def current_file_dir(file: str) -> str:
    return P(file).parent.resolve()


def ls(folder: P) -> list[P]:
    return [f for f in folder.iterdir() if not f.name.startswith(".")]


def Info(msg: str):
    print(f"[INFO] {msg}")


def read_json(file: P) -> dict:
    with open(file, "r") as f:
        return json.load(f)


def write_json(file: P, data: dict):
    if not file.parent.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def read_lines(file: P) -> list[str]:
    with open(file, "r") as f:
        return f.readlines()


def append_lines(file: P, lines: list[str]):
    if not file.parent.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
    if not file.exists():
        with open(file, "w") as f:
            pass
    with open(file, "a") as f:
        f.writelines(lines)


@cli.command()
def update_prompts(dry_run: bool = False):

    def copy(src_fldr: P, dst_fldr: P):
        for f in ls(src_fldr):
            to = dst_fldr / f.name
            Info(f"Updating {f} to {to}")

            if dry_run:
                continue

            if f.is_file():
                shutil.copy(f, to)
            elif f.is_dir():
                shutil.copytree(f, to, dirs_exist_ok=True)

    cwd = current_file_dir(__file__)
    copy(cwd / "assets/daksh-prompts", P(".daksh"))

    if P(".vscode/settings.json").exists():
        settings = read_json(P(".vscode/settings.json"))
    else:
        settings = {}

    chat_mode_files_locations = settings.get("chat.modeFilesLocations", {})
    chat_mode_files_locations[".daksh/prompts"] = True
    settings["chat.modeFilesLocations"] = chat_mode_files_locations
    write_json(P(".vscode/settings.json"), settings)

    if os.path.exists(".github/copilot-instructions.md"):
        if (
            input(
                "Found an existing .github/copilot-instructions.md should we back it up? [y/n]: "
            ).lower()
            != "y"
        ):
            Info("Skipping backup")
        else:
            bkp = f".github/copilot-instructions.md.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            Info(f"Backing up existing .github/copilot-instructions.md to {bkp}")
            shutil.copy(".github/copilot-instructions.md", bkp)
    if not os.path.exists(".github"):
        os.makedirs(".github")
    shutil.copy(
        cwd / "assets/copilot-instructions.md", ".github/copilot-instructions.md"
    )
    shutil.copy(cwd / "assets/mkdocs.yml", "mkdocs.yml")
    append_lines(P("makefile"), read_lines(cwd / "assets/makefile"))
    os.makedirs("docs/overrides", exist_ok=True)
    shutil.copy(cwd / "assets/extra.css", "docs/overrides/extra.css")
    shutil.copytree(cwd / "assets/overrides", "./overrides", dirs_exist_ok=True)
    if not os.path.exists("docs/index.md"):
        shutil.copy(cwd / "assets/index.md", "docs/index.md")
