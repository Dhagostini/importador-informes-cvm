import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from io import BytesIO

# Função para buscar documentos via API da B3
def buscar_documentos(cnpj):
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")
    url = f"https://fnet.bmfbovespa.com.br/fnet/publico/listarDocumentos?palavraChave=&codigoTipoFundo=&cnpj={cnpj_limpo}&idTipoDocumento=14"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        documentos = data.get("documentos", [])
        return documentos
    else:
        return []


# Função para importar e processar XML
def importar_e_exibir_xml(xml_bytes):
    try:
        df = pd.read_xml(BytesIO(xml_bytes))
        try:
            root = ET.fromstring(xml_bytes)
            data_referencia = None
            for elem in root.iter():
                if "DataReferencia" in elem.tag:
                    data_referencia = elem.text
                    break
            if data_referencia:
                df["DataReferencia"] = data_referencia
        except:
            pass
        return df
    except:
        return None

# === Interface Streamlit ===
st.set_page_config(page_title="Importador de Informes CVM", layout="wide")
st.title("📄 Importador de Informes Mensais da CVM")

cnpj_input = st.text_input("Digite o CNPJ do fundo:", "20.905.862/0001-70")

if st.button("🔍 Buscar e processar informes"):
    with st.spinner("Buscando documentos..."):
        docs = buscar_documentos(cnpj_input)

        if not docs:
            st.warning("Nenhum informe mensal encontrado para esse CNPJ.")
        else:
            st.success(f"{len(docs)} documentos encontrados.")
            dfs = []

            for doc in docs:
                nome = doc.get("nomeArquivo", "documento.xml")
                url = doc.get("url")
                if url and url.endswith(".xml"):
                    r = requests.get(url)
                    df = importar_e_exibir_xml(r.content)
                    if df is not None:
                        df["Arquivo"] = nome
                        dfs.append(df)

            if dfs:
                df_final = pd.concat(dfs, ignore_index=True)

                # Reorganizar colunas se "DataReferencia" estiver presente
                cols = df_final.columns.tolist()
                if "DataReferencia" in cols:
                    cols = ["DataReferencia", "Arquivo"] + [c for c in cols if c not in ("DataReferencia", "Arquivo")]
                    df_final = df_final[cols]

                st.dataframe(df_final)

                # Exportar para Excel
                output = BytesIO()
                df_final.to_excel(output, index=False, engine="openpyxl")
                st.download_button("📥 Baixar Excel", data=output.getvalue(), file_name="informes_cvm.xlsx")
            else:
                st.warning("Nenhum XML válido foi processado.")
