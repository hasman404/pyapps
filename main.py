import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


# Add the instructions markdown at the beginning of your code
instructions = """
## Loan Comparison Tool - Prodigy Finance vs Brain Capital

Welcome to the Loan Comparison Tool! Please note that this tool is designed for fun and educational purposes only (Also i am in the process of picking one of the 2 for my INSEAD MBA!). It likely contain bugs and hasn't been stress tested. Always consult with financial advisors or loan providers for accurate and personalized loan information.
For the prodigy loan I have used formulas for amortisation found online, additionally i have added the simple interest accrued during grace period + the admin fees. The results have a discrepancy of a few dollars from the values shown on Prodigy.
### Instructions:

1. Enter the variable interest (not APR) and loan amount quoted by Prodigy Finance. The loan amount you enter will be assumed for the Brain Capital comparison.

2. Brain Capital loans are capped at 2 times the loan amount. Enter your expected initial income and how much you expect it to increase over the years.

3. The cumulative graph will show which loan option may be more favorable. Additional detailed individual graphs are initially hidden and can be viewed by pressing the "Show Additional Curves" button.

### Disclaimer:

Please be aware that the calculations and results provided by this tool are based on formulas and assumptions i googled. They may not reflect the exact terms and conditions offered by financial institutions. This tool should not be considered as financial advice. Make sure to consult with financial professionals and loan providers for accurate and personalized loan information.

### Feedback:

If you have any suggestions or would like to see additional features added to the Loan Comparison Tool, please email us at hassnasir95@gmail.com.
"""
# Define a SessionState class to store the state of the button




# Defining functions for your calculations
def calculate_prodigy(apr_val, principal_val, duration_val):
    if apr_val < 0 or apr_val > 100:
        st.error("Error: APR value should be between 0 and 100.")
        return None, None

    if principal_val < 0:
        st.error("Error: Principal value should be a positive number.")
        return None, None

    if duration_val <= 0:
        st.error("Error: Duration value should be a positive number.")
        return None, None

    try:
        principal_with_fee = principal_val * 1.05  # Including 5% admin fee

        total_payments = duration_val * 12  #Total payments in months
        days_in_year = 365

        # Calculate simple interest during study and grace period
        days_study_grace = 18*30  # Assuming 18 months grace period
        interest_study_grace = principal_with_fee * ((apr_val/100) / days_in_year) * days_study_grace
        new_loan_amount=interest_study_grace+principal_with_fee

        monthly_interest_rate = apr_val / (12*100)

        monthly_payment = (new_loan_amount * monthly_interest_rate * (1+monthly_interest_rate)**(total_payments))/(((1+monthly_interest_rate)**total_payments)-1)





        total_paid = monthly_payment * total_payments






        return monthly_payment, total_paid
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None


def calculate_brain_capital(initial_income, annual_increase, interest_on_income, loan_amount_x2):
    try:
        total_repayment = 0
        total_years = 10
        yearly_payments = []
        monthly_payments = []

        for i in range(total_years):
            income = initial_income * ((1 + annual_increase) ** i)
            repayment = income * interest_on_income

            if total_repayment + repayment > loan_amount_x2:
                repayment = loan_amount_x2 - total_repayment
                total_repayment += repayment
                yearly_payments.append(repayment)
                monthly_payments.append(repayment / 12)
                # Append 0 to monthly_payments for the remaining years
                for _ in range(i+1, total_years):
                    monthly_payments.append(0)
                break
            else:
                total_repayment += repayment
                yearly_payments.append(repayment)
                monthly_payments.append(repayment / 12)

        return total_repayment, yearly_payments, monthly_payments
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None, None


# User inputs
st.sidebar.markdown(instructions)

# Initialize session state for storing the visibility of additional curves
if "additional_curves_visible" not in st.session_state:
    st.session_state.additional_curves_visible = False

col1, col2 = st.columns([1, 1])
with col1:

    st.header("Prodigy Finance Inputs")
    apr_val = st.number_input("Enter Variable Interest rate (Fixed + base rate)  (%):", min_value=0.0, max_value=100.0, value=10.0)
    principal_val = st.number_input("Enter Loan value ($)", min_value=0.0, max_value=500000.0, value=100000.0)
    st.markdown('**Note:** Prodigy %% admin fee is included, no need to add seperately. By default ths loan amount will be assumed for brain capital as well for fair comparison. There is an option to change this later.')
    duration_val = st.slider("Duration in Years", min_value=1, max_value=30, value=10)

    # Calculating and showing results
    monthly_payment, total_paid = calculate_prodigy(apr_val, principal_val, duration_val)
    if monthly_payment is not None and total_paid is not None:
        st.write(f'Monthly payment: ${monthly_payment:.2f}')
        st.write(f'Total payment over loan period: ${total_paid:.2f}')

    st.header("Brain Capital Inputs")
    st.markdown(
        "**Note:** The following calculations are based on the terms provided by Brain Capital. Each individual may receive unique loan terms. The maximum payment is capped at 2 times the loan amount. For a fair comparison, i set the loan amount in the Prodigy section. Please refer to your loan offer for the specific interest on income percentage and maximum loan amount.")
    initial_income = st.number_input("Enter initial income", min_value=0.0, max_value=500000.0, value=100000.0)
    annual_increase = st.slider("Enter annual increase percentage", min_value=0.0, max_value=100.0, value=4.0) / 100
    st.markdown('**Note:** This slider represents your estimated yearly salary increase percentage. '
                'Adjust it based on your own career expectations. Remember, salary progression may not be linear and can vary based on industry, '
                'role, and economic conditions.')
    interest_on_income = st.number_input("Enter interest on income percentage", min_value=0.0, max_value=100.0,
                                   value=10.0) / 100
    loan_amount_x2 = st.number_input("Brain Capital Loan Amount Cap:", min_value=0.0, max_value=1000000.0,
                                     value=2 * principal_val)
    total_repayment, yearly_payments, monthly_payments = calculate_brain_capital(initial_income, annual_increase,
                                                                                 interest_on_income, loan_amount_x2)
    st.write(f'Total repayment: €{total_repayment:.2f}')



# Prodigy cumulative payments
prodigy_cumulative_payments = [monthly_payment * i for i in range(1, int(duration_val * 12) + 1)]

# Create a DataFrame with the cumulative payments data
df_prodigy_cumulative = pd.DataFrame({
    'Month': list(range(1, len(prodigy_cumulative_payments) + 1)),
    'Cumulative Payments': prodigy_cumulative_payments
})
# Create interactive line chart

# Display the interactive line charts in Streamlit



# Brain Capital cumulative payments
# Brain Capital cumulative payments
monthly_cumulative_payments = []
cumulative_payment = 0

for monthly_payment in monthly_payments:
    for _ in range(12):
        cumulative_payment += monthly_payment
        monthly_cumulative_payments.append(cumulative_payment)

# Create a DataFrame with the cumulative payments data
df_brain_cumulative = pd.DataFrame({
    'Month': list(range(1, len(monthly_cumulative_payments) + 1)),  # Start from month 1
    'Cumulative Payments': monthly_cumulative_payments
})




# Create interactive line chart


# Display the interactive line charts in Streamlit


# Create a DataFrame with the yearly payments data and gross salary data
df_yearly_with_salary = pd.DataFrame({
    'Year': list(range(1, len(yearly_payments)+1)),
    'Payments': yearly_payments,
    'Gross Salary': [initial_income * ((1 + annual_increase) ** (i-1)) for i in range(1, len(yearly_payments)+1)]
})

# Create a DataFrame with the monthly payments data
df_monthly_with_salary = pd.DataFrame({
    'Year': list(range(1, len(monthly_payments)+1)),
    'Payments': monthly_payments,
    'Gross Salary': [initial_income * ((1 + annual_increase) ** (i-1)) for i in range(1, len(monthly_payments)+1)]
})

# Create the yearly payments line chart
fig_yearly = go.Figure()

# Add yearly payments line
fig_yearly.add_trace(go.Scatter(x=df_yearly_with_salary['Year'], y=df_yearly_with_salary['Payments'], name='Yearly Payments',
                               line=dict(color='blue', width=2)))

# Add gross salary bar chart on secondary y-axis
fig_yearly.add_trace(go.Bar(x=df_yearly_with_salary['Year'], y=df_yearly_with_salary['Gross Salary'], name='Gross Salary',
                           yaxis='y2', marker=dict(color='rgba(0, 128, 0, 0.7)')))

# Update layout
fig_yearly.update_layout(
    title='Yearly Payments with Gross Salary',
    xaxis=dict(title='Year'),
    yaxis=dict(title='Payments'),
    yaxis2=dict(title='Gross Salary', overlaying='y', side='right'),
)


# Create the monthly payments line chart
fig_monthly = go.Figure()

# Add monthly payments line
fig_monthly.add_trace(go.Scatter(x=df_monthly_with_salary['Year'], y=df_monthly_with_salary['Payments'],
                                name='Monthly Payments', line=dict(color='blue', width=2)))

# Add gross salary bar chart on secondary y-axis
fig_monthly.add_trace(go.Bar(x=df_monthly_with_salary['Year'], y=df_monthly_with_salary['Gross Salary'],
                            name='Gross Salary', yaxis='y2', marker=dict(color='rgba(0, 128, 0, 0.7)')))

# Update layout
fig_monthly.update_layout(
    title='Monthly Payments with Gross Salary',
    xaxis=dict(title='Year'),
    yaxis=dict(title='Payments'),
    yaxis2=dict(title='Gross Salary', overlaying='y', side='right'),
)


# Create interactive line charts
fig_prodigy_cumulative = px.line(df_prodigy_cumulative, x='Month', y='Cumulative Payments', title='Prodigy Cumulative Payments')



#fig_yearly = px.line(df_yearly_with_salary, x='Year', y='Payments', title='Brain Capital Yearly Payments')
#fig_monthly = px.line(df_monthly_with_salary, x='Year', y='Payments', title='Brain Capital Monthly Payments')
# Create bar chart for gross salary
#fig_gross_salary = px.bar(df_yearly_with_salary, x='Year', y='Gross Salary', title='Gross Salary')

fig_brain_cumulative = px.line(df_brain_cumulative, x='Month', y='Cumulative Payments', title='Brain Capital Cumulative Payments')




# Add a new column to both dataframes to label the source of the data
df_prodigy_cumulative['Source'] = 'Prodigy'
df_brain_cumulative['Source'] = 'Brain Capital'

# Combine the dataframes
df_combined_cumulative = pd.concat([df_prodigy_cumulative, df_brain_cumulative])

# Create a combined interactive line chart
fig_combined_cumulative = px.line(df_combined_cumulative,
                                  x='Month',
                                  y='Cumulative Payments',
                                  color='Source',
                                  title='Prodigy vs Brain Capital Cumulative Payments')

# Display the combined interactive line chart in Streamlit
#st.header('Combined Prodigy and Brain Capital Cumulative Payments')
with col2:
    st.plotly_chart(fig_combined_cumulative)

    # Add a button to show additional curves
    if st.button("Show Additional Curves"):
        st.session_state.additional_curves_visible = not st.session_state.additional_curves_visible

    # Check if additional curves should be visible
    if st.session_state.additional_curves_visible:
        # Display the additional curves
        st.plotly_chart(fig_yearly)
        st.plotly_chart(fig_monthly)
        st.plotly_chart(fig_brain_cumulative)
        st.plotly_chart(fig_prodigy_cumulative)

