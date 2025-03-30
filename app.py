import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import xml.etree.ElementTree as ET

# === Função para importar XML ===
def importar_e_exibir_xml(xml_bytes):
    try:
        df = pd.read_xml(BytesIO(xml_bytes))
        try:
            root = ET.fromstring(xml_bytes)
            data_ref = next((elem.text for elem in root.iter() if "DataReferencia" in elem.tag), None)
            if data_ref:
                df["DataReferencia"] = data_ref
        except:
            pass
        return df
    except:
        return None

# === Interface Streamlit ===
st.set_page_config(page_title="Importador CVM - Base CSV", layout="wide")
st.title("📄 Importador de Informes Mensais da CVM (via CSV oficial)")

# === Entrada do usuário ===
cnpj_input = st.text_input("Digite o CNPJ do fundo:", "20.905.862/0001-70")
ano = st.selectbox("Ano", options=[2025, 2024, 2023], index=0)

if st.button("🔍 Buscar e processar informes"):
    with st.spinner("Baixando base da CVM..."):
        url_csv = f"https://dados.cvm.gov.br/dados/FI/DOC/EVENTUAL/DADOS/eventual_fi_{ano}.csv"
        df_csv = pd.read_csv(url_csv, sep=";", encoding="latin1")

    with st.spinner("Filtrando documentos..."):
        cnpj_clean = cnpj_input.replace(".", "").replace("/", "").replace("-", "")
        df_filtrado = df_csv[
            (df_csv['CNPJ_FUNDO'].str.replace(r'\D', '', regex=True) == cnpj_clean) &
            (df_csv['TP_DOC'].str.contains("Informe Mensal", case=False, na=False)) &
            (df_csv['LINK_ARQ'].str.endswith(".xml", na=False))
        ]

    if df_filtrado.empty:
        st.warning("Nenhum informe mensal encontrado.")
    else:
        st.success(f"{len(df_filtrado)} documentos encontrados.")
        dfs = []

        for _, row in df_filtrado.iterrows():
            link = row["LINK_ARQ"]
            nome = row["NOME_DOCUMENTO"]
            try:
                r = requests.get(link)
                df_xml = importar_e_exibir_xml(r.content)
                if df_xml is not None:
                    df_xml["Arquivo"] = nome
                    dfs.append(df_xml)
            except:
                continue

        if dfs:
            df_final = pd.concat(dfs, ignore_index=True)
            cols = df_final.columns.tolist()
            if "DataReferencia" in cols:
                cols = ["DataReferencia", "Arquivo"] + [c for c in cols if c not in ("DataReferencia", "Arquivo")]
                df_final = df_final[cols]

            st.dataframe(df_final)

            # Exportar Excel
            output = BytesIO()
            df_final.to_excel(output, index=False, engine="openpyxl")
            st.download_button("📥 Baixar Excel", data=output.getvalue(), file_name=f"informes_{cnpj_clean}_{ano}.xlsx")
        else:
            st.warning("Não foi possível processar os XMLs encontrados.")
