import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import io

# --- 1. CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(
    page_title="Horário Pro | Digital",
    layout="wide",
    page_icon="📅"
)

# CSS para trazer o layout profissional de volta
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    /* Botão Salvar (Azul) */
    div[data-testid="column"]:nth-child(1) button {
        background-color: #1E88E5 !important;
        color: white !important;
    }
    /* Botão Excel (Verde) */
    div[data-testid="column"]:nth-child(2) button {
        background-color: #217346 !important;
        color: white !important;
    }
    .metric-card {
        background-color: #1d2127;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("Configuração pendente nos Secrets.")
    st.stop()

# --- 3. CÁLCULO DE HORÁRIOS (AULAS DE 55MIN) ---
horarios_duracao = [
    "07:30 - 08:25", "08:25 - 09:20", # Aula 1 e 2
    "09:40 - 10:35", "10:35 - 11:30", # Aula 3 e 4 (após intervalo 20min)
    "13:00 - 13:55", "13:55 - 14:50", # Aula 5 e 6 (após almoço 1h30)
    "15:10 - 16:05", "16:05 - 17:00"  # Aula 7 e 8 (após intervalo 20min)
]

indice_aulas = [f"{i+1}ª Aula ({horarios_duracao[i]})" for i in range(8)]

dados_reais = {
    "Segunda-feira": ["Inglês", "Geografia", "Matemática", "Matemática", "Estudo Orientado", "Ciências", "Matemática", "-"],
    "Terça-feira": ["Português", "Geografia", "Artes", "Português", "Inglês", "Inglês", "Int. Metodologia Científica", "-"],
    "Quarta-feira": ["Português", "Ciências", "Formação Cidadã", "Aprofundamento Oratória", "Matemática", "Matemática", "Projeto de Vida", "Projeto de Vida"],
    "Quinta-feira": ["Geografia", "Português", "Português", "Português", "Matemática", "Matemática", "Práticas Experimentais", "História"],
    "Sexta-feira": ["História", "Geografia", "Eletivas", "Eletivas", "Educação Física", "Educação Física", "História", "-"]
}

df_padrao = pd.DataFrame(dados_reais, index=indice_aulas)

# --- 4. LÓGICA DE LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>📅 Horário Pro</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u_email = st.text_input("E-mail")
            u_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": u_email, "password": u_pass})
                    st.session_state.user = res.user
                    st.rerun()
                except: st.error("Erro no login.")
else:
    # --- DASHBOARD ---
    st.title("🚀 Minha Grade Escolar")
    
    # Cards de Status
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="metric-card">🟢 Status: Sincronizado</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card">📅 {datetime.now().strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="metric-card">👤 Logado</div>', unsafe_allow_html=True)

    st.write("")
    
    if 'grade_editavel' not in st.session_state:
        st.session_state.grade_editavel = df_padrao.copy()

    # Editor da Planilha
    grade_final = st.data_editor(st.session_state.grade_editavel, use_container_width=True)

    # --- BOTÕES ---
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("💾 Salvar na Nuvem"):
            try:
                supabase.table("grades").insert({
                    "user_id": st.session_state.user.id,
                    "nome_grade": f"Grade_{datetime.now().strftime('%d/%m')}",
                    "dados_grade": grade_final.to_json()
                }).execute()
                st.toast("Salvo!", icon="✅")
            except Exception as e: st.error(f"Erro: {e}")

    with col_btn2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            grade_final.to_excel(writer, index=True)
        st.download_button(
            label="📥 Baixar em Excel (.xlsx)",
            data=output.getvalue(),
            file_name="meu_horario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()
