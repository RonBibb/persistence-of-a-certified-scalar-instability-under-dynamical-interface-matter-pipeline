#!/usr/bin/env python3
"""Render the exact D2A terminal cover and its certified residual floor."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle


HERE = Path(__file__).resolve().parent
RESULT = HERE.parent / "lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json"
OUT = HERE / "figures"

COLORS = {
    "NEGATIVE_CURVATURE_EXCLUDED": "#999999",
    "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO": "#0072B2",
    "UPPER_ISRAEL_EXCLUDED": "#D55E00",
    "UPPER_SCALAR_EXCLUDED": "#009E73",
}
LABELS = {
    "NEGATIVE_CURVATURE_EXCLUDED": "negative curvature (20)",
    "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO": "both residuals exclude zero (670)",
    "UPPER_ISRAEL_EXCLUDED": "Israel residual only (1)",
    "UPPER_SCALAR_EXCLUDED": "scalar residual only (2)",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def zero_distance(bounds: list[str]) -> Fraction:
    low, high = (Fraction(value) for value in bounds)
    if low > 0:
        return low
    if high < 0:
        return -high
    return Fraction(0)


def add_cover(ax, boxes, *, xlim, title, label_special=False):
    for index, box in enumerate(boxes):
        low, high = (float(Fraction(value)) for value in box["a_exact_bounds"])
        classification = box["classification"]
        ax.add_patch(
            Rectangle(
                (low, 0.12),
                high - low,
                0.76,
                facecolor=COLORS[classification],
                edgecolor="white",
                linewidth=0.18,
            )
        )
        if label_special and classification in {
            "UPPER_ISRAEL_EXCLUDED",
            "UPPER_SCALAR_EXCLUDED",
        }:
            center = (low + high) / 2
            marker = "I" if classification == "UPPER_ISRAEL_EXCLUDED" else "S"
            ax.annotate(
                marker,
                (center, 0.92),
                xytext=(center, 1.22 if marker == "I" else 1.07),
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color=COLORS[classification],
                arrowprops={"arrowstyle": "-", "color": COLORS[classification], "lw": 0.8},
            )
    ax.set_xlim(*xlim)
    ax.set_ylim(0, 1.42 if label_special else 1)
    ax.set_yticks([])
    ax.set_xlabel(r"lower-wall launch value $a=\Phi(0)$")
    ax.set_title(title, loc="left", fontweight="bold")
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)


def main() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    boxes = payload["terminal_boxes"]
    if len(boxes) != 693:
        raise RuntimeError(f"unexpected terminal-box count: {len(boxes)}")
    if payload["classification_counts"] != {
        "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO": 670,
        "NEGATIVE_CURVATURE_EXCLUDED": 20,
        "UPPER_ISRAEL_EXCLUDED": 1,
        "UPPER_SCALAR_EXCLUDED": 2,
    }:
        raise RuntimeError("unexpected classification counts")

    margins = []
    for index, box in enumerate(boxes):
        if box["classification"] == "NEGATIVE_CURVATURE_EXCLUDED":
            continue
        low, high = (Fraction(value) for value in box["a_exact_bounds"])
        record = box["record"]
        g_distance = zero_distance(record["G_exact_bounds"])
        h_distance = zero_distance(record["scalar_residual_exact_bounds"])
        margins.append(
            {
                "index": index,
                "low": float(low),
                "high": float(high),
                "margin": float(max(g_distance, h_distance)),
                "classification": box["classification"],
            }
        )
    minimum = min(margins, key=lambda item: item["margin"])
    if minimum["index"] != 569 or not minimum["margin"] > 0.0077:
        raise RuntimeError("unexpected minimum residual floor")

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.edgecolor": "#444444",
            "axes.labelcolor": "#222222",
            "xtick.color": "#444444",
            "ytick.color": "#444444",
        }
    )
    fig = plt.figure(figsize=(12.2, 8.0))
    grid = fig.add_gridspec(2, 2, height_ratios=[0.7, 2.7])
    ax_full = fig.add_subplot(grid[0, :])
    ax_zoom = fig.add_subplot(grid[1, 0])
    ax_floor = fig.add_subplot(grid[1, 1])

    add_cover(
        ax_full,
        boxes,
        xlim=(0, 0.1),
        title="A. Exact contiguous cover of the full declared launch interval",
    )
    ax_full.axvline(0.09239035959041748, color="#222222", lw=0.8, ls="--")
    ax_full.text(
        0.046,
        0.5,
        "negative-curvature route",
        ha="center",
        va="center",
        color="white",
        fontsize=9,
        fontweight="bold",
    )

    zoom = (0.09845, 0.09955)
    add_cover(
        ax_zoom,
        boxes,
        xlim=zoom,
        title="B. Cover detail near the narrow residual crossings",
        label_special=True,
    )
    ax_zoom.text(
        0.02,
        0.04,
        "I = Israel-only exclusion; S = scalar-only exclusion",
        transform=ax_zoom.transAxes,
        fontsize=8.5,
        color="#444444",
    )

    for item in margins:
        color = COLORS[item["classification"]]
        ax_floor.plot(
            [item["low"], item["high"]],
            [item["margin"], item["margin"]],
            color=color,
            lw=1.3,
            solid_capstyle="butt",
        )
    ax_floor.axhline(0.0077, color="#D55E00", ls="--", lw=1.2, label="theorem floor 0.0077")
    center = (minimum["low"] + minimum["high"]) / 2
    ax_floor.scatter([center], [minimum["margin"]], color="#D55E00", s=30, zorder=5)
    ax_floor.annotate(
        "minimum exact lower bound\n0.0077281481292751026\n(box 569, zero based)",
        xy=(center, minimum["margin"]),
        xytext=(0.09845, 0.018),
        fontsize=8.5,
        color="#222222",
        arrowprops={"arrowstyle": "->", "color": "#555555", "lw": 0.9},
    )
    ax_floor.set_xlim(0.09235, 0.10003)
    ax_floor.set_yscale("log")
    ax_floor.set_ylim(0.0055, 30)
    ax_floor.grid(True, which="both", color="#E5E5E5", lw=0.65)
    ax_floor.set_axisbelow(True)
    ax_floor.set_xlabel(r"lower-wall launch value $a=\Phi(0)$")
    ax_floor.set_ylabel(r"certified $\max\{\mathrm{dist}(0,G),\mathrm{dist}(0,h)\}$")
    ax_floor.set_title("C. Positive-route residual separation from zero", loc="left", fontweight="bold")
    ax_floor.legend(loc="upper right", frameon=False, fontsize=8.5)

    handles = [Patch(facecolor=COLORS[key], label=LABELS[key]) for key in COLORS]
    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.925),
    )
    fig.suptitle(
        "Exhaustive fixed-separation exclusion at D0 = 0.9996389747145851",
        fontsize=16,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.01,
        0.012,
        "All 693 exact terminal boxes are resolved; horizontal segments in panel C are boxwise interval lower bounds, not sampled point values. "
        f"Source RESULT.json SHA-256 {sha256(RESULT)}.",
        ha="left",
        va="bottom",
        fontsize=8.3,
        color="#555555",
    )
    fig.subplots_adjust(left=0.065, right=0.985, bottom=0.095, top=0.84, hspace=0.32, wspace=0.18)

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "d2a_exact_cover.png", dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / "d2a_exact_cover.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
