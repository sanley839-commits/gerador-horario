import streamlit as st

def resolver_horario(turmas, aulas_por_turma, slots):
    agenda = {t: {} for t in turmas}
    prof_ocupado = {s: set() for s in slots}
    
    def backtrack(idx):
        if idx == len(aulas_por_turma): return True
        turma, prof, disc = aulas_por_turma[idx]
        for s in slots:
            if s not in agenda[turma] and prof not in prof_ocupado[s]:
                agenda[turma][s] = f"{disc} ({prof})"
                prof_ocupado[s].add(prof)
                if backtrack(idx + 1): return True
                del agenda[turma][s]
                prof_ocupado[s].remove(prof)
        return False

    return agenda if backtrack(0) else None

st.title("🏫 Gerador de Horário Escolar")
turmas_input = st.text_input("Nomes das Turmas (ex: 101, 102)", "9A, 9B")
if st.button("Gerar Horário"):
    turmas = [t.strip() for t in turmas_input.split(",")]
    slots = ["SEG-1", "SEG-2", "TER-1", "TER-2", "QUA-1"]
    # Exemplo de carga horária fixa para teste
    aulas = []
    for t in turmas:
        aulas.extend([(t, "Prof. Alpha", "Mat"), (t, "Prof. Beta", "Port")])
    
    resultado = resolver_horario(turmas, aulas, slots)
    if resultado:
        for t in turmas:
            st.subheader(f"Turma {t}")
            st.table(resultado[t])
    else:
        st.error("Conflito impossível de resolver!")
