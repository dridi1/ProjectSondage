import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ----------------------------
# Configuration
# ----------------------------
st.set_page_config(
    page_title="Sampling Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Paths & Data Loading
# ----------------------------
THIS_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(THIS_DIR, 'data')
FILE_PATH = os.path.join(DATA_DIR, 'Cadre Tunisie.xlsx')

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load and concatenate all sheets from the Excel file."""
    sheets = pd.read_excel(path, sheet_name=None)
    frame = pd.concat(sheets.values(), ignore_index=True)
    return frame

# Load dataset
df = load_data(FILE_PATH)
# Compute once
total_units = len(df)

def current_timestamp():
    return pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("École Supérieure de la Statistique")
st.sidebar.markdown(
    "#### Projet Théorie de Sondage<br>2ème année | 2024-2025<br>" +
    "**Auteur**: Dridi Slim",
    unsafe_allow_html=True
)
st.sidebar.divider()
section = st.sidebar.radio(
    "Navigation",
    ["🏠 Introduction", "📊 Dashboard", "🎲 SRS", "🏷️ Stratified"],
    index=0
)

# ----------------------------
# Introduction
# ----------------------------
if section == "🏠 Introduction":
    st.title("Bienvenue au Tableau de Bord de l'Échantillonnage")
    st.markdown(
        "Ce projet permet de tirer automatiquement un échantillon de taille `n` selon :<br>"
        "1. Méthode Aléatoire Simple Sans Remise (SRS)<br>"
        "2. Stratification à allocation proportionnelle<br>"
        "<br>Utilisez la navigation dans la barre latérale pour commencer.",
        unsafe_allow_html=True
    )

# ----------------------------
# Dashboard
# ----------------------------
elif section == "📊 Dashboard":
    st.title("Population Dashboard")
    st.markdown("Vue d'ensemble du cadre d'échantillonnage.")

    default_strata = df.columns[0]
    strata_count = df[default_strata].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Units", f"{total_units:,}")
    col2.metric(f"Strates ({default_strata})", f"{strata_count}")
    col3.metric("Date Chargement", current_timestamp())

    st.divider()
    counts = df[default_strata].value_counts().reset_index()
    counts.columns = [default_strata, 'Count']
    counts['Percent'] = (counts['Count'] / total_units * 100).round(1)

    pie = px.pie(
        counts,
        names=default_strata,
        values='Count',
        title=f"Répartition par {default_strata}",
        hover_data=['Percent'],
        template='plotly_white'
    )
    st.plotly_chart(pie, use_container_width=True)

    st.subheader("Aperçu des Données")
    st.dataframe(df.head(10), use_container_width=True)

# ----------------------------
# Simple Random Sampling
# ----------------------------
elif section == "🎲 SRS":
    st.title("Simple Random Sampling (SRS)")
    st.markdown("Tirez un échantillon aléatoire simple sans remise.")

    with st.form(key='srs_form'):
        n = st.number_input(
            "Taille de l'échantillon (n)",
            min_value=1,
            max_value=total_units,
            value=min(100, total_units)
        )
        comp_var = st.selectbox("Variable de comparaison", df.columns)
        submit_srs = st.form_submit_button("Exécuter SRS")

    if submit_srs:
        sample = df.sample(n=n, replace=False)
        st.success(f"Échantillon de {n} unités tiré 🎉")

        # Compare proportions
        pop_props = df[comp_var].value_counts(normalize=True).rename('Population %')
        samp_props = sample[comp_var].value_counts(normalize=True).rename('Échantillon %')
        comp_df = pd.concat([pop_props, samp_props], axis=1).fillna(0).reset_index()
        comp_df.columns = [comp_var, 'Population %', 'Échantillon %']

        fig = px.bar(
            comp_df,
            x=comp_var,
            y=['Population %', 'Échantillon %'],
            barmode='group',
            title="Proportions Population vs Échantillon",
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Statistiques Descriptionnelles de l'Échantillon"):
            st.dataframe(sample.describe(include='all'), use_container_width=True)

        # Downloads
        c1, c2 = st.columns(2)
        c1.download_button(
            "Télécharger Échantillon CSV",
            sample.to_csv(index=False).encode('utf-8'),
            "echantillon_srs.csv",
            mime='text/csv'
        )
        c2.download_button(
            "Télécharger Comparaison CSV",
            comp_df.to_csv(index=False).encode('utf-8'),
            "comparaison_srs.csv",
            mime='text/csv'
        )

# ----------------------------
# Stratified Sampling
# ----------------------------
elif section == "🏷️ Stratified":
    st.title("Stratified Sampling")
    st.markdown("Allocation proportionnelle dans chaque strate.")

    with st.form(key='strat_form'):
        n_tot = st.number_input(
            "Taille Totale de l'Échantillon (n)",
            min_value=1,
            max_value=total_units,
            value=min(100, total_units)
        )
        strata = st.selectbox("Variable de Strate", df.columns)
        aux = st.selectbox("Variable Auxiliaire (optionnelle)", [None] + df.columns.tolist())
        submit_strat = st.form_submit_button("Exécuter Stratifié")

    if submit_strat:
        counts = df[strata].value_counts()
        alloc = (counts / total_units * n_tot).round().astype(int)
        diff = n_tot - alloc.sum()
        if diff != 0:
            alloc[alloc.idxmax()] += diff

        alloc_df = pd.DataFrame({
            strata: alloc.index,
            'N_h': counts.values,
            'n_h': alloc.values
        })

        if aux:
            if pd.api.types.is_numeric_dtype(df[aux]):
                means = df.groupby(strata)[aux].mean().round(2)
                alloc_df[f'Moyenne {aux}'] = alloc_df[strata].map(means)
            else:
                props = (
                    df.groupby(strata)[aux]
                      .value_counts(normalize=True)
                      .mul(100)
                      .round(1)
                      .rename('Pct')
                      .reset_index()
                      .pivot(index=strata, columns=aux, values='Pct')
                      .reset_index()
                )
                alloc_df = alloc_df.merge(props, on=strata, how='left')

        # Sample
        sampled = pd.concat([
            df[df[strata]==g].sample(n=min(s, len(df[df[strata]==g])), replace=False)
            for g, s in alloc.items()
        ])

        st.subheader("Tableau d'Allocation")
        st.dataframe(alloc_df, use_container_width=True)

        fig2 = px.bar(
            alloc_df,
            x=strata,
            y='n_h',
            title="Allocation n_h par Strate",
            template='plotly_white'
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Aperçu de l'Échantillon Stratifié")
        st.dataframe(sampled.head(10), use_container_width=True)
        with st.expander("Statistiques Descriptionnelles Stratifiées"):
            st.dataframe(sampled.describe(include='all'), use_container_width=True)

        # Downloads
        d1, d2 = st.columns(2)
        d1.download_button(
            "Télécharger Allocation CSV",
            alloc_df.to_csv(index=False).encode('utf-8'),
            "allocation_strat.csv",
            mime='text/csv'
        )
        d2.download_button(
            "Télécharger Échantillon CSV",
            sampled.to_csv(index=False).encode('utf-8'),
            "echantillon_strat.csv",
            mime='text/csv'
        )
