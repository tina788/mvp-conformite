"""
Application Streamlit - Assistant de Conformité Cybersécurité
Version Ultra Visuelle
"""

import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime
from utils.calculations import (
    calculer_economies,
    filtrer_referentiels_applicables,
    generer_recommandations,
    formater_cout
)

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Assistant Conformité Cyber",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== STYLES CSS AVANCÉS ====================
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Global */
* {
    font-family: 'Inter', sans-serif;
}

/* Header avec effet glassmorphism */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 1rem;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.main-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.main-subtitle {
    font-size: 1.2rem;
    font-weight: 400;
    opacity: 0.95;
}

/* Cartes avec effet hover */
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 1rem;
    color: white;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

/* Info boxes avec icônes */
.info-box {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    border-left: 4px solid #3B82F6;
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin: 1.5rem 0;
    box-shadow: 0 2px 10px rgba(59, 130, 246, 0.1);
}

.warning-box {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    border-left: 4px solid #F59E0B;
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin: 1.5rem 0;
    box-shadow: 0 2px 10px rgba(245, 158, 11, 0.1);
}

.success-box {
    background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
    border-left: 4px solid #10B981;
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin: 1.5rem 0;
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.1);
}

/* Boutons améliorés */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    border-radius: 0.5rem;
    border: none;
    padding: 0.75rem 2rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Progress bar personnalisée */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

/* Expander styling */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
    border-radius: 0.5rem;
    font-weight: 600;
    padding: 1rem !important;
}

/* Référentiel card */
.ref-card {
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.ref-card:hover {
    border-color: #667eea;
    box-shadow: 0 8px 15px rgba(102, 126, 234, 0.2);
    transform: translateY(-3px);
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 2rem;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.25rem;
}

.badge-mandatory {
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    color: white;
}

.badge-optional {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
    color: white;
}

/* Animations */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animated {
    animation: slideIn 0.5s ease-out;
}
</style>
""", unsafe_allow_html=True)

# ==================== CHARGEMENT DONNÉES ====================
@st.cache_data
def charger_donnees():
    data_path = Path(__file__).parent / "data" / "referentiels.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

data = charger_donnees()

# ==================== INITIALISATION SESSION ====================
if 'etape' not in st.session_state:
    st.session_state.etape = 1
if 'profil' not in st.session_state:
    st.session_state.profil = {}
if 'economies_selectionnees' not in st.session_state:
    st.session_state.economies_selectionnees = []

# ==================== HEADER MAGNIFIQUE ====================
st.markdown("""
<div class="main-header animated">
    <div class="main-title">🔒 Assistant de Conformité Cybersécurité</div>
    <div class="main-subtitle">Outil intelligent adapté à votre profil et budget</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box animated">
    <strong>📊 Sources des coûts:</strong> Estimations basées sur des consultants canadiens/québécois (2024-2026), 
    études de marché (Matayo AI, IAS Canada, Secureframe) et documents officiels (NIST, CAI Québec). 
    Les coûts réels peuvent varier de ±30% selon votre contexte spécifique.
</div>
""", unsafe_allow_html=True)

# Barre de progression stylée
progress = (st.session_state.etape - 1) / 2
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.progress(progress, text=f"🎯 Étape {st.session_state.etape}/3")

st.markdown("<br>", unsafe_allow_html=True)

# ==================== ÉTAPE 1: PROFIL ====================
if st.session_state.etape == 1:
    st.markdown("## 📋 Profil de l'organisation")
    st.markdown("<div class='animated'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏢 Informations de base")
        secteur = st.selectbox(
            "Secteur d'activité",
            options=["", "health", "finance", "public", "tech", "retail", "other"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "health": "🏥 Santé",
                "finance": "💰 Finance / Assurance",
                "public": "🏛️ Secteur public",
                "tech": "💻 Technologies / SaaS",
                "retail": "🛍️ Commerce / Retail",
                "other": "📊 Autre"
            }[x]
        )
        
        taille = st.selectbox(
            "Taille de l'organisation",
            options=["", "micro", "small", "medium", "large"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "micro": "👤 Micro (1-10 employés)",
                "small": "👥 Petite (11-49 employés)",
                "medium": "👨‍👩‍👧‍👦 Moyenne (50-199 employés)",
                "large": "🏢 Grande (200+ employés)"
            }[x]
        )
    
    with col2:
        st.markdown("### 💵 Budget et maturité")
        budget = st.selectbox(
            "Budget disponible",
            options=["", "low", "medium", "high"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "low": "💰 Limité (< 50K$)",
                "medium": "💰💰 Moyen (50-200K$)",
                "high": "💰💰💰 Élevé (> 200K$)"
            }[x]
        )
        
        maturite = st.selectbox(
            "Niveau de maturité cybersécurité",
            options=["", "initial", "managed", "defined", "optimized"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "initial": "🌱 Initial",
                "managed": "🌿 Géré",
                "defined": "🌳 Défini",
                "optimized": "🌲 Optimisé"
            }[x]
        )
    
    st.markdown("### ☁️ Infrastructure")
    cols = st.columns(3)
    infrastructure = []
    
    with cols[0]:
        if st.checkbox("🖥️ Sur site (On-premise)", key="infra_onprem"):
            infrastructure.append("onprem")
    with cols[1]:
        if st.checkbox("☁️ Cloud (AWS, Azure, GCP)", key="infra_cloud"):
            infrastructure.append("cloud")
    with cols[2]:
        if st.checkbox("🔄 Hybride", key="infra_hybrid"):
            infrastructure.append("hybrid")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("➡️ Suivant: Évaluation de l'existant", type="primary", use_container_width=True):
        if not secteur or not taille or not budget or not maturite or not infrastructure:
            st.error("⚠️ Veuillez remplir tous les champs obligatoires")
        else:
            st.session_state.profil = {
                'secteur': secteur,
                'taille': taille,
                'budget': budget,
                'maturite': maturite,
                'infrastructure': infrastructure
            }
            st.session_state.etape = 2
            st.rerun()

# ==================== ÉTAPE 2: EXISTANT ====================
elif st.session_state.etape == 2:
    st.markdown("## 💡 Évaluation de l'existant")
    
    st.markdown("""
    <div class="success-box animated">
        <strong>💡 Astuce:</strong> Cochez tout ce que vous avez DÉJÀ en place pour réduire considérablement 
        les coûts d'implémentation! Chaque élément coché = économies substantielles.
    </div>
    """, unsafe_allow_html=True)
    
    economies_data = data['economies']
    gouvernance = {k: v for k, v in economies_data.items() if v['categorie'] == 'gouvernance'}
    securite = {k: v for k, v in economies_data.items() if v['categorie'] == 'securite'}
    processus = {k: v for k, v in economies_data.items() if v['categorie'] == 'processus'}
    
    economies_selectionnees = []
    
    # Gouvernance avec style
    with st.expander("📋 **Gouvernance et Politiques**", expanded=True):
        for key, item in gouvernance.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(
                    f"**{item['label']}**",
                    help=item['description'],
                    key=f"eco_{key}"
                )
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: bold;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    # Sécurité avec style
    with st.expander("🔒 **Sécurité Technique**", expanded=True):
        for key, item in securite.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(
                    f"**{item['label']}**",
                    help=item['description'],
                    key=f"eco_{key}"
                )
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: bold;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    # Processus avec style
    with st.expander("⚙️ **Processus et Procédures**", expanded=True):
        for key, item in processus.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(
                    f"**{item['label']}**",
                    help=item['description'],
                    key=f"eco_{key}"
                )
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: bold;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    # Graphique économies
    total_economies = calculer_economies(economies_selectionnees, economies_data)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Métriques visuelles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                    padding: 1.5rem; border-radius: 1rem; text-align: center; color: white;
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>💰 Économies totales</div>
            <div style='font-size: 2rem; font-weight: bold; margin-top: 0.5rem;'>{formater_cout(total_economies)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); 
                    padding: 1.5rem; border-radius: 1rem; text-align: center; color: white;
                    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>✅ Éléments cochés</div>
            <div style='font-size: 2rem; font-weight: bold; margin-top: 0.5rem;'>{len(economies_selectionnees)}/10</div>
        </div>
        """, unsafe_allow_html=True)
    
    pct = round((total_economies / 170000) * 100) if total_economies > 0 else 0
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
                    padding: 1.5rem; border-radius: 1rem; text-align: center; color: white;
                    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>📊 Progression</div>
            <div style='font-size: 2rem; font-weight: bold; margin-top: 0.5rem;'>{pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); 
                    padding: 1.5rem; border-radius: 1rem; text-align: center; color: white;
                    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>🎯 Maximum</div>
            <div style='font-size: 2rem; font-weight: bold; margin-top: 0.5rem;'>170K$</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphique en donut
    if total_economies > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Pie(
            labels=['Économies réalisées', 'Potentiel restant'],
            values=[total_economies, 170000 - total_economies],
            hole=.6,
            marker_colors=['#10B981', '#E5E7EB']
        )])
        fig.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            annotations=[dict(text=f'{pct}%', x=0.5, y=0.5, font_size=40, showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.etape = 1
            st.rerun()
    with col_next:
        if st.button("🎯 Voir mes recommandations", type="primary", use_container_width=True):
            st.session_state.economies_selectionnees = economies_selectionnees
            st.session_state.etape = 3
            st.rerun()

# ==================== ÉTAPE 3: RÉSULTATS ====================
elif st.session_state.etape == 3:
    st.markdown("## 📊 Vos recommandations personnalisées")
    
    profil = st.session_state.profil
    economies_sel = st.session_state.economies_selectionnees
    total_economies = calculer_economies(economies_sel, data['economies'])
    obligatoires, optionnels = filtrer_referentiels_applicables(data['referentiels'], profil)
    recommandations = generer_recommandations(obligatoires, optionnels, total_economies, profil['budget'])
    
    # Profil résumé visuel
    st.markdown("### 👤 Votre profil")
    col1, col2, col3, col4 = st.columns(4)
    
    secteur_labels = {"health": "🏥 Santé", "finance": "💰 Finance", "public": "🏛️ Public", "tech": "💻 Tech", "retail": "🛍️ Retail", "other": "📊 Autre"}
    taille_labels = {"micro": "👤 Micro", "small": "👥 Petite", "medium": "👨‍👩‍👧‍👦 Moyenne", "large": "🏢 Grande"}
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='color: #6B7280; font-size: 0.85rem;'>Secteur</div>
            <div style='color: #1F2937; font-size: 1.2rem; font-weight: bold; margin-top: 0.25rem;'>{secteur_labels.get(profil['secteur'], profil['secteur'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #10B981; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='color: #6B7280; font-size: 0.85rem;'>Taille</div>
            <div style='color: #1F2937; font-size: 1.2rem; font-weight: bold; margin-top: 0.25rem;'>{taille_labels.get(profil['taille'], profil['taille'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #F59E0B; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='color: #6B7280; font-size: 0.85rem;'>Budget</div>
            <div style='color: #1F2937; font-size: 1.2rem; font-weight: bold; margin-top: 0.25rem;'>{formater_cout(recommandations['budget']['montant'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #8B5CF6; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='color: #6B7280; font-size: 0.85rem;'>Économies</div>
            <div style='color: #1F2937; font-size: 1.2rem; font-weight: bold; margin-top: 0.25rem;'>{formater_cout(total_economies)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Vue d'ensemble avec graphique
    st.markdown("### 📊 Vue d'ensemble - 3 approches")
    
    totaux = recommandations['totaux']
    budget_info = recommandations['budget']
    
    # Graphique comparatif
    fig = go.Figure()
    
    approaches = ['💰 Économique', '⭐ Recommandée', '🏆 Premium']
    costs = [totaux['minimal'], totaux['standard'], totaux['maximal']]
    colors = ['#10B981', '#3B82F6', '#8B5CF6']
    
    fig.add_trace(go.Bar(
        x=approaches,
        y=costs,
        marker_color=colors,
        text=[formater_cout(c) for c in costs],
        textposition='auto',
    ))
    
    fig.add_hline(y=budget_info['montant'], line_dash="dash", line_color="red", 
                  annotation_text=f"Budget: {formater_cout(budget_info['montant'])}")
    
    fig.update_layout(
        title="Comparaison des 3 approches",
        yaxis_title="Coût ($)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cartes des 3 approches
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center;
                    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);'>
            <div style='font-size: 1rem; margin-bottom: 0.5rem;'>💰 ÉCONOMIQUE</div>
            <div style='font-size: 2.5rem; font-weight: bold;'>{formater_cout(totaux['minimal'])}</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.9;'>
                {'✓ Reste: ' + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['minimal']['montant_depassement'])}
            </div>
            <hr style='border: none; border-top: 1px solid rgba(255,255,255,0.3); margin: 1rem 0;'>
            <div style='font-size: 0.8rem; text-align: left;'>
                ✓ 100% interne<br>
                ✓ Templates gratuits<br>
                ✓ Formation en ligne<br>
                ⚠️ + de temps requis
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center;
                    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
                    border: 3px solid #1e40af;'>
            <div style='font-size: 1rem; margin-bottom: 0.5rem;'>⭐ RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold;'>{formater_cout(totaux['standard'])}</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.9;'>
                {'✓ Reste: ' + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['standard']['montant_depassement'])}
            </div>
            <hr style='border: none; border-top: 1px solid rgba(255,255,255,0.3); margin: 1rem 0;'>
            <div style='font-size: 0.8rem; text-align: left;'>
                ✓ Mix interne/externe<br>
                ✓ Consultant GAP<br>
                ✓ Outils standards<br>
                ⭐ MEILLEUR ROI
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center;
                    box-shadow: 0 8px 20px rgba(168, 85, 247, 0.3);'>
            <div style='font-size: 1rem; margin-bottom: 0.5rem;'>🏆 PREMIUM</div>
            <div style='font-size: 2.5rem; font-weight: bold;'>{formater_cout(totaux['maximal'])}</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.9;'>
                {'✓ Reste: ' + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['maximal']['montant_depassement'])}
            </div>
            <hr style='border: none; border-top: 1px solid rgba(255,255,255,0.3); margin: 1rem 0;'>
            <div style='font-size: 0.8rem; text-align: left;'>
                ✓ Consultants seniors<br>
                ✓ Outils premium<br>
                ✓ Support 12 mois<br>
                🏆 Excellence garantie
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Obligations
    if recommandations['obligatoires']:
        st.markdown("### ⚠️ À implémenter MAINTENANT")
        
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Attention:</strong> Ces référentiels sont OBLIGATOIRES selon votre profil.
        </div>
        """, unsafe_allow_html=True)
        
        for idx, ref in enumerate(recommandations['obligatoires'], 1):
            st.markdown(f"""
            <div class="ref-card">
                <h3 style='color: #1F2937; margin: 0 0 0.5rem 0;'>
                    {idx}. {ref['name']}
                    <span class='badge badge-mandatory'>⚠️ OBLIGATOIRE</span>
                </h3>
                <p style='color: #6B7280; margin: 0 0 1rem 0;'>{ref['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**💰 Économique:** {formater_cout(ref['cout_minimal'])}")
            with col2:
                st.markdown(f"**⭐ Recommandé:** {formater_cout(ref['cout_standard'])}")
            with col3:
                st.markdown(f"**🏆 Premium:** {formater_cout(ref['cout_maximal'])}")
    
    # Optionnels
    if recommandations['optionnels']:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💡 Recommandations pour plus tard")
        
        cols = st.columns(2)
        for idx, ref in enumerate(recommandations['optionnels']):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="ref-card">
                    <h4 style='color: #3B82F6; margin: 0 0 0.5rem 0;'>
                        {ref['name']}
                        <span class='badge badge-optional'>💡 OPTIONNEL</span>
                    </h4>
                    <p style='color: #6B7280; font-size: 0.9rem; margin: 0 0 0.5rem 0;'>{ref['description']}</p>
                    <p style='font-size: 1.3rem; font-weight: bold; color: #3B82F6; margin: 0;'>
                        {formater_cout(ref['cout_standard'])}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Recommencer", use_container_width=True):
            st.session_state.etape = 1
            st.session_state.profil = {}
            st.session_state.economies_selectionnees = []
            st.rerun()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 1rem;'>
        <h2 style='margin: 0; font-size: 1.5rem;'>🔒 Assistant Conformité</h2>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Version MVP 1.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ℹ️ À propos")
    st.info("""
    ✅ Identifie obligations légales  
    💰 Calcule coûts réels  
    📊 Optimise budget  
    📋 Planifie implémentation
    """)
    
    st.markdown("### 📈 Opportunité")
    st.success("""
    **Marché québécois:**  
    • 277K PME concernées  
    • Marché 6,6G$  
    • Conformité < 40%
    """)
    
    st.divider()
    
    st.markdown("### 📞 Support")
    st.markdown("""
    📧 contact@example.ca  
    📞 514-XXX-XXXX  
    🌐 www.example.ca
    """)
    
    st.divider()
    st.caption("© 2026 - Tous droits réservés")