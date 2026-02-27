import streamlit as st
import numpy as np
from statistics import stdev
from scipy import stats
from scipy.stats import t

# --- 1. Page Configuration ---
st.set_page_config(page_title="T-Test Calculator", page_icon="🧪", layout="wide")

# --- 2. Core Math Function ---
def two_sample(a, b, alternative):
    xbar1, xbar2 = np.mean(a), np.mean(b)
    sd1, sd2 = stdev(a), stdev(b)
    n1, n2 = len(a), len(b)
    alpha = 0.05 / 2
    df = n1 + n2 - 2
    
    se = np.sqrt((sd1**2)/n1 + (sd2**2)/n2)
    t_table_pos = t.ppf(1-alpha, df)
    t_table_neg = t.ppf(alpha, df)
    tcal = ((xbar1 - xbar2) - 0) / se
    
    if alternative == "two-sided":
        p_val = 2 * (1 - t.cdf(abs(tcal), df))
    elif alternative == "left":
        p_val = t.cdf(tcal, df)
    elif alternative == "right":
        p_val = 1 - t.cdf(tcal, df)
        
    scipy_result = stats.ttest_ind(a, b, equal_var=False, alternative=alternative)
    
    return {
        "tcal": tcal, "p_val": p_val, 
        "t_crit_pos": t_table_pos, "t_crit_neg": t_table_neg,
        "scipy_stat": scipy_result.statistic, "scipy_pval": scipy_result.pvalue,
        "mean_a": xbar1, "mean_b": xbar2, "df": df
    }

# --- 3. App Layout & UI ---
st.title("🧪 Two-Sample T-Test Calculator")
st.markdown("Enter your sample data in the sidebar to calculate the t-statistic and p-value.")

# Sidebar for Inputs
with st.sidebar:
    st.header("📊 Input Parameters")
    
    sample_a_input = st.text_area("Sample A Data (comma-separated)", "10, 12, 14, 15, 18, 20")
    sample_b_input = st.text_area("Sample B Data (comma-separated)", "8, 9, 11, 13, 14, 15")
    
    alternative_input = st.selectbox(
        "Alternative Hypothesis", 
        options=["two-sided", "left", "right"],
        help="Choose the direction of your hypothesis test."
    )
    
    calculate_btn = st.button("Calculate T-Test", type="primary", use_container_width=True)

# --- 4. Process & Display Results ---
if calculate_btn:
    try:
        # Convert strings to lists of floats
        list_a = [float(x.strip()) for x in sample_a_input.split(",")]
        list_b = [float(x.strip()) for x in sample_b_input.split(",")]
        
        if len(list_a) < 2 or len(list_b) < 2:
            st.error("Please enter at least two numbers for each sample to calculate standard deviation.")
        else:
            # Run calculations
            res = two_sample(list_a, list_b, alternative_input)
            
            st.success("Calculations complete!")
            
            # Top-level metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Sample A Mean", f"{res['mean_a']:.2f}")
            col2.metric("Sample B Mean", f"{res['mean_b']:.2f}")
            col3.metric("Degrees of Freedom", f"{res['df']}")
            
            st.divider()
            
            # Detailed Results Columns
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.subheader("Manual Calculation")
                st.info(f"""
                **T-Statistic:** `{res['tcal']:.4f}`  
                **P-Value:** `{res['p_val']:.4f}`  
                **Critical Value (+):** `{res['t_crit_pos']:.4f}`  
                **Critical Value (-):** `{res['t_crit_neg']:.4f}`
                """)
                
            with res_col2:
                st.subheader("SciPy Verification")
                st.info(f"""
                **T-Statistic:** `{res['scipy_stat']:.4f}`  
                **P-Value:** `{res['scipy_pval']:.4f}`  
                *(Using Welch's t-test with unequal variance)*
                """)

    except ValueError:
        st.error("Invalid input detected. Please ensure you only enter numbers separated by commas (e.g., 1.5, 2.3, 4.0).")
        