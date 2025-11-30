import numpy as np
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys # Keep sys for exiting on errors

# --- UTILITY FUNCTIONS ---

def calculate_pmt(principal, annual_rate, months):
    """Calculates the fixed monthly principal and interest payment."""
    if annual_rate <= 0:
        return principal / months
    r = annual_rate / 100 / 12
    # Standard mortgage payment formula
    return principal * (r * (1 + r)**months) / ((1 + r)**months - 1)

def get_loan_status(principal, annual_rate, total_months, payments_made):
    """Calculates the remaining balance and remaining interest after a number of payments."""
    balance = principal
    r = annual_rate / 100 / 12
    pmt = calculate_pmt(principal, annual_rate, total_months)
    
    for _ in range(1, payments_made + 1):
        interest = balance * r
        principal_pay = pmt - interest
        balance -= principal_pay
        
    # Calculate total remaining interest on the original loan
    remaining_interest = (pmt * (total_months - payments_made)) - balance
        
    return balance, pmt, remaining_interest

def calculate_total_payments_until_sale(payments_made, sell_year, sell_month):
    """
    Calculates the total number of payments made from loan start until the sale date.
    
    Assumes current date is Nov 2025 (after 4th payment).
    """
    
    CURRENT_YEAR = 2025
    CURRENT_MONTH = 11

    # Calculate the month/year of the first payment
    first_payment_date = datetime(CURRENT_YEAR, CURRENT_MONTH, 1) - relativedelta(months=payments_made - 1)
    
    # Sale date (assuming payment is made in this month)
    sale_date = datetime(sell_year, sell_month, 1)

    # Total number of full payment months between P1 and Sale Date (inclusive)
    total_months = 12 * (sale_date.year - first_payment_date.year) + (sale_date.month - first_payment_date.month) + 1

    if total_months < payments_made:
        raise ValueError(
            f"The calculated sale date ({sale_date.strftime('%b %Y')}) is before the current payment date, "
            f"resulting in only {total_months} total payments."
        )

    return total_months, first_payment_date.strftime('%b %Y')

# --- MAIN ANALYSIS FUNCTION ---

def run_analysis(args):
    """Runs the two tipping point analyses using parsed arguments."""

    original_loan_amount = args.amount
    original_rate = args.rate
    original_term_months = args.term
    payments_made = args.paid
    sell_year = args.sell_year
    sell_month = args.sell_month
    closing_cost_pct = args.costs_pct
    
    try:
        months_until_sale, first_pmt_date_str = calculate_total_payments_until_sale(
            payments_made, sell_year, sell_month
        )
    except ValueError as e:
        print(f"Error in calculating sale period: {e}")
        sys.exit(1)

    # --- 1. Calculate Original Loan Status ---
    remaining_principal, pmt_orig, remaining_interest_orig = get_loan_status(
        original_loan_amount, original_rate, original_term_months, payments_made
    )
    
    # Constants derived from inputs
    closing_costs = remaining_principal * closing_cost_pct
    cost_refi_loan_amt = remaining_principal + closing_costs
    refi_payments_until_sale = months_until_sale - payments_made

    # --- 2. Calculate Original Loan Cost at Sale (Benchmark) ---
    rem_principal_orig_sale, _, _ = get_loan_status(
        original_loan_amount, original_rate, original_term_months, months_until_sale
    )
    total_payments_orig_at_sale = pmt_orig * months_until_sale
    total_cost_orig_at_sale = total_payments_orig_at_sale + rem_principal_orig_sale

    # --- 3. Iterative Search for Tipping Points ---
    tipping_rate_sale = None
    tipping_rate_lifetime = None
    search_rates = np.arange(original_rate, 2.99, -0.001)

    for r_new in search_rates:
        pmt_refi = calculate_pmt(cost_refi_loan_amt, r_new, 360)

        # A. Lifetime Tipping Point Check
        total_payments_orig_remaining = pmt_orig * (original_term_months - payments_made)
        total_payments_refi_lifetime = pmt_refi * 360

        if total_payments_refi_lifetime < total_payments_orig_remaining and tipping_rate_lifetime is None:
             tipping_rate_lifetime = r_new

        # B. Time-to-Sell Tipping Point Check
        rem_principal_refi_sale, _, _ = get_loan_status(
            cost_refi_loan_amt, r_new, 360, refi_payments_until_sale
        )
        total_payments_refi_at_sale = (pmt_orig * payments_made) + (pmt_refi * refi_payments_until_sale)
        total_cost_refi_at_sale = total_payments_refi_at_sale + rem_principal_refi_sale
        
        if total_cost_refi_at_sale < total_cost_orig_at_sale and tipping_rate_sale is None:
            tipping_rate_sale = r_new
    
    # Handle cases where tipping points are not found
    if tipping_rate_sale is None: tipping_rate_sale = original_rate
    if tipping_rate_lifetime is None: tipping_rate_lifetime = original_rate

    # --- 4. Generate Output Table Data ---
    table_rates = sorted(list(set([
        round(tipping_rate_sale + 0.075, 3), 
        round(tipping_rate_sale, 3), 
        round(tipping_rate_sale - 0.25, 3),
        round(tipping_rate_lifetime, 3),
        round(tipping_rate_lifetime - 0.25, 3)
    ])))
    table_rates = [r for r in table_rates if r < original_rate]
    table_rates = sorted(list(set(table_rates)), reverse=True)
    
    table_data = [] 
    
    for r_new in table_rates:
        pmt_refi = calculate_pmt(cost_refi_loan_amt, r_new, 360)
        monthly_savings = pmt_orig - pmt_refi

        # Savings at Sale
        rem_principal_refi_sale, _, _ = get_loan_status(cost_refi_loan_amt, r_new, 360, refi_payments_until_sale)
        total_payments_refi_at_sale = (pmt_orig * payments_made) + (pmt_refi * refi_payments_until_sale)
        savings_at_sale = total_cost_orig_at_sale - (total_payments_refi_at_sale + rem_principal_refi_sale)
        
        # Savings Lifetime
        total_payments_orig_remaining = pmt_orig * (original_term_months - payments_made)
        total_payments_refi_lifetime = pmt_refi * 360
        savings_lifetime = total_payments_orig_remaining - total_payments_refi_lifetime

        table_data.append({
            'rate': r_new,
            'monthly_savings': monthly_savings,
            'savings_at_sale': savings_at_sale,
            'savings_lifetime': savings_lifetime
        })

    # --- 5. Print Results ---
    print("## 📊 Mortgage Refinance Tipping Point Analysis 🏡")
    print("-" * 50)
    print("### 📌 Input Parameters")
    print(f"| Parameter | Value |")
    print(f"| :--- | :--- |")
    print(f"| Original Loan Amount | ${original_loan_amount:,.2f} |")
    print(f"| Current Interest Rate | {original_rate}% |")
    print(f"| Loan Start (First Payment) | {first_pmt_date_str} |")
    print(f"| Payments Made | {payments_made} |")
    print(f"| Sale Date | {datetime(sell_year, sell_month, 1).strftime('%b %Y')} |")
    print(f"| **Total Payments Until Sale** | **{months_until_sale}** |")
    print(f"| Estimated Closing Costs (Rolled In) | ${closing_costs:,.2f} |")

    print("\n### 📉 Critical Tipping Points")
    print(f"| Tipping Point | Required New Rate | Required Rate Drop |")
    print(f"| :--- | :--- | :--- |")
    print(f"| **Time-to-Sell** ({months_until_sale} months) | **{tipping_rate_sale:.3f}%** | **{(original_rate - tipping_rate_sale):.3f}%** |")
    print(f"| **Entire Loan Lifetime** (30 Years) | **{tipping_rate_lifetime:.3f}%** | **{(original_rate - tipping_rate_lifetime):.3f}%** |")
    
    print("\n### 📈 Refinance Comparison Table")
    print("| New Rate | Monthly P&I Savings | Savings at Sale | Savings Lifetime |")
    print("| :--- | :--- | :--- | :--- |")
    
    for row in table_data:
        rate_str = f"**{row['rate']:.3f}%**" if row['rate'] <= tipping_rate_sale else f"{row['rate']:.3f}%"
        
        sale_str = f"${row['savings_at_sale']:,.2f}"
        lifetime_str = f"${row['savings_lifetime']:,.2f}"
        
        sale_status = " (LOSS)" if row['savings_at_sale'] < 0.01 and abs(row['savings_at_sale']) > 0.01 else " (GAIN)"
        lifetime_status = " (LOSS)" if row['savings_lifetime'] < 0.01 and abs(row['savings_lifetime']) > 0.01 else " (GAIN)"
        
        print(f"| {rate_str} | ${row['monthly_savings']:,.2f} | {sale_str}{sale_status} | {lifetime_str}{lifetime_status} |")

# --- COMMAND LINE ARGUMENT PARSING ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate mortgage refinance tipping points based on a specific time-to-sell horizon.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Defaults are based on the current scenario
    parser.add_argument('--amount', type=float, default=697000.00, help="Original loan amount. (Default: 697000.00)")
    parser.add_argument('--rate', type=float, default=6.625, help="Original interest rate (e.g., 6.625). (Default: 6.625)")
    parser.add_argument('--term', type=int, default=360, help="Original loan term in months (e.g., 360 for 30 years). (Default: 360)")
    parser.add_argument('--paid', type=int, default=4, help="Number of payments already made. (Default: 4)")
    
    # Sell date defaults to July 2035 to result in 120 total payments (10 years)
    parser.add_argument('--sell-year', type=int, default=2035, help="Planned year of sale (e.g., 2035). (Default: 2035)")
    parser.add_argument('--sell-month', type=int, default=7, choices=range(1, 13), help="Planned month of sale (1=Jan, 12=Dec). (Default: 7)")
    
    parser.add_argument('--costs-pct', type=float, default=0.02, help="Closing costs as a percentage of remaining principal (e.g., 0.02 for 2%%). (Default: 0.02)")

    args = parser.parse_args()
    run_analysis(args)
