"""
Seguimiento de cartera 3-16 días — Metaliados
Dashboard para Marisol, Jessy, Eder y Yessica, más una pestaña Nacional
con el agregado de las sucursales de los 4 metaliados combinadas.
Saldo en riesgo: 0-2d=vencido, 3+d=saldo completo. (2026-06-23)
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

st.markdown(f"""
<style>
    .stApp {{ background-color: {GRIS_CLARO}; }}
    [data-testid="metric-container"] {{
        background-color: {BLANCO};
        border: 1px solid #D0DCF0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border-left: 4px solid {AZUL_MEDIO};
    }}
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
    .bk-ok    {{ background-color: #E2EFDA; }}
    .bk-casi  {{ background-color: #EBF3D1; }}
    .bk-leve  {{ background-color: #FFF2CC; }}
    .bk-mod   {{ background-color: #FFEB9C; }}
    .bk-alto  {{ background-color: #FFC7CE; }}
    .bk-fin   {{ background-color: #DDEBF7; }}
    .bk-total {{ background-color: {AZUL_CLARO}; font-weight: bold; }}
    div[data-testid="stDivider"] {{ margin: 0.5rem 0; }}
    footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def cargar_datos():
    df = pd.read_csv("data/seguimiento_metaliados.csv", low_memory=False)
    return df

@st.cache_data(ttl=600)
def cargar_cosechas():
    try:
        return pd.read_csv("data/seguimiento_cosechas.csv", low_memory=False)
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def cargar_riesgo():
    try:
        return pd.read_csv("data/seguimiento_riesgo.csv", low_memory=False)
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def cargar_goteo():
    try:
        return pd.read_csv("data/seguimiento_goteo.csv", low_memory=False)
    except FileNotFoundError:
        return pd.DataFrame()

df_all         = cargar_datos()
df_cosecha_all = cargar_cosechas()
df_riesgo_all  = cargar_riesgo()
df_goteo_all   = cargar_goteo()

# Bloques disponibles (ordenados desc para que el más reciente sea primero)
bloques_disponibles = sorted(df_all['bloque_num'].unique(), reverse=True)

# ── Header ─────────────────────────────────────────────────────────────────────
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.image(
        "https://cdn.prod.website-files.com/65cb9bd564b33f4f7de90ae8/6a024776f534d5547c65cf60_LogoCompleto-Azul.png",
        width=160,
    )
with col_titulo:
    # Info del bloque actual (más reciente)
    blq_cur = bloques_disponibles[0]
    row0 = df_all[df_all['bloque_num'] == blq_cur].iloc[0]
    st.markdown(f"""
    <div style="padding-top:8px">
        <span style="font-size:1.4rem; font-weight:800; color:{AZUL_OSCURO}">
            Seguimiento de Cartera — Metaliados
        </span><br>
        <span style="color:#555; font-size:0.9rem">
            Bloque&nbsp;<b>{blq_cur}</b> &nbsp;·&nbsp;
            {row0['inicio_bloque']} → {row0['fin_bloque']} &nbsp;·&nbsp;
            Corte: <b>{row0['corte_actual']}</b>
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
    ('0 días (Al corriente)',  lambda d: d == 0,      'bk-ok'),
    ('1 - 2 días',             lambda d: 1 <= d <= 2, 'bk-casi'),
    ('3 - 7 días',             lambda d: 3 <= d <= 7, 'bk-leve'),
    ('8 - 15 días',            lambda d: 8 <= d <= 15,'bk-mod'),
    ('16+ días',               lambda d: d >= 16,     'bk-alto'),
    ('Finalizó / Pagó',        lambda d: pd.isna(d),  'bk-fin'),
]

def colorear_dias(val):
    try: v = float(val)
    except: return 'background-color:#DDEBF7; color:#555'
    if v == 0:  return 'background-color:#E2EFDA'
    if v <= 2:  return 'background-color:#EBF3D1'
    if v <= 15: return 'background-color:#FFEB9C'
    return 'background-color:#FFC7CE'

def colorear_mov(val):
    s = str(val)
    if 'Regular'   in s: return 'color:#375623; font-weight:bold'
    if 'Mejoró'    in s: return f'color:{AZUL_MEDIO}; font-weight:bold'
    if 'Conten' in s: return 'color:#7B6200; font-weight:bold'
    if 'Deterioró' in s: return 'color:#C00000; font-weight:bold'
    if 'Finalizó'  in s: return 'color:#595959; font-style:italic'
    return ''

def preparar_df(df_sec, es_actual=False):
    cols = COLS_BASE + (['Movimiento'] if es_actual else [])
    cols = [c for c in cols if c in df_sec.columns]
    df = df_sec[cols].rename(columns=RENOMBRAR).copy()
    for col in COLS_MONEDA:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: f"${float(x):,.0f}" if pd.notna(x) and x != '' else '—')
    if 'Ficha Actual' in df.columns:
        df['Ficha Actual'] = df['Ficha Actual'].apply(
            lambda x: str(int(x)) if pd.notna(x) else '—')
    if 'Días Atraso' in df.columns:
        df['Días Atraso'] = df['Días Atraso'].apply(
            lambda x: str(int(float(x))) if pd.notna(x) else 'Finalizó')
    return df

def mostrar_tabla(df_sec, es_actual=False):
    df = preparar_df(df_sec, es_actual)
    styler = df.style.hide(axis='index')
    if 'Días Atraso' in df.columns:
        styler = styler.map(colorear_dias, subset=['Días Atraso'])
    if es_actual and 'Movimiento' in df.columns:
        styler = styler.map(colorear_mov, subset=['Movimiento'])
    st.dataframe(styler, use_container_width=True, height=min(550, 50 + len(df) * 36))

def tabla_buckets_html(df_sec, titulo_label=''):
    dias_raw    = pd.to_numeric(df_sec['Dias_De_Atraso'], errors='coerce')
    saldo_raw   = pd.to_numeric(df_sec['moneda_Saldo'],   errors='coerce').fillna(0)
    vencido_raw = pd.to_numeric(df_sec['moneda_Vencido'], errors='coerce').fillna(0)

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
                <th style="text-align:left">{titulo_label or 'Bucket'}</th>
                <th>Grupos</th>
                <th>Saldo</th>
                <th>Saldo Vencido</th>
            </tr>
        </thead>
        <tbody>{filas_html}</tbody>
    </table>"""

def metricas_rapidas(df_act):
    mov = df_act['Movimiento'].value_counts() if 'Movimiento' in df_act.columns else pd.Series()
    regular    = sum(v for k, v in mov.items() if 'Regular'    in k)
    mejoro     = sum(v for k, v in mov.items() if 'Mejoró'     in k)
    contencion = sum(v for k, v in mov.items() if 'Conten' in k)
    deterioro  = sum(v for k, v in mov.items() if 'Deterioró'  in k)
    finalizo   = sum(v for k, v in mov.items() if 'Finalizó'   in k)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("✓ Regularizaron", regular)
    c2.metric("↑ Mejoraron",     mejoro)
    c3.metric("= Contención",    contencion)
    c4.metric("↓ Deterioraron",  deterioro)
    c5.metric("Finalizaron",     finalizo)

def seccion_cosechas(nombre_meta):
    """Muestra cosecha por sucursal de los últimos 6 meses."""
    if df_cosecha_all.empty:
        st.info("Datos de cosecha no disponibles. Ejecuta el generador primero.")
        return

    df_cos = df_cosecha_all[df_cosecha_all['metaliado'] == nombre_meta].copy()
    if df_cos.empty:
        st.info(f"Sin datos de cosecha para {nombre_meta}.")
        return

    meses_orden = sorted(df_cos['mes'].unique())

    # Métricas generales (fila TOTAL, mes más reciente)
    df_total = df_cos[df_cos['sucursal'] == 'TOTAL']
    if not df_total.empty:
        df_total_sorted = df_total.sort_values('mes')
        total_monto    = df_total['monto_colocado'].sum()
        total_creditos = int(df_total['n_creditos'].sum())
        periodo_str    = f"{meses_orden[0]} – {meses_orden[-1]}" if meses_orden else ''

        # Cosecha general = promedio ponderado por monto de los 6 meses
        cosecha_general = (
            (df_total['cosecha_pct'] * df_total['monto_colocado']).sum() / total_monto
            if total_monto > 0 else 0.0
        )
        # Delta: mes más reciente vs mes anterior
        ultimo_mes = df_total_sorted.iloc[-1]
        penultimo  = df_total_sorted.iloc[-2] if len(df_total_sorted) >= 2 else None
        delta = (round(ultimo_mes['cosecha_pct'] - penultimo['cosecha_pct'], 1)
                 if penultimo is not None else None)

        c1, c2, c3 = st.columns(3)
        c1.metric(
            f"Cosecha general ({periodo_str})",
            f"{cosecha_general:.1f}%",
            delta=f"{delta:+.1f}pp último mes" if delta is not None else None,
        )
        c2.metric("Créditos analizados", total_creditos,
                  help=f"Total de créditos colocados en el período {periodo_str}")
        c3.metric(f"Saldo colocado ({periodo_str})",
                  f"${total_monto:,.0f}")

    st.write("")

    # Pivot: sucursal × mes
    df_suc = df_cos[df_cos['sucursal'] != 'TOTAL'].copy()
    if df_suc.empty:
        return

    pivot = df_suc.pivot_table(
        index='sucursal', columns='mes', values='cosecha_pct', aggfunc='first'
    ).reindex(columns=meses_orden)

    # Añadir fila TOTAL al pivot
    df_tot_pivot = df_total.set_index('mes')['cosecha_pct'].reindex(meses_orden)
    pivot.loc['TOTAL'] = df_tot_pivot

    # Formatear para mostrar
    pivot_fmt = pivot.map(lambda x: f"{x:.1f}%" if pd.notna(x) else '—')

    def color_cosecha(val):
        try:
            v = float(str(val).replace('%',''))
        except:
            return ''
        if v >= 92:  return 'background-color:#E2EFDA; color:#375623; font-weight:bold'
        if v >= 88:  return 'background-color:#FFEB9C'
        if v >= 80:  return 'background-color:#FFB347; color:#7A3B00; font-weight:bold'
        return 'background-color:#FFC7CE; color:#C00000; font-weight:bold'

    styler = (pivot_fmt.style
              .map(color_cosecha)
              .set_table_styles([{
                  'selector': 'th',
                  'props': [('background-color', AZUL_OSCURO),
                            ('color', 'white'),
                            ('font-weight', 'bold'),
                            ('text-align', 'center')]
              }]))
    st.dataframe(styler, use_container_width=True,
                 height=min(400, 50 + len(pivot_fmt) * 35))

    # ── Grupos en riesgo ──────────────────────────────────────────────────────
    if df_riesgo_all.empty:
        return
    df_riesgo_meta = df_riesgo_all[df_riesgo_all['metaliado'] == nombre_meta].copy()
    if df_riesgo_meta.empty:
        return

    meses_riesgo = sorted(df_riesgo_meta['mes'].unique(), reverse=True)
    st.write("")
    st.markdown(
        '<div class="seccion-titulo">🔴 Grupos con saldo en riesgo</div>',
        unsafe_allow_html=True)

    c_mes, c_suc, c_info = st.columns([2, 2, 4])
    with c_mes:
        mes_sel = st.selectbox(
            'Mes de colocación',
            meses_riesgo,
            key=f'riesgo_mes_{nombre_meta}',
        )
    df_sel = df_riesgo_meta[df_riesgo_meta['mes'] == mes_sel].copy()
    with c_suc:
        sucursales_disp = ['Todas'] + sorted(df_sel['Sucursal'].dropna().unique().tolist())
        suc_sel = st.selectbox(
            'Sucursal',
            sucursales_disp,
            key=f'riesgo_suc_{nombre_meta}',
        )
    if suc_sel != 'Todas':
        df_sel = df_sel[df_sel['Sucursal'] == suc_sel].copy()
    with c_info:
        st.caption(
            f"{len(df_sel)} crédito{'s' if len(df_sel) != 1 else ''} en riesgo "
            f"colocados en **{mes_sel}**"
            + (f" · {suc_sel}" if suc_sel != 'Todas' else '') +
            f" · saldo en riesgo: **${df_sel['saldo_riesgo'].sum():,.0f}**"
        )

    RENAME_R = {
        'Grupo': 'Grupo', 'Solicitud': 'Solicitud',
        'Sucursal': 'Sucursal', 'Asesor_Actual': 'Asesor',
        'Dias_De_Atraso': 'Días Atraso',
        'moneda_Saldo': 'Saldo', 'moneda_Vencido': 'Saldo Vencido',
        'saldo_riesgo': 'Saldo en Riesgo', 'moneda_Monto_a_Pagar': 'Monto a Pagar',
    }
    show_cols = [c for c in RENAME_R if c in df_sel.columns]
    df_show = df_sel[show_cols].rename(columns=RENAME_R).copy()

    for col in ['Saldo', 'Saldo Vencido', 'Saldo en Riesgo', 'Monto a Pagar']:
        if col in df_show.columns:
            df_show[col] = df_show[col].apply(
                lambda x: f"${float(x):,.0f}" if pd.notna(x) else '—')

    styler_r = df_show.style.hide(axis='index')
    if 'Días Atraso' in df_show.columns:
        styler_r = styler_r.map(colorear_dias, subset=['Días Atraso'])

    st.dataframe(styler_r, use_container_width=True,
                 height=min(500, 50 + len(df_show) * 36))


# ── Tabs: Nacional + por metaliado ──────────────────────────────────────────────
METALIADOS = ['Nacional', 'Marisol', 'Jessy', 'Eder', 'Yessica']
ICONOS = {'Nacional': '🌎'}
tabs = st.tabs([f"{ICONOS.get(m, '👤')} {m}" for m in METALIADOS])

for tab, nombre in zip(tabs, METALIADOS):
    with tab:
        # ── Selector de bloque ──────────────────────────────────────────────
        if len(bloques_disponibles) > 1:
            blq_labels = {}
            for b in bloques_disponibles:
                row_b = df_all[df_all['bloque_num'] == b].iloc[0]
                es_actual = bool(row_b.get('es_bloque_actual', False))
                label = (f"Bloque {b} — {row_b['inicio_bloque']} → {row_b['fin_bloque']}"
                         f"{' (actual)' if es_actual else ' (anterior)'}")
                blq_labels[label] = b

            seleccion = st.radio(
                "Bloque a visualizar",
                options=list(blq_labels.keys()),
                horizontal=True,
                key=f"blq_{nombre}",
            )
            bloque_sel = blq_labels[seleccion]
        else:
            bloque_sel = bloques_disponibles[0]

        df_bloque = df_all[
            (df_all['metaliado'] == nombre) &
            (df_all['bloque_num'] == bloque_sel)
        ]

        corte_sel      = df_bloque['corte_actual'].iloc[0] if not df_bloque.empty else '—'
        inicio_sel     = df_bloque['inicio_bloque'].iloc[0] if not df_bloque.empty else '—'

        df_ini = df_bloque[df_bloque['seccion'] == 'inicio_bloque'].copy()
        df_act = df_bloque[df_bloque['seccion'] == 'estado_actual'].copy()

        if df_ini.empty:
            st.info(f"Sin grupos en rango 3-16 días al inicio del bloque {bloque_sel} para {nombre}.")
        else:
            # Filtro por sucursal (aplica a métricas, buckets y tablas)
            suc_seg_opts = ['Todas'] + sorted(df_ini['Sucursal'].dropna().unique().tolist())
            suc_seg = st.selectbox(
                'Filtrar por sucursal',
                suc_seg_opts,
                key=f'suc_seg_{nombre}_{bloque_sel}',
            )
            if suc_seg != 'Todas':
                df_ini = df_ini[df_ini['Sucursal'] == suc_seg].copy()
                df_act = df_act[df_act['Sucursal'] == suc_seg].copy()

            # Métricas de movimiento
            metricas_rapidas(df_act)
            st.write("")

            # Distribución por bucket lado a lado
            cb_ini, cb_act = st.columns(2)

            with cb_ini:
                st.markdown(
                    f'<div class="seccion-titulo">📊 Distribución al Inicio — {inicio_sel}</div>',
                    unsafe_allow_html=True)
                st.markdown(tabla_buckets_html(df_ini, 'Bucket — Inicio bloque'),
                            unsafe_allow_html=True)

            with cb_act:
                st.markdown(
                    f'<div class="seccion-titulo-actual">📊 Distribución Actual — {corte_sel}</div>',
                    unsafe_allow_html=True)
                st.markdown(tabla_buckets_html(df_act, 'Bucket — Estado actual'),
                            unsafe_allow_html=True)

            # Tablas detalle lado a lado
            c_ini, c_act = st.columns(2)

            with c_ini:
                st.markdown(
                    f'<div class="seccion-titulo">📅 Inicio Bloque {bloque_sel} — {inicio_sel}</div>',
                    unsafe_allow_html=True)
                st.caption(f"{len(df_ini)} grupos con 3-16 días de atraso al inicio")
                mostrar_tabla(df_ini, es_actual=False)

            with c_act:
                st.markdown(
                    f'<div class="seccion-titulo-actual">🔄 Estado — {corte_sel}</div>',
                    unsafe_allow_html=True)
                st.caption(f"{len(df_act)} grupos seguidos desde el inicio del bloque")
                mostrar_tabla(df_act, es_actual=True)

        # ── Goteo ───────────────────────────────────────────────────────────
        if not df_goteo_all.empty:
            df_goteo_blq = df_goteo_all[
                (df_goteo_all['metaliado'] == nombre) &
                (df_goteo_all['bloque_num'] == bloque_sel)
            ].copy()

            st.divider()
            st.markdown(
                '<div class="seccion-titulo">💧 Goteo del bloque</div>',
                unsafe_allow_html=True)
            st.caption(
                "Grupos que entraron a ≥3 días de atraso durante el bloque "
                "y NO estaban en ese nivel al inicio.")

            if df_goteo_blq.empty:
                st.info("Sin goteo en este bloque.")
            else:
                cg1, cg2, cg3 = st.columns([2, 2, 4])
                with cg1:
                    suc_goteo_opts = ['Todas'] + sorted(
                        df_goteo_blq['Sucursal'].dropna().unique().tolist())
                    suc_goteo = st.selectbox(
                        'Sucursal', suc_goteo_opts, key=f'goteo_suc_{nombre}')
                df_g_show = (df_goteo_blq if suc_goteo == 'Todas'
                             else df_goteo_blq[df_goteo_blq['Sucursal'] == suc_goteo])
                with cg2:
                    st.metric('Grupos en goteo', len(df_g_show))
                with cg3:
                    saldo_goteo = pd.to_numeric(
                        df_g_show['moneda_Saldo'], errors='coerce').sum()
                    st.metric('Saldo en goteo', f'${saldo_goteo:,.0f}')

                RENAME_G = {
                    'Grupo': 'Grupo', 'Sucursal': 'Sucursal',
                    'Asesor_Actual': 'Asesor', 'Dias_De_Atraso': 'Días Atraso',
                    'Pago Semanal': 'Pago Semanal', 'Falta Sig. Ficha': 'Falta Sig. Ficha',
                    'moneda_Saldo': 'Saldo', 'moneda_Vencido': 'Saldo Vencido',
                    'Solicitud': 'Solicitud',
                }
                g_cols = [c for c in RENAME_G if c in df_g_show.columns]
                df_g = df_g_show[g_cols].rename(columns=RENAME_G).copy()
                for col in ['Saldo', 'Saldo Vencido', 'Pago Semanal', 'Falta Sig. Ficha']:
                    if col in df_g.columns:
                        df_g[col] = df_g[col].apply(
                            lambda x: f"${float(x):,.0f}" if pd.notna(x) else '—')
                styler_g = df_g.style.hide(axis='index')
                if 'Días Atraso' in df_g.columns:
                    styler_g = styler_g.map(colorear_dias, subset=['Días Atraso'])
                st.dataframe(styler_g, use_container_width=True,
                             height=min(500, 50 + len(df_g) * 36))

        # ── Cosechas ────────────────────────────────────────────────────────
        st.divider()
        st.markdown(
            f'<div class="seccion-titulo">🌾 Cosecha últimos 6 meses — {nombre}</div>',
            unsafe_allow_html=True)
        st.caption("Calculada sobre créditos colocados en cada mes, con el estado del corte actual.")
        seccion_cosechas(nombre)

# ── Leyenda ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="font-size:0.8rem; color:#666; display:flex; gap:1.5rem; flex-wrap:wrap">
    <span style="background:#E2EFDA; padding:2px 8px; border-radius:4px">🟩 0 días — Al corriente</span>
    <span style="background:#EBF3D1; padding:2px 8px; border-radius:4px">🟩 1-2 días — Casi</span>
    <span style="background:#FFEB9C; padding:2px 8px; border-radius:4px">🟨 3-15 días — Contención</span>
    <span style="background:#FFC7CE; padding:2px 8px; border-radius:4px">🟥 16+ días — Deterioró</span>
    <span style="background:#DDEBF7; padding:2px 8px; border-radius:4px">🔵 Finalizó / Pagó</span>
    <b style="margin-left:1rem">Cosecha:</b>
    <span style="background:#E2EFDA; padding:2px 8px; border-radius:4px">≥92% Buena</span>
    <span style="background:#FFEB9C; padding:2px 8px; border-radius:4px">88-91% Alerta</span>
    <span style="background:#FFB347; padding:2px 8px; border-radius:4px">80-87% Urgente</span>
    <span style="background:#FFC7CE; padding:2px 8px; border-radius:4px">&lt;80% Crítico</span>
</div>
""", unsafe_allow_html=True)
