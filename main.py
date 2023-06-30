import streamlit as st
import plotly.express as px
import pandas as pd


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
        monthly_interest_rate = apr_val / 100 / 12
        total_payments = duration_val * 12

        numerator = monthly_interest_rate * principal_with_fee
        denominator = 1 - (1 + monthly_interest_rate) ** (-total_payments)
        monthly_payment = numerator / denominator
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
st.header("Prodigy Finance Calculator")
apr_val = st.slider("Enter APR (%) value", min_value=0.0, max_value=100.0, value=10.0)
principal_val = st.number_input("Enter Loan value (usd)", min_value=0.0, max_value=500000.0, value=100000.0)
st.markdown('**Note:** This loan amount will be assumed for brain capital as well for fair comparison. Brain capital will only use this loan amount to set a max cap')
duration_val = st.slider("Enter Duration value", min_value=1, max_value=30, value=10)

# Calculating and showing results
monthly_payment, total_paid = calculate_prodigy(apr_val, principal_val, duration_val)
if monthly_payment is not None and total_paid is not None:
    st.write(f'Monthly payment: ${monthly_payment:.2f}')
    st.write(f'Total payment over loan period: ${total_paid:.2f}')

# Prodigy cumulative payments
prodigy_cumulative_payments = [monthly_payment * (i + 1) for i in range(int(duration_val * 12))]

# Create a DataFrame with the cumulative payments data
df_prodigy_cumulative = pd.DataFrame({
    'Month': list(range(1, len(prodigy_cumulative_payments) + 1)),
    'Cumulative Payments': prodigy_cumulative_payments
})
# Create interactive line chart
fig_prodigy_cumulative = px.line(df_prodigy_cumulative, x='Month', y='Cumulative Payments', title='Prodigy Cumulative Payments')
# Display the interactive line charts in Streamlit
st.plotly_chart(fig_prodigy_cumulative)




st.header("Brain Capital Calculator")
st.markdown("**Note:** The following calculations are based on the terms provided by Brain Capital. Each individual may receive unique loan terms. The maximum payment is capped at 2 times the loan amount. For a fair comparison, i set the loan amount in the Prodigy section. Please refer to your loan offer for the specific interest on income percentage and maximum loan amount.")
initial_income = st.number_input("Enter initial income", min_value=0.0, max_value=500000.0, value=100000.0)
annual_increase = st.slider("Enter annual increase percentage", min_value=0.0, max_value=100.0, value=4.0) / 100
st.markdown('**Note:** This slider represents your estimated yearly salary increase percentage. '
            'Adjust it based on your own career expectations. Remember, salary progression may not be linear and can vary based on industry, '
            'role, and economic conditions.')
interest_on_income = st.slider("Enter interest on income percentage", min_value=0.0, max_value=100.0, value=10.0) / 100
loan_amount_x2 = st.number_input("Enter Brain Capital Loan Amount", min_value=0.0, max_value=2 * principal_val, value=2 * principal_val)
total_repayment, yearly_payments, monthly_payments = calculate_brain_capital(initial_income, annual_increase, interest_on_income, loan_amount_x2)
st.write(f'Total repayment: €{total_repayment:.2f}')

# Brain Capital cumulative payments
brain_cumulative_payments = [12*sum(monthly_payments[:i]) for i in range(len(monthly_payments))]

# Create a DataFrame with the cumulative payments data
df_brain_cumulative = pd.DataFrame({
    'Month': [i*12 for i in range(0, len(brain_cumulative_payments))],  # Multiplying by 12 to convert years into months
    'Cumulative Payments': brain_cumulative_payments
})

# Create interactive line chart
fig_brain_cumulative = px.line(df_brain_cumulative, x='Month', y='Cumulative Payments', title='Brain Capital Cumulative Payments')

# Display the interactive line charts in Streamlit
st.plotly_chart(fig_brain_cumulative)

# Create a DataFrame with the yearly payments data
df_yearly = pd.DataFrame({
    'Year': list(range(1, len(yearly_payments)+1)),
    'Payments': yearly_payments
})

# Create a DataFrame with the monthly payments data
df_monthly = pd.DataFrame({
    'Year': list(range(1, len(monthly_payments)+1)),
    'Payments': monthly_payments
})

# Create interactive line charts
fig_yearly = px.line(df_yearly, x='Year', y='Payments', title='Yearly Payments')
fig_monthly = px.line(df_monthly, x='Year', y='Payments', title='Monthly Payments')

# Display the interactive line charts in Streamlit
st.plotly_chart(fig_yearly)
st.plotly_chart(fig_monthly)

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
st.header('Combined Prodigy and Brain Capital Cumulative Payments')
st.plotly_chart(fig_combined_cumulative)