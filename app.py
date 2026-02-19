"""
Application Streamlit - Assistant de Conformité Cybersécurité
Version Complète et Professionnelle
"""

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

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Assistant Conformité Cyber",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== STYLES CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

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
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.main-subtitle {
    font-size: 1.1rem;
    opacity: 0.95;
}

.info-box {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    border-left: 4px solid #3B82F6;
    padding: 1rem;
    border-radius: 0.75rem;
    margin: 1rem 0;
    font-size: 0.95rem;
    line-height: 1.6;
}

.warning-box {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    border-left: 4px solid #F59E0B;
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin: 1.5rem 0;
}

.success-box {
    background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
    border-left: 4px solid #10B981;
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin: 1.5rem 0;
}

.ref-card {
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    border: 2px solid #E5E7EB;
}

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

.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    border-radius: 0.5rem;
    border: none;
    padding: 0.75rem 2rem;
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

# ==================== SESSION STATE ====================
if 'etape' not in st.session_state:
    st.session_state.etape = 1
if 'profil' not in st.session_state:
    st.session_state.profil = {}
if 'economies_selectionnees' not in st.session_state:
    st.session_state.economies_selectionnees = []

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <div class="main-title">🔒 Assistant de Conformité Cybersécurité</div>
    <div class="main-subtitle">Outil intelligent adapté à votre profil et budget</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>📊 Sources des coûts:</strong> Estimations basées sur des consultants canadiens/québécois (2024-2026), 
    études de marché (Matayo AI, IAS Canada, Secureframe) et documents officiels (NIST, CAI Québec).
</div>
""", unsafe_allow_html=True)

progress = (st.session_state.etape - 1) / 2
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.progress(progress, text=f"🎯 Étape {st.session_state.etape}/3")

st.markdown("<br>", unsafe_allow_html=True)

# ==================== ÉTAPE 1: PROFIL ====================
if st.session_state.etape == 1:
    st.markdown("## 📋 Profil de l'organisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏢 Informations de base")
        secteur = st.selectbox(
            "Secteur d'activité",
            options=["", "health", "finance", "public", "tech", "retail", "other"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "health": "🏥 Santé",
                "finance": "💰 Finance",
                "public": "🏛️ Public",
                "tech": "💻 Tech",
                "retail": "🛍️ Retail",
                "other": "📊 Autre"
            }[x]
        )
        
        taille = st.selectbox(
            "Taille",
            options=["", "micro", "small", "medium", "large"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "micro": "Micro (1-10)",
                "small": "Petite (11-49)",
                "medium": "Moyenne (50-199)",
                "large": "Grande (200+)"
            }[x]
        )
    
    with col2:
        st.markdown("### 💵 Budget et maturité")
        budget = st.selectbox(
            "Budget disponible",
            options=["", "low", "medium", "high"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "low": "Limité (< 50K$)",
                "medium": "Moyen (50-200K$)",
                "high": "Élevé (> 200K$)"
            }[x]
        )
        
        maturite = st.selectbox(
            "Maturité cybersécurité",
            options=["", "initial", "managed", "defined", "optimized"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "initial": "Initial",
                "managed": "Géré",
                "defined": "Défini",
                "optimized": "Optimisé"
            }[x]
        )
    
    st.markdown("### ☁️ Infrastructure")
    cols = st.columns(3)
    infrastructure = []
    
    with cols[0]:
        if st.checkbox("Sur site", key="infra_onprem"):
            infrastructure.append("onprem")
    with cols[1]:
        if st.checkbox("Cloud", key="infra_cloud"):
            infrastructure.append("cloud")
    with cols[2]:
        if st.checkbox("Hybride", key="infra_hybrid"):
            infrastructure.append("hybrid")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("➡️ Suivant: Évaluation de l'existant", type="primary", use_container_width=True):
        if not secteur or not taille or not budget or not maturite or not infrastructure:
            st.error("⚠️ Veuillez remplir tous les champs")
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
    <div class="success-box">
        <strong>💡 Astuce:</strong> Cochez tout ce que vous avez DÉJÀ en place pour réduire les coûts!
    </div>
    """, unsafe_allow_html=True)
    
    economies_data = data['economies']
    gouvernance = {k: v for k, v in economies_data.items() if v['categorie'] == 'gouvernance'}
    securite = {k: v for k, v in economies_data.items() if v['categorie'] == 'securite'}
    processus = {k: v for k, v in economies_data.items() if v['categorie'] == 'processus'}
    
    economies_selectionnees = []
    
    with st.expander("📋 **Gouvernance et Politiques**", expanded=True):
        for key, item in gouvernance.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(f"**{item['label']}**", help=item['description'], key=f"eco_{key}")
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: bold;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    with st.expander("🔒 **Sécurité Technique**", expanded=True):
        for key, item in securite.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(f"**{item['label']}**", help=item['description'], key=f"eco_{key}")
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: bold;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    with st.expander("⚙️ **Processus et Procédures**", expanded=True):
        for key, item in processus.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(f"**{item['label']}**", help=item['description'], key=f"eco_{key}")
            with col2:
                if checked:
                    economies_selectionnees.append(key)
                    st.markdown(f"<span style='color: #10B981; font-weight: bold;'>+{formater_cout(item['economie'])}</span>", unsafe_allow_html=True)
    
    total_economies = calculer_economies(economies_selectionnees, economies_data)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Économies totales", formater_cout(total_economies))
    with col2:
        st.metric("✅ Éléments", f"{len(economies_selectionnees)}/10")
    with col3:
        pct = round((total_economies / 170000) * 100) if total_economies > 0 else 0
        st.metric("📊 Progression", f"{pct}%")
    with col4:
        st.metric("🎯 Maximum", "170K$")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.etape = 1
            st.rerun()
    with col_next:
        if st.button("🎯 Voir recommandations", type="primary", use_container_width=True):
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
    
    # Profil
    st.markdown("### 👤 Votre profil")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Secteur", profil['secteur'].title())
    with col2:
        st.metric("Taille", profil['taille'].title())
    with col3:
        st.metric("Budget", formater_cout(recommandations['budget']['montant']))
    with col4:
        st.metric("Économies", formater_cout(total_economies))
    
    st.divider()
    
    # Vue d'ensemble
    totaux = recommandations['totaux']
    budget_info = recommandations['budget']
    
    st.markdown("### 📊 Vue d'ensemble - 3 approches")
    
    # GRAPHIQUE COMPARATIF
    fig = go.Figure()
    
    approaches = ['💰 Économique', '⭐ Recommandée', '🏆 Premium']
    costs = [totaux['minimal'], totaux['standard'], totaux['maximal']]
    colors = ['#10B981', '#3B82F6', '#A855F7']
    
    fig.add_trace(go.Bar(
        x=approaches,
        y=costs,
        marker_color=colors,
        text=[formater_cout(c) for c in costs],
        textposition='auto',
        textfont=dict(size=16, color='white', family='Inter')
    ))
    
    fig.add_hline(
        y=budget_info['montant'], 
        line_dash="dash", 
        line_color="#EF4444", 
        line_width=3,
        annotation_text=f"Budget: {formater_cout(budget_info['montant'])}", 
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Comparaison des 3 approches vs votre budget",
        yaxis_title="Coût ($)",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3 Cartes des approches
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);'>
            <div style='font-size: 1rem; font-weight: 600;'>💰 ÉCONOMIQUE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['minimal'])}</div>
            <div style='font-size: 0.9rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.5rem; margin-top: 0.5rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['minimal']['montant_depassement'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center; border: 3px solid #1e40af; box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);'>
            <div style='font-size: 1rem; font-weight: 600;'>⭐ RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['standard'])}</div>
            <div style='font-size: 0.9rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.5rem; margin-top: 0.5rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['standard']['montant_depassement'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(168, 85, 247, 0.3);'>
            <div style='font-size: 1rem; font-weight: 600;'>🏆 PREMIUM</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['maximal'])}</div>
            <div style='font-size: 0.9rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.5rem; margin-top: 0.5rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['maximal']['montant_depassement'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Obligations DÉTAILLÉES
    if recommandations['obligatoires']:
        st.markdown("### ⚠️ À IMPLÉMENTER MAINTENANT")
        
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Attention:</strong> Ces référentiels sont OBLIGATOIRES selon votre profil.
        </div>
        """, unsafe_allow_html=True)
        
        for idx, ref in enumerate(recommandations['obligatoires'], 1):
            st.markdown(f"""
            <div class="ref-card">
                <h3 style='margin: 0 0 0.5rem 0; color: #1F2937;'>{idx}. {ref['name']} 
                <span class='badge badge-mandatory'>⚠️ OBLIGATOIRE</span></h3>
                <p style='color: #6B7280; margin: 0;'>{ref['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 💵 CHOIX D'APPROCHES - Quel investissement?")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='background: #F0FDF4; padding: 1.5rem; border-radius: 0.75rem; border: 2px solid #10B981; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);'>
                    <div style='text-align: center; background: #10B981; color: white; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                        <div style='font-size: 0.85rem; font-weight: 600;'>💰 APPROCHE ÉCONOMIQUE</div>
                        <div style='font-size: 2rem; font-weight: bold;'>{formater_cout(ref['cout_minimal'])}</div>
                    </div>
                    <div style='font-size: 0.9rem; color: #1F2937;'>
                        <strong style='color: #10B981;'>✓ Ce qui EST inclus:</strong><br>
                        <ul style='margin: 0.5rem 0; padding-left: 1.2rem;'>
                            <li>Travail 100% interne</li>
                            <li>Templates gratuits (CAI)</li>
                            <li>Outils Excel/Google</li>
                            <li>Formation en ligne</li>
                            <li>ÉFVP simplifiées</li>
                        </ul>
                        <strong style='color: #F59E0B;'>✗ Ce qui MANQUE:</strong><br>
                        <ul style='margin: 0.5rem 0; padding-left: 1.2rem;'>
                            <li>Consultants externes</li>
                            <li>Outils automatisés</li>
                            <li>Formation présentielle</li>
                            <li>Audits externes</li>
                        </ul>
                        <div style='background: #FEF3C7; padding: 0.75rem; border-radius: 0.5rem; margin-top: 1rem; border-left: 3px solid #F59E0B;'>
                            <strong style='color: #92400E;'>⚠️ Risque:</strong> Plus de temps requis (9-12 mois)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: #EFF6FF; padding: 1.5rem; border-radius: 0.75rem; border: 2px solid #3B82F6; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);'>
                    <div style='text-align: center; background: #3B82F6; color: white; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                        <div style='font-size: 0.85rem; font-weight: 600;'>⭐ APPROCHE RECOMMANDÉE</div>
                        <div style='font-size: 2rem; font-weight: bold;'>{formater_cout(ref['cout_standard'])}</div>
                    </div>
                    <div style='font-size: 0.9rem; color: #1F2937;'>
                        <strong style='color: #3B82F6;'>✓ Ce qui EST inclus:</strong><br>
                        <ul style='margin: 0.5rem 0; padding-left: 1.2rem;'>
                            <li>Consultant GAP analysis</li>
                            <li>Mix 60% interne / 40% externe</li>
                            <li>Outils standards conformité</li>
                            <li>Formation mixte</li>
                            <li>ÉFVP 2-3 processus critiques</li>
                            <li>Documentation complète</li>
                        </ul>
                        <strong style='color: #10B981;'>💡 Pourquoi choisir:</strong><br>
                        <ul style='margin: 0.5rem 0; padding-left: 1.2rem;'>
                            <li>Équilibre coût/qualité optimal</li>
                            <li>Expertise externe ciblée</li>
                            <li>Conformité solide et durable</li>
                        </ul>
                        <div style='background: #D1FAE5; padding: 0.75rem; border-radius: 0.5rem; margin-top: 1rem; border-left: 3px solid #10B981;'>
                            <strong style='color: #065F46;'>✓ MEILLEUR ROI</strong> selon nos analyses
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='background: #FAF5FF; padding: 1.5rem; border-radius: 0.75rem; border: 2px solid #A855F7; box-shadow: 0 2px 8px rgba(168, 85, 247, 0.15);'>
                    <div style='text-align: center; background: #A855F7; color: white; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                        <div style='font-size: 0.85rem; font-weight: 600;'>🏆 APPROCHE PREMIUM</div>
                        <div style='font-size: 2rem; font-weight: bold;'>{formater_cout(ref['cout_maximal'])}</div>
                    </div>
                    <div style='font-size: 0.9rem; color: #1F2937;'>
                        <strong style='color: #A855F7;'>✓ Ce qui EST inclus:</strong><br>
                        <ul style='margin: 0.5rem 0; padding-left: 1.2rem;'>
                            <li>Consultants seniors dédiés</li>
                            <li>Outils automatisés premium</li>
                            <li>Formation sur mesure présentielle</li>
                            <li>ÉFVP approfondies tous processus</li>
                            <li>Audits externes complets</li>
                            <li>Support continu 12 mois</li>
                            <li>Certification/attestation</li>
                        </ul>
                        <strong style='color: #A855F7;'>💎 Avantages:</strong><br>
                        <ul style='margin: 0.5rem 0; padding-left: 1.2rem;'>
                            <li>Implémentation plus rapide (3-6 mois)</li>
                            <li>Risque minimisé</li>
                            <li>Excellence garantie</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Tableau comparatif
            st.markdown("##### 📊 Comparaison détaillée:")
            df = pd.DataFrame({
                'Poste': ['Coût initial', 'Économies existant', 'Optimisations', 'Premium +', 'TOTAL'],
                'Économique': [
                    formater_cout(ref['baseCost']),
                    f"-{formater_cout(ref['economies'])}",
                    f"-{formater_cout(ref['cout_standard'] - ref['cout_minimal'])}",
                    "-",
                    formater_cout(ref['cout_minimal'])
                ],
                'Recommandé': [
                    formater_cout(ref['baseCost']),
                    f"-{formater_cout(ref['economies'])}",
                    "-",
                    "-",
                    formater_cout(ref['cout_standard'])
                ],
                'Premium': [
                    formater_cout(ref['baseCost']),
                    "-",
                    "-",
                    f"+{formater_cout(ref['cout_maximal'] - ref['baseCost'])}",
                    formater_cout(ref['cout_maximal'])
                ]
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # DÉTAILS amélioré
            with st.expander("📋 **DÉTAILS: Ce qui doit être mis en place** (cliquez pour voir)", expanded=False):
                tab1, tab2, tab3 = st.tabs(["💰 Version minimale", "⭐ Version recommandée", "🏆 Version premium"])
                
                with tab1:
                    st.markdown("""
                    <div style='background: #F0FDF4; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #10B981;'>
                        <h4 style='color: #065F46; margin-top: 0;'>⚠️ Version minimale - Strict essentiel uniquement</h4>
                        <p><strong>Substitutions pour réduire les coûts:</strong></p>
                        <ul>
                            <li>Consultants externes → <strong>Travail 100% interne</strong></li>
                            <li>Formation complète → <strong>Formation de base gratuite en ligne</strong></li>
                            <li>Outils automatisés → <strong>Excel et documents Word</strong></li>
                            <li>Audits externes → <strong>Auto-évaluations internes</strong></li>
                        </ul>
                        <p><strong>⏱️ Délai:</strong> 9-12 mois</p>
                        <p><strong>👥 Ressources:</strong> 1-2 personnes internes à temps partiel</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("""
                    <div style='background: #EFF6FF; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #3B82F6;'>
                        <h4 style='color: #1E40AF; margin-top: 0;'>⭐ Version recommandée - Équilibre optimal</h4>
                        <p><strong>Mix optimal 60% interne / 40% externe:</strong></p>
                        <ul>
                            <li><strong>Consultant externe:</strong> GAP analysis initiale (2-3 semaines)</li>
                            <li><strong>Équipe interne:</strong> Mise en œuvre quotidienne</li>
                            <li><strong>Outils:</strong> Standards de conformité (Vanta, Drata, ou similaire)</li>
                            <li><strong>Formation:</strong> Mixte en ligne + 2-3 sessions présentielles</li>
                            <li><strong>ÉFVP:</strong> Sur 2-3 processus critiques avec support consultant</li>
                            <li><strong>Documentation:</strong> Templates professionnels + personnalisation</li>
                        </ul>
                        <p><strong>⏱️ Délai:</strong> 6-9 mois</p>
                        <p><strong>👥 Ressources:</strong> 2-3 personnes internes + consultant ponctuel</p>
                        <p><strong>✓ MEILLEUR RAPPORT QUALITÉ/PRIX</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with tab3:
                    st.markdown("""
                    <div style='background: #FAF5FF; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #A855F7;'>
                        <h4 style='color: #7C3AED; margin-top: 0;'>🏆 Version premium - Excellence garantie</h4>
                        <p><strong>Package complet clés en main:</strong></p>
                        <ul>
                            <li><strong>Consultants seniors dédiés:</strong> Équipe de 2-3 experts assignés</li>
                            <li><strong>Outils premium:</strong> Suite automatisée complète (OneTrust, ServiceNow, etc.)</li>
                            <li><strong>Formation sur mesure:</strong> Programme présentiel personnalisé</li>
                            <li><strong>ÉFVP approfondies:</strong> Tous les processus analysés en détail</li>
                            <li><strong>Audits externes:</strong> Vérification par organisme certifié</li>
                            <li><strong>Support continu:</strong> 12 mois post-implémentation</li>
                            <li><strong>Certification:</strong> Préparation et obtention certification officielle</li>
                        </ul>
                        <p><strong>⏱️ Délai:</strong> 3-6 mois</p>
                        <p><strong>👥 Ressources:</strong> Équipe consultants + 1 personne interne coordination</p>
                        <p><strong>→ Pour:</strong> Grandes organisations, secteurs hautement réglementés</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    # RÉSUMÉ TOTAL
    st.markdown("---")
    st.markdown("## 💰 RÉSUMÉ: TOTAL À INVESTIR MAINTENANT")
    
    nb_obligatoires = len(recommandations['obligatoires'])
    
    st.markdown(f"**{nb_obligatoires} référentiel(s) obligatoire(s) - Choisissez votre approche**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 600;'>💰 Approche ÉCONOMIQUE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['minimal'])}</div>
            <div style='background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.3rem; margin-top: 0.5rem; font-size: 0.9rem;'>
                {'✓ RESTE: ' + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['minimal']['montant_depassement'])}
            </div>
            <div style='font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.95;'>Travail interne, templates gratuits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center; border: 3px solid #1E40AF; box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 600;'>⭐ Approche RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['standard'])}</div>
            <div style='background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.3rem; margin-top: 0.5rem; font-size: 0.9rem;'>
                {'✓ RESTE: ' + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['standard']['montant_depassement'])}
            </div>
            <div style='font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.95;'>Mix interne/externe, meilleur ROI</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #A855F7 0%, #9333EA 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(168, 85, 247, 0.3);'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 600;'>🏆 Approche PREMIUM</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['maximal'])}</div>
            <div style='background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.3rem; margin-top: 0.5rem; font-size: 0.9rem;'>
                {'✓ RESTE: ' + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['maximal']['montant_depassement'])}
            </div>
            <div style='font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.95;'>Consultants seniors, outils premium</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quelle approche choisir
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💡 Quelle approche choisir?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Économique si:**
        • Budget très limité
        • Expertise interne solide
        • Temps disponible (9-12 mois)
        """)
    
    with col2:
        st.markdown("""
        **Recommandée si:**
        • Budget moyen
        • Mix expertise interne/externe
        • Délai standard (6-9 mois)
        • **MEILLEUR RAPPORT QUALITÉ/PRIX**
        """)
    
    with col3:
        st.markdown("""
        **Premium si:**
        • Budget élevé disponible
        • Secteur hautement réglementé
        • Besoin rapidité (3-6 mois)
        • Risque à minimiser
        """)
    
    # Budget total
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); padding: 1.5rem; border-radius: 1rem; color: #78350F; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <div style='font-size: 0.9rem; font-weight: bold;'>💰 VOTRE BUDGET TOTAL DISPONIBLE</div>
                <div style='font-size: 2.5rem; font-weight: bold; margin-top: 0.5rem;'>{formater_cout(budget_info['montant'])}</div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 0.9rem; font-weight: bold;'>Obligations légales</div>
                <div style='font-size: 2rem; font-weight: bold; color: #DC2626;'>{nb_obligatoires} référentiel(s)</div>
            </div>
        </div>
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
        <h2 style='margin: 0; font-size: 1.5rem;'>🔒 Conformité</h2>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Version MVP 1.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ℹ️ À propos")
    st.info("""
    ✅ Obligations légales  
    💰 Calcul coûts réels  
    📊 Optimisation budget  
    📋 Plan d'action
    """)
    
    st.divider()
    
    st.markdown("### 📞 Support")
    st.markdown("""
    📧 contact@example.ca  
    📞 514-XXX-XXXX  
    🌐 www.example.ca
    """)
    
    st.divider()
    st.caption("© 2026")