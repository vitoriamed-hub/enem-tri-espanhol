import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Simulador TRI - Blocos de 40", page_icon="🎯", layout="wide"
)

st.title("🎯 Plataforma de Estudos TRI - Espanhol")
st.write(
    "Resolva blocos focados de 40 questões baseados nas suas estratégias de"
    " Escudo e Acelerador."
)

st.sidebar.header("Painel de Controle")
estrategia = st.sidebar.selectbox(
    "Escolha a Estratégia", ["Escudo", "Acelerador"]
)
ano = st.sidebar.selectbox("Escolha o Ano", [2022, 2023, 2024, 2025])

nome_arquivo = f"{estrategia}_Espanhol_{ano}.csv"

try:
  df = pd.read_csv(nome_arquivo, sep=";")

  if "TX_ENUNCIADO" not in df.columns:
    df["TX_ENUNCIADO"] = (
        "Enunciado não encontrado. Consulte a Prova Azul (Posição: "
        + df["CO_POSICAO"].astype(str)
        + ")"
    )

  st.sidebar.success(f"Carregado: {len(df)} questões para {estrategia} ({ano})")

  tamanho_bloco = 40
  total_questoes = len(df)
  total_blocos = (total_questoes + tamanho_bloco - 1) // tamanho_bloco

  lista_blocos = [
      f"Bloco {i+1} (Questões {i*tamanho_bloco + 1} a {min((i+1)*tamanho_bloco, total_questoes)})"
      for i in range(total_blocos)
  ]

  bloco_selecionado = st.sidebar.selectbox(
      "Escolha o Bloco de Estudo", lista_blocos
  )
  indice_bloco = lista_blocos.index(bloco_selecionado)

  inicio = indice_bloco * tamanho_bloco
  fim = min(inicio + tamanho_bloco, total_questoes)
  df_bloco = df.iloc[inicio:fim].reset_index(drop=True)

  st.subheader(
      f"📝 {estrategia} - {ano} | {bloco_selecionado} ({len(df_bloco)}"
      " questões)"
  )

  if "respostas_usuario" not in st.session_state:
    st.session_state.respostas_usuario = {}

  with st.form(key=f"form_bloco_{estrategia}_{ano}_{indice_bloco}"):
    for idx, row in df_bloco.iterrows():
      qid = f"Q_{row['CO_POSICAO']}_{row['CO_PROVA']}_{idx}"

      st.markdown("---")
      st.markdown(
          f"**Questão {inicio + idx + 1}** (Posição Original Prova Azul:"
          f" {row['CO_POSICAO']}) | Habilidade: {row['CO_HABILIDADE']}"
      )
      st.write(row["TX_ENUNCIADO"])

      resposta = st.radio(
          f"Sua resposta para a Questão {inicio + idx + 1}:",
          options=["A", "B", "C", "D", "E"],
          key=qid,
          horizontal=True,
      )

      st.session_state.respostas_usuario[qid] = {
          "escolhida": resposta,
          "gabarito": row["TX_GABARITO"],
          "param_a": row["NU_PARAM_A"],
          "param_b": row["NU_PARAM_B"],
          "param_c": row["NU_PARAM_C"],
      }

    botao_enviar = st.form_submit_button(
        label="🚀 Finalizar Bloco e Calcular Nota TRI"
    )

  if botao_enviar:
    acertos = 0
    questoes_acertadas = []
    total_respondidas = len(df_bloco)

    for idx, row in df_bloco.iterrows():
      qid = f"Q_{row['CO_POSICAO']}_{row['CO_PROVA']}_{idx}"
      if qid in st.session_state.respostas_usuario:
        dados = st.session_state.respostas_usuario[qid]
        if dados["escolhida"] == dados["gabarito"]:
          acertos += 1
          questoes_acertadas.append(dados)

    st.balloons()
    st.success("### 📊 Resultado do Bloco")

    col1, col2 = st.columns(2)
    col1.metric("Acertos no Bloco", f"{acertos} / {total_respondidas}")
    percentual = (
        (acertos / total_respondidas) * 100 if total_respondidas > 0 else 0
    )
    col2.metric("Aproveitamento", f"{percentual:.1f}%")

    if acertos > 0:
      media_b = sum([q["param_b"] for q in questoes_acertadas]) / len(
          questoes_acertadas
      )
      media_a = sum([q["param_a"] for q in questoes_acertadas]) / len(
          questoes_acertadas
      )

      nota_estimada = 500 + (media_b * 100) + (media_a * 50)
      nota_estimada = max(300, min(1000, nota_estimada))

      st.metric(
          label="🎯 Nota TRI Estimada para este Bloco",
          value=f"{nota_estimada:.1f} pts",
      )
    else:
      st.warning(
          "Você não pontuou questões suficientes neste bloco para projetar a"
          " nota TRI."
      )

except FileNotFoundError:
  st.error(
      f"⚠️ O arquivo `{nome_arquivo}` não foi encontrado. Certifique-se de"
      " colocá-lo na mesma pasta do código."
  )