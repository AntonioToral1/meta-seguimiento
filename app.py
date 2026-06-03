"""
Seguimiento de cartera 3-16 días — Metaliados
Dashboard para Brisa, Jessy, Eder y Yessica.
"""
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Seguimiento Metaliados — Meta Financiera",
    page_icon="https://cdn.prod.website-files.com/65cb9bd564b33f4f7de90ae8/6a024776f534d5547c65cf60_LogoCompleto-Azul.png",
    layout="wide",
)

# ── Colores Meta Financiera ────────────────────────────────────────────────────
AZUL_OSCURO  = "#003875"
AZUL_MEDIO   = "#0066CC"
AZUL_CLARO   = "#E8F0FB"
BLANCO       = "#FFFFFF"
GRIS_CLARO   = "#F5F7FA"
TEXTO_OSCURO = "#1A1A2E"

st.markdown(f"""
<style>
    /* Fondo general */
    .stApp {{ background-color: {GRIS_CLARO}; }}

    /* Header personalizado */
    .meta-header {{
        background-color: {AZUL_OSCURO};
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }}
    .meta-header h1 {{
        color: {BLANCO};
        margin: 0;
        font-size: 1.3rem;
        font-weight: 700;
    }}
    .meta-header .subtitle {{
        color: #B8CCE8;
        font-size: 0.85rem;
        margin-top: 2px;
    }}

    /* Tarjetas de métricas */
    [data-testid="metric-container"] {{
        background-color: {BLANCO};
        border: 1px solid #D0DCF0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border-left: 4px solid {AZUL_MEDIO};
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {AZUL_OSCURO};
        border-radius: 8px 8px 0 0;
        padding: 4px;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #B8CCE8 !important;
        font-weight: 600;
        border-radius: 6px;
        padding: 6px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {AZUL_MEDIO} !important;
        color: {BLANCO} !important;
    }}

    /* Sección headers */
    .seccion-titulo {{
        background-color: {AZUL_OSCURO};
        color: {BLANCO};
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 6px;
    }}
    .seccion-titulo-actual {{
        background-color: {AZUL_MEDIO};
        color: {BLANCO};
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 6px;
    }}

    /* Tabla de buckets */
    .bucket-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        margin-bottom: 1rem;
    }}
    .bucket-table th {{
        background-color: {AZUL_OSCURO};
        color: {BLANCO};
        padding: 7px 12px;
        text-align: center;
    }}
    .bucket-table td {{
        padding: 6px 12px;
        text-align: center;
        border-bottom: 1px solid #E0E0E0;
    }}
    .bk-ok      {{ background-color: #E2EFDA; }}
    .bk-casi    {{ background-color: #EBF3D1; }}
    .bk-leve    {{ background-color: #FFF2CC; }}
    .bk-mod     {{ background-color: #FFEB9C; }}
    .bk-alto    {{ background-color: #FFC7CE; }}
    .bk-fin     {{ background-color: #DDEBF7; }}
    .bk-total   {{ background-color: {AZUL_CLARO}; font-weight: bold; }}

    div[data-testid="stDivider"] {{ margin: 0.5rem 0; }}
    footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def cargar_datos():
    return pd.read_csv("data/seguimiento_metaliados.csv", low_memory=False)

df_all = cargar_datos()

bloque_num    = int(df_all['bloque_num'].iloc[0])
inicio_bloque = df_all['inicio_bloque'].iloc[0]
fin_bloque    = df_all['fin_bloque'].iloc[0]
corte_actual  = df_all['corte_actual'].iloc[0]

# ── Header ─────────────────────────────────────────────────────────────────────
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.image(
        "https://cdn.prod.website-files.com/65cb9bd564b33f4f7de90ae8/6a024776f534d5547c65cf60_LogoCompleto-Azul.png",
        width=160,
    )
with col_titulo:
    st.markdown(f"""
    <div style="padding-top:8px">
        <span style="font-size:1.4rem; font-weight:800; color:{AZUL_OSCURO}">
            Seguimiento de Cartera — Metaliados
        </span><br>
        <span style="color:#555; font-size:0.9rem">
            Bloque&nbsp;<b>{bloque_num}</b> &nbsp;·&nbsp;
            {inicio_bloque} → {fin_bloque} &nbsp;·&nbsp;
            Corte: <b>{corte_actual}</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Helpers ────────────────────────────────────────────────────────────────────
COLS_BASE = [
    'Grupo','Solicitud','Asesor_Actual','moneda_Capital',
    'moneda_Monto_a_Pagar','moneda_Saldo','moneda_Vencido','moneda_Pagado',
    'Pago Semanal','Ficha Actual','Falta Sig. Ficha','Dias_De_Atraso',
]
RENOMBRAR = {
    'Asesor_Actual':'Asesor','moneda_Capital':'Capital',
    'moneda_Monto_a_Pagar':'Monto a Pagar','moneda_Saldo':'Saldo',
    'moneda_Vencido':'Saldo Vencido','moneda_Pagado':'Pagado',
    'Dias_De_Atraso':'Días Atraso',
}
COLS_MONEDA = ['Capital','Monto a Pagar','Saldo','Saldo Vencido',
               'Pagado','Pago Semanal','Falta Sig. Ficha']

BUCKETS = [
    ('0 días (Al corriente)',  lambda d: d == 0,             'bk-ok'),
    ('1 - 2 días',             lambda d: 1 <= d <= 2,        'bk-casi'),
    ('3 - 7 días',             lambda d: 3 <= d <= 7,        'bk-leve'),
    ('8 - 15 días',            lambda d: 8 <= d <= 15,       'bk-mod'),
    ('16+ días',               lambda d: d >= 16,            'bk-alto'),
    ('Finalizó / Pagó',        lambda d: pd.isna(d),         'bk-fin'),
]

def colorear_dias(val):
    try: v = float(val)
    except: return f'background-color:#DDEBF7; color:#555'
    if v == 0:  return 'background-color:#E2EFDA'
    if v <= 2:  return 'background-color:#EBF3D1'
    if v <= 15: return 'background-color:#FFEB9C'
    return 'background-color:#FFC7CE'

def colorear_mov(val):
    s = str(val)
    if 'Regular' in s: return f'color:#375623; font-weight:bold'
    if 'Mejoró'  in s: return f'color:{AZUL_MEDIO}; font-weight:bold'
    if 'Deterioró' in s: return 'color:#C00000; font-weight:bold'
    if 'Finalizó'  in s: return 'color:#595959; font-style:italic'
    return ''

def preparar_df(df_sec, es_actual=False):
    cols = COLS_BASE + (['Movimiento'] if es_actual else [])
    cols = [c for c in cols if c in df_sec.columns]
    df = df_sec[cols].rename(columns=RENOMBRAR).copy()
    for col in COLS_MONEDA:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"${float(x):,.0f}" if pd.notna(x) and x != '' else '—')
    if 'Ficha Actual' in df.columns:
        df['Ficha Actual'] = df['Ficha Actual'].apply(lambda x: str(int(x)) if pd.notna(x) else '—')
    if 'Días Atraso' in df.columns:
        df['Días Atraso'] = df['Días Atraso'].apply(lambda x: str(int(float(x))) if pd.notna(x) else 'Finalizó')
    return df

def mostrar_tabla(df_sec, es_actual=False):
    df = preparar_df(df_sec, es_actual)
    styler = df.style.hide(axis='index')
    if 'Días Atraso' in df.columns:
        styler = styler.map(colorear_dias, subset=['Días Atraso'])
    if es_actual and 'Movimiento' in df.columns:
        styler = styler.map(colorear_mov, subset=['Movimiento'])
    st.dataframe(styler, use_container_width=True, height=min(550, 50 + len(df) * 36))

def tabla_buckets_html(df_act):
    """Genera tabla HTML con distribución por bucket."""
    dias_raw = pd.to_numeric(df_act['Dias_De_Atraso'], errors='coerce')
    saldo_raw   = pd.to_numeric(df_act['moneda_Saldo'],   errors='coerce').fillna(0)
    vencido_raw = pd.to_numeric(df_act['moneda_Vencido'], errors='coerce').fillna(0)

    filas_html = ""
    tot_n = tot_s = tot_v = 0

    for label, cond, css in BUCKETS:
        mask = dias_raw.apply(lambda d: cond(d))
        n = mask.sum()
        s = saldo_raw[mask].sum()
        v = vencido_raw[mask].sum()
        tot_n += n; tot_s += s; tot_v += v
        if n == 0:
            continue
        filas_html += f"""
        <tr class="{css}">
            <td style="text-align:left; padding-left:14px">{label}</td>
            <td><b>{n}</b></td>
            <td>${s:,.0f}</td>
            <td>${v:,.0f}</td>
        </tr>"""

    filas_html += f"""
    <tr class="bk-total">
        <td style="text-align:left; padding-left:14px">TOTAL</td>
        <td><b>{tot_n}</b></td>
        <td>${tot_s:,.0f}</td>
        <td>${tot_v:,.0f}</td>
    </tr>"""

    return f"""
    <table class="bucket-table">
        <thead>
            <tr>
                <th style="text-align:left">Bucket</th>
                <th>Grupos</th>
                <th>Saldo</th>
                <th>Saldo Vencido</th>
            </tr>
        </thead>
        <tbody>{filas_html}</tbody>
    </table>"""

def metricas_rapidas(df_act):
    mov = df_act['Movimiento'].value_counts() if 'Movimiento' in df_act.columns else pd.Series()
    regular  = sum(v for k, v in mov.items() if 'Regular' in k)
    mejoro   = sum(v for k, v in mov.items() if 'Mejoró'  in k)
    igual    = sum(v for k, v in mov.items() if 'cambio'  in k)
    deterioro= sum(v for k, v in mov.items() if 'Deterioró' in k)
    finalizo = sum(v for k, v in mov.items() if 'Finalizó'  in k)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("✓ Regularizaron", regular)
    c2.metric("↑ Mejoraron",     mejoro)
    c3.metric("= Sin cambio",    igual)
    c4.metric("↓ Deterioraron",  deterioro)
    c5.metric("Finalizaron",     finalizo)

# ── Tabs por metaliado ─────────────────────────────────────────────────────────
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

        # Métricas de movimiento
        metricas_rapidas(df_act)
        st.write("")

        # Distribución por bucket (estado actual)
        st.markdown(f'<div class="seccion-titulo-actual">📊 Distribución por Bucket — Estado Actual ({corte_actual})</div>',
                    unsafe_allow_html=True)
        st.markdown(tabla_buckets_html(df_act), unsafe_allow_html=True)

        # Tablas lado a lado
        c_ini, c_act = st.columns(2)

        with c_ini:
            st.markdown(f'<div class="seccion-titulo">📅 Inicio Bloque {bloque_num} — {inicio_bloque}</div>',
                        unsafe_allow_html=True)
            st.caption(f"{len(df_ini)} grupos con 3-16 días de atraso al inicio del bloque")
            mostrar_tabla(df_ini, es_actual=False)

        with c_act:
            st.markdown(f'<div class="seccion-titulo-actual">🔄 Estado Actual — {corte_actual}</div>',
                        unsafe_allow_html=True)
            st.caption(f"{len(df_act)} grupos seguidos desde el inicio del bloque")
            mostrar_tabla(df_act, es_actual=True)

# ── Leyenda ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="font-size:0.8rem; color:#666; display:flex; gap:1.5rem; flex-wrap:wrap">
    <span style="background:#E2EFDA; padding:2px 8px; border-radius:4px">🟩 0 días — Al corriente</span>
    <span style="background:#EBF3D1; padding:2px 8px; border-radius:4px">🟩 1-2 días — Casi</span>
    <span style="background:#FFEB9C; padding:2px 8px; border-radius:4px">🟨 3-15 días — En rango</span>
    <span style="background:#FFC7CE; padding:2px 8px; border-radius:4px">🟥 16+ días — Deterioró</span>
    <span style="background:#DDEBF7; padding:2px 8px; border-radius:4px">🔵 Finalizó / Pagó</span>
</div>
""", unsafe_allow_html=True)
