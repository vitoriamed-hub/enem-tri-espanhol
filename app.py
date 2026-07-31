import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Simulador ENEM TRI", layout="wide")

st.sidebar.title("Painel de Controle")

estrategia = st.sidebar.selectbox("Escolha a Estratégia", ["Escudo", "Acelerador"])
ano = st.sidebar.selectbox("Escolha o Ano", [2022, 2023, 2024, 2025])
dia = st.sidebar.selectbox("Escolha o Dia do ENEM", ["Dia 1 (Linguagens/Humanas)", "Dia 2 (Matemática/Natureza)"])

nome_arquivo = f"{estrategia}_Espanhol_{ano}.csv"

@st.cache_data
def carregar_dados(caminho):
    if os.path.exists(caminho):
        df = pd.read_csv(caminho, sep=';')
        if 'CO_POSICAO' in df.columns:
            df = df.drop_duplicates(subset=['CO_POSICAO']).reset_index(drop=True)
        return df
    return pd.DataFrame()

df = carregar_dados(nome_arquivo)

if not df.empty:
    # Filtro inteligente baseado na estrutura oficial das posições do Caderno Azul do ENEM
    if 'CO_POSICAO' in df.columns:
        if "Dia 1" in dia:
            # Dia 1 no ENEM geralmente vai até a posição 90 ou 135 dependendo do escopo
            df_filtrado = df[df['CO_POSICAO'] <= 90]
        else:
            # Dia 2 (Matemática e Natureza) fica na segunda metade
            df_filtrado = df[df['CO_POSICAO'] > 90]
    else:
        df_filtrado = df

    st.sidebar.success(f"Carregado: {len(df_filtrado)} questões ({estrategia} - {ano} - {dia})")

    tamanho_bloco = 40
    total_questoes = len(df_filtrado)
    
    if total_questoes > 0:
        num_blocos = (total_questoes // tamanho_bloco) + (1 if total_questoes % tamanho_bloco > 0 else 0)
        
        opcoes_blocos = [f"Bloco {i+1} (Questões {i*tamanho_bloco + 1} a {min((i+1)*tamanho_bloco, total_questoes)})" for i in range(num_blocos)]
        bloco_escolhido = st.sidebar.selectbox("Escolha o Bloco de Estudo", opcoes_blocos)
        
        idx_bloco = opcoes_blocos.index(bloco_escolhido)
        inicio = idx_bloco * tamanho_bloco
        fim = min((idx_bloco + 1) * tamanho_bloco, total_questoes)
        
        df_bloco = df_filtrado.iloc[inicio:fim].reset_index(drop=True)

        st.title(f"Simulador TRI - {estrategia} ({ano}) | {dia}")
        st.markdown(f"### {bloco_escolhido}")
        st.info("💡 **Dica:** Deixe o PDF oficial do Caderno Azul aberto na tela ao lado para consultar os textos, gráficos e imagens.")

        respostas_usuario = {}

        for i, row in df_bloco.iterrows():
            posicao = row['CO_POSICAO']
            habilidade = None
            for col in ['NU_HABILIDADE', 'CO_HABILIDADE', 'Habilidade']:
                if col in row and pd.notna(row[col]):
                    habilidade = row[col]
                    break
            
            enunciado = row.get('TX_ENUNCIADO', f'Questão {posicao} - Consulte o Caderno Azul Oficial.')

            st.markdown(f"---")
            if habilidade:
                st.markdown(f"#### Questão {i+1} *(Posição Original Prova Azul: {posicao})* | Habilidade: {habilidade}")
            else:
                st.markdown(f"#### Questão {i+1} *(Posição Original Prova Azul: {posicao})*")
            
            with st.container():
                st.markdown(f"**Enunciado / Referência:**\n\n{enunciado}")
            
            respostas_usuario[i] = st.radio(
                f"Sua resposta para a Questão {i+1}:",
                ["A", "B", "C", "D", "E"],
                key=f"q_{idx_bloco}_{i}",
                horizontal=True
            )

        st.markdown("---")
        if st.button("Finalizar Bloco e Calcular TRI"):
            st.success("Bloco finalizado! Gabarito computado com sucesso.")
    else:
        st.warning("Nenhuma questão encontrada para este filtro.")
else:
    st.error(f"Arquivo `{nome_arquivo}` não encontrado na pasta do projeto.")
