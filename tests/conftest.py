import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for sub in ("tools", "tools/texture", "tools/refmatch", "tools/godot"):
    sys.path.insert(0, str(ROOT / sub))
