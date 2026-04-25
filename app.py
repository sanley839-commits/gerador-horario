import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIGURAÇÃO VISUAL DE ELITE ---
st.set_page_config(
    page_title="Horário Pro | Digital",
    layout="wide",
    page_icon="📅",
    initial_sidebar_state="expanded"
)

# CSS para customizar botões e a tabela
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff1a1a;
        transform: scale(1.02);
    }
    div[data-testid="stExpander"] {
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("⚠️ Configuração pendente: Insira as chaves nos Secrets.")
    st.stop()

# --- 3. DADOS REAIS ---
dados_reais = {
    "Segunda-feira": ["Inglês", "Geografia", "Matemática", "Matemática", "Estudo Orientado", "Ciências", "Matemática", "-"],
    "Terça-feira": ["Português", "Geografia", "Artes", "Português", "Inglês", "Inglês", "Int. Metodologia Científica", "-"],
    "Quarta-feira": ["Português", "Ciências", "Formação Cidadã", "Aprofundamento Oratória", "Matemática", "Matemática", "Projeto de Vida", "Projeto de Vida"],
    "Quinta-feira": ["Geografia", "Português", "Português", "Português", "Matemática", "Matemática", "Práticas Experimentais", "História"],
    "Sexta-feira": ["História", "Geografia", "Eletivas", "Eletivas", "Educação Física", "Educação Física", "História", "-"]
}
df_padrao = pd.DataFrame(dados_reais, index=[f"{i+1}º Horário" for i in range(8)])

# --- 4. LÓGICA DE ACESSO ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # --- TELA DE BOAS-VINDAS ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>📅 Horário Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Organize sua rotina escolar com precisão.</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.subheader("🔒 Acesso ao Sistema")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar no Dashboard"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                    st.session_state.user = res.user
                    st.rerun()
                except:
                    st.error("E-mail ou senha incorretos.")
else:
    # --- DASHBOARD PROFISSIONAL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.write(f"**Usuário:**\n{st.session_state.user.email}")
        st.divider()
        if st.button("Sair da Conta"):
            st.session_state.user = None
            st.rerun()

    # Cabeçalho com métricas
    st.title("🚀 Meu Dashboard Escolar")
    c1, c2, c3 = st.columns(3)
    c1.metric("Status", "Online", "Conectado")
    c2.metric("Aulas Hoje", "7 Aulas" if datetime.now().weekday() in [0, 1, 4] else "8 Aulas")
    c3.metric("Semestre", "2026.1")

    st.markdown("---")

    # Área da Planilha
    st.subheader("📑 Grade de Horários")
    
    if 'grade_editavel' not in st.session_state:
        st.session_state.grade_editavel = df_padrao.copy()

    # Estilo do editor de dados (moderno)
    grade_final = st.data_editor(
        st.session_state.grade_editavel,
        use_container_width=True,
        hide_index=False,
        num_rows="fixed"
    )

    # Botão de Ação
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("💾 Salvar Grade"):
            try:
                dados_json = grade_final.to_json()
                supabase.table("grades").insert({
                    "user_id": st.session_state.user.id,
                    "nome_grade": f"Grade_{datetime.now().strftime('%d/%m/%Y')}",
                    "dados_grade": dados_json
                }).execute()
                st.success("Dados sincronizados!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    # Legendas em Cards
    st.divider()
    exp = st.expander("🔍 Detalhes das Disciplinas e Siglas")
    with exp:
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.markdown("- **Estudo Orientado:** Foco em tarefas.")
            st.markdown("- **Int. Metodologia Científica:** Pesquisa e ciência.")
        with col_l2:
            st.markdown("- **Práticas Experimentais:** Laboratório e testes.")
            st.markdown("- **Formação Cidadã:** Ética e sociedade.")
