import shutil, json
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


@cli.command()
def update_prompts(dry_run: bool = False):

    def copy(src_fldr: P, dst_fldr: P):
        for f in ls(src_fldr):
            to = dst_fldr / f.name
            Info(f"Updating {f} to {to}")

            if dry_run:
                continue

            if f.is_file():
                f.cp(to)
            elif f.is_dir():
                shutil.copytree(f, to, dirs_exist_ok=True)

    copy(current_file_dir(__file__) / "../../.daksh", P(".daksh"))

    if P(".vscode/settings.json").exists():
        settings = read_json(P(".vscode/settings.json"))
    else:
        settings = {}

    chat_mode_files_locations = settings.get("chat.modeFilesLocations", {})
    chat_mode_files_locations[".daksh/prompts"] = True
    settings["chat.modeFilesLocations"] = chat_mode_files_locations
    write_json(P(".vscode/settings.json"), settings)
