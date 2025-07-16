import plotly.graph_objects as go
import numpy as np
from plotly.offline import plot
from django.conf import settings
import os
import json
from datetime import datetime, timedelta

def generate_risk_surface(risk_data):
    """
    Generate 3D surface plot of risk distribution
    """
    # Sample data - in a real app this would come from your database
    x = np.arange(0, 100, 5)  # Risk scores
    y = np.arange(0, 12, 1)    # Loan terms (months)
    X, Y = np.meshgrid(x, y)
    
    # Z = probability of default
    Z = 1 / (1 + np.exp(-0.1 * (X - 50))) * (1 + Y/24)
    
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
    
    fig.update_layout(
        title='Risk Surface: Probability of Default by Risk Score and Loan Term',
        scene=dict(
            xaxis_title='Risk Score',
            yaxis_title='Loan Term (months)',
            zaxis_title='Probability of Default',
        ),
        autosize=True,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    
    return plot(fig, output_type='div', include_plotlyjs=False)

def generate_portfolio_risk_chart(customers):
    """
    Generate a 3D scatter plot of customers in the portfolio
    """
    # Sample data - in a real app this would come from your database
    num_customers = len(customers)
    x = np.random.normal(50, 15, num_customers)  # Risk scores
    y = np.random.uniform(1000, 10000, num_customers)  # Loan amounts
    z = np.random.uniform(0, 1, num_customers)  # Probability of default
    
    # Create size array based on loan amount
    sizes = y / 200
    
    # Create color scale based on PD
    colors = z
    
    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            colorscale='Viridis',
            opacity=0.8,
            colorbar=dict(title='PD')
        ),
        text=[f"Customer: {c.name}<br>Score: {x[i]:.0f}<br>Amount: ${y[i]:,.0f}<br>PD: {z[i]:.2%}" 
              for i, c in enumerate(customers)],
        hoverinfo='text'
    )])
    
    fig.update_layout(
        title='Portfolio Risk Distribution',
        scene=dict(
            xaxis_title='Risk Score',
            yaxis_title='Loan Amount',
            zaxis_title='Probability of Default',
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    
    return plot(fig, output_type='div', include_plotlyjs=False)

def generate_default_timeline(defaulters):
    """
    Generate a timeline of default events
    """
    # Sample data - in a real app this would come from your database
    dates = [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in defaulters]
    amounts = [np.random.uniform(1000, 50000) for _ in defaulters]
    names = [d.customer.name for d in defaulters]
    
    fig = go.Figure()
    
    for i, defaulter in enumerate(defaulters):
        fig.add_trace(go.Scatter3d(
            x=[dates[i]],
            y=[amounts[i]],
            z=[0],
            mode='markers',
            marker=dict(
                size=10,
                color='red'
            ),
            name=names[i],
            text=f"Customer: {names[i]}<br>Amount: ${amounts[i]:,.2f}<br>Date: {dates[i].strftime('%Y-%m-%d')}",
            hoverinfo='text'
        ))
    
    fig.update_layout(
        title='Default Event Timeline',
        scene=dict(
            xaxis_title='Date',
            yaxis_title='Amount',
            zaxis_title='',
        ),
        showlegend=True
    )
    
    return plot(fig, output_type='div', include_plotlyjs=False)