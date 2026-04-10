import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar e limpar os dados
@st.cache_data
def load_and_clean_data():
    df_retail = pd.read_csv('online_retail.csv')
    # Certificar que 'total_vendas' é calculada no app
    df_retail['total_vendas'] = df_retail['UnitPrice'] * df_retail['Quantity']
    df_retail_cleaned = df_retail.dropna(subset=['CustomerID', 'Description']).copy()
    df_retail_cleaned['InvoiceDate'] = pd.to_datetime(df_retail_cleaned['InvoiceDate'])
    return df_retail_cleaned

df = load_and_clean_data()

# Título do Dashboard
st.title('Dashboard de Vendas Online: Visão Geral')
st.markdown('Este painel interativo apresenta a análise de vendas de varejo online.')

# Sidebar para filtros
st.sidebar.header('Filtros')

# Filtro por País
paises = df['Country'].unique()
selected_country = st.sidebar.multiselect('Selecione o País', paises, default=paises)

# Filtro por Período de Vendas
df_filtered_date = df[df['Country'].isin(selected_country)]
min_date = df_filtered_date['InvoiceDate'].min().date()
max_date = df_filtered_date['InvoiceDate'].max().date()
date_range = st.sidebar.date_input('Selecione o Período', value=(min_date, max_date))

# Garante que date_range tenha 2 elementos
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    df_filtered = df_filtered_date[(df_filtered_date['InvoiceDate'] >= start_date) & (df_filtered_date['InvoiceDate'] <= end_date)]
else:
    # Se apenas uma data for selecionada (ex: após mudar de duas para uma), use a data mínima para a segunda data
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[0])
    df_filtered = df_filtered_date[(df_filtered_date['InvoiceDate'] >= start_date) & (df_filtered_date['InvoiceDate'] <= end_date)]


# Exibir KPIs (Key Performance Indicators)
st.subheader('Performance Geral')
total_vendas_geral = df_filtered['total_vendas'].sum()
st.metric('Faturamento Total (período selecionado)', f'R$ {total_vendas_geral:,.2f}')


# Visualização 1: Vendas por Categoria de Produto (usando Description como proxy)
st.subheader('Vendas por Categoria de Produto')
st.info('**Nota:** Usamos a coluna `Description` como proxy para categorias de produto, o que pode ser muito granular. Para uma análise mais robusta, seria ideal ter uma coluna de `Categoria` pré-definida.')

# Agrupar por Description e somar total_vendas
sales_by_description = df_filtered.groupby('Description')['total_vendas'].sum().nlargest(15).reset_index()
fig_desc = px.bar(sales_by_description, x='Description', y='total_vendas',
                 title='Top 15 Produtos por Faturamento',
                 labels={'Description': 'Produto/Descrição', 'total_vendas': 'Faturamento (R$)'})
st.plotly_chart(fig_desc)

# Visualização 2: Faturamento Total por País
st.subheader('Faturamento Total por País')
sales_by_country = df_filtered.groupby('Country')['total_vendas'].sum().reset_index()
fig_country_sales = px.bar(sales_by_country, x='Country', y='total_vendas',
                          title='Faturamento Total por País',
                          labels={'Country': 'País', 'total_vendas': 'Faturamento (R$)'},
                          color='Country')
st.plotly_chart(fig_country_sales)

# Visualização 3: Vendas por Método de Pagamento (placeholder)
st.subheader('Vendas por Método de Pagamento')
st.warning('**Informação ausente:** A coluna de **Método de Pagamento** não está disponível neste dataset. Para incluir esta análise, seria necessário adicionar essa informação aos dados.')

# Exemplo de alternativa: Vendas por País ao longo do tempo (se o método de pagamento não for viável)
st.subheader('Vendas por País ao longo do tempo (Alternativa)')
sales_by_country_time = df_filtered.groupby([df_filtered['InvoiceDate'].dt.to_period('M'), 'Country'])['total_vendas'].sum().reset_index()
sales_by_country_time['InvoiceDate'] = sales_by_country_time['InvoiceDate'].astype(str)

fig_country_time = px.line(sales_by_country_time, x='InvoiceDate', y='total_vendas', color='Country',
                           title='Faturamento Mensal por País',
                           labels={'InvoiceDate': 'Mês', 'total_vendas': 'Faturamento (R$)', 'Country': 'País'})
st.plotly_chart(fig_country_time)
