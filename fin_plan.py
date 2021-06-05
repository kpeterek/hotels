import streamlit as st
import plotly.graph_objects as go
import numpy as np


def fin_planning():
  @st.cache
  st.title("Hotel Valuation Calculator")
  st.header("**Hotel Details**")
  st.subheader("Rooms")
  rooms = st.beta_columns(1)

  colRooms, colRevPAR,colNOImargin = st.beta_columns(3)

  with colRooms:
      rooms = st.slider("Enter the hotel room count: ", min_value=1, max_value = 400, step = 1,format='%d')
  with colRevPAR:
      rev_par = st.slider("Enter stabilized RevPAR: ", min_value=20, max_value = 300, step = 1,format='%d')
  with colRevPAR:
      noi_margin = st.number_input("Enter your NOI Margin(%): ", min_value=0,step = 1,format='%d')/100
  ann_revenue = 365*rooms*rev_par
  noi_value = ann_revenue*noi_margin
  st.write(float(ann_revenue),noi_value)
  

  with colExpenses1:
      st.subheader("Monthly Rental")
      monthly_rental = st.number_input("Enter your monthly rental($): ", min_value=0.0,format='%f' )

      st.subheader("Daily Food Budget")
      daily_food = st.number_input("Enter your daily food budget ($): ", min_value=0.0,format='%f' )
      monthly_food = daily_food * 30

      st.subheader("Monthly Unforeseen Expenses")
      monthly_unforeseen = st.number_input("Enter your monthly unforeseen expenses ($): ", min_value=0.0,format='%f' ) 

  with colExpenses2:
      st.subheader("Monthly Transport")
      monthly_transport = st.number_input("Enter your monthly transport fee ($): ", min_value=0.0,format='%f' )   

      st.subheader("Monthly Utilities Fees")
      monthly_utilities = st.number_input("Enter your monthly utilities fees ($): ", min_value=0.0,format='%f' )

      st.subheader("Monthly Entertainment Budget")
      monthly_entertainment = st.number_input("Enter your monthly entertainment budget ($): ", min_value=0.0,format='%f' )   

  monthly_expenses = monthly_rental + monthly_food + monthly_transport + monthly_entertainment + monthly_utilities + monthly_unforeseen
  monthly_savings = monthly_takehome_salary - monthly_expenses 

  st.header("**Savings**")
  st.subheader("Monthly Take Home Salary: $" + str(round(monthly_takehome_salary,2)))
  st.subheader("Monthly Expenses: $" + str(round(monthly_expenses, 2)))
  st.subheader("Monthly Savings: $" + str(round(monthly_savings, 2)))

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
