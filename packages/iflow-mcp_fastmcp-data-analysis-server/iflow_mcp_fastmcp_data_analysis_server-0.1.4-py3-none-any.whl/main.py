"""
FastMCP Data Analysis Server
A Model Context Protocol server providing data analysis utilities that an LLM can offload to.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import List, Dict, Any
from fastmcp import FastMCP

mcp = FastMCP("Data Analysis Server")

@mcp.tool()
def poisson_probability(lam: float, k: int, prob_type: str = "point") -> Dict[str, Any]:
    """
    Calculate Poisson probability with different types.

    Args:
        lam: Lambda parameter (rate parameter, average events per interval)
        k: Number of events
        prob_type: Type of probability ("point", "cumulative", "survival")

    Returns:
        Dictionary with probability value and distribution info
    """
    if lam <= 0:
        raise ValueError("Lambda must be positive")
    if k < 0:
        raise ValueError("k must be non-negative")
    if prob_type not in ["point", "cumulative", "survival"]:
        raise ValueError("prob_type must be 'point', 'cumulative', or 'survival'")

    poisson_dist = stats.poisson(lam)

    if prob_type == "point":
        probability = poisson_dist.pmf(k)
        description = f"P(X = {k})"
    elif prob_type == "cumulative":
        probability = poisson_dist.cdf(k)
        description = f"P(X ≤ {k})"
    else:  # survival
        probability = poisson_dist.sf(k)
        description = f"P(X > {k})"

    return {
        "probability": float(probability),
        "description": description,
        "lambda": lam,
        "k": k,
        "prob_type": prob_type,
        "mean": lam,
        "variance": lam,
        "std_dev": np.sqrt(lam)
    }

@mcp.tool()
def descriptive_statistics(data: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive descriptive statistics for a dataset.

    Args:
        data: List of numerical values

    Returns:
        Dictionary with various statistical measures
    """
    if not data:
        raise ValueError("Data list cannot be empty")

    arr = np.array(data)

    return {
        "count": len(data),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "mode": float(stats.mode(arr, keepdims=True)[0][0]),
        "std_dev": float(np.std(arr, ddof=1)),
        "variance": float(np.var(arr, ddof=1)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "range": float(np.max(arr) - np.min(arr)),
        "q1": float(np.percentile(arr, 25)),
        "q3": float(np.percentile(arr, 75)),
        "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25)),
        "skewness": float(stats.skew(arr)),
        "kurtosis": float(stats.kurtosis(arr))
    }

@mcp.tool()
def normal_probability(x: float, mean: float = 0, std_dev: float = 1, prob_type: str = "point") -> Dict[str, Any]:
    """
    Calculate normal distribution probabilities.

    Args:
        x: Value to calculate probability for
        mean: Mean of the normal distribution
        std_dev: Standard deviation of the normal distribution
        prob_type: Type of probability ("point", "cumulative", "survival")

    Returns:
        Dictionary with probability value and distribution info
    """
    if std_dev <= 0:
        raise ValueError("Standard deviation must be positive")
    if prob_type not in ["point", "cumulative", "survival"]:
        raise ValueError("prob_type must be 'point', 'cumulative', or 'survival'")

    normal_dist = stats.norm(mean, std_dev)

    if prob_type == "point":
        probability = normal_dist.pdf(x)
        description = f"f({x}) - probability density"
    elif prob_type == "cumulative":
        probability = normal_dist.cdf(x)
        description = f"P(X ≤ {x})"
    else:  # survival
        probability = normal_dist.sf(x)
        description = f"P(X > {x})"

    return {
        "probability": float(probability),
        "description": description,
        "x": x,
        "mean": mean,
        "std_dev": std_dev,
        "prob_type": prob_type,
        "z_score": (x - mean) / std_dev
    }

@mcp.tool()
def correlation_analysis(x_data: List[float], y_data: List[float]) -> Dict[str, Any]:
    """
    Perform correlation analysis between two datasets.

    Args:
        x_data: First dataset
        y_data: Second dataset

    Returns:
        Dictionary with correlation coefficients and analysis
    """
    if len(x_data) != len(y_data):
        raise ValueError("Both datasets must have the same length")
    if len(x_data) < 2:
        raise ValueError("Need at least 2 data points for correlation")

    x_arr = np.array(x_data)
    y_arr = np.array(y_data)

    pearson_corr, pearson_p = stats.pearsonr(x_arr, y_arr)
    spearman_corr, spearman_p = stats.spearmanr(x_arr, y_arr)

    return {
        "pearson_correlation": float(pearson_corr),
        "pearson_p_value": float(pearson_p),
        "spearman_correlation": float(spearman_corr),
        "spearman_p_value": float(spearman_p),
        "sample_size": int(len(x_data)),
        "interpretation": str(_interpret_correlation(pearson_corr))
    }

def _interpret_correlation(corr: float) -> str:
    """Helper function to interpret correlation strength."""
    abs_corr = abs(corr)
    if abs_corr < 0.1:
        return "Negligible correlation"
    elif abs_corr < 0.3:
        return "Weak correlation"
    elif abs_corr < 0.5:
        return "Moderate correlation"
    elif abs_corr < 0.7:
        return "Strong correlation"
    else:
        return "Very strong correlation"

@mcp.tool()
def hypothesis_test_ttest(sample_data: List[float], population_mean: float, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Perform one-sample t-test.

    Args:
        sample_data: Sample data for testing
        population_mean: Hypothesized population mean
        alpha: Significance level

    Returns:
        Dictionary with test results
    """
    if len(sample_data) < 2:
        raise ValueError("Need at least 2 data points for t-test")

    arr = np.array(sample_data)
    t_stat, p_value = stats.ttest_1samp(arr, population_mean)

    sample_mean = np.mean(arr)
    degrees_freedom = len(sample_data) - 1
    critical_value = stats.t.ppf(1 - alpha/2, degrees_freedom)

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "degrees_freedom": degrees_freedom,
        "critical_value": float(critical_value),
        "sample_mean": float(sample_mean),
        "population_mean": population_mean,
        "alpha": alpha,
        "significant": bool(p_value < alpha),
        "conclusion": "Reject H0" if p_value < alpha else "Fail to reject H0"
    }

@mcp.tool()
def linear_regression_analysis(x_data: List[float], y_data: List[float]) -> Dict[str, Any]:
    """
    Perform simple linear regression analysis.

    Args:
        x_data: Independent variable data
        y_data: Dependent variable data

    Returns:
        Dictionary with regression results
    """
    if len(x_data) != len(y_data):
        raise ValueError("Both datasets must have the same length")
    if len(x_data) < 2:
        raise ValueError("Need at least 2 data points for regression")

    x_arr = np.array(x_data)
    y_arr = np.array(y_data)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_arr, y_arr)

    # Calculate additional metrics
    y_pred = slope * x_arr + intercept
    mse = np.mean((y_arr - y_pred) ** 2)
    rmse = np.sqrt(mse)

    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value ** 2),
        "correlation_coefficient": float(r_value),
        "p_value": float(p_value),
        "standard_error": float(std_err),
        "mse": float(mse),
        "rmse": float(rmse),
        "equation": f"y = {slope:.4f}x + {intercept:.4f}"
    }

@mcp.tool()
def data_summary_from_csv_text(csv_text: str, delimiter: str = ",") -> Dict[str, Any]:
    """
    Generate summary statistics from CSV text data.

    Args:
        csv_text: CSV data as text
        delimiter: CSV delimiter

    Returns:
        Dictionary with data summary and statistics
    """
    try:
        from io import StringIO
        df = pd.read_csv(StringIO(csv_text), delimiter=delimiter)

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        summary = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": {}
        }

        # Add numeric summaries
        for col in numeric_cols:
            summary["numeric_summary"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "count": int(df[col].count())
            }

        return summary

    except Exception as e:
        raise ValueError(f"Error processing CSV data: {str(e)}")

@mcp.tool()
def binomial_probability(n: int, k: int, p: float, prob_type: str = "point") -> Dict[str, Any]:
    """
    Calculate binomial probability.

    Args:
        n: Number of trials
        k: Number of successes
        p: Probability of success on each trial
        prob_type: Type of probability ("point", "cumulative", "survival")

    Returns:
        Dictionary with probability value and distribution info
    """
    if not (0 <= p <= 1):
        raise ValueError("Probability p must be between 0 and 1")
    if n < 0 or k < 0:
        raise ValueError("n and k must be non-negative")
    if k > n:
        raise ValueError("k cannot be greater than n")
    if prob_type not in ["point", "cumulative", "survival"]:
        raise ValueError("prob_type must be 'point', 'cumulative', or 'survival'")

    binomial_dist = stats.binom(n, p)

    if prob_type == "point":
        probability = binomial_dist.pmf(k)
        description = f"P(X = {k})"
    elif prob_type == "cumulative":
        probability = binomial_dist.cdf(k)
        description = f"P(X ≤ {k})"
    else:  # survival
        probability = binomial_dist.sf(k)
        description = f"P(X > {k})"

    return {
        "probability": float(probability),
        "description": description,
        "n": n,
        "k": k,
        "p": p,
        "prob_type": prob_type,
        "mean": n * p,
        "variance": n * p * (1 - p),
        "std_dev": np.sqrt(n * p * (1 - p))
    }

def main():
    """Main entry point for the FastMCP Data Analysis Server."""
    mcp.run()

if __name__ == "__main__":
    main()