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
st.markdown("Faça o upload de um arquivo XML para visualizar seus dados.")

# Upload do arquivo XML
uploaded_file = st.file_uploader("Escolha um arquivo XML", type="xml")

if uploaded_file is not None:
    # Carregar o conteúdo do XML
    st.write("Arquivo carregado com sucesso!")
    
    # Converta o arquivo para um DataFrame e exiba
    df = parse_xml(uploaded_file)
    st.dataframe(df)

