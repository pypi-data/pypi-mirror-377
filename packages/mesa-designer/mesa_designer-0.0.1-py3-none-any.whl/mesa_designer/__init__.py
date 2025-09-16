import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "tmd/tmd_list.json", "r") as f:
    TMD_DATA: dict = dict(json.load(f))

with open(DATA_DIR / "aip/aip_list.json", "r") as f:
    AIP_DATA: dict = dict(json.load(f))

with open(DATA_DIR / "FRET/ICDs.json", "r") as f:
    FRET_ICDs: dict = dict(json.load(f))

with open(DATA_DIR / "intracellular/CTEV_list.json", "r") as f:
    CTEV_DATA: dict = dict(json.load(f))

with open(DATA_DIR / "intracellular/NTEV_list.json", "r") as f:
    NTEV_DATA: dict = dict(json.load(f))

with open(DATA_DIR / "intracellular/TEVp_list.json", "r") as f:
    TEVP_DATA: dict = dict(json.load(f))

with open(DATA_DIR / "prs/prs_list.json", "r") as f:
    PRS_DATA: dict = dict(json.load(f))

with open(DATA_DIR / "signal_seqs/signal_sequences.json", "r") as f:
    SIGNAL_SEQS: dict = dict(json.load(f))

with open(DATA_DIR / "tags/tag_sequences.json", "r") as f:
    TAG_SEQS: dict = dict(json.load(f))