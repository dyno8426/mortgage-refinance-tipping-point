## 🏡 Mortgage Refinance Tipping Point Calculator

This Python command-line utility provides a comprehensive financial analysis to determine the precise interest rate at which refinancing a 30-year fixed mortgage becomes financially beneficial. This critical rate is often referred to as the **tipping point** or **break-even point**. The tool is specifically designed to account for a **defined time horizon until sale** (e.g., 5 or 10 years) versus the traditional calculation over the entire life of the loan.

The tool helps homeowners address a critical financial question: "What is the **minimum interest rate drop** required to make refinancing worthwhile given a specific moving timeline?"

-----

### 🌟 How This Tool Helps: Modeling the Core Trade-Off

The decision to refinance a loan involves a key financial trade-off that goes beyond just looking at the difference in the monthly payment. A core concern for borrowers is the perceived **wasting of initial payments** that heavily focused on interest. This tool clarifies the financial logic by focusing on the **Total Cost** of both options from the point of refinancing forward.

#### The Underlying Financial Trade-Off

The code models the trade-off between **Lower Interest Rate Savings** and **Increased Principal Cost**:

1.  **Gain (Lower Interest Rate):** A new, lower interest rate reduces the interest paid on the remaining principal balance, leading to cumulative savings.
2.  **Cost (Closing Fees):** Refinancing incurs **closing costs** (typically 2% of the loan principal) which are **rolled into the new loan balance**. This immediately increases the principal, resulting in the borrower paying *more interest* on the fees over the life of the new loan.

#### Clarifying the Total Cost Comparison

The analysis compares the total financial commitment from the present date onward.

  * **Original Loan Commitment:** The total remaining money paid without refinancing is:
    `Original Cost = (Remaining Principal) + (Total Remaining Interest)`

  * **Refinancing Commitment (Lifetime View):** The total cost of the refinanced loan, reflecting the borrower's goal of ensuring the total cost of the "reset" loan is less than the original remaining commitment. The code uses the most accurate measure: **Total Payments (P\&I)** over the life of the loan. The cost is:
    `Refi Cost = Sum of (All P&I Payments on New Loan)`
    *(This sum is based on the new, higher principal amount that includes the rolled-in fees).*

The tool is designed to find the maximum new rate where **Refi Cost** is lower than the **Original Cost**.

-----

### 📉 Critical Financial Metrics

The tool calculates two specific tipping points and, for every rate in the output table, computes **four key performance indicators (KPIs)**:

#### 1\. Performance Indicators Calculated Per Rate

The following metrics are computed for each potential new interest rate shown in the output table:

  * **Monthly P\&I Savings:** The simple monthly reduction in the Principal and Interest payment compared to the original loan.
  * **Break-Even Period (Months):** Also known as the **payback period**, this is the number of months required for the cumulative monthly savings to exactly recoup the closing fees rolled into the loan.
    `Break-Even Months = Closing Costs / Monthly P&I Savings`
  * **Savings at Sale:** The **net financial gain or loss** realized if the property is sold exactly at the user-defined time horizon. This is calculated by comparing the total cash outflow (payments + remaining principal) of the original loan versus the refinanced loan up to the sale date.
  * **Savings Lifetime:** The **total net financial gain or loss** realized over the entire 30-year term if the property is held for the full duration. This compares the total remaining P\&I payments on the original loan against the total P\&I payments on the new 30-year refinanced loan.

#### 2\. Tipping Point / Break-Even Point (Rate Thresholds)

The "tipping point" is the **maximum new interest rate** at which the total cost of the refinanced loan equals the total cost of keeping the original loan. Any rate below this point results in a net financial gain.

The tool calculates two specific tipping points:

  * **Time-to-Sell Tipping Point (Practical):** This is the threshold for borrowers planning to sell the property within a defined timeframe. It is the rate that minimizes the **Total Cash Outflow** in the short term. The cost is the sum of **P\&I Payments Made Before Sale** and the **Remaining Principal at the Sale Date**.
  * **Entire Loan Lifetime Tipping Point (Theoretical):** This is the rate where the **sum of all P\&I payments on the refinanced loan** (30 years) is less than the sum of the remaining P\&I payments on the original loan.

-----

### 🔎 SEO and Financial Context

This tool is a crucial resource for **mortgage rate analysis** and **refinancing calculation**. Understanding the **tipping point rate** is key to smart financial planning. Whether evaluating a **cash-out refinance**, a simple **rate-and-term refinance**, or simply tracking the **best time to refinance**, this calculator provides the objective data needed. It answers the common question: "What is my **refinance break-even rate**?" by quantifying the **opportunity cost** of the closing fees against potential long-term interest savings. Use this utility to determine the financial wisdom of **lowering an interest rate** on a **30-year fixed mortgage**.

-----

### 🚀 Getting Started (Command-Line Usage)

The script relies on Python and the `numpy`, `argparse`, and `python-dateutil` libraries.

#### Installation

```bash
# Clone the repository
git clone [repository URL]
cd [repository directory]

# Install required packages
pip install numpy python-dateutil
```

#### Running the Analysis

Execute the script, passing the loan details as arguments.

```bash
python refi_calculator.py \
  --amount [ORIGINAL_LOAN_AMOUNT] \
  --rate [CURRENT_RATE] \
  --paid [PAYMENTS_MADE] \
  --sell-year [SALE_YEAR] \
  --sell-month [SALE_MONTH]
```

#### Example (Using the default parameters):

The following command uses the original scenario: $697,000 at 6.625%, 4 payments made, selling in July 2035 (120 total payments).

```bash
python refi_calculator.py --amount 697000 --rate 6.625 --paid 4 --sell-year 2035 --sell-month 7
```

#### Key Arguments

| Argument | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--amount` | `float` | Original total loan amount. | `697000.00` |
| `--rate` | `float` | Current interest rate (e.g., 6.625). | `6.625` |
| `--paid` | `int` | Number of payments already made. | `4` |
| `--sell-year`| `int` | Planned year of sale (e.g., 2035). | `2035` |
| `--sell-month`| `int` | Planned month of sale (1=Jan, 12=Dec). | `7` (July) |
| `--term` | `int` | Original loan term in months (e.g., 360). | `360` |
| `--costs-pct`| `float` | Closing costs as a % of remaining principal (e.g., 0.02 for 2%). | `0.02` |

-----

### ⚙️ Contextual Assumptions and Limitations

#### Mortgage Model Assumptions (US Real Estate)

1.  **30-Year Fixed Term:** Both the original loan and the refinanced loan are assumed to be standard 30-year (360-month) fixed-rate mortgages.
2.  **Amortization:** All calculations use the standard US amortization formula, where monthly payments are constant and interest is compounded monthly on the unpaid principal balance.
3.  **Refi Costs:** Closing costs are modeled as a fixed percentage (`--costs-pct`) of the **remaining principal** and are **100% rolled into the new loan's principal**. The new loan amount is: `Remaining Principal + Closing Costs`.
4.  **Payment Timing:** The script accurately infers the **First Payment Date** (e.g., August 2025) based on the current date (Nov 2025) and the number of payments made (`--paid`) to calculate the exact number of total payments until the sale date.

#### Modeled Limitations (Accuracy)

  * **P&I Only:** The analysis focuses strictly on Principal and Interest (P&I) payments.
  * **Total Cost at Sale:** The "Time-to-Sell" tipping point correctly models the total net cost: $(\text{Total P&I Payments}) + (\text{Remaining Principal at Sale})$.

#### Unmodeled Limitations (Simplifications)

The following real-world factors are **NOT** included in this model:

  * **Taxes and Insurance (Escrow):** These are assumed to be constant and are ignored.
  * **Discount Points:** The cost or benefit of **buying down the rate** (paying points upfront) is **not** included.
  * **Time Value of Money (Discounting):** The analysis is done in **nominal dollars** (total cost) and does not account for the opportunity cost of having cash now versus later.