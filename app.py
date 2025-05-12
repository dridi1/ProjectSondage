import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ----------------------------
# Configuration
# ----------------------------
st.set_page_config(
    page_title="Sampling & Exploration Dashboard",
    layout="wide",
    initial_sidebar_state="auto"
)

# ----------------------------
# Paths & Data Loading
# ----------------------------
THIS_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(THIS_DIR, 'data')
DEFAULT_FP = os.path.join(DATA_DIR, 'Cadre Tunisie.xlsx')

@st.cache_data
def load_excel(path_or_buffer) -> pd.DataFrame:
    sheets = pd.read_excel(path_or_buffer, sheet_name=None)
    return pd.concat(sheets.values(), ignore_index=True)

@st.cache_data
def load_csv(path_or_buffer) -> pd.DataFrame:
    return pd.read_csv(path_or_buffer)

# File uploader in sidebar
with st.sidebar:
    st.title("Charger vos données")
    uploaded = st.file_uploader(
        "Fichier Excel ou CSV",
        type=["xlsx", "csv"],
        help="Si non fourni, données par défaut utilisées."
    )

if uploaded:
    ext = uploaded.name.split('.')[-1].lower()
    df = load_csv(uploaded) if ext == 'csv' else load_excel(uploaded)
else:
    df = load_excel(DEFAULT_FP)

total_units = len(df)

def current_timestamp():
    return pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")

# ----------------------------
# Navigation with tabs
# ----------------------------
tabs = st.tabs(["🏠 Introduction", "📊 Dashboard", "🔍 Exploratoire", "🎲 SRS", "🏷️ Stratif"])

# Introduction
with tabs[0]:
    st.title("Bienvenue au Dashboard d'Échantillonnage & Exploration")
    st.markdown(
        "Cette application permet :<br>"
        "- Exploration descriptive des données<br>"
        "- Échantillonnage aléatoire simple (SRS)<br>"
        "- Échantillonnage stratifié proportionnel<br>"
        "- Tests d'hypothèses (moyennes & proportions)",
        unsafe_allow_html=True
    )

# Dashboard
with tabs[1]:
    st.title("Vue d'ensemble des données")
    var0 = df.columns[0]
    count0 = df[var0].value_counts().reset_index()
    count0.columns = [var0, 'Count']
    count0['Percent'] = (count0['Count']/total_units*100).round(1)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total unités", f"{total_units:,}")
    c2.metric(f"Modalités de {var0}", df[var0].nunique())
    c3.metric("Chargé le", current_timestamp())
    pie = px.pie(count0, names=var0, values='Count', hover_data=['Percent'], title=f"Répartition par {var0}", template='plotly_white')
    st.plotly_chart(pie, use_container_width=True)
    st.subheader("Aperçu des données brutes")
    st.dataframe(df.head(10), use_container_width=True)

# Exploratoire
with tabs[2]:
    st.title("Analyse Descriptive & Graphiques")

    # Descriptive table
    desc = df.describe(include='all').T.reset_index().rename(columns={'index':'Variable'})
    st.dataframe(desc, use_container_width=True)

    # Pick which columns to chart
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object','category']).columns.tolist()

    # Sidebar (or in‐page) selectors
    st.markdown("#### Sélectionnez les variables à tracer")
    sel_num = st.multiselect("Numériques", num_cols, default=num_cols[:2])
    sel_cat = st.multiselect("Catégorielles", cat_cols, default=cat_cols[:2])

    # Plot histograms for selected numeric cols
    if sel_num:
        st.markdown("##### Histogrammes")
        for col in sel_num:
            fig = px.histogram(
                df, x=col, marginal='box', nbins=30,
                title=f"Histogramme de {col}", template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

    # Plot bar‐charts for selected categorical cols
    if sel_cat:
        st.markdown("##### Barres")
        for col in sel_cat:
            vc = df[col].value_counts().reset_index()
            vc.columns = [col, 'Count']
            fig = px.bar(
                vc, x=col, y='Count',
                title=f"Barres de {col}", template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)


# SRS
with tabs[3]:
    st.title("Simple Random Sampling (SRS)")
    st.markdown("Tirez un échantillon sans remise.")
    with st.form('srs_form'):
        n = st.number_input("Taille n", 1, total_units, min(100,total_units))
        comp = st.selectbox("Comparer la variable", df.columns)
        submit_srs = st.form_submit_button("Générer SRS")
    if submit_srs:
        sample = df.sample(n)
        st.success(f"Échantillon de {n} unités généré.")
        popp = df[comp].value_counts(normalize=True).rename('Pop %')
        samp = sample[comp].value_counts(normalize=True).rename('Sample %')
        comp_df = pd.concat([popp,samp],axis=1).fillna(0).reset_index()
        comp_df.columns=[comp,'Pop %','Sample %']
        st.plotly_chart(px.bar(comp_df, x=comp, y=['Pop %','Sample %'], barmode='group', title="Pop vs Échantillon", template='plotly_white'), use_container_width=True)
        st.subheader("Stats échantillon")
        st.dataframe(sample.describe(include='all'), use_container_width=True)
        csv = sample.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger SRS CSV", data=csv, file_name='srs_sample.csv', mime='text/csv')

# Stratifié
with tabs[4]:
    st.title("Échantillonnage Stratifié")
    with st.form('strat_form'):
        n_tot = st.number_input("Taille totale n",1,total_units, min(100,total_units))
        strat = st.selectbox("Strate", df.columns)
        aux = st.selectbox("Variable aux (opt)",[None]+df.columns.tolist())
        submit_strat = st.form_submit_button("Générer Stratification")
    if submit_strat:
        counts = df[strat].value_counts()
        nh = (counts/total_units*n_tot).round().astype(int)
        diff = n_tot - nh.sum()
        if diff:
            # adjust the stratum with the largest allocation
            max_stratum = nh.idxmax()
            nh[max_stratum] += diff
        alloc = pd.DataFrame({strat: nh.index, 'N_h': counts.values, 'n_h': nh.values})
        if aux:
            if pd.api.types.is_numeric_dtype(df[aux]):
                alloc[f"Moy {aux}"] = df.groupby(strat)[aux].mean().round(2).values
            else:
                props = df.groupby(strat)[aux].value_counts(normalize=True).mul(100).round(1).rename('Pct').reset_index()
                alloc = alloc.merge(props.pivot(index=strat,columns=aux,values='Pct').reset_index(), on=strat)
        sampled = pd.concat([df[df[strat]==g].sample(min(s, len(df[df[strat]==g]))) for g, s in nh.items()])
        st.subheader("Allocation")
        st.dataframe(alloc, use_container_width=True)
        st.plotly_chart(px.bar(alloc, x=strat, y='n_h', title="n_h par strate", template='plotly_white'), use_container_width=True)
        st.subheader("Aperçu stratifié")
        st.dataframe(sampled.head(10), use_container_width=True)
        with st.expander("Stats descriptives"):
            st.dataframe(sampled.describe(include='all'), use_container_width=True)
        csv_strat = sampled.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger Stratifié CSV", data=csv_strat, file_name='stratified_sample.csv', mime='text/csv')
