#!/usr/bin/env python3
"""SE-02 PRM -> single-patch SYX generator (Roland DT1 x4).

This generator uses a template .syx (4 DT1 messages) and overwrites the merged
payload bytes that we can map confidently from your dataset (54/60 params).
Unmapped params remain as in the template.

Usage:
  python3 se02_prm_to_syx.py --prm SE02_PATCH60.PRM --template TEMPLATE.syx --out OUT.syx --slot-display 60
  python3 se02_prm_to_syx.py --prm SE02_PATCH60.PRM --template TEMPLATE.syx --out OUT.syx --slot-bb 59
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

_PARAM_RE = re.compile(r'^([A-Za-z0-9_]+)\((-?\d+)\);')

def read_prm(path: Path) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = _PARAM_RE.match(line.strip())
        if m:
            d[m.group(1)] = int(m.group(2))
    return d

def split_sysex(blob: bytes) -> List[bytes]:
    msgs: List[bytes] = []
    i, n = 0, len(blob)
    while i < n:
        if blob[i] != 0xF0:
            j = blob.find(b"\xF0", i)
            if j == -1:
                break
            i = j
        j = blob.find(b"\xF7", i)
        if j == -1:
            break
        msgs.append(blob[i:j+1])
        i = j + 1
    return msgs

def roland_checksum_7bit(addr4: bytes, data: bytes) -> int:
    s = (sum(addr4) + sum(data)) & 0x7F
    return (-s) & 0x7F

def recalc_checksum(msg: bytes) -> bytes:
    b = bytearray(msg)
    addr4 = bytes(b[8:12])
    data = bytes(b[12:-2])
    b[-2] = roland_checksum_7bit(addr4, data)
    return bytes(b)

def parse_dt1(msg: bytes) -> Tuple[bytes, bytearray]:
    if not (len(msg) >= 15 and msg[0] == 0xF0 and msg[1] == 0x41 and msg[6] == 0x44 and msg[7] == 0x12 and msg[-1] == 0xF7):
        raise ValueError("Not a Roland/SE-02 DT1 SysEx")
    addr4 = msg[8:12]
    data = bytearray(msg[12:-2])
    return addr4, data

def merge_nibbles(data: bytes) -> bytes:
    if len(data) % 2 != 0:
        raise ValueError("Odd nibble length in DT1 data")
    return bytes(((data[i] & 0x0F) << 4) | (data[i+1] & 0x0F) for i in range(0, len(data), 2))

def split_to_nibbles(merged: bytes) -> bytes:
    out = bytearray()
    for v in merged:
        out.append((v >> 4) & 0x0F)
        out.append(v & 0x0F)
    return bytes(out)

BLOCK_MERGED_LENS = [32, 32, 32, 24]  # total 120 bytes

RESOLVED_PARAM_TO_PAYLOAD_INDEX: Dict[str, int] = {
    "COM_AFT_SENS1": 2,
    "COM_AFT_SENS2": 3,
    "COM_BENDRANGE": 0,
    "COM_DYNAMICS": 4,
    "COM_MOD_SENS": 1,
    "COM_TRNS_SW": 19,
    "COM_VOLUME": 5,
    "CTRL_GLIDE": 20,
    "CTRL_GLIDE_TYPE": 21,
    "CTRL_WHL": 22,
    "DLY_AMOUNT": 87,
    "DLY_REGEN": 86,
    "DLY_TIME": 85,
    "FLT_ATTACK1": 56,
    "FLT_ATTACK2": 57,
    "FLT_CONTOUR": 65,
    "FLT_CUTOFF": 55,
    "FLT_DECAY1": 59,
    "FLT_DECAY2": 60,
    "FLT_EMPHASIS": 58,
    "FLT_GATE": 69,
    "FLT_KEY13": 61,
    "FLT_KEY23": 62,
    "FLT_MTRIG": 66,
    "FLT_NORM": 67,
    "FLT_REL": 68,
    "FLT_SUSTAIN1": 63,
    "FLT_SUSTAIN2": 64,
    "LFO_FILTER": 78,
    "LFO_FLT": 80,
    "LFO_MODE": 81,
    "LFO_RATE": 75,
    "LFO_SYNC": 82,
    "LFO_WAVE": 77,
    "MIX_FEEDBACK": 48,
    "MIX_NOISE": 49,
    "MIX_OSC1": 45,
    "MIX_OSC2": 46,
    "MIX_OSC3": 47,
    "OSC_ENV1": 35,
    "OSC_FINE1": 29,
    "OSC_FINE2": 30,
    "OSC_KYBD": 36,
    "OSC_RANGE1": 25,
    "OSC_RANGE2": 26,
    "OSC_RANGE3": 27,
    "OSC_SYNC": 34,
    "OSC_WAVEFORM1": 31,
    "OSC_WAVEFORM2": 32,
    "OSC_WAVEFORM3": 33,
    "OSC_XMOD": 37,
    "XMOD_O2FLT": 40,
    "XMOD_O3PW": 42,
    "XMOD_O3TO": 41,
}

def apply_mapping(prm: Dict[str, int], merged_payload: bytearray) -> None:
    for name, pidx in RESOLVED_PARAM_TO_PAYLOAD_INDEX.items():
        if name not in prm:
            continue
        merged_payload[pidx] = int(prm[name]) & 0xFF

def generate(prm_path: Path, template_syx_path: Path, out_path: Path,
             slot_bb: Optional[int] = None, slot_display: Optional[int] = None) -> None:
    prm = read_prm(prm_path)

    msgs = split_sysex(template_syx_path.read_bytes())
    if len(msgs) != 4:
        raise ValueError(f"Template must contain 4 SysEx messages; found {len(msgs)}")

    addrs: List[bytearray] = []
    datas: List[bytearray] = []
    merged_parts: List[bytes] = []

    for m in msgs:
        addr4, data = parse_dt1(m)
        addrs.append(bytearray(addr4))
        datas.append(data)
        merged_parts.append(merge_nibbles(bytes(data)))

    merged_payload = bytearray(b"".join(merged_parts))
    if len(merged_payload) != sum(BLOCK_MERGED_LENS):
        raise ValueError("Unexpected merged payload length")

    apply_mapping(prm, merged_payload)

    if slot_bb is None and slot_display is not None:
        slot_bb = int(slot_display) - 1

    if slot_bb is not None:
        bb = int(slot_bb) & 0x7F
        for a in addrs:
            a[1] = bb

    off = 0
    for bi, blen in enumerate(BLOCK_MERGED_LENS):
        block_merged = bytes(merged_payload[off:off+blen])
        off += blen
        nibs = split_to_nibbles(block_merged)
        if len(nibs) != len(datas[bi]):
            raise ValueError(f"Block {bi} size mismatch: expected {len(datas[bi])}, got {len(nibs)}")
        datas[bi][:] = nibs

    out_msgs: List[bytes] = []
    for m, a, d in zip(msgs, addrs, datas):
        b = bytearray(m)
        b[8:12] = bytes(a)
        b[12:-2] = bytes(d)
        out_msgs.append(recalc_checksum(bytes(b)))

    out_path.write_bytes(b"".join(out_msgs))

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prm", required=True, type=Path)
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--slot-bb", type=int, default=None)
    g.add_argument("--slot-display", type=int, default=None)
    args = ap.parse_args()
    generate(args.prm, args.template, args.out, slot_bb=args.slot_bb, slot_display=args.slot_display)
    print(f"Wrote: {args.out}")

if __name__ == "__main__":
    main()
