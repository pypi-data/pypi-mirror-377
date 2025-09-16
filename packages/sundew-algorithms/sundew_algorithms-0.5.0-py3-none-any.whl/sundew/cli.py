# src/sundew/cli.py
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from . import get_preset, list_presets
from .config import SundewConfig
from .core import ProcessingResult, SundewAlgorithm
from .demo import synth_event


def _stdout_supports_unicode() -> bool:
    enc = getattr(sys.stdout, "encoding", None) or ""
    try:
        # Test both emoji and special characters
        test_chars = "🌿✅⏸🏁ΔE≈"
        test_chars.encode(enc or "utf-8", errors="strict")
        return True
    except Exception:
        return False


EMOJI_OK = _stdout_supports_unicode()
BULLET = "🌿" if EMOJI_OK else "[sundew]"
CHECK = "✅" if EMOJI_OK else "[ok]"
PAUSE = "⏸" if EMOJI_OK else "[idle]"
FLAG_DONE = "🏁" if EMOJI_OK else "[done]"
DELTA = "Δ" if EMOJI_OK else "d"
APPROX = "≈" if EMOJI_OK else "~"
DISK = "💾" if EMOJI_OK else "[saved]"


def _energy_float(algo: SundewAlgorithm) -> float:
    e = getattr(algo, "energy", 0.0)
    v = getattr(e, "value", e)
    try:
        return float(v)
    except Exception:
        return 0.0


def _to_plain(obj: object) -> dict[str, Any]:
    """Dataclass-safe serializer (works with slots=True)."""
    if is_dataclass(obj):
        return asdict(obj)  # type: ignore[arg-type]
    d = getattr(obj, "__dict__", {})
    return dict(d) if isinstance(d, dict) else {}


def cmd_list_presets(_: argparse.Namespace) -> int:
    for p in list_presets():
        print(p)
    return 0


def cmd_print_config(ns: argparse.Namespace) -> int:
    cfg: SundewConfig = get_preset(ns.preset) if ns.preset else SundewConfig()
    print(json.dumps(_to_plain(cfg), indent=2))
    return 0


def cmd_demo(ns: argparse.Namespace) -> int:  # pragma: no cover
    """Inline demo (interactive printout) with optional save."""
    # Enhanced CLI demo function v0.3.0 with improved stability and formatting
    try:
        # Validate inputs
        if ns.events <= 0:
            print("ERROR: Number of events must be positive")
            return 1
        if ns.events > 10000:
            print("WARNING: Large number of events may take a while")

        if not 0.0 <= ns.temperature <= 1.0:
            print("ERROR: Temperature must be between 0.0 and 1.0")
            return 1

        # Use preset with CLI parameter overrides
        preset_name = getattr(ns, 'preset', 'auto_tuned')
        try:
            cfg = get_preset(preset_name)
        except KeyError:
            print(f"ERROR: Unknown preset '{preset_name}'. Available: {list_presets()}")
            return 1

        # Apply CLI parameter overrides
        cfg.gate_temperature = ns.temperature

        if hasattr(ns, 'max_threshold') and ns.max_threshold is not None:
            cfg.max_threshold = ns.max_threshold
        if hasattr(ns, 'ema_alpha') and ns.ema_alpha is not None:
            cfg.ema_alpha = ns.ema_alpha
        if hasattr(ns, 'hysteresis') and ns.hysteresis is not None:
            cfg.hysteresis_gap = ns.hysteresis

        cfg.validate()  # Ensure configuration is valid
        algo = SundewAlgorithm(cfg)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return 1

    # Output lock for thread safety
    output_lock = threading.Lock()

    print(f"{BULLET} Sundew Algorithm — Demo")
    print("=" * 60)
    print(f"Initial threshold: {algo.threshold:.3f} | Energy: {_energy_float(algo):.1f}")
    print()

    # Flush output to prevent buffering issues
    sys.stdout.flush()

    try:
        processed: list[ProcessingResult] = []
        last_activation_rate = 0.0

        for i in range(ns.events):
            try:
                x = synth_event(i)
                res = algo.process(x)

                with output_lock:
                    if res is None:
                        # Format dormant events with consistent spacing
                        line = f"{i + 1:02d}. {x['type']:<15} {PAUSE} dormant"
                        status = f"| energy {_energy_float(algo):6.1f} | thr {algo.threshold:.3f}"
                        print(f"{line:35} {status}")
                    else:
                        processed.append(res)
                        # Format processed events with detailed info
                        line = f"{i + 1:02d}. {x['type']:<15} {CHECK} processed"
                        details = f"(sig={res.significance:.3f}, {res.processing_time:.3f}s, {DELTA}E{APPROX}{res.energy_consumed:.1f})"
                        status = f"| energy {_energy_float(algo):6.1f} | thr {algo.threshold:.3f}"
                        print(f"{line:35} {details:35} {status}")

                    # Flush output immediately for real-time display
                    sys.stdout.flush()

                    # Brief delay to prevent overwhelming output
                    time.sleep(0.01)

            except KeyboardInterrupt:
                print(f"\nDemo interrupted at event {i + 1}")
                break
            except Exception as e:
                print(f"\nError processing event {i + 1}: {e}")
                continue

    except Exception as e:
        print(f"Critical error during demo: {e}")
        return 1

    print(f"\n{FLAG_DONE} Final Report (Enhanced v0.3.0)")
    print("=" * 60)

    report = algo.report()

    # Core metrics with improved formatting
    print("Performance Metrics:")
    print(f"  Total Events              : {report.get('total_inputs', 0):>8}")
    print(f"  Activations               : {report.get('activations', 0):>8}")
    print(f"  Activation Rate           : {report.get('activation_rate', 0):>7.1%}")
    print(f"  EMA Activation Rate       : {report.get('ema_activation_rate', 0):>7.1%}")
    print()

    # Enhanced energy analysis with fixed accounting
    energy_savings = report.get('estimated_energy_savings_pct', 0)
    print("Energy Analysis:")
    print(f"  Energy Remaining          : {report.get('energy_remaining', 0):>7.1f}")
    print(f"  Total Energy Spent        : {report.get('total_energy_spent', 0):>7.1f}")
    print(f"  Net Energy Consumed       : {report.get('net_energy_consumed', 0):>7.1f}")
    print(f"  Energy Recovered          : {report.get('energy_recovered', 0):>7.1f}")
    print(f"  Processing Energy         : {report.get('energy_spent_processing', 0):>7.1f}")
    print(f"  Dormancy Energy           : {report.get('energy_spent_dormancy', 0):>7.1f}")
    print(f"  Energy Savings            : {energy_savings:>7.1f}%")

    # Performance rating based on energy savings
    if energy_savings > 90:
        rating = "Excellent"
    elif energy_savings > 80:
        rating = "Good"
    elif energy_savings > 70:
        rating = "Fair"
    else:
        rating = "Poor"
    print(f"  Performance Rating        : {rating}")
    print()

    # Enhanced control system status with debugging info
    print("Control System:")
    print(f"  Final Threshold           : {algo.threshold:>7.3f}")
    print(f"  Threshold Utilization     : {report.get('threshold_utilization', 0):>7.1%}")
    print(f"  Hysteresis Gap            : {report.get('hysteresis_gap', 0):>7.3f}")
    print(f"  EMA Alpha                 : {report.get('ema_alpha', 0):>7.3f}")
    print(f"  EMA Discrepancy           : {report.get('ema_discrepancy', 0):>7.3f}")
    print(f"  Avg Processing Time       : {report.get('avg_processing_time', 0):>7.3f}s")

    # Enhanced convergence analysis
    rate_diff = abs(report.get('activation_rate', 0) - report.get('ema_activation_rate', 0))
    convergence_status = "Converged" if rate_diff < 0.05 else "Oscillating"
    print(f"  Convergence Status        : {convergence_status}")
    print()

    # Enhanced suggestions based on multiple metrics
    print("Optimization Suggestions:")
    if report.get('ema_discrepancy', 0) > 0.05:
        print("  - Consider adjusting EMA alpha for better rate tracking")
    if report.get('threshold_utilization', 0) > 0.9:
        print("  - Threshold near max - reduce gains to prevent saturation")
    if report.get('energy_at_cap_pct', 0) > 50:
        print("  - Energy frequently at cap - capacity may be underutilized")
    if abs(report.get('controller_integral_error', 0)) > 0.2:
        print("  - High integral error - consider anti-windup measures")
    if rate_diff > 0.1:
        print("  - Consider tuning PI controller gains for better stability")

    if ns.save:
        try:
            out = {
                "config": _to_plain(cfg),
                "report": report,
                "processed_events": [_to_plain(r) for r in processed],
                "metadata": {
                    "version": "0.3.0",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_events": len(processed) + (ns.events - len(processed))
                }
            }
            path = Path(ns.save)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2)
            print(f"\nResults saved to {path}")
        except PermissionError:
            print(f"\nError: Permission denied writing to {ns.save}")
            return 1
        except OSError as e:
            print(f"\nError saving file: {e}")
            return 1
        except Exception as e:
            print(f"\nUnexpected error saving results: {e}")
            return 1

    return 0


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    """
    Sundew Algorithm CLI entrypoint.

    Tests look for 'Sundew Algorithm CLI' or 'Sundew Algorithm' in help text.
    """
    ap = argparse.ArgumentParser(description="Sundew Algorithm CLI")
    sub = ap.add_subparsers(dest="cmd")

    # list-presets
    ap_list = sub.add_parser("list-presets", help="List available configuration presets")
    ap_list.set_defaults(func=cmd_list_presets)

    # print-config
    ap_print = sub.add_parser("print-config", help="Print a preset config as JSON")
    ap_print.add_argument(
        "--preset",
        type=str,
        default="",
        help="Preset name (default: inline defaults)",
    )
    ap_print.set_defaults(func=cmd_print_config)

    # demo flags (top-level shortcut)
    ap.add_argument(
        "--demo",
        action="store_true",
        help="Run the interactive demo (shortcut without subcommand)",
    )
    ap.add_argument("--events", type=int, default=40, help="Number of demo events")
    ap.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Gating temperature (0=hard)",
    )
    ap.add_argument(
        "--preset",
        type=str,
        default="auto_tuned",
        help="Configuration preset (default: auto_tuned)",
    )
    ap.add_argument(
        "--save",
        type=str,
        default="",
        help="Optional path to save demo results JSON",
    )

    # Auto-tuner CLI flags
    ap.add_argument(
        "--max-threshold",
        type=float,
        help="Maximum threshold (auto-tuner: 0.88)",
    )
    ap.add_argument(
        "--ema-alpha",
        type=float,
        help="EMA learning rate (auto-tuner: 0.35)",
    )
    ap.add_argument(
        "--hysteresis",
        type=float,
        help="Hysteresis gap (auto-tuner: 0.02)",
    )

    # demo subcommand (explicit) - copy tuning flags
    ap_demo = sub.add_parser("demo", help="Run the interactive demo")
    ap_demo.add_argument("--events", type=int, default=40)
    ap_demo.add_argument("--temperature", type=float, default=0.1)
    ap_demo.add_argument("--preset", type=str, default="auto_tuned")
    ap_demo.add_argument("--save", type=str, default="")
    ap_demo.add_argument("--max-threshold", type=float, help="Maximum threshold")
    ap_demo.add_argument("--ema-alpha", type=float, help="EMA learning rate")
    ap_demo.add_argument("--hysteresis", type=float, help="Hysteresis gap")
    ap_demo.set_defaults(func=cmd_demo)

    ns = ap.parse_args(argv)

    if ns.cmd in ("list-presets", "print-config"):
        return ns.func(ns)

    if ns.cmd == "demo" or getattr(ns, "demo", False):
        # Support both `sundew demo` and `sundew --demo`
        return cmd_demo(ns)

    # No subcommand → print help and exit 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
