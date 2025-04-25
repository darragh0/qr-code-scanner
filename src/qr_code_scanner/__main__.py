import os
import platform
import subprocess as sp
import sys
import webbrowser
from pathlib import Path
from subprocess import CalledProcessError

from PIL import ImageGrab
from pyzbar.pyzbar import decode


def perr(msg: str, ext_code: int = 0) -> None:
    print(f"\033[1;91merror:\033[0m {msg}")
    sys.exit(ext_code)


def is_wsl() -> bool:
    return "microsoft" in platform.uname().release.lower() or os.environ.get("WSL_DISTRO_NAME", None) is not None


def take_nt_ss() -> None:
    img = ImageGrab.grab()
    qr_codes = decode(img)

    if qr_codes:
        qr_data = {qr.data.decode() for qr in qr_codes}
        if len(qr_data) == 1:
            webbrowser.open(qr_data.pop())
        else:
            print("\033[1;32mLinks:\033[0m")
            for n, link in enumerate(qr_data, 1):
                print(f"  \033[1m[{n}] \033[0;36m{link}\033[0m")
    else:
        perr("no QR codes found", 0)


def get_bin(cmd: str) -> Path:
    try:
        return Path(run_cmd("which", cmd))
    except CalledProcessError:
        perr(f"no `{cmd}` found on system", 2)


def run_cmd(*argv: str, capture: bool = True) -> str | None:
    if capture:
        return sp.run([*argv], capture_output=capture, text=True, check=True).stdout.strip()  # noqa: S603
    sp.run([*argv], check=True)  # noqa: S603
    return None


def take_wsl_ss() -> None:
    wslpath_bin = get_bin("wslpath")
    cmd_exe_bin = get_bin("cmd.exe")

    this_path_wsl = Path(__file__).absolute()
    script_path_win = run_cmd(wslpath_bin, "-w", this_path_wsl)

    py_path_win: str
    try:
        py_path_win = run_cmd(cmd_exe_bin, "/c", "where", "python").lower().split("\n")[0]
    except CalledProcessError:
        perr("no python executable found on Windows system", 3)

    win_root = run_cmd(wslpath_bin, "-u", "C:\\")

    os.chdir(win_root)
    py_path_wsl = run_cmd(wslpath_bin, "-u", py_path_win)

    run_cmd(py_path_wsl, script_path_win, capture=False)


def main() -> None:
    if os.name == "nt":
        take_nt_ss()
    elif is_wsl():
        take_wsl_ss()
    elif os.name == "posix":
        perr("could not take screenshot", 1)

    sys.exit(0)


if __name__ == "__main__":
    main()
