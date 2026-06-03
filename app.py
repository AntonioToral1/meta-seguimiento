"""
Seguimiento de cartera 3-16 días — Metaliados
Dashboard para Brisa, Jessy, Eder y Yessica.
"""
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Seguimiento Metaliados",
    page_icon="📋",
    layout="wide",
)

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)   # refresca cada hora
def cargar_datos():
    return pd.read_csv("data/seguimiento_metaliados.csv", low_memory=False)

df_all = cargar_datos()

# ── Info del bloque ───────────────────────────────────────────────────────────
bloque_num    = int(df_all['bloque_num'].iloc[0])
inicio_bloque = df_all['inicio_bloque'].iloc[0]
fin_bloque    = df_all['fin_bloque'].iloc[0]
corte_actual  = df_all['corte_actual'].iloc[0]

COLS_MOSTRAR = [
    'Grupo', 'Solicitud', 'Asesor_Actual', 'moneda_Capital',
    'moneda_Monto_a_Pagar', 'moneda_Saldo', 'moneda_Vencido', 'moneda_Pagado',
    'Pago Semanal', 'Ficha Actual', 'Falta Sig. Ficha', 'Dias_De_Atraso',
]
COLS_MOSTRAR_ACT = COLS_MOSTRAR + ['Movimiento']

RENOMBRAR = {
    'Asesor_Actual':       'Asesor Actual',
    'moneda_Capital':      'Capital',
    'moneda_Monto_a_Pagar':'Monto a Pagar',
    'moneda_Saldo':        'Saldo',
    'moneda_Vencido':      'Saldo Vencido',
    'moneda_Pagado':       'Pagado',
    'Dias_De_Atraso':      'Días Atraso',
}

FMT_MONEDA = {
    'Capital':'${:,.0f}', 'Monto a Pagar':'${:,.0f}', 'Saldo':'${:,.0f}',
    'Saldo Vencido':'${:,.0f}', 'Pagado':'${:,.0f}',
    'Pago Semanal':'${:,.0f}', 'Falta Sig. Ficha':'${:,.0f}',
}

def colorear_dias(val):
    try:
        v = float(val)
    except (TypeError, ValueError):
        return 'background-color:#DDEBF7; color:#333'  # finalizado
    if v == 0:   return 'background-color:#E2EFDA'
    if v <= 2:   return 'background-color:#EBF3D1'
    if v <= 16:  return 'background-color:#FFEB9C'
    return 'background-color:#FFC7CE'

def colorear_movimiento(val):
    s = str(val)
    if 'Regular' in s: return 'color:#375623; font-weight:bold'
    if 'Mejoró'  in s: return 'color:#1F497D; font-weight:bold'
    if 'Deterioró' in s: return 'color:#C00000; font-weight:bold'
    if 'Finalizó'  in s: return 'color:#595959; font-style:italic'
    return ''

def mostrar_tabla(df_sec, es_actual=False):
    cols = COLS_MOSTRAR_ACT if es_actual else COLS_MOSTRAR
    cols_presentes = [c for c in cols if c in df_sec.columns]
    df_show = df_sec[cols_presentes].rename(columns=RENOMBRAR).copy()

    # Formatear monedas
    for col, fmt in FMT_MONEDA.items():
        if col in df_show.columns:
            df_show[col] = df_show[col].apply(
                lambda x: fmt.format(x) if pd.notna(x) and x != '' else '—')

    # Formatear Ficha Actual
    if 'Ficha Actual' in df_show.columns:
        df_show['Ficha Actual'] = df_show['Ficha Actual'].apply(
            lambda x: str(int(x)) if pd.notna(x) else '—')

    # Formatear Días Atraso
    if 'Días Atraso' in df_show.columns:
        df_show['Días Atraso'] = df_show['Días Atraso'].apply(
            lambda x: str(int(x)) if pd.notna(x) else 'Finalizó')

    # Aplicar estilos
    styler = df_show.style.hide(axis='index')
    if 'Días Atraso' in df_show.columns:
        styler = styler.map(colorear_dias, subset=['Días Atraso'])
    if es_actual and 'Movimiento' in df_show.columns:
        styler = styler.map(colorear_movimiento, subset=['Movimiento'])

    st.dataframe(styler, use_container_width=True, height=min(600, 50 + len(df_show)*36))

def metricas_rapidas(df_ini, df_act, label_ini, label_act):
    n_ini = len(df_ini)
    n_act = len(df_act[df_act['Dias_De_Atraso'].notna()]) if 'Dias_De_Atraso' in df_act else 0

    mov = df_act['Movimiento'].value_counts() if 'Movimiento' in df_act.columns else pd.Series()
    regular = sum(v for k, v in mov.items() if 'Regular' in k)
    mejoro   = sum(v for k, v in mov.items() if 'Mejoró' in k)
    deterioro= sum(v for k, v in mov.items() if 'Deterioró' in k)
    finalizo = sum(v for k, v in mov.items() if 'Finalizó' in k)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Grupos al inicio bloque", n_ini)
    c2.metric("✓ Regularizaron", regular)
    c3.metric("↑ Mejoraron", mejoro)
    c4.metric("↓ Deterioraron", deterioro)
    c5.metric("Finalizaron", finalizo)

# ── Header principal ──────────────────────────────────────────────────────────
st.title("📋 Seguimiento de Cartera — Metaliados")
st.caption(
    f"**Bloque {bloque_num}** &nbsp;|&nbsp; "
    f"{inicio_bloque} → {fin_bloque} &nbsp;|&nbsp; "
    f"Corte: **{corte_actual}**"
)
st.divider()

# ── Tabs por metaliado ────────────────────────────────────────────────────────
METALIADOS = ['Brisa', 'Jessy', 'Eder', 'Yessica']
tabs = st.tabs([f"👤 {m}" for m in METALIADOS])

for tab, nombre in zip(tabs, METALIADOS):
    with tab:
        df_meta = df_all[df_all['metaliado'] == nombre]
        df_ini  = df_meta[df_meta['seccion'] == 'inicio_bloque'].copy()
        df_act  = df_meta[df_meta['seccion'] == 'estado_actual'].copy()

        if df_ini.empty:
            st.info(f"Sin grupos en rango 3-16 días al inicio del bloque para {nombre}.")
            continue

        metricas_rapidas(df_ini, df_act, inicio_bloque, corte_actual)
        st.write("")

        col_ini, col_act = st.columns(2)

        with col_ini:
            st.markdown(f"#### 📅 Inicio Bloque {bloque_num} — {inicio_bloque}")
            st.caption(f"{len(df_ini)} grupos con 3-16 días de atraso")
            mostrar_tabla(df_ini, es_actual=False)

        with col_act:
            st.markdown(f"#### 🔄 Estado Actual — {corte_actual}")
            st.caption(f"{len(df_act)} grupos seguidos")
            mostrar_tabla(df_act, es_actual=True)

# ── Leyenda ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "🟩 0 días — Regularizó &nbsp;&nbsp;"
    "🟨 1-2 días — Casi &nbsp;&nbsp;"
    "🟧 3-16 días — En rango &nbsp;&nbsp;"
    "🟥 17+ días — Deterioró &nbsp;&nbsp;"
    "🔵 Finalizó / Pagó"
)
