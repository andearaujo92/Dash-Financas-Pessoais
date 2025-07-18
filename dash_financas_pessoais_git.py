import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# Dados 
dados = pd.read_excel("financas_pessoais.xlsx")
dados['ano'] = dados.data.dt.year
dados['mes_num'] = dados.data.dt.month
dados['mes'] = dados.data.dt.month_name(locale='pt_BR.utf8')
dados = dados.drop(columns=['data'])

# Configurando a página
st.set_page_config(page_title='Dashboard Finanças Pessoais', layout="wide")

# Criando as Tabs
tab1, tab2, tab3 = st.tabs(['Dashboard','Lançamento de Despesas', 'Instruções de Uso'])

# Criando a primeira tab com Dashboard
with tab1:

    # Titulo do Dashboard
    st.title('Dashboard de Finanças pessoais')

    # Filtros
    st.sidebar.header("Filtros")
    categoria_filtro = st.sidebar.multiselect("Categoria", list(dados['categoria'].unique()),default=list(dados['categoria'].unique()))
    metodo_filtro = st.sidebar.multiselect("Método de Pagamento", list(dados['metodo'].unique()),default=list(dados['metodo'].unique()))
    tipo_filtro = st.sidebar.multiselect("Tipo de Despesa", list(dados['tipo despesa'].unique()),default=list(dados['tipo despesa'].unique()))
    cartao_filtro = st.sidebar.multiselect("Cartão", list(dados['cartao'].unique()) ,default=list(dados['cartao'].unique()))
    ano_filtro = st.sidebar.multiselect("Ano", list(dados['ano'].unique()) ,default= datetime.today().year)
    mes_filtro = st.sidebar.multiselect("Mês", list(dados['mes'].unique()) ,default=list(dados['mes'].unique()))

    # Filtrar dados
    dados_filtrados = dados[
        (dados['categoria'].isin(categoria_filtro)) &
        (dados['metodo'].isin(metodo_filtro)) &
        (dados['tipo despesa'].isin(tipo_filtro)) &
        (dados['cartao'].isin(cartao_filtro)) &
        (dados['ano'].isin(ano_filtro)) & 
        (dados['mes'].isin(mes_filtro))
    ]

    # Card Total de Despesas
    total_despesas = round(dados_filtrados['valor'].sum(), 2)
    salario = 3000 * len(mes_filtro)
    sobra = round(salario - total_despesas,2)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Despesas (R$)', total_despesas,)
    style_metric_cards(border_left_color='red')

    # Card Categoria com Maior Despesa
    categoria_maior_despesa = dados_filtrados.groupby('categoria')['valor'].sum().idxmax()
    col2.metric('Categoria com maior despesa', categoria_maior_despesa)
    style_metric_cards()

    # Card Método com Maior Despesa
    metodo_maior_despesa = dados_filtrados.groupby('metodo')['valor'].sum().idxmax()
    col3.metric('Método mais utilizado', metodo_maior_despesa)
    style_metric_cards()

    # Card de Sobra do Salário
    col4.metric('Quanto sobra do salário?', sobra)
    style_metric_cards()

    # Layout dos gráficos de barras
    g1, g2 = st.columns(2)

    # Gráfico de Total de Despesas por mês
    dados_linha = dados_filtrados.groupby(['ano','mes','mes_num']).sum().reset_index().sort_values(by = 'mes_num')
    graf_linha = px.line(data_frame= dados_linha, x = 'mes', y = 'valor', labels={'mes':'Mês', 'valor':'Total Despesas'}, title='Total Despesas por mês')
    st.plotly_chart(graf_linha, use_container_width= True)

    # Grafico de Total de Despesas por categoria
    dados_categoria = dados_filtrados.groupby(['categoria']).sum().reset_index().sort_values(by = 'valor')
    graf_categoria = px.bar(data_frame= dados_categoria, x = 'valor', y = 'categoria', labels={'categoria':'Categoria', 'valor':'Total Despesas'}, title='Total Despesas por Categoria')
    g1.plotly_chart(graf_categoria, use_container_width= True)

    # Grafico de Total de Despesas por Método de Pagamento
    dados_metodo = dados_filtrados.groupby(['metodo']).sum().reset_index().sort_values(by = 'valor')
    graf_categoria = px.bar(data_frame= dados_metodo, x = 'valor', y = 'metodo', labels={'metodo':'Método de Pagamento', 'valor':'Total Despesas'}, title='Total Despesas por Método de Pagamento')
    g2.plotly_chart(graf_categoria, use_container_width= True)

    # Data Frame com os detalhes
    st.dataframe(data= dados_filtrados, use_container_width=True)

# Criando a segunda tab de Lançamento de Despesas

with tab2:
    st.title('Lançamento de despesas pessoais')
    despesa = st.text_input('Identifique a despesa')
    data = st.date_input('Data da compra')
    data_fechamento = st.date_input('Data de fechamento da fatura')
    categoria = st.selectbox('Categoria da compra', ['casa', 'transporte', 'lazer','gastos pessoais','saúde','comida'])
    valor = st.number_input('Valor')
    metodo_pag = st.selectbox('Método de pagamento', ['crédito','débito','pix'])
    tipo_despesa = st.selectbox('Tipo de Despesa', ['fixo','variável'])
    cartao = st.selectbox('Cartão / Conta', ['inter','nubank', 'efi', 'meli'])
    recorrencia = st.selectbox('Despesa recorrente?', ['Não', 'Sim'],)

    if recorrencia == 'Sim':
        recor = 1
        parcelas = st.number_input('Quantidade de parcelas', step=1)
    else:
        recor = 2

    def ajustar_data_fatura(data_compra, data_fechamento):
        if (data_compra <= data_fechamento) and (data_compra.month == data_fechamento.month):
            return data_compra.replace(day=1)
        elif (data_compra > data_fechamento) and (data_compra.month == data_fechamento.month):
            return (data_compra + relativedelta(months=2)).replace(day=1)

    if st.button('Enviar dados', type='primary'):
        st.write('Dados enviados!')

        if recor == 1 and parcelas > 0:
            for i in range(parcelas):
                data_parcela = data + relativedelta(months=i)
                data_fatura = ajustar_data_fatura(data_parcela, data_fechamento)

                if 'financas_pessoais.xlsx' in os.listdir():
                    df = pd.read_excel('financas_pessoais.xlsx')
                else:
                    df = pd.DataFrame(columns=['data','despesa','valor','metodo','cartao',
                                               'categoria','tipo despesa','unidade','parcela_a_pagar','parcela_total'])

                linha = {
                    'data': data_fatura,
                    'despesa': despesa,
                    'valor': valor,
                    'metodo': metodo_pag,
                    'cartao': cartao,
                    'categoria': categoria,
                    'tipo despesa': tipo_despesa,
                    'unidade':1,
                    'parcela_a_pagar': i + 1,
                    'parcela_total': parcelas
                }

                df = df._append(linha, ignore_index=True)
                df.to_excel('financas_pessoais.xlsx', sheet_name="financas_pessoais", index=False)

        elif recor == 2:
            data_fatura = data

            if 'financas_pessoais.xlsx' in os.listdir():
                df = pd.read_excel('financas_pessoais.xlsx')
            else:
                df = pd.DataFrame(columns=['data','despesa','valor','metodo','cartao','categoria','tipo despesa'])

            linha = {
                'data': data_fatura,
                'despesa': despesa,
                'valor': valor,
                'metodo': metodo_pag,
                'cartao': cartao,
                'categoria': categoria,
                'tipo despesa': tipo_despesa,
                'unidade': None,
                'parcela_a_pagar': None,
                'parcela_total': None
            }

            df = df._append(linha, ignore_index=True)
            df.to_excel('financas_pessoais.xlsx', sheet_name="financas_pessoais", index=False)

    else:
        st.write('Dados pendente de envio')

with tab3:
    st.title('Instruções de Uso')
    st.markdown(
        '''
        - **Para compras a vista no crédito:** Recorrência = Sim e Parcelas = 1
        - **Para compras a vista no Pix:** Recorrência = Não
        - Coloque a data de fechamento da fatura dentro do mesmo mês da compra
        '''
    )

