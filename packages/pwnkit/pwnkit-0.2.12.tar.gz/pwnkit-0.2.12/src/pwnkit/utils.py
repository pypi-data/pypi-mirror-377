from __future__ import annotations
import inspect
import binascii
from pwn import success  
from typing import Literal, Optional, Tuple, Sequence, Union
from urllib.parse import quote, quote_plus, unquote, urlencode
import logging, sys, os

__all__ = [
        "leak", "pa",
        "itoa", "i2a", "bytex", "hex2b", "b2hex", "url_qs",
        "init_pr",
        "logger", "pr_debug", "pr_info", "pr_warn", "pr_error", "pr_critical", "pr_exception",
        "parse_argv",
        ]

# Data Transformers
# ------------------------------------------------------------------------
def itoa(a: int) -> bytes:
    return str(a).encode()

i2a = itoa

def bytex(x) -> bytes:
    if isinstance(x, bytes): return x
    if isinstance(x, bytearray): return bytes(x)
    if isinstance(x, memoryview): return x.tobytes()
    if isinstance(x, str): return x.encode()
    if isinstance(x, int): return str(x).encode()  # like itoa()
    raise TypeError(f"cannot bytes(): {type(x)}")

def hex2b(s: Union[str, bytes]) -> bytes:
    if isinstance(s, (bytes, bytearray)): s = s.decode()
    s = s.strip().lower()
    if s.startswith('0x'): s = s[2:]
    s = re.sub(r'[^0-9a-f]', '', s)  # drop spaces/colons
    if len(s) % 2: s = '0' + s
    try: return binascii.unhexlify(s)
    except binascii.Error as e: raise ValueError(f"bad hex: {e}")

def b2hex(b: Union[bytes, bytearray, memoryview]) -> str:
    """
    b2hex(b"aaa") # '0x616161'
    """
    hexstr = "0x" + binascii.hexlify(ensure_bytes(b)).decode()
    return hexstr

def url_qs(params, *, rfc3986=True, doseq=True):
    """
    dict / list[tuples] -> query string.
    rfc3986=True: spaces -> %20 ; False: spaces -> '+'

    e.g.,
    url_qs({"q": "a b", "tag": ["x/y", "z"]})   # "q=a%20b&tag=x%2Fy&tag=z"
    """
    qv = quote if rfc3986 else quote_plus
    return urlencode(params, doseq=doseq, quote_via=qv, safe="-._~")

# Leak (print) memory addresses
# ------------------------------------------------------------------------
def leak(addr: int) -> None:
    """
    Pretty-print a leaked address with variable name if possible.

    Example:
        buf = 0xdeadbeef
        leak(buf)  # prints "Leak buf addr: 0xdeadbeef"
    """
    frame = inspect.currentframe().f_back
    desc = "unknown"
    try:
        # Try to find which local variable equals this address
        variables = {k: v for k, v in frame.f_locals.items() if isinstance(v, int) and v == addr}
        if variables:
            desc = next(iter(variables.keys()))
    except Exception:
        pass

    c_desc = f"\033[1;31m{desc:<16}\033[0m"     # red
    c_addr = f"\033[1;33m{addr:#x}\033[0m"      # yellow
    success(f"Leak {c_desc:<16} addr: {c_addr}")

pa = leak

# Logging
# ------------------------------------------------------------------------
class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG':    "\033[32m",     # Green
        'INFO':     "\033[94m",     # blue
        'WARNING':  "\033[33m",     # Yellow
        'ERROR':    "\033[31m",     # Red
        'CRITICAL': "\033[1;33;41m" # Bold yellow text red bg
    }
    RESET = "\033[0m"

    def format(self, record):
        orig = record.levelname
        try:
            color = self.COLORS.get(orig, self.RESET)
            record.levelname = f"{color}{orig}{self.RESET}"
            return super().format(record)
        finally:
            record.levelname = orig

logger = logging.getLogger("pwnkit")

def init_pr(
    level: Literal["debug","info","warning","error","critical"] = "info",
    fmt: str = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt: str = "%H:%M:%S",
) -> None:
    """
    Initialize logging for the 'pwnkit' namespace.

    - Configures only the 'pwnkit' logger (not root), so pwntools' own logging
      remains intact.
    - Installs a single StreamHandler with colored output.
    - Allows switching level at runtime: "debug", "info", etc.
    """
    lvl = getattr(logging, level.upper(), logging.INFO)

    logger.propagate = False    # avoids duplicate messages
    logger.setLevel(lvl)
    logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]

    h = logging.StreamHandler()
    h.setFormatter(ColorFormatter(fmt=fmt, datefmt=datefmt))
    h.setLevel(lvl)  # optional
    logger.addHandler(h)

    plog = logging.getLogger("pwnlib")  # Align pwntools' logging level
    if lvl <= logging.DEBUG:
        plog.setLevel(logging.DEBUG)
    plog.propagate = False

def pr_debug(msg):
    logger.debug(msg)

def pr_info(msg):
    logger.info(msg)

def pr_warn(msg):
    logger.warning(msg)

def pr_error(msg):
    logger.error(msg)

def pr_critical(msg):
    logger.critical(msg)

def pr_exception(msg):
    logger.exception(msg)

# Usage
# ------------------------------------------------------------------------
def _usage(argv: Sequence[str]) -> Tuple[None, None]:
    prog = sys.argv[0] if sys.argv else "xpl.py"
    print(f"Usage: {prog} [IP PORT] | [IP:PORT]\n"
          f"Examples:\n"
          f"  {prog}\n"
          f"  {prog} 10.10.10.10 31337\n"
          f"  {prog} 10.10.10.10:31337\n")
    sys.exit(1)

# Parse argv (ip, host)
# ------------------------------------------------------------------------
def parse_argv(argv: Sequence[str],
                default_host: Optional[str] = None,
                default_port: Optional[int] = None
                ) -> Tuple[Optional[str], Optional[int]]:
    """
    Accepts:
      []
      [IP PORT]
      [IP:PORT]
    Returns (host, port) where either may be None (local mode).
    """
    host, port = default_host, default_port
    if len(argv) == 0:
        return host, port

    if len(argv) == 1 and ":" in argv[0]:
        h, p = argv[0].split(":", 1)
        if not h or not p.isdigit():
            return _usage(argv)
        return h, int(p)

    if len(argv) == 2:
        h, p = argv[0], argv[1]
        if not p.isdigit():
            return _usage(argv)
        return h, int(p)

    return _usage(argv)

# Helpers
# ------------------------------------------------------------------------
def _colorize():
    if sys.stdout.isatty() and not os.environ.get("NO_COLOR"):
        return {
            "bold": "\033[1m",
            "grn":  "\033[32m",
            "cya":  "\033[36m",
            "clr":  "\033[0m",
        }
    return dict.fromkeys(["bold", "grn", "cya", "clr"], "")
