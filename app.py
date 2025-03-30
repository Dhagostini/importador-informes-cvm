import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
from io import StringIO

# Função para processar o XML e extrair dados
def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    
    # Aqui você vai adaptar para extrair os dados do XML conforme sua estrutura
    data = []
    for elem in root.iter():
        data.append([elem.tag, elem.text])

    df = pd.DataFrame(data, columns=['Tag', 'Valor'])
    return df

# App Streamlit
st.title("Importar e Exibir XML")

# Estilo HTML customizado
html_styles = """
    <style>
        .header {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            margin-top: 20px;
        }
        .section {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-top: 30px;
        }
        .data-table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        .data-table th, .data-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .data-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
    </style>
"""
st.markdown(html_styles, unsafe_allow_html=True)

st.markdown("<div class='header'>Faça o upload de um arquivo XML para visualizar seus dados estruturados:</div>", unsafe_allow_html=True)

# Upload do arquivo XML
uploaded_file = st.file_uploader("Escolha um arquivo XML", type="xml")

if uploaded_file is not None:
    # Carregar o conteúdo do XML
    st.markdown("<div class='section'>Arquivo carregado com sucesso!</div>", unsafe_allow_html=True)
    
    # Converte o arquivo para um DataFrame e exibe
    df = parse_xml(uploaded_file)
    
    # Exibe a tabela com estilo HTML
    st.markdown("<div class='section'>Dados extraídos do XML:</div>", unsafe_allow_html=True)
    
    # Transformando o DataFrame para HTML e exibindo com a formatação da tabela
    table_html = df.to_html(classes='data-table', index=False)
    st.markdown(table_html, unsafe_allow_html=True)

