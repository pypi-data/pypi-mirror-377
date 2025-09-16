#!/usr/bin/env python3
"""
Run Sundew on an ECG CSV and export metrics + energy report.

Examples

PowerShell:
  py -3.13 -m benchmarks.run_ecg `
    --csv "data\\MIT-BIH Arrhythmia Database.csv" `
    --preset tuned_v2 --limit 50000 `
    --overrides "target_activation_rate=0.12,gate_temperature=0.07" `
    --save "results\\ecg_run.json"

Bash:
  python -m benchmarks.run_ecg \
    --csv "data/MIT-BIH Arrhythmia Database.csv" \
    --preset tuned_v2 --limit 50000 \
    --overrides "target_activation_rate=0.12,gate_temperature=0.07" \
    --save results/ecg_run.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

from sundew import SundewAlgorithm
from sundew.config_presets import get_preset

# ---------------------- Streaming stats & EMA ----------------------


class RunningStats:
    """Welford’s algorithm for running mean/std (numerically stable)."""

    __slots__ = ("n", "mean", "M2")

    def __init__(self) -> None:
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0

    def update(self, x: float) -> None:
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2

    @property
    def variance(self) -> float:
        return self.M2 / max(1, self.n - 1)

    @property
    def std(self) -> float:
        v = self.variance
        return math.sqrt(v) if v > 1e-12 else 0.0


class EMA:
    __slots__ = ("alpha", "y")

    def __init__(self, alpha: float, init: float = 0.0) -> None:
        self.alpha = float(alpha)
        self.y = float(init)

    def update(self, x: float) -> float:
        self.y = (1 - self.alpha) * self.y + self.alpha * float(x)
        return self.y


# ---------------------- CSV parsing helpers ----------------------

COMMON_SIGNAL_KEYS: List[str] = [
    "ml2",
    "signal",
    "ecg",
    "value",
    "val",
    "amplitude",
    "lead",
    "lead1",
    "lead2",
]
COMMON_LABEL_KEYS: List[str] = [
    "label",
    "annotation",
    "ann",
    "y",
    "class",
    "arrhythmia",
    "beat_type",
]


def _best_key(header: Sequence[str], candidates: Sequence[str]) -> Optional[str]:
    """Pick the best-matching header key (exact or fuzzy contains)."""
    lower = {h.lower(): h for h in header}
    for k in candidates:
        if k in lower:
            return lower[k]
    for h in header:
        hlow = h.lower()
        for k in candidates:
            if k in hlow:
                return h
    return None


def _label_to_binary(v: Optional[str]) -> int:
    """
    Map raw label to 0/1.
    - Numeric: any nonzero -> 1
    - Strings: treat typical arrhythmia symbols or non-'N' as positive
    """
    if v is None:
        return 0
    s = str(v).strip()
    if s == "":
        return 0
    try:
        f = float(s)
        return 1 if abs(f) > 1e-9 else 0
    except ValueError:
        pass
    if s.upper() in ("N", "NORMAL"):
        return 0
    return 1


def _rows_from_csv(path: str) -> Iterator[Dict[str, str]]:
    """Yield raw dict rows from CSV (dict values are strings)."""
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV appears to have no header.")
        for row in reader:
            yield row


def ecg_events_from_csv(path: str) -> Iterator[Dict[str, float | int]]:
    """
    Yield dicts with 'signal' (float) and optional 'label' (int 0/1) from CSV.
    Auto-detect plausible columns for signal/label without hard-coding schema.
    """
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
    if not header:
        raise ValueError("CSV appears to have no header.")

    key_signal = _best_key(header, COMMON_SIGNAL_KEYS) or header[0]
    key_label = _best_key(header, COMMON_LABEL_KEYS)

    for row in _rows_from_csv(path):
        raw = row.get(key_signal, "")
        try:
            sig = float(raw)
        except ValueError:
            # skip non-numeric line
            continue
        item: Dict[str, float | int] = {"signal": sig}
        if key_label is not None:
            item["label"] = _label_to_binary(row.get(key_label))
        yield item


# ---------------------- Feature engineering ----------------------


def sigmoid(x: float) -> float:
    # protect from overflow a bit
    x = max(min(x, 40.0), -40.0)
    return 1.0 / (1.0 + math.exp(-x))


def make_feature_stream(
    rows: Iterable[Dict[str, float | int]],
    max_abs_for_scale: float = 3.0,
) -> Iterator[Dict[str, float | int]]:
    """
    Convert raw ECG rows into Sundew-compatible features.

    Returns dicts with:
      - magnitude (0..100)
      - anomaly_score (0..1)
      - context_relevance (0..1)
      - urgency (0..1)
      - label (optional)
    """
    stats = RunningStats()
    ema_anom = EMA(alpha=0.02, init=0.0)
    prev_sig: Optional[float] = None

    for row in rows:
        sig = float(row["signal"])
        stats.update(sig)
        sd = stats.std or 1.0

        # z-score with running mean/std
        z = (sig - stats.mean) / sd
        anom = sigmoid(abs(z) / max_abs_for_scale)  # smooth anomaly in [0,1]
        ctx = ema_anom.update(anom)

        # derivative
        deriv = 0.0 if prev_sig is None else (sig - prev_sig)
        prev_sig = sig
        urg = math.tanh(abs(deriv) / (5.0 * sd + 1e-6))  # normalize to [0,1]

        # scale |z| to 0..100 for magnitude (~6σ -> ~100)
        mag = max(0.0, min(100.0, 100.0 * (abs(z) / (6.0 + 1e-9))))

        out: Dict[str, float | int] = {
            "magnitude": mag,
            "anomaly_score": anom,
            "context_relevance": ctx,
            "urgency": urg,
        }
        if "label" in row:
            out["label"] = int(row["label"])
        yield out


# ---------------------- Core runner ----------------------


def _parse_overrides(s: Optional[str]) -> Optional[Dict[str, float | int | bool | str]]:
    if not s:
        return None
    out: Dict[str, float | int | bool | str] = {}
    for pair in s.split(","):
        if "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        k = k.strip()
        v = v.strip()
        try:
            if "." in v or "e" in v.lower():
                out[k] = float(v)
            else:
                out[k] = int(v)
        except ValueError:
            if v.lower() in ("true", "false"):
                out[k] = v.lower() == "true"
            else:
                out[k] = v
    return out


def run(
    csv_path: str,
    preset: str = "tuned_v2",
    limit: Optional[int] = None,
    save_path: Optional[str] = None,
    refractory: int = 0,
    overrides: Optional[Dict[str, float | int | bool | str]] = None,
) -> Dict[str, object]:
    """Execute Sundew on a CSV stream and return a result dict."""
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    cfg = get_preset(preset, overrides=overrides or {})
    algo = SundewAlgorithm(cfg)

    y_true: List[int] = []
    y_pred: List[int] = []

    cooldown = 0

    for i, ev in enumerate(make_feature_stream(ecg_events_from_csv(csv_path))):
        if limit is not None and i >= limit:
            break

        gt = int(ev.get("label", 0))
        y_true.append(gt)

        if cooldown > 0:
            y_pred.append(0)
            cooldown -= 1
            continue

        res = algo.process(ev)
        pred = 1 if res is not None else 0
        y_pred.append(pred)

        if pred == 1 and refractory > 0:
            cooldown = refractory

    # Confusion and metrics (only meaningful if labels present)
    tp = fp = fn = tn = 0
    if any(y_true):
        for t, p_ in zip(y_true, y_pred):
            if t == 1 and p_ == 1:
                tp += 1
            elif t == 0 and p_ == 1:
                fp += 1
            elif t == 1 and p_ == 0:
                fn += 1
            else:
                tn += 1

    prec = tp / max(1, (tp + fp))
    rec = tp / max(1, (tp + fn))
    f1 = (2 * prec * rec) / max(1e-12, (prec + rec)) if (tp + fp + fn) > 0 else 0.0

    report = algo.report()

    # Robust config serialization: works for slotted dataclasses too
    try:
        cfg_dict: Dict[str, Any] = asdict(cfg)
    except Exception:
        cfg_dict = {
            k: getattr(cfg, k)
            for k in dir(cfg)
            if not k.startswith("_") and not callable(getattr(cfg, k, None))
        }

    out: Dict[str, object] = {
        "config": cfg_dict,
        "report": report,
        "counts": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "total_inputs": len(y_true),
            "activations": sum(1 for p_ in y_pred if p_ == 1),
        },
    }

    if save_path:
        out_path = Path(save_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"Saved results to {save_path}")

        # Also print a compact summary to stdout (useful in CI)
        for k, v in report.items():
            print(f"{k:25s} : {v}")

    return out


def run_once(
    csv_path: str,
    preset: str = "tuned_v2",
    limit: Optional[int] = None,
    save_path: Optional[str] = None,
    refractory: int = 0,
    overrides: Optional[Dict[str, float | int | bool | str]] = None,
) -> Dict[str, object]:
    """Explicit alias for single-run usage."""
    return run(csv_path, preset, limit, save_path, refractory, overrides)


# ---------------------- CLI ----------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Run Sundew on an ECG CSV and save results.")
    ap.add_argument(
        "--csv",
        required=True,
        help="Path to ECG CSV (e.g., MIT-BIH export).",
    )
    ap.add_argument("--preset", default="tuned_v2", help="Config preset name.")
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit of samples to process.",
    )
    ap.add_argument(
        "--save",
        type=str,
        default=None,
        help="Optional JSON output path.",
    )
    ap.add_argument(
        "--refractory",
        type=int,
        default=0,
        help="Samples to suppress further activations after a detection.",
    )
    ap.add_argument(
        "--overrides",
        type=str,
        default=None,
        help=('Preset overrides, e.g. "gate_temperature=0.12,target_activation_rate=0.15"'),
    )

    args = ap.parse_args()
    overrides_dict = _parse_overrides(args.overrides)

    run(
        csv_path=args.csv,
        preset=args.preset,
        limit=args.limit,
        save_path=args.save,
        refractory=args.refractory,
        overrides=overrides_dict,
    )


if __name__ == "__main__":
    main()
