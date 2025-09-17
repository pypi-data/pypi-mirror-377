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
        Dictionary containing probability result and parameters
    """
    if lam <= 0:
        raise ValueError("Lambda must be positive")
    if k < 0:
        raise ValueError("k must be non-negative")
    if prob_type not in ["point", "cumulative", "survival"]:
        raise ValueError("prob_type must be 'point', 'cumulative', or 'survival'")

    if prob_type == "point":
        prob = stats.poisson.pmf(k, lam)
    elif prob_type == "cumulative":
        prob = stats.poisson.cdf(k, lam)
    else:  # survival
        prob = stats.poisson.sf(k, lam)

    return {
        "probability": float(prob),
        "lambda": lam,
        "k": k,
        "prob_type": prob_type,
        "mean": lam,
        "variance": lam
    }

@mcp.tool()
def normal_probability(mean: float, std: float, x: float, prob_type: str = "pdf") -> Dict[str, Any]:
    """
    Calculate normal distribution probability.

    Args:
        mean: Mean of the distribution
        std: Standard deviation (must be positive)
        x: Value to calculate probability for
        prob_type: Type of calculation ("pdf", "cdf", "survival")

    Returns:
        Dictionary containing probability result and parameters
    """
    if std <= 0:
        raise ValueError("Standard deviation must be positive")
    if prob_type not in ["pdf", "cdf", "survival"]:
        raise ValueError("prob_type must be 'pdf', 'cdf', or 'survival'")

    if prob_type == "pdf":
        prob = stats.norm.pdf(x, mean, std)
    elif prob_type == "cdf":
        prob = stats.norm.cdf(x, mean, std)
    else:  # survival
        prob = stats.norm.sf(x, mean, std)

    return {
        "probability": float(prob),
        "mean": mean,
        "std": std,
        "x": x,
        "prob_type": prob_type,
        "variance": std**2
    }

@mcp.tool()
def binomial_probability(n: int, p: float, k: int, prob_type: str = "point") -> Dict[str, Any]:
    """
    Calculate binomial probability.

    Args:
        n: Number of trials (must be positive)
        p: Probability of success (0 <= p <= 1)
        k: Number of successes
        prob_type: Type of probability ("point", "cumulative", "survival")

    Returns:
        Dictionary containing probability result and parameters
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= p <= 1:
        raise ValueError("p must be between 0 and 1")
    if not 0 <= k <= n:
        raise ValueError("k must be between 0 and n")
    if prob_type not in ["point", "cumulative", "survival"]:
        raise ValueError("prob_type must be 'point', 'cumulative', or 'survival'")

    if prob_type == "point":
        prob = stats.binom.pmf(k, n, p)
    elif prob_type == "cumulative":
        prob = stats.binom.cdf(k, n, p)
    else:  # survival
        prob = stats.binom.sf(k, n, p)

    return {
        "probability": float(prob),
        "n": n,
        "k": k,
        "p": p,
        "prob_type": prob_type,
        "mean": n * p,
        "variance": n * p * (1 - p),
        "std_dev": np.sqrt(n * p * (1 - p))
    }

@mcp.tool()
def descriptive_statistics(data: List[float]) -> Dict[str, Any]:
    """
    Calculate comprehensive descriptive statistics for a dataset.

    Args:
        data: List of numerical values

    Returns:
        Dictionary containing various statistical measures
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    arr = np.array(data)
    
    return {
        "count": len(data),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "mode": float(stats.mode(arr, keepdims=True)[0][0]) if len(set(data)) < len(data) else None,
        "std_dev": float(np.std(arr, ddof=1)) if len(data) > 1 else 0.0,
        "variance": float(np.var(arr, ddof=1)) if len(data) > 1 else 0.0,
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
def correlation_analysis(x: List[float], y: List[float], method: str = "pearson") -> Dict[str, Any]:
    """
    Calculate correlation between two variables.

    Args:
        x: First variable data
        y: Second variable data
        method: Correlation method ("pearson" or "spearman")

    Returns:
        Dictionary containing correlation coefficient and p-value
    """
    if not x or not y:
        raise ValueError("Both datasets must be non-empty")
    if len(x) != len(y):
        raise ValueError("Both datasets must have the same length")
    if method not in ["pearson", "spearman"]:
        raise ValueError("Method must be 'pearson' or 'spearman'")

    if method == "pearson":
        corr, p_value = stats.pearsonr(x, y)
    else:  # spearman
        corr, p_value = stats.spearmanr(x, y)

    return {
        "correlation": float(corr),
        "p_value": float(p_value),
        "method": method,
        "sample_size": len(x),
        "significant": p_value < 0.05
    }

@mcp.tool()
def one_sample_ttest(data: List[float], population_mean: float, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Perform one-sample t-test.

    Args:
        data: Sample data
        population_mean: Hypothesized population mean
        alpha: Significance level (default 0.05)

    Returns:
        Dictionary containing test results
    """
    if not data:
        raise ValueError("Data cannot be empty")
    if len(data) < 2:
        raise ValueError("Need at least 2 data points for t-test")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1")

    t_stat, p_value = stats.ttest_1samp(data, population_mean)
    
    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "degrees_of_freedom": len(data) - 1,
        "sample_mean": float(np.mean(data)),
        "population_mean": population_mean,
        "alpha": alpha,
        "significant": p_value < alpha,
        "reject_null": p_value < alpha
    }

@mcp.tool()
def linear_regression(x: List[float], y: List[float]) -> Dict[str, Any]:
    """
    Perform simple linear regression.

    Args:
        x: Independent variable data
        y: Dependent variable data

    Returns:
        Dictionary containing regression results
    """
    if not x or not y:
        raise ValueError("Both datasets must be non-empty")
    if len(x) != len(y):
        raise ValueError("Both datasets must have the same length")
    if len(x) < 2:
        raise ValueError("Need at least 2 data points for regression")

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Calculate additional metrics
    y_pred = np.array(x) * slope + intercept
    mse = np.mean((np.array(y) - y_pred) ** 2)
    
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value ** 2),
        "correlation": float(r_value),
        "p_value": float(p_value),
        "std_error": float(std_err),
        "mse": float(mse),
        "equation": f"y = {slope:.4f}x + {intercept:.4f}",
        "sample_size": len(x)
    }

@mcp.tool()
def analyze_csv_data(csv_text: str) -> Dict[str, Any]:
    """
    Analyze CSV data and provide comprehensive summary.

    Args:
        csv_text: CSV data as text string

    Returns:
        Dictionary containing data analysis results
    """
    if not csv_text.strip():
        raise ValueError("CSV text cannot be empty")

    try:
        # Read CSV from string
        from io import StringIO
        df = pd.read_csv(StringIO(csv_text))
        
        if df.empty:
            raise ValueError("CSV contains no data")

        results = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_columns": [],
            "categorical_columns": [],
            "numeric_summary": {},
            "categorical_summary": {}
        }

        # Identify numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        results["numeric_columns"] = numeric_cols
        results["categorical_columns"] = categorical_cols

        # Numeric summary
        if numeric_cols:
            numeric_summary = df[numeric_cols].describe()
            results["numeric_summary"] = numeric_summary.to_dict()

        # Categorical summary
        if categorical_cols:
            cat_summary = {}
            for col in categorical_cols:
                cat_summary[col] = {
                    "unique_count": df[col].nunique(),
                    "most_frequent": df[col].mode().iloc[0] if not df[col].mode().empty else None,
                    "frequency_count": df[col].value_counts().head().to_dict()
                }
            results["categorical_summary"] = cat_summary

        return results

    except Exception as e:
        raise ValueError(f"Error processing CSV data: {str(e)}")

def main():
    """Main entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()