import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.stats import mannwhitneyu, shapiro, ttest_ind
try:
    from skbio.stats.distance import DistanceMatrix, permanova
    HAS_SKBIO = True
except ImportError:
    DistanceMatrix = None
    permanova = None
    HAS_SKBIO = False

ANALYSIS_METRICS = ["shortest_path_len", "dead_end_count", "tortuosity"]


def load_dataset(csv_path, label):
    df = pd.read_csv(csv_path)
    print(f"Loaded {label}: {len(df)} rows")
    return df


def clean_numeric(series):
    s = pd.to_numeric(series, errors="coerce")
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    return s.to_numpy()


def format_p(p_value):
    if p_value is None or np.isnan(p_value):
        return "N/A"
    if p_value < 0.001:
        return f"{p_value:.2e}"
    return f"{p_value:.6f}"


def shapiro_with_sampling(data, alpha, max_n, rng):
    n_total = len(data)
    if n_total < 3:
        return {
            "n_total": n_total,
            "n_used": n_total,
            "W": np.nan,
            "p_value": np.nan,
            "is_normal": None,
            "note": "Too few values for Shapiro-Wilk.",
        }

    used = data
    note = ""
    if n_total > max_n:
        idx = rng.choice(n_total, size=max_n, replace=False)
        used = data[idx]
        note = f"Sampled {max_n} from {n_total} for Shapiro-Wilk"

    w_stat, p_value = shapiro(used)
    return {
        "n_total": n_total,
        "n_used": len(used),
        "W": float(w_stat),
        "p_value": float(p_value),
        "is_normal": bool(p_value >= alpha),
        "note": note,
    }


def run_univariate_test(metric, prng_data, qrng_data, alpha):
    if len(prng_data) < 2 or len(qrng_data) < 2:
        return {
            "metric": metric,
            "test": "INSUFFICIENT_DATA",
            "p_value": np.nan,
            "significant": False,
        }

    # Welch as requested when normality is acceptable.
    t_stat, t_p = ttest_ind(prng_data, qrng_data, equal_var=False)
    mwu_stat, mwu_p = mannwhitneyu(prng_data, qrng_data, alternative="two-sided")

    return {
        "metric": metric,
        "welch_t": float(t_stat),
        "welch_p": float(t_p),
        "mwu_u": float(mwu_stat),
        "mwu_p": float(mwu_p),
        "mean_prng": float(np.mean(prng_data)),
        "mean_qrng": float(np.mean(qrng_data)),
        "median_prng": float(np.median(prng_data)),
        "median_qrng": float(np.median(qrng_data)),
        "n_prng": len(prng_data),
        "n_qrng": len(qrng_data),
        "alpha": alpha,
    }


def zscore_columns(matrix):
    means = np.mean(matrix, axis=0)
    stds = np.std(matrix, axis=0, ddof=0)
    stds = np.where(stds == 0, 1.0, stds)
    return (matrix - means) / stds


def run_permanova(prng_df, qrng_df, metrics, perms, alpha, max_per_group, rng):
    if not HAS_SKBIO:
        return {
            "error": (
                "scikit-bio is not installed. PERMANOVA requires scikit-bio and, on this Python "
                "environment, installing it currently fails because biom-format needs Microsoft C++ "
                "Build Tools."
            )
        }

    prng_clean = prng_df[metrics].apply(pd.to_numeric, errors="coerce").dropna()
    qrng_clean = qrng_df[metrics].apply(pd.to_numeric, errors="coerce").dropna()

    if len(prng_clean) == 0 or len(qrng_clean) == 0:
        return {"error": "No valid multivariate rows after dropna across selected metrics."}

    n_prng_total = len(prng_clean)
    n_qrng_total = len(qrng_clean)

    if len(prng_clean) > max_per_group:
        prng_clean = prng_clean.iloc[rng.choice(len(prng_clean), size=max_per_group, replace=False)]
    if len(qrng_clean) > max_per_group:
        qrng_clean = qrng_clean.iloc[rng.choice(len(qrng_clean), size=max_per_group, replace=False)]

    X = np.vstack([prng_clean.to_numpy(), qrng_clean.to_numpy()])
    X = zscore_columns(X)

    ids = [f"PRNG_{i}" for i in range(len(prng_clean))] + [
        f"QRNG_{i}" for i in range(len(qrng_clean))
    ]
    grouping = ["PRNG"] * len(prng_clean) + ["QRNG"] * len(qrng_clean)

    # Euclidean distance on z-scored features, then library PERMANOVA.
    condensed = pdist(X, metric="euclidean")
    distance_matrix = squareform(condensed)
    dm = DistanceMatrix(distance_matrix, ids=ids)

    grouping_series = pd.Series(grouping, index=ids, name="group")
    result = permanova(dm, grouping=grouping_series, permutations=perms)

    pseudo_f = float(result["test statistic"])
    p_value = float(result["p-value"])
    df_between = int(result["number of groups"] - 1)
    df_within = int(result["sample size"] - result["number of groups"])

    return {
        "method": "scikit-bio permanova",
        "metrics": metrics,
        "n_prng_total": n_prng_total,
        "n_qrng_total": n_qrng_total,
        "n_prng_used": len(prng_clean),
        "n_qrng_used": len(qrng_clean),
        "pseudo_F": pseudo_f,
        "p_value": float(p_value),
        "significant": bool(p_value < alpha),
        "df_between": df_between,
        "df_within": df_within,
        "permutations": int(perms),
    }


def build_report_text(
    alpha,
    metrics,
    prng_path,
    qrng_path,
    shapiro_results,
    univariate_results,
    permanova_result,
):
    lines = []
    lines.append("=" * 88)
    lines.append("STATISTICAL ANALYSIS REPORT: PRNG vs QRNG MAZE METRICS")
    lines.append("=" * 88)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"PRNG file: {prng_path}")
    lines.append(f"QRNG file: {qrng_path}")
    lines.append(f"Significance level (alpha): {alpha}")
    lines.append("")

    lines.append("PART 1: SHAPIRO-WILK NORMALITY")
    lines.append("-" * 88)
    lines.append("Decision: if p < alpha, reject normality.")
    lines.append("")
    for metric in metrics:
        pr = shapiro_results[metric]["PRNG"]
        qr = shapiro_results[metric]["QRNG"]
        lines.append(f"Metric: {metric}")
        lines.append(
            f"  PRNG: n_total={pr['n_total']}, n_used={pr['n_used']}, W={pr['W']:.6f}, "
            f"p={format_p(pr['p_value'])}, normal={pr['is_normal']}"
        )
        if pr["note"]:
            lines.append(f"    Note: {pr['note']}")
        lines.append(
            f"  QRNG: n_total={qr['n_total']}, n_used={qr['n_used']}, W={qr['W']:.6f}, "
            f"p={format_p(qr['p_value'])}, normal={qr['is_normal']}"
        )
        if qr["note"]:
            lines.append(f"    Note: {qr['note']}")
        lines.append("")

    lines.append("PART 2: UNIVARIATE GROUP COMPARISONS")
    lines.append("-" * 88)
    lines.append("Rule: if both groups are normal, interpret Welch t-test; otherwise interpret Mann-Whitney U.")
    lines.append("")
    univariate_sig = 0
    for metric in metrics:
        row = univariate_results[metric]
        pr_norm = shapiro_results[metric]["PRNG"]["is_normal"]
        qr_norm = shapiro_results[metric]["QRNG"]["is_normal"]
        use_welch = bool(pr_norm and qr_norm)
        if use_welch:
            p_value = row["welch_p"]
            significant = p_value < alpha
            lines.append(f"Metric: {metric} | Test: Welch t-test")
            lines.append(
                f"  Means: PRNG={row['mean_prng']:.6f}, QRNG={row['mean_qrng']:.6f}, "
                f"t={row['welch_t']:.6f}, p={format_p(p_value)}"
            )
        else:
            p_value = row["mwu_p"]
            significant = p_value < alpha
            lines.append(f"Metric: {metric} | Test: Mann-Whitney U")
            lines.append(
                f"  Medians: PRNG={row['median_prng']:.6f}, QRNG={row['median_qrng']:.6f}, "
                f"U={row['mwu_u']:.3f}, p={format_p(p_value)}"
            )
        lines.append(f"  Significant at alpha={alpha}: {significant}")
        lines.append("")
        if significant:
            univariate_sig += 1

    lines.append("PART 3: TRUE MULTIVARIATE PERMANOVA")
    lines.append("-" * 88)
    if "error" in permanova_result:
        lines.append(f"PERMANOVA could not be computed: {permanova_result['error']}")
    else:
        lines.append(f"Method: {permanova_result['method']} (Euclidean distance on z-scored metrics)")
        lines.append(f"Metrics included: {', '.join(permanova_result['metrics'])}")
        lines.append(
            f"Rows used (after per-metric complete cases and sampling): "
            f"PRNG={permanova_result['n_prng_used']} of {permanova_result['n_prng_total']}, "
            f"QRNG={permanova_result['n_qrng_used']} of {permanova_result['n_qrng_total']}"
        )
        lines.append(
            f"Pseudo-F={permanova_result['pseudo_F']:.6f}, p={format_p(permanova_result['p_value'])}, "
            f"permutations={permanova_result['permutations']}"
        )
        lines.append(
            f"Degrees of freedom: between={permanova_result['df_between']}, within={permanova_result['df_within']}"
        )
        lines.append(f"Significant at alpha={alpha}: {permanova_result['significant']}")
    lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 88)
    lines.append(f"Univariate significant metrics: {univariate_sig}/{len(metrics)}")
    if "error" in permanova_result:
        lines.append("Multivariate PERMANOVA: not available")
    else:
        lines.append(
            f"Multivariate PERMANOVA significant: {permanova_result['significant']} "
            f"(p={format_p(permanova_result['p_value'])})"
        )
    lines.append("=" * 88)

    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Consistent PRNG vs QRNG statistical analysis with true multivariate PERMANOVA."
    )
    parser.add_argument("--prng", required=True, help="PRNG metrics CSV file")
    parser.add_argument("--qrng", required=True, help="QRNG metrics CSV file")
    parser.add_argument("--output", default="statistical_analysis_report.txt", help="Output TXT report")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level")
    parser.add_argument("--permanova-perms", type=int, default=1000, help="PERMANOVA permutations")
    parser.add_argument(
        "--shapiro-max-sample",
        type=int,
        default=5000,
        help="Max N used per group for Shapiro-Wilk",
    )
    parser.add_argument(
        "--permanova-max-sample",
        type=int,
        default=5000,
        help="Max N per group for PERMANOVA",
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=ANALYSIS_METRICS,
        help="Metric columns to analyze",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def main():
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    prng_df = load_dataset(args.prng, "PRNG")
    qrng_df = load_dataset(args.qrng, "QRNG")

    missing_in_prng = [m for m in args.metrics if m not in prng_df.columns]
    missing_in_qrng = [m for m in args.metrics if m not in qrng_df.columns]
    if missing_in_prng or missing_in_qrng:
        raise ValueError(
            "Missing required metrics. "
            f"PRNG missing: {missing_in_prng} | QRNG missing: {missing_in_qrng}"
        )

    shapiro_results = {}
    univariate_results = {}

    for metric in args.metrics:
        prng_vals = clean_numeric(prng_df[metric])
        qrng_vals = clean_numeric(qrng_df[metric])

        shapiro_results[metric] = {
            "PRNG": shapiro_with_sampling(prng_vals, args.alpha, args.shapiro_max_sample, rng),
            "QRNG": shapiro_with_sampling(qrng_vals, args.alpha, args.shapiro_max_sample, rng),
        }
        univariate_results[metric] = run_univariate_test(metric, prng_vals, qrng_vals, args.alpha)

    # PERMANOVA over all selected non-normal metrics.
    non_normal_metrics = []
    for metric in args.metrics:
        pr_norm = shapiro_results[metric]["PRNG"]["is_normal"]
        qr_norm = shapiro_results[metric]["QRNG"]["is_normal"]
        if not (pr_norm and qr_norm):
            non_normal_metrics.append(metric)

    if non_normal_metrics:
        permanova_result = run_permanova(
            prng_df,
            qrng_df,
            metrics=non_normal_metrics,
            perms=args.permanova_perms,
            alpha=args.alpha,
            max_per_group=args.permanova_max_sample,
            rng=rng,
        )
    else:
        permanova_result = {
            "error": "All selected metrics were normal in both groups; PERMANOVA was not required."
        }

    report_text = build_report_text(
        alpha=args.alpha,
        metrics=args.metrics,
        prng_path=args.prng,
        qrng_path=args.qrng,
        shapiro_results=shapiro_results,
        univariate_results=univariate_results,
        permanova_result=permanova_result,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_text, encoding="utf-8")
    print(f"Saved report: {out_path}")


if __name__ == "__main__":
    main()
