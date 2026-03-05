#!/usr/bin/env python3
"""
SE-02 PRM (text) -> SysEx (SYX) converter.

- Uses a template .syx (single patch) containing 4 Roland DT1 messages.
- Applies parameter values to merged payload bytes using a mapping JSON.
- Unmapped parameters remain as-is from the template (template-dependent).
- Recalculates Roland checksum for each DT1 message.
"""

from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Dict, List, Tuple

PARAM_RE = re.compile(r"^([A-Za-z0-9_]+)\((-?\d+)\);")

def read_prm_text(path: Path) -> Dict[str,int]:
    d: Dict[str,int] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = PARAM_RE.match(line.strip())
        if m:
            d[m.group(1)] = int(m.group(2))
    return d

def split_sysex(blob: bytes) -> List[bytes]:
    msgs: List[bytes] = []
    i = 0
    while True:
        i = blob.find(b"\xF0", i)
        if i < 0:
            break
        j = blob.find(b"\xF7", i)
        if j < 0:
            break
        msgs.append(blob[i:j+1])
        i = j + 1
    return msgs

def merge_nibbles(nibbles: bytes) -> bytes:
    if len(nibbles) % 2:
        raise ValueError("Odd nibble length")
    return bytes(((nibbles[i] & 0x0F) << 4) | (nibbles[i+1] & 0x0F) for i in range(0, len(nibbles), 2))

def split_to_nibbles(merged: bytes) -> bytes:
    out = bytearray()
    for v in merged:
        out.append((v >> 4) & 0x0F)
        out.append(v & 0x0F)
    return bytes(out)

def roland_checksum_7bit(addr4: bytes, data: bytes) -> int:
    # Roland DT1 checksum: checksum = (128 - (sum(addr+data) % 128)) % 128
    s = (sum(addr4) + sum(data)) & 0x7F
    return (-s) & 0x7F

def recalc_checksum(msg: bytes) -> bytes:
    b = bytearray(msg)
    addr4 = bytes(b[8:12])
    data = bytes(b[12:-2])
    b[-2] = roland_checksum_7bit(addr4, data)
    return bytes(b)

def parse_dt1(msg: bytes) -> Tuple[bytearray, bytearray]:
    addr4 = bytearray(msg[8:12])
    data = bytearray(msg[12:-2])  # nibble stream
    return addr4, data

def build_payload_from_msgs(msgs: List[bytes]) -> Tuple[List[bytearray], List[bytearray], bytearray]:
    addrs: List[bytearray] = []
    datas: List[bytearray] = []
    merged_parts: List[bytes] = []
    for m in msgs:
        a, d = parse_dt1(m)
        addrs.append(a)
        datas.append(d)
        merged_parts.append(merge_nibbles(bytes(d)))
    merged_payload = bytearray(b"".join(merged_parts))  # 120 bytes
    if len(merged_payload) != 120:
        raise ValueError(f"Unexpected merged payload length: {len(merged_payload)}")
    return addrs, datas, merged_payload

def write_payload_back(datas: List[bytearray], merged_payload: bytes) -> None:
    # merged payload blocks: 32,32,32,24
    blens = [32, 32, 32, 24]
    off = 0
    for i, blen in enumerate(blens):
        block = merged_payload[off:off+blen]
        off += blen
        datas[i][:] = split_to_nibbles(block)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prm", required=True, help="Input PRM text file (ORM-style)")
    ap.add_argument("--template", required=True, help="Template SYX (single patch, 4 DT1 messages)")
    ap.add_argument("--out", required=True, help="Output SYX path")
    ap.add_argument("--mapping", default="se02_prm_to_syx_mapping_resolved_1_128.json",
                    help="Mapping JSON path")
    ap.add_argument("--slot-display", type=int, default=None,
                    help="Optional display slot number 1-128; will be converted to base-0 for DT1 address byte[1].")
    args = ap.parse_args()

    prm = read_prm_text(Path(args.prm))
    mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    resolved: Dict[str,int] = mapping["resolved_param_to_payload_index"]

    tmpl_blob = Path(args.template).read_bytes()
    msgs = split_sysex(tmpl_blob)
    if len(msgs) != 4:
        raise SystemExit(f"Template must contain 4 DT1 messages; found {len(msgs)}")

    addrs, datas, merged_payload = build_payload_from_msgs(msgs)

    # Apply mapped params
    for name, idx in resolved.items():
        if name in prm:
            merged_payload[int(idx)] = int(prm[name]) & 0xFF

    # Slot address patching
    if args.slot_display is not None:
        if not (1 <= args.slot_display <= 128):
            raise SystemExit("--slot-display must be 1..128")
        slot0 = args.slot_display - 1
        for a in addrs:
            a[1] = slot0

    # Write payload back and rebuild messages
    write_payload_back(datas, bytes(merged_payload))
    out_msgs: List[bytes] = []
    for m, a, d in zip(msgs, addrs, datas):
        b = bytearray(m)
        b[8:12] = bytes(a)
        b[12:-2] = bytes(d)
        out_msgs.append(recalc_checksum(bytes(b)))

    Path(args.out).write_bytes(b"".join(out_msgs))
    print(f"Wrote: {args.out}")

if __name__ == "__main__":
    main()
