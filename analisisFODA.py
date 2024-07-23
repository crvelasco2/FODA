import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# Cargar datos desde el archivo CSV
datos_foda = pd.read_csv('ideas_foda_3.csv')

# Crear una lista con las ideas de negocio únicas
ideas_negocio = datos_foda['Idea de Negocio'].unique()

# Función para obtener los puntajes de una idea de negocio
def obtener_puntajes(idea):
    puntajes = datos_foda.loc[datos_foda['Idea de Negocio'] == idea, 'Puntaje']
    fortalezas = puntajes.loc[datos_foda['Factor'] == 'Fortalezas'].sum()
    debilidades = puntajes.loc[datos_foda['Factor'] == 'Debilidades'].sum()
    oportunidades = puntajes.loc[datos_foda['Factor'] == 'Oportunidades'].sum()
    amenazas = puntajes.loc[datos_foda['Factor'] == 'Amenazas'].sum()
    return [fortalezas, debilidades, oportunidades, amenazas]

# Crear la aplicación Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Análisis FODA: Comparación de Ideas de Negocio'),
    html.Div([
        dcc.Checklist(
            id='factors-checklist',
            options=[
                {'label': 'Fortalezas', 'value': 'Fortalezas'},
                {'label': 'Debilidades', 'value': 'Debilidades'},
                {'label': 'Oportunidades', 'value': 'Oportunidades'},
                {'label': 'Amenazas', 'value': 'Amenazas'}
            ],
            value=['Fortalezas', 'Debilidades', 'Oportunidades', 'Amenazas'],
            inline=True
        ),
        dcc.Dropdown(
            id='ideas-dropdown',
            options=[{'label': idea, 'value': idea} for idea in ideas_negocio],
            value=ideas_negocio,
            multi=True
        ),
    ]),
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='radar-chart', style={'width': '80%', 'height': '80vh', 'margin': 'auto'}),  # Ajuste del tamaño del gráfico de radar
    dcc.Graph(id='best-idea-chart')
])

@app.callback(
    [Output('bar-chart', 'figure'), Output('radar-chart', 'figure'), Output('best-idea-chart', 'figure')],
    [Input('factors-checklist', 'value'), Input('ideas-dropdown', 'value')]
)
def update_charts(selected_factors, selected_ideas):
    if not selected_factors:
        return go.Figure(), go.Figure(), go.Figure()

    # Gráfico de barras apiladas
    fig_bar = go.Figure()
    bottom = np.zeros(len(selected_ideas))
    for factor in selected_factors:
        puntajes = [obtener_puntajes(idea)[['Fortalezas', 'Debilidades', 'Oportunidades', 'Amenazas'].index(factor)] for idea in selected_ideas]
        fig_bar.add_trace(go.Bar(
            x=selected_ideas,
            y=puntajes,
            name=factor,
            offsetgroup=0
        ))

    fig_bar.update_layout(
        title='Análisis FODA: Comparación de Ideas de Negocio',
        xaxis_title='Idea de Negocio',
        yaxis_title='Puntaje',
        barmode='stack',
        xaxis=dict(
            tickangle=0,
            automargin=True,
            tickmode='array',
            tickvals=selected_ideas,
            ticktext=[idea.replace("-", "<br>") for idea in selected_ideas]  # Realizar un salto de línea en "-"
        )
    )

    # Gráfico de radar
    categorias = ['Fortalezas', 'Oportunidades', 'Amenazas', 'Debilidades']
    N = len(categorias)
    valores_angulo = [n / float(N) * 2 * np.pi for n in range(N)]
    valores_angulo += valores_angulo[:1]

    fig_radar = go.Figure()

    for idea in selected_ideas:
        valores = obtener_puntajes(idea)
        valores = [valores[categorias.index(factor)] if factor in selected_factors else 0 for factor in categorias]
        valores += valores[:1]
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=categorias + [categorias[0]],
            fill='toself',
            name=idea
        ))

    fig_radar.update_layout(
        title='Análisis FODA: Perfil de Ideas de Negocio',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3]
            ),
            angularaxis=dict(
                direction="clockwise"
            )
        ),
        showlegend=True
    )

    # Gráfico de la mejor idea
    mejores_ideas = {}
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'pink']  # Lista de colores para cada idea
    for i, idea in enumerate(selected_ideas):
        puntajes = obtener_puntajes(idea)
        score = (puntajes[0] + puntajes[2]) - (puntajes[1] + puntajes[3])  # Fortalezas + Oportunidades - Debilidades - Amenazas
        mejores_ideas[idea] = score

    sorted_ideas = dict(sorted(mejores_ideas.items(), key=lambda item: item[1], reverse=True))

    best_idea_chart = go.Figure()
    for i, (idea, score) in enumerate(sorted_ideas.items()):
        best_idea_chart.add_trace(go.Bar(
            x=[idea],
            y=[score],
            #mode='markers',
            name=idea,
            marker=dict(
                color=colors[i],
                #size=12
            )
        ))

    best_idea_chart.update_layout(
        title='Mejor Idea de Negocio',
        xaxis_title='Idea de Negocio',
        yaxis_title='Puntaje',
        showlegend=False,
        xaxis=dict(
            tickangle=0,
            automargin=True,
            tickmode='array',
            tickvals=list(sorted_ideas.keys()),
            ticktext=[idea.replace("-", "<br>") for idea in sorted_ideas.keys()]  # Realizar un salto de línea en "-"
        ),
        margin=dict(
            l=100,
            r=100,
            b=100,
            t=100,
            pad=4
        )
    )

    return fig_bar, fig_radar, best_idea_chart

if __name__ == '__main__':
    app.run_server(debug=True)
