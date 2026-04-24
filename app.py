import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Horário Pro", layout="wide", page_icon="📅")

# --- 2. LIGAÇÃO AO BANCO DE DADOS (SUPABASE) ---
# O código vai buscar as chaves que colaste no campo "Secrets" do Streamlit
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("⚠️ Erro: As chaves do Supabase não foram configuradas nos Secrets do Streamlit.")
    st.stop()

# --- 3. DADOS REAIS DO TEU CADERNO ---
# Horário fiel à foto: Segunda, Terça e Sexta (7 aulas) | Quarta e Quinta (8 aulas)
dados_reais = {
    "SEG": ["ING", "GEO", "MT", "MT", "EO", "CIE", "MT", "-"],
    "TER": ["PT", "GEO", "ART", "PT", "ING", "ING", "IMC", "-"],
    "QUA": ["PT", "CIE", "FC", "AO", "MT", "MT", "PV", "PV"],
    "QUI": ["GEO", "PT", "PT", "PT", "MT", "MT", "PEX", "HIS"],
    "SEXTA": ["HIS", "GEO", "ELET", "ELET", "EF", "EF", "HIS", "-"]
}

df_padrao = pd.DataFrame(dados_reais, index=[f"{i+1}º Horário" for i in range(8)])

# --- 4. LÓGICA DE LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None

def autenticacao():
    st.sidebar.title("🔐 Área de Acesso")
    opcao = st.sidebar.radio("Escolha:", ["Entrar", "Criar Conta"])
    email = st.sidebar.text_input("Teu E-mail")
    senha = st.sidebar.text_input("Tua Senha", type="password")
    
    if opcao == "Criar Conta":
        if st.sidebar.button("Registar"):
            try:
                supabase.auth.sign_up({"email": email, "password": senha})
                st.sidebar.success("Conta criada! Já podes fazer login.")
            except Exception as e:
                st.sidebar.error(f"Erro ao registar: {e}")
    else:
        if st.sidebar.button("Fazer Login"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                st.session_state.user = res.user
                st.rerun()
            except Exception:
                st.sidebar.error("E-mail ou senha incorretos.")

# --- 5. INTERFACE PRINCIPAL ---
if st.session_state.user is None:
    st.title("📅 Horário Pro - Digital")
    st.info("Bem-vindo! Faz login na barra lateral para veres e editares o teu horário.")
    autenticacao()
else:
    st.sidebar.success(f"Logado como: {st.session_state.user.email}")
    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()

    st.title("📝 Minha Grade Escolar")
    st.write("Edita as tuas aulas diretamente na tabela abaixo e clica em Guardar.")

    # Inicializa o editor com os teus dados reais
    if 'grade_editavel' not in st.session_state:
        st.session_state.grade_editavel = df_padrao.copy()

    # Tabela Interativa
    grade_final = st.data_editor(st.session_state.grade_editavel, use_container_width=True)

    # Botão para Salvar no Supabase
    if st.button("💾 Guardar Alterações no Histórico"):
        try:
            dados_para_salvar = {
                "user_id": st.session_state.user.id,
                "nome_grade": f"Horário_{datetime.now().strftime('%d/%m/%Y')}",
                "dados_grade": grade_final.to_json()
            }
            supabase.table("grades").insert(dados_para_salvar).execute()
            st.success("✅ Horário guardado com sucesso na nuvem!")
        except Exception as e:
            st.error(f"❌ Erro ao guardar: {e}. Verificaste se criaste a tabela 'grades' no SQL Editor do Supabase?")

    # Rodapé informativo
    st.markdown("---")
    with st.expander("ℹ️ Legenda das Matérias"):
        st.write("**EO:** Estudo Orientado")
        st.write("**IMC:** Introdução à Metodologia Científica")
        st.write("**PV:** Projeto de Vida")
        st.write("**PEX:** Práticas Experimentais")
