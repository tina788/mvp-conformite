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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center;'>
            <div style='font-size: 1rem;'>💰 ÉCONOMIQUE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['minimal'])}</div>
            <div style='font-size: 0.9rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['minimal']['montant_depassement'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center; border: 3px solid #1e40af;'>
            <div style='font-size: 1rem;'>⭐ RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['standard'])}</div>
            <div style='font-size: 0.9rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['standard']['montant_depassement'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); 
                    padding: 2rem; border-radius: 1rem; color: white; text-align: center;'>
            <div style='font-size: 1rem;'>🏆 PREMIUM</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['maximal'])}</div>
            <div style='font-size: 0.9rem;'>
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
            <strong>⚠️ Attention:</strong> Ces référentiels sont OBLIGATOIRES.
        </div>
        """, unsafe_allow_html=True)
        
        for idx, ref in enumerate(recommandations['obligatoires'], 1):
            st.markdown(f"""
            <div class="ref-card">
                <h3 style='margin: 0 0 0.5rem 0;'>{idx}. {ref['name']} 
                <span class='badge badge-mandatory'>⚠️ OBLIGATOIRE</span></h3>
                <p style='color: #6B7280;'>{ref['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 💵 CHOIX D'APPROCHES - Quel investissement?")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='background: #DEF7EC; padding: 1rem; border-radius: 0.5rem; border: 2px solid #10B981;'>
                    <div style='text-align: center; background: #10B981; color: white; padding: 0.5rem; border-radius: 0.3rem; margin-bottom: 0.5rem;'>
                        <div style='font-size: 0.8rem;'>💰 APPROCHE ÉCONOMIQUE</div>
                        <div style='font-size: 1.8rem; font-weight: bold;'>{formater_cout(ref['cout_minimal'])}</div>
                    </div>
                    <div style='font-size: 0.85rem;'>
                        <strong>✓ Ce qui EST inclus:</strong><br>
                        • Travail 100% interne<br>
                        • Templates gratuits<br>
                        • Outils Excel/Google<br>
                        • Formation en ligne<br>
                        • ÉFVP simplifiées<br><br>
                        <strong style='color: #F59E0B;'>✗ Ce qui MANQUE:</strong><br>
                        • Consultants externes<br>
                        • Outils automatisés<br>
                        • Formation présentielle<br>
                        • Audits externes<br><br>
                        <strong style='color: #EF4444;'>⚠️ Risque:</strong> Plus de temps requis
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: #DBEAFE; padding: 1rem; border-radius: 0.5rem; border: 2px solid #3B82F6;'>
                    <div style='text-align: center; background: #3B82F6; color: white; padding: 0.5rem; border-radius: 0.3rem; margin-bottom: 0.5rem;'>
                        <div style='font-size: 0.8rem;'>⭐ APPROCHE RECOMMANDÉE</div>
                        <div style='font-size: 1.8rem; font-weight: bold;'>{formater_cout(ref['cout_standard'])}</div>
                    </div>
                    <div style='font-size: 0.85rem;'>
                        <strong>✓ Ce qui EST inclus:</strong><br>
                        • Consultant GAP analysis<br>
                        • Mix interne/externe<br>
                        • Outils standards<br>
                        • Formation mixte<br>
                        • ÉFVP 2-3 processus<br>
                        • Documentation complète<br><br>
                        <strong style='color: #10B981;'>💡 Pourquoi:</strong><br>
                        • Équilibre optimal<br>
                        • Expertise ciblée<br>
                        • Conformité solide<br><br>
                        <strong style='color: #10B981;'>✓ MEILLEUR ROI</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='background: #F3E8FF; padding: 1rem; border-radius: 0.5rem; border: 2px solid #A855F7;'>
                    <div style='text-align: center; background: #A855F7; color: white; padding: 0.5rem; border-radius: 0.3rem; margin-bottom: 0.5rem;'>
                        <div style='font-size: 0.8rem;'>🏆 APPROCHE PREMIUM</div>
                        <div style='font-size: 1.8rem; font-weight: bold;'>{formater_cout(ref['cout_maximal'])}</div>
                    </div>
                    <div style='font-size: 0.85rem;'>
                        <strong>✓ Ce qui EST inclus:</strong><br>
                        • Consultants seniors<br>
                        • Outils premium<br>
                        • Formation sur mesure<br>
                        • ÉFVP tous processus<br>
                        • Audits complets<br>
                        • Support 12 mois<br>
                        • Certification<br><br>
                        <strong style='color: #A855F7;'>💎 Avantages:</strong><br>
                        • Plus rapide<br>
                        • Risque minimal<br>
                        • Excellence garantie
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
            
            # DÉTAILS: Ce qui doit être mis en place
            with st.expander("📋 **DÉTAILS: Ce qui doit être mis en place** (cliquez pour voir)", expanded=False):
                st.markdown("""
                **⚠️ Version minimale:**
                • Consultants externes → Travail interne
                • Formation complète → Formation de base
                • Outils automatisés → Excel et documents
                • À compléter dans 6-12 mois
                
                **⭐ Version recommandée:**
                • Mix 60% interne / 40% externe
                • Consultant pour GAP analysis initiale
                • Outils standards de conformité
                • Formation mixte (en ligne + présentiel)
                • ÉFVP sur 2-3 processus critiques
                • À compléter dans 4-6 mois
                
                **🏆 Version premium:**
                • Consultants seniors dédiés
                • Outils automatisés premium
                • Formation sur mesure présentielle
                • ÉFVP approfondies tous processus
                • Audits externes complets
                • Support continu 12 mois
                • À compléter dans 3-4 mois
                """)
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    # RÉSUMÉ TOTAL
    st.markdown("---")
    st.markdown("## 💰 RÉSUMÉ: TOTAL À INVESTIR MAINTENANT")
    
    nb_obligatoires = len(recommandations['obligatoires'])
    
    st.markdown(f"**{nb_obligatoires} référentiel(s) obligatoire(s) - Choisissez votre approche**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>💰 Approche ÉCONOMIQUE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['minimal'])}</div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 0.3rem; margin-top: 0.5rem;'>
                {'✓ RESTE: ' + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['minimal']['montant_depassement'])}
            </div>
            <div style='font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.9;'>Travail interne, templates gratuits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center; border: 3px solid #1E40AF;'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>⭐ Approche RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['standard'])}</div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 0.3rem; margin-top: 0.5rem;'>
                {'✓ RESTE: ' + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['standard']['montant_depassement'])}
            </div>
            <div style='font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.9;'>Mix interne/externe, meilleur ROI</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #A855F7 0%, #9333EA 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>🏆 Approche PREMIUM</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['maximal'])}</div>
            <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 0.3rem; margin-top: 0.5rem;'>
                {'✓ RESTE: ' + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['maximal']['montant_depassement'])}
            </div>
            <div style='font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.9;'>Consultants seniors, outils premium</div>
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
    <div style='background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); padding: 1.5rem; border-radius: 1rem; color: #78350F;'>
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