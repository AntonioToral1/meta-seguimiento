"""
Cosechas por región — últimos 6 meses (rolling window).
Página Streamlit del seguimiento Meta Financiera.
v2: Salamanca → Suc. Digital
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from datetime import date, timedelta

st.set_page_config(
    page_title='Cosechas | Meta Financiera',
    page_icon='🌾',
    layout='wide',
)

# ── Datos ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / 'data'

@st.cache_data(ttl=600)
def cargar_datos():
    gen = pd.read_csv(DATA_DIR / 'cosechas_general.csv', parse_dates=['fecha'])
    men = pd.read_csv(DATA_DIR / 'cosechas_mensual.csv', parse_dates=['fecha'])
    return gen, men

df_gen, df_men = cargar_datos()

REGIONES = sorted(df_gen['region'].unique())
COLORES_SUC = [
    '#2E75B6', '#ED7D31', '#70AD47', '#FFC000',
    '#7030A0', '#00B0F0', '#FF0000', '#92D050',
]

MESES_ORDEN = {
    'Enero':1,'Febrero':2,'Marzo':3,'Abril':4,'Mayo':5,'Junio':6,
    'Julio':7,'Agosto':8,'Septiembre':9,'Octubre':10,'Noviembre':11,'Diciembre':12
}
MESES_ABREV = {
    'Enero':'Ene','Febrero':'Feb','Marzo':'Mar','Abril':'Abr','Mayo':'May','Junio':'Jun',
    'Julio':'Jul','Agosto':'Ago','Septiembre':'Sep','Octubre':'Oct','Noviembre':'Nov','Diciembre':'Dic'
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def semaforo_color(v):
    if pd.isna(v):     return '#CCCCCC'
    if v >= 0.95:      return '#70AD47'
    if v >= 0.85:      return '#FFC000'
    return '#FF0000'

def semaforo_emoji(v):
    if pd.isna(v):  return '⚪'
    if v >= 0.95:   return '🟢'
    if v >= 0.85:   return '🟡'
    return '🔴'

def fmt_pct(v):
    return f'{v:.1%}' if not pd.isna(v) else '—'

def orden_bloques(df):
    """Ordena etiquetas de bloque: B1, B2, ..., Hoy."""
    def key(b):
        if b == 'Hoy': return 9999
        return int(b[1:]) if b[1:].isdigit() else 0
    return sorted(df['bloque'].unique(), key=key)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title('🌾 Cosechas')
region_sel = st.sidebar.radio('Región', REGIONES, index=0)

# Ventana de bloques (últimos 6 meses)
fecha_max = df_gen['fecha'].max()
fecha_min_ventana = fecha_max - pd.DateOffset(months=6)
df_gen_v = df_gen[df_gen['fecha'] >= fecha_min_ventana].copy()
df_men_v = df_men[df_men['fecha'] >= fecha_min_ventana].copy()

bloques_ventana = orden_bloques(df_gen_v)
st.sidebar.markdown('---')
st.sidebar.caption(f'Ventana: últimos 6 meses  \n'
                   f'{fecha_min_ventana.date()} → {fecha_max.date()}  \n'
                   f'Bloques: {bloques_ventana[0]} – {bloques_ventana[-1]}')

# ── Filtrar región ─────────────────────────────────────────────────────────────
df_r = df_gen_v[df_gen_v['region'] == region_sel].copy()
df_rm = df_men_v[df_men_v['region'] == region_sel].copy()
sucursales = sorted(df_r['sucursal'].unique())

# ── Header ────────────────────────────────────────────────────────────────────
st.title(f'🌾 Cosechas — {region_sel}')
st.caption(f'Créditos colocados en los últimos 6 meses · Corte: {fecha_max.date()}')

# ── Métricas rápidas (último corte) ───────────────────────────────────────────
ultimo_bloque = bloques_ventana[-1]
df_ult = df_r[df_r['bloque'] == ultimo_bloque]

cols_met = st.columns(len(sucursales))
for i, suc in enumerate(sucursales):
    row = df_ult[df_ult['sucursal'] == suc]
    if row.empty:
        cols_met[i].metric(suc, '—')
        continue
    v = row.iloc[0]['cosecha']
    # Buscar bloque anterior para delta
    idx_ult = bloques_ventana.index(ultimo_bloque)
    delta = None
    if idx_ult > 0:
        bloque_ant = bloques_ventana[idx_ult - 1]
        row_ant = df_r[(df_r['bloque'] == bloque_ant) & (df_r['sucursal'] == suc)]
        if not row_ant.empty:
            v_ant = row_ant.iloc[0]['cosecha']
            if not pd.isna(v_ant) and not pd.isna(v):
                delta = v - v_ant
    cols_met[i].metric(
        label=f'{semaforo_emoji(v)} {suc}',
        value=fmt_pct(v),
        delta=fmt_pct(delta) if delta is not None else None,
    )

st.markdown('---')

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(['📈 Evolución General', '📅 Por Mes de Colocación', '📊 Tabla Detalle', '🗓️ Calendario de Bloques'])

# ═══════════════════════════════════════════════════════════════════════════════
# Tab 1: Evolución General
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f'Cosecha general por bloque — {region_sel}')
    st.caption('Créditos incluidos: todos los colocados en los últimos 6 meses a cada fecha de corte')

    suc_filtro = st.multiselect(
        'Sucursales a mostrar', sucursales, default=sucursales, key='suc_filtro'
    )
    if not suc_filtro:
        st.info('Selecciona al menos una sucursal.')
        st.stop()

    df_r_f = df_r[df_r['sucursal'].isin(suc_filtro)]

    # Gráfica
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#FAFAFA')

    xs = list(range(len(bloques_ventana)))
    for i, suc in enumerate(suc_filtro):
        color = COLORES_SUC[i % len(COLORES_SUC)]
        ys = []
        for b in bloques_ventana:
            row = df_r_f[(df_r_f['bloque'] == b) & (df_r_f['sucursal'] == suc)]
            ys.append(row.iloc[0]['cosecha'] if not row.empty else np.nan)

        mask = [not pd.isna(y) for y in ys]
        xs_v = [x for x, m in zip(xs, mask) if m]
        ys_v = [y for y, m in zip(ys, mask) if m]
        if xs_v:
            ax.plot(xs_v, ys_v, marker='o', linewidth=2.2, markersize=6,
                    color=color, label=suc)
            ax.annotate(f'{ys_v[-1]:.1%}',
                        (xs_v[-1], ys_v[-1]),
                        textcoords='offset points', xytext=(7, 0),
                        fontsize=8.5, color=color, fontweight='bold')

    # Líneas de referencia
    ax.axhline(0.95, color='#70AD47', linewidth=1, linestyle='--', alpha=0.6, label='95% (meta)')
    ax.axhline(0.85, color='#FFC000', linewidth=1, linestyle='--', alpha=0.6, label='85% (atención)')

    ax.set_xticks(xs)
    ax.set_xticklabels(bloques_ventana, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.01))
    ax.grid(True, color='#E0E0E0', linewidth=0.8)
    ax.grid(True, which='minor', color='#E0E0E0', linewidth=0.4, linestyle=':')
    ax.legend(loc='lower left', fontsize=9, framealpha=0.9, ncol=3)
    ax.set_ylim(bottom=max(0, min([y for ys in [[df_r_f[(df_r_f['bloque']==b)&(df_r_f['sucursal']==s)]['cosecha'].values[0]
                                                   if not df_r_f[(df_r_f['bloque']==b)&(df_r_f['sucursal']==s)].empty else np.nan
                                                   for b in bloques_ventana] for s in suc_filtro] for y in ys
                                    if not pd.isna(y)], default=0.7) - 0.03),
               top=1.02)
    ax.set_title(f'Cosecha General — {region_sel}', fontsize=11,
                 fontweight='bold', color='#1F3864', pad=10)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Tabla resumen rápido
    st.markdown('**Tabla: cosecha general por sucursal y bloque**')
    pivot = df_r_f.pivot_table(index='sucursal', columns='bloque',
                               values='cosecha', aggfunc='first')
    pivot = pivot.reindex(columns=bloques_ventana)
    pivot_display = pivot.map(lambda v: fmt_pct(v) if not pd.isna(v) else '—')
    st.dataframe(pivot_display, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Tab 2: Por Mes de Colocación
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(f'Cosecha por mes de colocación — {region_sel}')

    suc_sel = st.selectbox('Sucursal', ['Todas las sucursales'] + sucursales, key='suc_mes')

    # Etiqueta "Ene 2026" para cada combinación año+mes
    df_rm = df_rm.copy()
    df_rm['periodo'] = df_rm.apply(
        lambda r: f"{MESES_ABREV.get(r['mes_nombre'], r['mes_nombre'][:3])} {int(r['anio_num'])}",
        axis=1
    )

    # Orden cronológico de periodos
    periodos_orden = (df_rm[['anio_num','mes_num','periodo']]
                      .drop_duplicates()
                      .sort_values(['anio_num','mes_num'])['periodo']
                      .tolist())
    periodos_disp = list(dict.fromkeys(periodos_orden))  # deduplica manteniendo orden

    if suc_sel == 'Todas las sucursales':
        df_plot2 = df_rm.copy()
        df_plot2['peso_cos'] = df_plot2['cosecha'] * df_plot2['capital']
        df_plot_agg = df_plot2.groupby(['bloque', 'fecha', 'anio_num', 'mes_num', 'periodo']).agg(
            peso_cos=('peso_cos', 'sum'),
            capital=('capital', 'sum'),
            n_creditos=('n_creditos', 'sum'),
        ).reset_index()
        df_plot_agg['cosecha'] = np.where(
            df_plot_agg['capital'] > 0,
            df_plot_agg['peso_cos'] / df_plot_agg['capital'],
            np.nan)
        df_plot = df_plot_agg
        titulo_graf = f'Todas las sucursales — {region_sel}'
    else:
        df_plot = df_rm[df_rm['sucursal'] == suc_sel].copy()
        titulo_graf = f'{suc_sel} — {region_sel}'

    # Gráfica: una línea por periodo (Ene 2026, Feb 2026, …)
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    fig2.patch.set_facecolor('white')
    ax2.set_facecolor('#FAFAFA')

    cmap = matplotlib.colormaps.get_cmap('tab10')
    xs2 = list(range(len(bloques_ventana)))

    for i, periodo in enumerate(periodos_disp):
        df_m = df_plot[df_plot['periodo'] == periodo]
        if df_m.empty:
            continue
        color = cmap(i % 10)
        ys2 = []
        for b in bloques_ventana:
            row = df_m[df_m['bloque'] == b]
            ys2.append(row.iloc[0]['cosecha'] if not row.empty and not pd.isna(row.iloc[0]['cosecha']) else np.nan)

        mask2 = [not pd.isna(y) for y in ys2]
        xs2_v = [x for x, m2 in zip(xs2, mask2) if m2]
        ys2_v = [y for y, m2 in zip(ys2, mask2) if m2]
        if xs2_v:
            ax2.plot(xs2_v, ys2_v, marker='o', linewidth=1.8, markersize=5,
                     color=color, label=periodo, alpha=0.9)
            ax2.annotate(f'{ys2_v[-1]:.0%}',
                         (xs2_v[-1], ys2_v[-1]),
                         textcoords='offset points', xytext=(6, 0),
                         fontsize=7.5, color=color)

    ax2.axhline(0.95, color='#70AD47', linewidth=1, linestyle='--', alpha=0.5)
    ax2.axhline(0.85, color='#FFC000', linewidth=1, linestyle='--', alpha=0.5)
    ax2.set_xticks(xs2)
    ax2.set_xticklabels(bloques_ventana, fontsize=9)
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax2.grid(True, color='#E0E0E0', linewidth=0.8)
    ax2.legend(loc='lower left', fontsize=8.5, framealpha=0.9, ncol=3)
    ax2.set_title(f'Cosecha por mes de colocación — {titulo_graf}',
                  fontsize=11, fontweight='bold', color='#1F3864', pad=10)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # Tabla: periodo × bloque
    st.markdown('**Tabla: cosecha por mes de colocación y bloque**')
    pivot2 = df_plot.pivot_table(index='periodo', columns='bloque',
                                  values='cosecha', aggfunc='first')
    pivot2 = pivot2.reindex(index=periodos_disp, columns=bloques_ventana)
    pivot2_display = pivot2.map(lambda v: fmt_pct(v) if not pd.isna(v) else '—')
    st.dataframe(pivot2_display, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Tab 3: Tabla Detalle
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader(f'Detalle de créditos y montos — {region_sel}')

    bloque_det = st.selectbox('Bloque a ver', bloques_ventana[::-1], key='bloque_det')
    df_det = df_r[df_r['bloque'] == bloque_det].copy()
    df_det['semaforo'] = df_det['cosecha'].apply(semaforo_emoji)
    df_det['cosecha_fmt'] = df_det['cosecha'].apply(fmt_pct)
    df_det['capital_fmt'] = df_det['capital'].apply(lambda v: f'${v:,.0f}')
    df_det['pagado_fmt'] = df_det['pagado'].apply(lambda v: f'${v:,.0f}')
    df_det['sr_fmt'] = df_det['saldo_riesgo'].apply(lambda v: f'${v:,.0f}')

    tabla_det = df_det[['semaforo', 'sucursal', 'n_creditos',
                         'capital_fmt', 'pagado_fmt', 'sr_fmt', 'cosecha_fmt']].rename(columns={
        'semaforo': '',
        'sucursal': 'Sucursal',
        'n_creditos': 'Créditos',
        'capital_fmt': 'Monto a Pagar',
        'pagado_fmt': 'Pagado',
        'sr_fmt': 'Saldo en Riesgo',
        'cosecha_fmt': 'Cosecha',
    })
    st.dataframe(tabla_det, use_container_width=True, hide_index=True)

    # Total región
    total_cap = df_det['capital'].sum()
    total_pag = df_det['pagado'].sum()
    total_sr  = df_det['saldo_riesgo'].sum()
    total_cos = (total_pag - total_sr + total_cap - total_sr) / total_cap if total_cap > 0 else np.nan
    # Recalcular correctamente: falta saldo, usar ponderación por capital
    cos_ponderada = (df_det['cosecha'] * df_det['capital']).sum() / total_cap if total_cap > 0 else np.nan

    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Total créditos', f'{int(df_det["n_creditos"].sum()):,}')
    c2.metric('Monto a Pagar', f'${total_cap:,.0f}')
    c3.metric('Total Pagado', f'${total_pag:,.0f}')
    c4.metric(f'Cosecha {region_sel}', fmt_pct(cos_ponderada))

    st.markdown('---')
    st.caption('🟢 ≥ 95%  ·  🟡 ≥ 85%  ·  🔴 < 85%  ·  ⚪ Sin datos')

# ═══════════════════════════════════════════════════════════════════════════════
# Tab 4: Calendario de Bloques
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader('🗓️ Calendario de Bloques')
    st.caption('Inicio de cada bloque = lunes · Duración: 14 días · Referencia: B1 = 5 ene 2026')

    INICIO_B1 = date(2026, 1, 5)

    # Construir tabla con todos los bloques disponibles en el dataset completo
    bloques_todos = orden_bloques(df_gen)
    snap_por_bloque = df_gen.groupby('bloque')['fecha'].first().to_dict()

    filas_cal = []
    for b in bloques_todos:
        if b == 'Hoy':
            snap = snap_por_bloque.get('Hoy', pd.NaT)
            filas_cal.append({
                'Bloque': 'Hoy',
                'Inicio del bloque': '—',
                'Fin del bloque': '—',
                'Snapshot usado': str(snap.date()) if pd.notna(snap) else '—',
            })
        else:
            n = int(b[1:])
            ini = INICIO_B1 + timedelta(days=(n - 1) * 14)
            fin = ini + timedelta(days=13)
            snap = snap_por_bloque.get(b, pd.NaT)
            filas_cal.append({
                'Bloque': b,
                'Inicio del bloque': ini.strftime('%d %b %Y'),
                'Fin del bloque': fin.strftime('%d %b %Y'),
                'Snapshot usado': str(snap.date()) if pd.notna(snap) else '—',
            })

    df_cal = pd.DataFrame(filas_cal)
    st.dataframe(df_cal, use_container_width=True, hide_index=True)
