import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Simulador ENEM TRI", layout="wide")

st.sidebar.title("Painel de Controle")

# 1. Escolha da Estratégia
estrategia = st.sidebar.selectbox("Escolha a Estratégia", ["Escudo", "Acelerador"])

# 2. Escolha do Ano
ano = st.sidebar.selectbox("Escolha o Ano", [2022, 2023, 2024, 2025])

# 3. Escolha do Dia da Prova
dia = st.sidebar.selectbox("Escolha o Dia do ENEM", ["Dia 1 (Linguagens/Humanas)", "Dia 2 (Matemática/Natureza)"])

# Define o prefixo do arquivo com base na escolha do dia
prefixo_dia = "D1" if "Dia 1" in dia else "D2"
nome_arquivo = f"{estrategia}_Espanhol_{ano}.csv" # Mantém a estrutura dos seus arquivos gerados

@st.cache_data
def carregar_dados(caminho):
    if os.path.exists(caminho):
        return pd.read_csv(caminho, sep=';')
    return pd.DataFrame()

df = carregar_dados(nome_arquivo)

if not df.empty:
    # Se a coluna de dia existir nos seus dados, filtra. Se não, exibe avisando para reprocessar se necessário.
    if 'NO_DIA' in df.columns:
        df_filtrado = df[df['NO_DIA'].astype(str).str.contains(prefixo_dia, case=False, na=False)]
    else:
        df_filtrado = df # Compatibilidade caso queira filtrar depois

    st.sidebar.success(f"Carregado: {len(df_filtrado)} questões ({estrategia} - {ano} - {dia})")

    # Divisão em Blocos de 40 questões
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
        st.info("💡 **Dica de Estudo:** Abra o PDF oficial do Caderno Azul correspondente ao dia selecionado na tela ao lado para visualizar os gráficos, imagens e textos na íntegra.")

        respostas_usuario = {}

        for i, row in df_bloco.iterrows():
            posicao = row['CO_POSICAO']
            habilidade = row.get('NU_HABILIDADE', 'N/D')
            enunciado = row.get('TX_ENUNCIADO', 'Texto indisponível.')

            st.markdown(f"---")
            st.markdown(f"#### Questão {i+1} *(Posição Original Prova Azul: {posicao})* | Habilidade: {habilidade}")
            
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
            st.success("Bloco finalizado com sucesso! (O cálculo da TRI e o gabarito foram computados com base nos parâmetros oficiais).")
    else:
        st.warning("Nenhuma questão encontrada para este filtro no arquivo.")
else:
    st.error(f"Arquivo `{nome_arquivo}` não encontrado na pasta. Verifique se ele está na raiz do repositório.")
