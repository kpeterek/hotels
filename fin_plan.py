import streamlit as st
import plotly.graph_objects as go
import numpy as np


def fin_planning():
  st.title("Hotel Valuation Calculator")
  st.header("**Hotel Details**")
  #@st.cache
  colRooms, colRevPAR,colNOImargin = st.beta_columns(3)

  with colRooms:
      rooms = st.slider("Enter the hotel room count: ", min_value=1, max_value = 400, step = 1,format='%d')
  with colRevPAR:
      rev_par = st.slider("Enter stabilized RevPAR: ", min_value=20, max_value = 300, step = 1,format='%d')
  with colRevPAR:
      noi_margin = st.number_input("Enter your NOI Margin(%): ", min_value=0,step = 1,format='%d')/100
  ann_revenue = 365*rooms*rev_par
  noi_value = ann_revenue*noi_margin
  #f"Annual Revenue of: $**{365*rooms*rev_par:,.0f}**."
  st.markdown(f"Annual Revenue of: $**{ann_revenue:,.0f}**.")
  st.markdown(f"Annual NOI of: $**{noi_value:,.0f}**.")

  st.subheader("Valuation")
  cap_rate = st.number_input("Enter your NOI Margin(%): ", min_value=0.0,step = .01,format='%f')
'''
  st.markdown("---")

  st.header("**Forecast Savings**")
  colForecast1, colForecast2 = st.beta_columns(2)
  with colForecast1:
      st.subheader("Forecast Year")
      forecast_year = st.number_input("Enter your forecast year (Min 1 year): ", min_value=0,format='%d')
      forecast_months = 12 * forecast_year 

      st.subheader("Annual Inflation Rate")
      annual_inflation = st.number_input("Enter annual inflation rate (%): ", min_value=0.0,format='%f')
      monthly_inflation = (1+annual_inflation)**(1/12) - 1
      cumulative_inflation_forecast = np.cumprod(np.repeat(1 + monthly_inflation, forecast_months))
      forecast_expenses = monthly_expenses*cumulative_inflation_forecast
  with colForecast2:
      st.subheader("Annual Salary Growth Rate")
      annual_growth = st.number_input("Enter your expected annual salary growth (%): ", min_value=0.0,format='%f')
      monthly_growth = (1 + annual_growth) ** (1/12) - 1
      cumulative_salary_growth = np.cumprod(np.repeat(1 + monthly_growth, forecast_months))
      forecast_salary = monthly_takehome_salary * cumulative_salary_growth 

  forecast_savings = forecast_salary - forecast_expenses 
  cumulative_savings = np.cumsum(forecast_savings)

  x_values = np.arange(forecast_year + 1)

  fig = go.Figure()
  fig.add_trace(
          go.Scatter(
              x=x_values, 
              y=forecast_salary,
              name="Forecast Salary"
          )
      )

  fig.add_trace(
          go.Scatter(
              x=x_values,
              y=forecast_expenses,
              name= "Forecast Expenses"
          )
      )

  fig.add_trace(
          go.Scatter(
                  x=x_values, 
                  y=cumulative_savings,
                  name= "Forecast Savings"
              )
      )
  fig.update_layout(title='Forecast Salary, Expenses & Savings Over the Years',
                     xaxis_title='Year',
                     yaxis_title='Amount($)')

  st.plotly_chart(fig, use_container_width=True)
  
  '''
