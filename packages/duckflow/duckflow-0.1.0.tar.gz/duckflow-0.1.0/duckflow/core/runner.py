import sys
import argparse
import logging
from dotenv import load_dotenv
from .settings import load_settings
from .flock import load_ducks, load_flock_defs, run_flock

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("duckflow")

DEFAULT_DUCKS_DIR = "ducks"
DEFAULT_FLOCK_FILE = "flock.json"


def main():
    parser = argparse.ArgumentParser(description="Run DuckFlow flock(s)")
    parser.add_argument("flock", help="Flock name to run")
    parser.add_argument("text", nargs="?", help="Input text")
    parser.add_argument("--file", help="Path to input file", default=None)
    parser.add_argument(
        "--ducks-dir",
        default=DEFAULT_DUCKS_DIR,
        help="Path to ducks directory (default: ./ducks)"
    )
    parser.add_argument(
        "--flock-file",
        default=DEFAULT_FLOCK_FILE,
        help="Path to flock definition file (default: ./flock.json)"
    )
    parser.add_argument(
        "--log-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override the logging level"
    )
    args = parser.parse_args()

    settings = load_settings() or {}
    defaults = settings.get("defaults", {})

    log_level = args.log_level or settings.get("logging", {}).get("level", "INFO")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if args.text:
        input_text = args.text
    elif args.file:
        with open(args.file) as f:
            input_text = f.read().strip()
    else:
        input_text = sys.stdin.read().strip()

    if not input_text:
        logger.error("No input text provided (via argument, file, or stdin)")
        sys.exit(1)

    try:
        duck_map = load_ducks(args.ducks_dir, defaults)
        flocks = load_flock_defs(args.flock_file)
        results = {}
        final_output = run_flock(flocks, args.flock, duck_map, results, input_text)
        logger.info(f"Final flock result: {final_output}")
    except Exception:
        logger.exception("Flock execution failed")
        sys.exit(1)
