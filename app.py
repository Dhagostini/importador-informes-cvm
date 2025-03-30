import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from xml.etree import ElementTree as ET
import urllib3

# Desabilita os avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def importar_e_exibir_xml(conteudo_xml):
    try:
        df = pd.read_xml(conteudo_xml)
        try:
            root = ET.fromstring(conteudo_xml)
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

def buscar_links_informes(cnpj):
    url = f"https://fnet.bmfbovespa.com.br/fnet/publico/abrirGerenciadorDocumentosCVM?cnpjFundo={cnpj}"
    response = requests.get(url, verify=False)  # Desativa a verificação SSL
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    rows = soup.select("table tbody tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            tipo = cols[0].get_text(strip=True)
            nome = cols[2].get_text(strip=True)
            a = cols[3].find("a")
            href = a["href"] if a else ""
            if "Informe Mensal" in tipo and href.endswith(".xml"):
                links.append({"nome": nome, "link": href})
    return links

st.title("📄 Importador de Informes Mensais - CVM")

cnpj = st.text_input("Digite o CNPJ do fundo:", "20.905.862/0001-70")

if st.button("Buscar e processar"):
    with st.spinner("Buscando documentos..."):
        links = buscar_links_informes(cnpj)
        if not links:
            st.warning("Nenhum informe mensal encontrado.")
        else:
            dfs = []
            for item in links:
                r = requests.get(item["link"])
                df = importar_e_exibir_xml(r.content)
                if df is not None:
                    df["Arquivo"] = item["nome"]
                    dfs.append(df)

            if dfs:
                df_final = pd.concat(dfs, ignore_index=True)
                if "DataReferencia" in df_final.columns:
                    cols = df_final.columns.tolist()
                    cols = ["DataReferencia", "Arquivo"] + [c for c in cols if c not in ("DataReferencia", "Arquivo")]
                    df_final = df_final[cols]

                st.success("Informes processados com sucesso!")
                st.dataframe(df_final)

                # Baixar como Excel
                excel_file = "informes_cvm.xlsx"
                df_final.to_excel(excel_file, index=False)
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Baixar Excel", f, file_name=excel_file)
            else:
                st.error("Erro ao processar os arquivos XML.")
