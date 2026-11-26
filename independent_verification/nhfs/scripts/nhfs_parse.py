"""Parse NHFS PUF fixed-width file using the @col INPUT layout in nhfspuf.sas."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import re
RAW = SURVEY_DATA_ROOT + "/nhfs-2009/raw/"

def lower_priority():
    try:
        import psutil, os
        psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass

def layout():
    sas = open(RAW + "nhfspuf.sas", encoding="latin-1").read()
    block = sas[sas.index("INPUT\n"):]
    block = block[:block.index(";")]
    out = []
    for m in re.finditer(r"@(\d+)\s+(\w+)\s+(\$?)(\d+)\.(\d*)", block):
        out.append((m.group(2), int(m.group(1)) - 1, int(m.group(4)), m.group(3) == "$", m.group(5)))
    return out

def read():
    lay = layout()
    recs = []
    with open(RAW + "nhfspuf.dat", encoding="latin-1") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            r = {}
            for name, start, w, ischar, dec in lay:
                s = line[start:start + w].strip()
                if ischar:
                    r[name] = s if s else None
                else:
                    if s in ("", "."):
                        r[name] = None
                    elif name == "FLUWT":
                        r[name] = float(s) if "." in s else float(s) / 10 ** int(dec or 0)
                    else:
                        r[name] = int(s)
            recs.append(r)
    return lay, recs
