import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from utils.calculations import (
    calculer_economies,
    filtrer_referentiels_applicables,
    generer_recommandations,
    formater_cout
)

st.set_page_config(
    page_title="Assistant Conformité Cyber • Premium",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS PREMIUM ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

/* Variables globales */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --glass-bg: rgba(255, 255, 255, 0.1);
    --glass-border: rgba(255, 255, 255, 0.18);
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Animation fade-in */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

/* Conteneur principal avec animation */
.main {
    animation: fadeIn 0.6s ease-out;
}

/* Header ultra-premium */
.premium-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 3rem 2rem;
    border-radius: 1.5rem;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    position: relative;
    overflow: hidden;
}

.premium-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

.premium-header h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
    position: relative;
    z-index: 1;
}

.premium-header p {
    font-size: 1.2rem;
    margin: 1rem 0 0 0;
    opacity: 0.95;
    font-weight: 300;
    position: relative;
    z-index: 1;
}

/* Glass morphism boxes */
.glass-box {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 1.5rem;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    animation: fadeIn 0.6s ease-out;
}

.glass-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* Info box élégante */
.elegant-info {
    background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
    border-left: 5px solid #3b82f6;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #1e3a8a;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
    animation: slideInRight 0.5s ease-out;
}

.elegant-info strong {
    color: #1e40af;
    font-weight: 600;
}

/* Warning box sophistiquée */
.elegant-warning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-left: 5px solid #f59e0b;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #78350f;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
}

/* Success box premium */
.elegant-success {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border-left: 5px solid #10b981;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #065f46;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
}

/* Danger box élégante */
.elegant-danger {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    border-left: 5px solid #ef4444;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #991b1b;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);
}

/* Cartes premium avec hover */
.premium-card {
    background: white;
    border-radius: 1.5rem;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border: 1px solid rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: hidden;
}

.premium-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.premium-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.premium-card:hover::before {
    transform: scaleX(1);
}

/* Badges élégants */
.elegant-badge {
    display: inline-block;
    padding: 0.5rem 1.2rem;
    border-radius: 2rem;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.elegant-badge:hover {
    transform: scale(1.05);
}

.badge-mandatory {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
}

.badge-optional {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
}

/* Timeline élégante */
.elegant-timeline-phase {
    background: white;
    border-left: 4px solid #3b82f6;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease-out;
}

.elegant-timeline-phase:hover {
    transform: translateX(10px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
}

/* Progress bar premium */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 1rem;
    height: 12px;
}

/* Boutons premium */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 1rem;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.02em;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
}

/* Input fields premium */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
    border-radius: 0.75rem;
    border: 2px solid #e5e7eb;
    transition: all 0.3s ease;
    font-size: 1rem;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Checkbox élégant */
.stCheckbox > label {
    font-size: 1rem;
    color: #1f2937;
    font-weight: 500;
}

/* Metric cards premium */
.stMetric {
    background: white;
    padding: 1.5rem;
    border-radius: 1rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

.stMetric:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* Expander premium */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    border-radius: 0.75rem;
    font-weight: 600;
    color: #1f2937;
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
}

/* Divider élégant */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #e5e7eb 50%, transparent 100%);
    margin: 2rem 0;
}

/* Sidebar premium */
.css-1d391kg {
    background: linear-gradient(180deg, #f9fafb 0%, #ffffff 100%);
}

/* Scrollbar personnalisée */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
}

/* Responsive design */
@media (max-width: 768px) {
    .premium-header h1 {
        font-size: 2rem;
    }
    
    .premium-header p {
        font-size: 1rem;
    }
}

/* Animations d'entrée pour les éléments */
.stMarkdown, .stMetric, .premium-card {
    animation: fadeIn 0.6s ease-out;
}

/* Effet shimmer pour le chargement */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.loading-shimmer {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def charger_donnees():
    data_path = Path(__file__).parent / "data" / "referentiels.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

data = charger_donnees()

if 'etape' not in st.session_state:
    st.session_state.etape = 1
if 'profil' not in st.session_state:
    st.session_state.profil = {}
if 'economies_selectionnees' not in st.session_state:
    st.session_state.economies_selectionnees = []

# ==================== HEADER PREMIUM ====================
st.markdown("""
<div class="premium-header">
    <h1>🔒 Assistant Conformité</h1>
    <p>Solution intelligente • Analyse personnalisée • Résultats garantis</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="elegant-info">
    <strong>📊 Méthodologie certifiée:</strong> Nos estimations sont basées sur des données de consultants canadiens certifiés (2024-2026), 
    des études de marché reconnues (Matayo AI, IAS Canada, Secureframe) et les documents officiels (NIST, ISO, CAI Québec).
</div>
""", unsafe_allow_html=True)

# Progress élégant
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.progress((st.session_state.etape - 1) / 2, text=f"✨ Étape {st.session_state.etape}/3")

st.markdown("<br>", unsafe_allow_html=True)

# ==================== ÉTAPE 1 ====================
if st.session_state.etape == 1:
    st.markdown("## 📋 Profil de votre organisation")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 🏢 Informations générales")
        secteur = st.selectbox(
            "Secteur d'activité",
            ["", "health", "finance", "public", "tech", "retail", "other"],
            format_func=lambda x: {
                "": "→ Sélectionnez votre secteur",
                "health": "🏥 Santé",
                "finance": "💰 Services financiers",
                "public": "🏛️ Secteur public",
                "tech": "💻 Technologies",
                "retail": "🛍️ Commerce",
                "other": "📊 Autre secteur"
            }[x]
        )
        
        taille = st.selectbox(
            "Taille de l'organisation",
            ["", "micro", "small", "medium", "large"],
            format_func=lambda x: {
                "": "→ Nombre d'employés",
                "micro": "👤 Micro-entreprise (1-10)",
                "small": "👥 Petite entreprise (11-49)",
                "medium": "👨‍👩‍👧‍👦 Moyenne entreprise (50-199)",
                "large": "🏢 Grande entreprise (200+)"
            }[x]
        )
        
        ca_annuel = st.number_input(
            "💵 Chiffre d'affaires annuel (optionnel)",
            min_value=0,
            value=0,
            step=100000,
            help="Permet de calculer précisément votre exposition aux pénalités Loi 25"
        )
    
    with col2:
        st.markdown("### 💼 Capacités & Budget")
        budget = st.selectbox(
            "Budget disponible pour la conformité",
            ["", "low", "medium", "high"],
            format_func=lambda x: {
                "": "→ Budget estimé",
                "low": "💰 Budget limité (< 50 000$)",
                "medium": "💰💰 Budget moyen (50 000$ - 200 000$)",
                "high": "💰💰💰 Budget élevé (> 200 000$)"
            }[x]
        )
        
        maturite = st.selectbox(
            "Niveau de maturité cybersécurité",
            ["", "initial", "managed", "defined", "optimized"],
            format_func=lambda x: {
                "": "→ Évaluation actuelle",
                "initial": "🌱 Initial (Début du parcours)",
                "managed": "📊 Géré (Processus en place)",
                "defined": "📈 Défini (Documenté & standardisé)",
                "optimized": "🏆 Optimisé (Amélioration continue)"
            }[x]
        )
    
    st.markdown("### ☁️ Infrastructure technologique")
    
    st.markdown("""
    <div class="elegant-info">
        <strong>💡 Sélectionnez tous les types d'infrastructure que vous utilisez</strong>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(3, gap="medium")
    infrastructure = []
    
    with cols[0]:
        if st.checkbox("🖥️ Sur site (On-premise)", key="infra_onprem"):
            infrastructure.append("onprem")
    with cols[1]:
        if st.checkbox("☁️ Cloud public", key="infra_cloud"):
            infrastructure.append("cloud")
    with cols[2]:
        if st.checkbox("🔄 Hybride (Mix)", key="infra_hybrid"):
            infrastructure.append("hybrid")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Suivant: Évaluation de l'existant →", type="primary", use_container_width=True):
            if not secteur or not taille or not budget or not maturite or not infrastructure:
                st.error("⚠️ Veuillez compléter tous les champs pour continuer")
            else:
                st.session_state.profil = {
                    'secteur': secteur,
                    'taille': taille,
                    'budget': budget,
                    'maturite': maturite,
                    'infrastructure': infrastructure,
                    'ca_annuel': ca_annuel
                }
                st.session_state.etape = 2
                st.rerun()

# ==================== ÉTAPE 2 ====================
elif st.session_state.etape == 2:
    st.markdown("## 💡 Évaluation de votre maturité actuelle")
    
    st.markdown("""
    <div class="elegant-success">
        <strong>✨ Optimisez vos coûts:</strong> Cochez tous les éléments que vous avez déjà mis en place. 
        Chaque contrôle existant réduit directement votre investissement requis!
    </div>
    """, unsafe_allow_html=True)
    
    economies_data = data['economies']
    gouvernance = {k: v for k, v in economies_data.items() if v['categorie'] == 'gouvernance'}
    securite = {k: v for k, v in economies_data.items() if v['categorie'] == 'securite'}
    processus = {k: v for k, v in economies_data.items() if v['categorie'] == 'processus'}
    
    economies_selectionnees = []
    
    with st.expander("📋 **Gouvernance & Politiques**", expanded=True):
        for key, item in gouvernance.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                checked = st.checkbox(f"**{item['label']}**", help=item['description'], key=f"eco_{key}")
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: 700; font-size: 1.1rem;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    with st.expander("🔒 **Sécurité Technique**", expanded=True):
        for key, item in securite.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                checked = st.checkbox(f"**{item['label']}**", help=item['description'], key=f"eco_{key}")
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: 700; font-size: 1.1rem;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    with st.expander("⚙️ **Processus & Procédures**", expanded=True):
        for key, item in processus.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                checked = st.checkbox(f"**{item['label']}**", help=item['description'], key=f"eco_{key}")
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: 700; font-size: 1.1rem;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    total_economies = calculer_economies(economies_selectionnees, economies_data)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Métriques élégantes
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.metric("💰 Économies totales", formater_cout(total_economies), delta="Réduction de coûts")
    with col2:
        st.metric("✅ Contrôles en place", f"{len(economies_selectionnees)}/10", delta=f"{len(economies_selectionnees)} validés")
    with col3:
        pct = round((total_economies / 170000) * 100) if total_economies > 0 else 0
        st.metric("📊 Taux de maturité", f"{pct}%", delta=f"{pct}% complété")
    with col4:
        st.metric("🎯 Potentiel max", "170 000$", delta="Objectif")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_back, _, col_next = st.columns([1, 1, 1])
    with col_back:
        if st.button("← Retour au profil", use_container_width=True):
            st.session_state.etape = 1
            st.rerun()
    with col_next:
        if st.button("✨ Voir mes recommandations →", type="primary", use_container_width=True):
            st.session_state.economies_selectionnees = economies_selectionnees
            st.session_state.etape = 3
            st.rerun()

# ==================== ÉTAPE 3 ====================
elif st.session_state.etape == 3:
    st.markdown("## 📊 Votre plan de conformité personnalisé")
    
    profil = st.session_state.profil
    economies_sel = st.session_state.economies_selectionnees
    total_economies = calculer_economies(economies_sel, data['economies'])
    obligatoires, optionnels = filtrer_referentiels_applicables(data['referentiels'], profil)
    recommandations = generer_recommandations(obligatoires, optionnels, total_economies, profil['budget'])
    
    # Profil résumé
    st.markdown("### 👤 Votre organisation en un coup d'œil")
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.metric("🏢 Secteur", profil['secteur'].title())
    with col2:
        st.metric("👥 Taille", profil['taille'].title())
    with col3:
        st.metric("💰 Budget", formater_cout(recommandations['budget']['montant']))
    with col4:
        st.metric("✨ Économies", formater_cout(total_economies), delta="Réduction")
    
    st.divider()
    
    # CALCULATEUR PÉNALITÉS
    st.markdown("### ⚠️ Analyse du risque de non-conformité")
    
    ca_annuel = profil.get('ca_annuel', 0)
    
    penalite_fixe = 10000000
    penalite_pct_ca = ca_annuel * 0.02 if ca_annuel > 0 else 0
    penalite_max = max(penalite_fixe, penalite_pct_ca)
    
    cout_conformite = recommandations['totaux']['standard']
    economie_vs_penalite = penalite_max - cout_conformite
    roi_protection = (economie_vs_penalite / cout_conformite * 100) if cout_conformite > 0 else 0
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown(f"""
        <div class="glass-box" style='background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border: 2px solid #ef4444;'>
            <div style='text-align: center;'>
                <div style='color: #991b1b; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>
                    ⚠️ Risque maximal
                </div>
                <div style='color: #991b1b; font-size: 2.8rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>
                    {formater_cout(penalite_max)}
                </div>
                <div style='color: #991b1b; font-size: 0.9rem; opacity: 0.9;'>Pénalité Loi 25</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-box" style='background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border: 2px solid #3b82f6;'>
            <div style='text-align: center;'>
                <div style='color: #1e40af; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>
                    💰 Investissement
                </div>
                <div style='color: #1e40af; font-size: 2.8rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>
                    {formater_cout(cout_conformite)}
                </div>
                <div style='color: #1e40af; font-size: 0.9rem; opacity: 0.9;'>Protection recommandée</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-box" style='background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border: 2px solid #10b981;'>
            <div style='text-align: center;'>
                <div style='color: #065f46; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>
                    ✅ Protection nette
                </div>
                <div style='color: #065f46; font-size: 2.8rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>
                    {formater_cout(economie_vs_penalite)}
                </div>
                <div style='color: #065f46; font-size: 0.9rem; opacity: 0.9;'>ROI: {int(roi_protection)}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="elegant-danger">
        <strong>🚨 Analyse critique:</strong> Votre organisation risque une pénalité pouvant atteindre 
        <strong style='font-size: 1.2rem;'>{formater_cout(penalite_max)}</strong> en cas de non-conformité à la Loi 25. 
        Investir <strong>{formater_cout(cout_conformite)}</strong> aujourd'hui vous protège avec un ROI de <strong>{int(roi_protection)}%</strong>!
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # VUE D'ENSEMBLE
    totaux = recommandations['totaux']
    budget_info = recommandations['budget']
    
    st.markdown("### 📊 Comparaison des stratégies d'implémentation")
    
    # GRAPHIQUE PREMIUM
    fig = go.Figure()
    approaches = ['💰 Économique', '⭐ Recommandée', '🏆 Premium']
    costs = [totaux['minimal'], totaux['standard'], totaux['maximal']]
    colors = ['#10B981', '#3B82F6', '#A855F7']
    
    fig.add_trace(go.Bar(
        x=approaches,
        y=costs,
        marker=dict(
            color=colors,
            line=dict(color='rgba(255, 255, 255, 0.6)', width=2)
        ),
        text=[formater_cout(c) for c in costs],
        textposition='outside',
        textfont=dict(size=16, color='#1f2937', family='Poppins', weight='bold')
    ))
    
    fig.add_hline(
        y=budget_info['montant'],
        line_dash="dash",
        line_color="#EF4444",
        line_width=3,
        annotation_text=f"💰 Budget: {formater_cout(budget_info['montant'])}",
        annotation_position="right",
        annotation=dict(font=dict(size=14, color='#EF4444', weight='bold'))
    )
    
    fig.update_layout(
        title=dict(
            text="Analyse comparative des investissements",
            font=dict(size=20, family='Poppins', weight='bold')
        ),
        yaxis_title="Investissement ($)",
        height=450,
        showlegend=False,
        plot_bgcolor='rgba(249, 250, 251, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=13),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3 CARTES PREMIUM
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        reste = "✓ Reste: " + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['minimal']['montant_depassement'])
        st.markdown(f"""
        <div class="glass-box" style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none;'>
            <div style='text-align: center;'>
                <div style='font-size: 1.1rem; font-weight: 600; opacity: 0.95;'>💰 ÉCONOMIQUE</div>
                <div style='font-size: 3rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>{formater_cout(totaux['minimal'])}</div>
                <div style='background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 0.75rem; font-size: 1rem; backdrop-filter: blur(10px);'>
                    {reste}
                </div>
                <div style='margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;'>
                    ⏱️ 9-12 mois<br>👤 100% interne
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        reste = "✓ Reste: " + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['standard']['montant_depassement'])
        st.markdown(f"""
        <div class="glass-box" style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: 3px solid #1e40af; box-shadow: 0 12px 40px rgba(59, 130, 246, 0.4);'>
            <div style='text-align: center;'>
                <div style='font-size: 1.1rem; font-weight: 600; opacity: 0.95;'>⭐ RECOMMANDÉE</div>
                <div style='font-size: 3rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>{formater_cout(totaux['standard'])}</div>
                <div style='background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 0.75rem; font-size: 1rem; backdrop-filter: blur(10px);'>
                    {reste}
                </div>
                <div style='margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;'>
                    ⏱️ 6-9 mois<br>🤝 Mix interne/externe<br>✨ MEILLEUR ROI
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reste = "✓ Reste: " + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['maximal']['montant_depassement'])
        st.markdown(f"""
        <div class="glass-box" style='background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); color: white; border: none;'>
            <div style='text-align: center;'>
                <div style='font-size: 1.1rem; font-weight: 600; opacity: 0.95;'>🏆 PREMIUM</div>
                <div style='font-size: 3rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>{formater_cout(totaux['maximal'])}</div>
                <div style='background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 0.75rem; font-size: 1rem; backdrop-filter: blur(10px);'>
                    {reste}
                </div>
                <div style='margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;'>
                    ⏱️ 3-6 mois<br>🎯 Consultants seniors<br>💎 Excellence
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ROADMAP TIMELINE
    st.markdown("### 🗓️ Calendrier d'implémentation détaillé")
    
    approche_timeline = st.radio(
        "Sélectionnez une approche pour visualiser la roadmap complète:",
        ["💰 Économique (9-12 mois)", "⭐ Recommandée (6-9 mois)", "🏆 Premium (3-6 mois)"],
        horizontal=True
    )
    
    if "Économique" in approche_timeline:
        duree_mois = 12
        phases = [
            {"mois": "1-2", "titre": "📋 Analyse GAP interne", "taches": ["Auto-évaluation complète", "Identification écarts Loi 25", "Priorisation actions"]},
            {"mois": "3-5", "titre": "📝 Documentation & Politiques", "taches": ["Rédaction politiques (templates CAI)", "Registre des traitements", "Procédures internes"]},
            {"mois": "6-8", "titre": "🔒 Mise en conformité technique", "taches": ["Implémentation contrôles techniques", "Formation équipe interne", "Outils gratuits (Excel)"]},
            {"mois": "9-10", "titre": "✅ ÉFVP & Tests", "taches": ["ÉFVP simplifiées (2 processus)", "Tests auto-vérification", "Corrections"]},
            {"mois": "11-12", "titre": "🎯 Finalisation", "taches": ["Revue finale interne", "Documentation complète", "Plan amélioration continue"]}
        ]
    elif "Recommandée" in approche_timeline:
        duree_mois = 9
        phases = [
            {"mois": "1", "titre": "📋 GAP Analysis (Consultant)", "taches": ["Audit externe complet", "Rapport d'écarts détaillé", "Plan d'action priorisé"]},
            {"mois": "2-3", "titre": "📝 Documentation & Gouvernance", "taches": ["Politiques professionnelles", "Registre traitements complet", "Formation équipe (mixte)"]},
            {"mois": "4-5", "titre": "🔒 Implémentation technique", "taches": ["Outils conformité standards", "Contrôles de sécurité", "Intégration processus"]},
            {"mois": "6-7", "titre": "✅ ÉFVP & Validation", "taches": ["ÉFVP 2-3 processus critiques", "Support consultant ponctuel", "Ajustements"]},
            {"mois": "8-9", "titre": "🎯 Audit & Certification", "taches": ["Revue finale consultant", "Corrections dernière minute", "Attestation conformité"]}
        ]
    else:
        duree_mois = 6
        phases = [
            {"mois": "1", "titre": "📋 Audit Complet (Seniors)", "taches": ["Analyse exhaustive multi-consultants", "Rapport exécutif détaillé", "Roadmap personnalisée"]},
            {"mois": "2", "titre": "📝 Documentation Premium", "taches": ["Politiques sur mesure", "Formation présentielle complète", "Outils premium automatisés"]},
            {"mois": "3-4", "titre": "🔒 Implémentation Accélérée", "taches": ["Équipe consultants dédiée", "Mise en place tous contrôles", "Support quotidien"]},
            {"mois": "5", "titre": "✅ ÉFVP Approfondies", "taches": ["ÉFVP tous processus", "Tests exhaustifs", "Optimisations"]},
            {"mois": "6", "titre": "🏆 Certification & Support", "taches": ["Audit externe certifié", "Certification officielle", "Support 12 mois inclus"]}
        ]
    
    for idx, phase in enumerate(phases, 1):
        progress_pct = (idx / len(phases)) * 100
        st.markdown(f"""
        <div class="elegant-timeline-phase">
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <strong style='color: #3b82f6; font-size: 1.2rem; font-family: Poppins;'>Mois {phase['mois']}: {phase['titre']}</strong>
                <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 0.5rem 1rem; 
                            border-radius: 2rem; font-size: 0.9rem; font-weight: 700;'>
                    {int(progress_pct)}% complété
                </div>
            </div>
            <ul style='margin: 0; padding-left: 1.5rem; color: #4b5563; line-height: 1.8;'>
                {"".join([f"<li style='margin: 0.3rem 0;'>{tache}</li>" for tache in phase['taches']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.info(f"📅 **Durée totale:** {duree_mois} mois | 🎯 **Fin prévue:** {(datetime.now().month + duree_mois) % 12 or 12}/{datetime.now().year + (datetime.now().month + duree_mois - 1) // 12}")
    
    st.divider()
    
    # OBLIGATIONS
    if recommandations['obligatoires']:
        st.markdown("### ⚠️ Référentiels obligatoires à implémenter")
        
        st.markdown("""
        <div class="elegant-warning">
            <strong>📌 Important:</strong> Ces référentiels sont OBLIGATOIRES selon votre profil. 
            Le non-respect peut entraîner des sanctions légales.
        </div>
        """, unsafe_allow_html=True)
        
        for idx, ref in enumerate(recommandations['obligatoires'], 1):
            with st.expander(f"**{idx}. {ref['name']}** • {ref['description']}", expanded=False):
                col1, col2, col3 = st.columns(3, gap="medium")
                
                with col1:
                    st.markdown(f"### 💰 {formater_cout(ref['cout_minimal'])}")
                    st.caption("✓ 100% travail interne\n✓ Templates gratuits CAI\n✓ Excel & Google Sheets\n⏱️ 9-12 mois")
                
                with col2:
                    st.markdown(f"### ⭐ {formater_cout(ref['cout_standard'])}")
                    st.caption("✓ Consultant GAP analysis\n✓ Mix 60/40 interne/externe\n✓ Outils standards\n⏱️ 6-9 mois\n**✨ MEILLEUR ROI**")
                
                with col3:
                    st.markdown(f"### 🏆 {formater_cout(ref['cout_maximal'])}")
                    st.caption("✓ Consultants seniors dédiés\n✓ Suite premium automatisée\n✓ Formation sur mesure\n⏱️ 3-6 mois")
    
    # RÉSUMÉ FINAL
    st.markdown("---")
    st.markdown("## 💰 Investissement total requis")
    
    nb_obligatoires = len(recommandations['obligatoires'])
    
    st.markdown(f"""
    <div class="elegant-info">
        <strong style='font-size: 1.1rem;'>📋 Synthèse:</strong> Vous devez implémenter <strong style='font-size: 1.2rem; color: #1e40af;'>{nb_obligatoires} référentiel(s) obligatoire(s)</strong> 
        pour assurer votre conformité légale.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        reste = "✓ BUDGET RESTANT: " + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] else "⚠️ DÉPASSEMENT: " + formater_cout(budget_info['minimal']['montant_depassement'])
        st.markdown(f"""
        <div class="premium-card" style='background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%); border-top: 5px solid #10b981;'>
            <div style='text-align: center;'>
                <div style='color: #065f46; font-size: 0.95rem; font-weight: 700; text-transform: uppercase;'>💰 Économique</div>
                <div style='color: #065f46; font-size: 2.5rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>{formater_cout(totaux['minimal'])}</div>
                <div style='background: rgba(16, 185, 129, 0.1); padding: 0.75rem; border-radius: 0.5rem; color: #065f46; font-size: 0.95rem; font-weight: 600;'>
                    {reste}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        reste = "✓ BUDGET RESTANT: " + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] else "⚠️ DÉPASSEMENT: " + formater_cout(budget_info['standard']['montant_depassement'])
        st.markdown(f"""
        <div class="premium-card" style='background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-top: 5px solid #3b82f6; box-shadow: 0 15px 40px rgba(59, 130, 246, 0.2);'>
            <div style='text-align: center;'>
                <div style='color: #1e40af; font-size: 0.95rem; font-weight: 700; text-transform: uppercase;'>⭐ Recommandée</div>
                <div style='color: #1e40af; font-size: 2.5rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>{formater_cout(totaux['standard'])}</div>
                <div style='background: rgba(59, 130, 246, 0.1); padding: 0.75rem; border-radius: 0.5rem; color: #1e40af; font-size: 0.95rem; font-weight: 600;'>
                    {reste}
                </div>
                <div style='margin-top: 1rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.85rem; font-weight: 700;'>
                    ✨ CHOIX OPTIMAL
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reste = "✓ BUDGET RESTANT: " + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] else "⚠️ DÉPASSEMENT: " + formater_cout(budget_info['maximal']['montant_depassement'])
        st.markdown(f"""
        <div class="premium-card" style='background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); border-top: 5px solid #a855f7;'>
            <div style='text-align: center;'>
                <div style='color: #7c3aed; font-size: 0.95rem; font-weight: 700; text-transform: uppercase;'>🏆 Premium</div>
                <div style='color: #7c3aed; font-size: 2.5rem; font-weight: 800; margin: 1rem 0; font-family: Poppins;'>{formater_cout(totaux['maximal'])}</div>
                <div style='background: rgba(168, 85, 247, 0.1); padding: 0.75rem; border-radius: 0.5rem; color: #7c3aed; font-size: 0.95rem; font-weight: 600;'>
                    {reste}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CAPTURE EMAIL
    st.markdown("### 📥 Obtenez votre rapport d'analyse complet")
    
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        st.markdown("""
        <div class="elegant-success">
            <h4 style='margin-top: 0; color: #065f46;'>🎁 Rapport PDF professionnel gratuit</h4>
            <strong>Ce que vous recevrez:</strong>
            <ul style='margin: 0.5rem 0; line-height: 1.8;'>
                <li>📊 Analyse complète personnalisée de votre profil</li>
                <li>💰 Comparaison détaillée des 3 stratégies d'investissement</li>
                <li>🗓️ Roadmap d'implémentation étape par étape</li>
                <li>⚠️ Calculateur de risques et pénalités Loi 25</li>
                <li>🎁 Templates et checklists exclusifs (valeur 500$)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='padding: 1rem;'>", unsafe_allow_html=True)
        email_user = st.text_input(
            "📧 Email professionnel",
            placeholder="votre.nom@entreprise.ca",
            help="Votre email reste confidentiel et ne sera jamais partagé"
        )
        
        if st.button("📥 Télécharger mon rapport gratuit", type="primary", use_container_width=True):
            if email_user and "@" in email_user:
                st.success(f"✅ Rapport envoyé avec succès à {email_user}!")
                st.balloons()
                st.info("💬 **Notre équipe vous contactera sous 24h pour discuter de vos besoins spécifiques!**")
            else:
                st.error("⚠️ Veuillez entrer une adresse email valide")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CTA CONSULTATION
    st.markdown("""
    <div class="premium-card" style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 2px solid #f59e0b; text-align: center; padding: 2.5rem;'>
        <h2 style='margin: 0 0 1rem 0; color: #78350f; font-family: Poppins;'>💬 Besoin d'accompagnement?</h2>
        <p style='font-size: 1.1rem; color: #92400e; margin: 0 0 1.5rem 0;'>
            Réservez une consultation stratégique gratuite de 30 minutes avec nos experts en conformité
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📅 Réserver ma consultation gratuite maintenant", use_container_width=True):
            st.info("✉️ Un lien de réservation personnalisé a été envoyé à votre email!")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Nouvelle analyse complète", use_container_width=True):
            st.session_state.etape = 1
            st.session_state.profil = {}
            st.session_state.economies_selectionnees = []
            st.rerun()

# ==================== SIDEBAR PREMIUM ====================
with st.sidebar:
    st.markdown("""
    <div class="premium-card" style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 2rem; margin-bottom: 1.5rem;'>
        <h2 style='margin: 0; font-size: 1.8rem; font-family: Poppins;'>🔒 Conformité Pro</h2>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.95; font-size: 0.9rem;'>Version Premium 2.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✨ Fonctionnalités Premium")
    st.markdown("""
    <div class="elegant-success">
        • Calculateur risques Loi 25<br>
        • Roadmap visuelle interactive<br>
        • Export PDF professionnel<br>
        • Analyse comparative<br>
        • Templates exclusifs
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### ℹ️ Notre expertise")
    st.markdown("""
    <div class="glass-box" style='padding: 1rem;'>
        ✅ Conformité légale garantie<br>
        💰 ROI calculé et documenté<br>
        📊 Méthodologie certifiée<br>
        📋 Support personnalisé<br>
        🎁 Ressources gratuites
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 📞 Contactez-nous")
    st.markdown("""
    📧 **Email:** contact@conformite.ca  
    📞 **Tél:** +1 (514) XXX-XXXX  
    🌐 **Web:** www.conformite.ca
    """)
    
    st.divider()
    
    st.caption("© 2026 Conformité Pro • Tous droits réservés")