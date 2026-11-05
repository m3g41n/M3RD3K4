"""Terminal control: alt screen, cursor, keyboard polling, guaranteed restore."""
import atexit
import os
import shutil
import sys

from core.renderer import ENTER_SEQ, LEAVE_SEQ


class Terminal:
    def __init__(self):
        self.active = False
        self._old_tty = None
        self._fd = None

    # -- lifecycle ---------------------------------------------------------
    def start(self):
        if self.active:
            return
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        if os.name == "nt":
            self._enable_windows_vt()
        else:
            try:
                import termios
                import tty
                if sys.stdin.isatty():
                    self._fd = sys.stdin.fileno()
                    self._old_tty = termios.tcgetattr(self._fd)
                    tty.setcbreak(self._fd)      # no echo; Ctrl+C still works
            except Exception:
                self._old_tty = None
        self.write(ENTER_SEQ)
        self.active = True
        atexit.register(self.stop)

    def stop(self):
        if not self.active:
            return
        self.active = False
        try:
            self.write(LEAVE_SEQ)
        except Exception:
            pass
        if self._old_tty is not None:
            try:
                import termios
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_tty)
            except Exception:
                pass

    @staticmethod
    def _enable_windows_vt():
        try:
            import ctypes
            k = ctypes.windll.kernel32
            handle = k.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if k.GetConsoleMode(handle, ctypes.byref(mode)):
                k.SetConsoleMode(handle, mode.value | 0x0004)   # VT processing
        except Exception:
            os.system("")      # classic trick that also enables VT on Win10+

    # -- io ----------------------------------------------------------------
    def write(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def size(self):
        c, r = shutil.get_terminal_size(fallback=(100, 30))
        return max(1, c - 1), r      # keep the last column free (no auto-wrap scroll)

    def poll_key(self):
        """Non-blocking. Returns 'q','esc','space','enter','right','left','other' or None."""
        try:
            if os.name == "nt":
                import msvcrt
                if not msvcrt.kbhit():
                    return None
                c = msvcrt.getwch()
                if c in ("\x00", "\xe0"):
                    c2 = msvcrt.getwch()
                    return {"M": "right", "K": "left"}.get(c2, "other")
                return self._norm(c)
            if self._old_tty is None:
                return None
            import select
            if not select.select([sys.stdin], [], [], 0)[0]:
                return None
            data = os.read(self._fd, 16).decode("utf-8", "ignore")
            if data == "\x1b":
                return "esc"
            if data.startswith("\x1b["):
                return {"C": "right", "D": "left"}.get(data[2:3], "other")
            return self._norm(data[:1]) if data else None
        except Exception:
            return None

    @staticmethod
    def _norm(c):
        if c in ("q", "Q"):
            return "q"
        if c == "\x1b":
            return "esc"
        if c == " ":
            return "space"
        if c in ("\r", "\n"):
            return "enter"
        return "other"
