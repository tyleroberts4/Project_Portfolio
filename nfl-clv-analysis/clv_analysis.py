"""
Closing Line Value (CLV) analysis and line movement.

CLV: Did your bet get a better price than the closing line?
- Spread: You took home -3.5, close was -4 → you have CLV (better price)
- Total: You took over 47.5, close was 46.5 → you have CLV
"""

from pathlib import Path

import pandas as pd
import numpy as np


def analyze_clv(df: pd.DataFrame) -> dict:
    """
    Compute CLV metrics.

    Without open lines, we use closing line as proxy. CLV analysis typically
    compares bet price to close. Here we simulate: assume "your" line is
    closing minus random noise (simulating early bet). Then compute how often
    you'd have CLV vs a different simulated close.

    For real CLV: need your actual bet timestamp and price vs closing line.
    """
    results = {}

    # Spread: negative = home favored. Home covers if margin + spread > 0
    df["home_covered"] = (df["margin"] + df["spread_line"]) > 0

    # Simulated "your" spread (add small noise to closing - as if you bet early)
    np.random.seed(42)
    noise = np.random.uniform(-1.5, 1.5, len(df))
    df["your_spread"] = df["spread_line"] + noise

    # CLV = you got a better price than closing. For home spread: more points = better (your_spread > close)
    df["spread_clv"] = df["your_spread"] > df["spread_line"]
    results["spread_clv_pct"] = df["spread_clv"].mean()

    # Total: you got over at lower total = better. your_total < close means you got over 47, close was 48 → CLV
    noise_t = np.random.uniform(-1.5, 1.5, len(df))
    df["your_total"] = df["total_line"] + noise_t
    # Over bet: CLV if you got lower total than close. Under: higher. Simulate over bets.
    df["total_clv"] = df["your_total"] < df["total_line"]
    results["total_clv_pct"] = df["total_clv"].mean()

    return results


def line_movement_summary(df: pd.DataFrame) -> dict:
    """Summarize line movement (if open/close available)."""
    out = {}
    if "spread_line" in df.columns:
        out["spread_std"] = df["spread_line"].std()
        out["spread_mean"] = df["spread_line"].mean()
    if "total_line" in df.columns:
        out["total_std"] = df["total_line"].std()
        out["total_mean"] = df["total_line"].mean()
    return out


def main():
    data_dir = Path(__file__).parent / "data"
    csv_path = data_dir / "schedule_lines.csv"
    if not csv_path.exists():
        from load_data import main as load_main
        load_main()

    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["spread_line", "total_line", "margin", "total"])

    clv = analyze_clv(df)
    movement = line_movement_summary(df)

    print("=== Closing Line Value (CLV) Analysis ===")
    print(f"Spread CLV rate (simulated): {clv['spread_clv_pct']:.1%}")
    print(f"Total CLV rate (simulated):  {clv['total_clv_pct']:.1%}")
    print()
    print("=== Line Summary ===")
    print(f"Spread: mean={movement.get('spread_mean', 0):.2f}, std={movement.get('spread_std', 0):.2f}")
    print(f"Total:  mean={movement.get('total_mean', 0):.2f}, std={movement.get('total_std', 0):.2f}")

    report_path = Path(__file__).parent / "report.md"
    with open(report_path, "w") as f:
        f.write("# NFL CLV and Market Efficiency Report\n\n")
        f.write("## Closing Line Value (CLV)\n\n")
        f.write("CLV measures how often your bet price was better than the closing line. ")
        f.write("Sharp bettors aim for positive CLV as a proxy for getting value.\n\n")
        f.write(f"- **Spread CLV rate (simulated):** {clv['spread_clv_pct']:.1%}\n")
        f.write(f"- **Total CLV rate (simulated):** {clv['total_clv_pct']:.1%}\n\n")
        f.write("## Line Movement\n\n")
        f.write("With full open/close data, analyze movement by game and identify ")
        f.write("games with significant line movement (sharp vs public action).\n\n")
        f.write("## Notes\n\n")
        f.write("This analysis uses nflverse closing lines. For true CLV, use ")
        f.write("your actual bet prices and timestamps vs. closing lines.\n")
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
