"""Compatibility forwarding only; scripts.record_input owns the parser."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.record_input import MAX_RECORD_BYTES, read_record
