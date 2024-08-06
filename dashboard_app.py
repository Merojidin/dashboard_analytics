import os
from flask import Flask
import pandas as pd
import plotly.express as px
import dash 
from dash import dcc, html
from dash.dependencies import Output, Input
from dash import dash_table
from get_data import get_data_xlsx
from datetime import datetime as dtime

# Загрузка данных
customer = get_data_xlsx('olist_order_customers_dataset')
orders = get_data_xlsx('olist_orders_dataset')
products = get_data_xlsx('olist_products_dataset')
sellers = get_data_xlsx('olist_sellers_dataset')
order_items = get_data_xlsx('olist_order_items_dataset')
payments = get_data_xlsx('olist_order_payments_dataset')

# Объединение данных
merged_data = order_items.merge(orders, on='order_id') \
                         .merge(products, on='product_id') \
                         .merge(customer, on='customer_id') \
                         .merge(payments, on='order_id')

# Подготовка данных для дашборда
min_date = pd.to_datetime(orders['order_purchase_timestamp']).min()
max_date = pd.to_datetime(orders['order_purchase_timestamp']).max()
years = pd.to_datetime(orders['order_purchase_timestamp']).dt.year.unique().tolist()

# Исправление пустых значений
products['product_category_name'] = products['product_category_name'].fillna('unknown')

# Блоки интерфейса
slider_block = html.Div(
    children=[
        html.H2('Dates'),
        html.Div(
            dcc.RangeSlider(
                id='range_slider',
                min=years[0],
                max=years[-1],
                step=1,
                value=[min(years), max(years)],
                marks={y: str(y) for y in years}
            ),
        )
    ]
)

date_picker_block = dcc.DatePickerRange(
    id='date_prange',
    min_date_allowed=min_date,
    max_date_allowed=max_date,
    display_format='YYYY-MM-DD'
)

category_filter_block = html.Div(
    children=[
        html.H2('Product Categories'),
        dcc.Dropdown(
            id='category_filter',
            options=[{'label': cat, 'value': cat} for cat in products['product_category_name'].unique()],
            value=[products['product_category_name'].unique()[0]],
            multi=True
        )
    ]
)

payment_type_filter_block = html.Div(
    children=[
        html.H2('Payment Types'),
        dcc.Dropdown(
            id='payment_type_filter',
            options=[{'label': pt, 'value': pt} for pt in payments['payment_type'].unique()],
            value=payments['payment_type'].unique()[0]
        )
    ]
)

state_filter_block = html.Div(
    children=[
        html.H2('Customer States'),
        dcc.Dropdown(
            id='state_filter',
            options=[{'label': state, 'value': state} for state in customer['customer_state'].unique()],
            value=customer['customer_state'].unique()[0]
        )
    ]
)

tbl_columns = [{'name': col, 'id': col} for col in merged_data.columns.tolist()]
tbl_block = html.Div(
    dash_table.DataTable(
        id='tbl',
        columns=tbl_columns,
        data=merged_data.to_dict('records'),
        sort_action='native',
        filter_action='native',
        page_action='native',
        page_current=0,
        page_size=20
    )
)

app = dash.Dash()
app.layout = html.Div([
    html.Div(
        children=[
            html.H1('Order Information', style={'text-align': 'center'}),
            html.Div(
                children=[slider_block, date_picker_block, category_filter_block, payment_type_filter_block, state_filter_block],
                style={'width': '50%', 'display': 'inline-block'}
            ),
            html.Div(
                children=[
                    dcc.Graph(id='line_fig', style={'width': '50%', 'display': 'inline-block'}),
                    dcc.Graph(id='bar_fig', style={'width': '50%', 'display': 'inline-block'}),
                    dcc.Graph(id='payment_type_fig', style={'width': '50%', 'display': 'inline-block'}),
                    dcc.Graph(id='state_payment_fig', style={'width': '50%', 'display': 'inline-block'}),
                ]
            ),
            tbl_block
        ]
    )
])

@app.callback(
    Output(component_id='date_prange', component_property='start_date'),
    Output(component_id='date_prange', component_property='end_date'),
    Input(component_id='range_slider', component_property='value')
)
def update_drange(value):
    start_date = dtime(value[0], 1, 1)
    end_date = dtime(value[1], 12, 31)
    return str(start_date), str(end_date)

@app.callback(
    Output(component_id='line_fig', component_property='figure'),
    Input(component_id='date_prange', component_property='start_date'),
    Input(component_id='date_prange', component_property='end_date'),
    Input(component_id='category_filter', component_property='value')
)
def update_line_plot(start_date, end_date, selected_categories):
    sales = merged_data.copy()
    sales['order_purchase_timestamp'] = pd.to_datetime(sales['order_purchase_timestamp'])

    if selected_categories:
        sales = sales[sales['product_category_name'].isin(selected_categories)]
    if start_date and end_date:
        sales = sales[(sales['order_purchase_timestamp'] >= start_date) & 
                      (sales['order_purchase_timestamp'] <= end_date)]
    
    sales_grouped = sales.groupby(['order_purchase_timestamp', 'product_category_name']).sum().reset_index()

    line_fig = px.line(
        data_frame=sales_grouped,
        x='order_purchase_timestamp',
        y='price',
        color='product_category_name',
        title='Sales by Product Category Over Time',
        labels={"order_purchase_timestamp": "Purchase Date", "price": "Total Price"}
    )
    
    line_fig.update_xaxes(rangeslider_visible=True)  # Включение слайдера для оси X

    return line_fig

@app.callback(
    Output(component_id='bar_fig', component_property='figure'),
    Input(component_id='date_prange', component_property='start_date'),
    Input(component_id='date_prange', component_property='end_date'),
    Input(component_id='category_filter', component_property='value')
)
def update_bar_plot(start_date, end_date, selected_categories):
    sales = merged_data.copy()
    sales['order_purchase_timestamp'] = pd.to_datetime(sales['order_purchase_timestamp'])

    if selected_categories:
        sales = sales[sales['product_category_name'].isin(selected_categories)]
    if start_date and end_date:
        sales = sales[(sales['order_purchase_timestamp'] >= start_date) & 
                      (sales['order_purchase_timestamp'] <= end_date)]
    
    grouped_sales = sales.groupby('product_category_name', as_index=False)['price'].sum()

    bar_fig = px.bar(
        data_frame=grouped_sales,
        x='product_category_name',
        y='price',
        title='Total Sales by Product Category',
        labels={"product_category_name": "Product Category", "price": "Total Price"},
        orientation='v'
    )
    
    bar_fig.update_xaxes(categoryorder="total descending")  # Упорядочение оси X по убыванию

    return bar_fig

@app.callback(
    Output(component_id='payment_type_fig', component_property='figure'),
    Input(component_id='category_filter', component_property='value')
)
def update_payment_type_plot(selected_categories):
    sales = merged_data.copy()

    if selected_categories:
        sales = sales[sales['product_category_name'].isin(selected_categories)]
    
    payment_type_counts = sales.groupby(['product_category_name', 'payment_type']).size().reset_index(name='counts')

    payment_type_fig = px.bar(
        data_frame=payment_type_counts,
        x='payment_type',
        y='counts',
        color='product_category_name',
        title='Payment Types by Product Category',
        labels={"payment_type": "Payment Type", "counts": "Count"},
        orientation='v'
    )
    
    return payment_type_fig

@app.callback(
    Output(component_id='state_payment_fig', component_property='figure'),
    Input(component_id='state_filter', component_property='value')
)
def update_state_payment_plot(selected_state):
    sales = merged_data.copy()

    if selected_state:
        sales = sales[sales['customer_state'] == selected_state]
    
    state_payment_counts = sales.groupby(['customer_state', 'payment_type']).size().reset_index(name='counts')

    state_payment_fig = px.bar(
        data_frame=state_payment_counts,
        x='payment_type',
        y='counts',
        color='customer_state',
        title='Payment Types by Customer State',
        labels={"payment_type": "Payment Type", "counts": "Count"},
        orientation='v'
    )
    
    return state_payment_fig

@app.callback(
    Output(component_id='tbl', component_property='data'),
    Input(component_id='date_prange', component_property='start_date'),
    Input(component_id='date_prange', component_property='end_date'),
    Input(component_id='category_filter', component_property='value')
)
def update_table(start_date, end_date, selected_categories):
    sales = merged_data.copy()
    sales['order_purchase_timestamp'] = pd.to_datetime(sales['order_purchase_timestamp'])

    if selected_categories:
        sales = sales[sales['product_category_name'].isin(selected_categories)]
    if start_date and end_date:
        sales = sales[(sales['order_purchase_timestamp'] >= start_date) & 
                      (sales['order_purchase_timestamp'] <= end_date)]
    
    return sales.to_dict('records')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=True, host='0.0.0.0', port=port)


