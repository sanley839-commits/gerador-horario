import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Horário Pro", layout="wide", page_icon="📅")

# --- CONEXÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("Erro nas chaves do Supabase. Verifique os Secrets.")
    st.stop()

# --- DADOS REAIS (EXTENSO) ---
dados_reais = {
    "Segunda-feira": ["Inglês", "Geografia", "Matemática", "Matemática", "Estudo Orientado", "Ciências", "Matemática", "-"],
    "Terça-feira": ["Português", "Geografia", "Artes", "Português", "Inglês", "Inglês", "Int. Metodologia Científica", "-"],
    "Quarta-feira": ["Português", "Ciências", "Formação Cidadã", "Aprofundamento Oratória", "Matemática", "Matemática", "Projeto de Vida", "Projeto de Vida"],
    "Quinta-feira": ["Geografia", "Português", "Português", "Português", "Matemática", "Matemática", "Práticas Experimentais", "História"],
    "Sexta-feira": ["História", "Geografia", "Eletivas", "Eletivas", "Educação Física", "Educação Física", "História", "-"]
}

df_padrao = pd.DataFrame(dados_reais, index=[f"{i+1}º Horário" for i in range(8)])

# --- LÓGICA DE LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("📅 Horário Pro - Digital")
    st.sidebar.title("🔐 Acesso")
    email = st.sidebar.text_input("E-mail")
    senha = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state.user = res.user
            st.rerun()
        except: st.sidebar.error("Dados incorretos.")
else:
    # --- INTERFACE LOGADA ---
    st.sidebar.success(f"Logado: {st.session_state.user.email}")
    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()

    st.title("📝 Minha Grade Escolar")
    
    if 'grade_editavel' not in st.session_state:
        st.session_state.grade_editavel = df_padrao.copy()

    # Tabela editável
    grade_final = st.data_editor(st.session_state.grade_editavel, use_container_width=True)

    # Botão Salvar
    if st.button("💾 Salvar no Histórico"):
        try:
            dados_json = grade_final.to_json()
            supabase.table("grades").insert({
                "user_id": st.session_state.user.id,
                "nome_grade": f"Grade_{datetime.now().strftime('%d/%m/%Y')}",
                "dados_grade": dados_json
            }).execute()
            st.success("✅ Salvo com sucesso no banco de dados!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}. Verifique se criou a tabela 'grades' no SQL Editor do Supabase.")
