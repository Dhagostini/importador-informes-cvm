import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

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

# Estilo HTML customizado para organização visual
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
        .description {
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        }
    </style>
"""
st.markdown(html_styles, unsafe_allow_html=True)

# Adiciona o cabeçalho do aplicativo com HTML
st.markdown("<div class='header'>Faça o upload de um arquivo XML para visualizar seus dados estruturados:</div>", unsafe_allow_html=True)

# Upload do arquivo XML
uploaded_file = st.file_uploader("Escolha um arquivo XML", type="xml")

if uploaded_file is not None:
    # Cabeçalho indicando que o arquivo foi carregado com sucesso
    st.markdown("<div class='section'>Arquivo carregado com sucesso!</div>", unsafe_allow_html=True)
    
    # Converte o arquivo XML em um DataFrame
    df = parse_xml(uploaded_file)
    
    # Exibe a descrição dos dados extraídos do XML
    st.markdown("<div class='description'>Abaixo estão os dados extraídos do arquivo XML:</div>", unsafe_allow_html=True)
    
    # Exibe a tabela com o formato simples
    st.dataframe(df)
