# spacex-dash-app.py — versión completa y funcional

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# =========================
# Cargar datos
# =========================
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Columnas esperadas en el CSV:
# 'Launch Site', 'class', 'Payload Mass (kg)', 'Booster Version Category'

# Rango de payload para el slider
min_payload = float(spacex_df['Payload Mass (kg)'].min())
max_payload = float(spacex_df['Payload Mass (kg)'].max())

# =========================
# Inicializar app
# =========================
app = dash.Dash(__name__)

# =========================
# LAYOUT
# =========================
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),

    # --- TAREA 1: Dropdown de Sitio de Lanzamiento ---
    html.Div([
        html.Label("Select a Launch Site:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True,
            style={'width': '100%'}
        ),
    ], style={'padding': '0 20px'}),

    html.Br(),

    # --- TAREA 2: Pie Chart (éxitos por sitio / éxito vs fallo) ---
    html.Div([
        dcc.Graph(id='success-pie-chart')
    ], style={'padding': '0 20px'}),

    html.Br(),

    # --- TAREA 3: RangeSlider para Payload ---
    html.Div([
        html.Label("Payload range (Kg):", style={'fontWeight': 'bold'}),
        dcc.RangeSlider(
            id='payload-slider',
            min=0, max=10000, step=1000,
            marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
            value=[min_payload, max_payload],
            allowCross=False
        )
    ], style={'padding': '0 20px'}),

    html.Br(),

    # --- TAREA 4: Scatter Chart Payload vs Éxito ---
    html.Div([
        dcc.Graph(id='success-payload-scatter-chart')
    ], style={'padding': '0 20px'})
])

# =========================
# CALLBACKS
# =========================

# Pie chart:
# - ALL: muestra la suma de éxitos (class=1) por sitio.
# - Sitio específico: muestra éxito vs fallo en ese sitio.
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Suma de éxitos por sitio (class es 0/1, así que sum = # éxitos)
        success_by_site = (spacex_df.groupby('Launch Site')['class']
                           .sum()
                           .reset_index(name='success_count'))
        fig = px.pie(
            success_by_site,
            values='success_count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = (site_df['class']
                          .value_counts()
                          .rename_axis('Outcome')
                          .reset_index(name='count'))
        outcome_counts['Outcome'] = outcome_counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            outcome_counts,
            values='count',
            names='Outcome',
            title=f'Total Success vs Failure for site {entered_site}'
        )
        return fig

# Scatter chart de payload vs class, coloreado por versión del booster
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ].copy()

    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]

    fig = px.scatter(
        df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=("Payload vs Outcome for All Sites"
               if entered_site == 'ALL'
               else f"Payload vs Outcome for site {entered_site}"),
        hover_data=['Launch Site']
    )
    return fig

# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8051, debug=False)


