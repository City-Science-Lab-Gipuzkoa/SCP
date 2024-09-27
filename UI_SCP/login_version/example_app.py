from flask import Flask, render_template, request
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = Flask(__name__)
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

# Define the layout of the Dash app
dash_app.layout = html.Div([
    html.Div([
        html.H1('My App'),
        html.Div([
            html.H3('Menu'),
            html.Ul([
                html.Li(html.A('Page 1', href='/page1')),
                html.Li(html.A('Page 2', href='/page2')),
            ])
        ]),
        html.Div([
            html.H3('Plot'),
            dcc.Graph(
                id='plot',
                figure={
                    'data': [{'x': [1, 2, 3], 'y': [4, 1, 2]}],
                    'layout': {'title': 'My Plot'}
                }
            )
        ])
    ])
])

# Define the callback for the plot
@dash_app.callback(
    Output('plot', 'figure'),
    [Input('plot', 'clickData')]
)
def update_plot(click_data):
    if click_data:
        x = click_data['points'][0]['x']
        return {'data': [{'x': [x], 'y': [x**2]}], 'layout': {'title': 'Squared Value'}}
    else:
        return {'data': [{'x': [1, 2, 3], 'y': [4, 1, 2]}], 'layout': {'title': 'My Plot'}}

# Define the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform login authentication
        username = request.form['username']
        password = request.form['password']

        # Add your authentication logic here
        if username == 'beppe' and password == 'cslBeppe':
            return dash_app.index()
        else:
            return 'Invalid username or password'

    # If the request method is GET, render the login template
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)