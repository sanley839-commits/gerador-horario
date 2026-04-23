import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Horário Pro", layout="wide")

st.title("📅 Horário Pro - Grade Personalizada")

def calcular_horarios(num_aulas):
    horarios = []
    # Primeira aula começa 07:30
    atual = datetime.strptime("07:30", "%H:%M")
    
    for i in range(1, num_aulas + 1):
        inicio = atual.strftime("%H:%M")
        fim = (atual + timedelta(minutes=55)).strftime("%H:%M")
        horarios.append(f"{i}ª Aula ({inicio} - {fim})")
        
        # Define o próximo horário
        proximo_inicio = atual + timedelta(minutes=55)
        
        # Lógica de Intervalos
        if i == 2: # Intervalo da Manhã (pós 2ª aula)
            proximo_inicio += timedelta(minutes=20)
        elif i == 4: # Almoço (pós 4ª aula)
            proximo_inicio += timedelta(minutes=90)
        elif i == 6: # Intervalo da Tarde (pós 6ª aula)
            proximo_inicio += timedelta(minutes=20)
        
        atual = proximo_inicio
    return horarios

# --- Interface ---
with st.sidebar:
    st.header("Configurações")
    turmas_input = st.text_input("Suas Turmas/Disciplinas", "Minha Grade")
    if st.button("Gerar Horário Escolar"):
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        grade_final = {}
        
        for dia in dias:
            # Regra: Seg, Ter e Sex = 7 aulas | Qua e Qui = 8 aulas
            n_aulas = 7 if dia in ["Segunda", "Terça", "Sexta"] else 8
            col_horarios = calcular_horarios(n_aulas)
            
            # Preenche com vazio para manter o DataFrame alinhado
            if n_aulas == 7:
                col_horarios.append("--- Fim do Período ---")
            
            grade_final[dia] = col_horarios
        
        # Criar DataFrame (Colunas = Dias, Linhas = Aulas)
        df = pd.DataFrame(grade_final)
        # Ajustar index para números ordinais 1-8
        df.index = [f"{i+1}º Horário" for i in range(8)]
        
        # Criar uma versão para edição onde as células estão vazias
        # mas mantemos os nomes das aulas como referência visual se desejar
        df_edit = pd.DataFrame("", index=df.index, columns=df.columns)
        
        # Guardar as legendas de horários para mostrar ao usuário
        st.session_state['legendas'] = df
        st.session_state['grade_editavel'] = df_edit

# --- Visualização ---
if 'grade_editavel' in st.session_state:
    st.subheader("📝 Preencha sua Grade")
    st.write("🕒 **Referência de Horários (Automático):**")
    st.table(st.session_state['legendas']) # Mostra a tabela de horários calculada
    
    st.markdown("---")
    st.write("✍️ **Sua Planilha (Edite abaixo):**")
    
    # Editor onde você coloca as matérias
    grade_preenchida = st.data_editor(
        st.session_state['grade_editavel'],
        use_container_width=True,
        height=400
    )
    
    st.session_state['grade_editavel'] = grade_preenchida
    
    csv = grade_preenchida.to_csv().encode('utf-8-sig')
    st.download_button("📥 Baixar Planilha", csv, "meu_horario.csv", "text/csv")
