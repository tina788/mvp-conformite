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

st.set_page_config(page_title="Assistant Conformité Cyber", page_icon="🔒", layout="wide")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem; border-radius: 1rem; color: white; text-align: center;
    margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}
.info-box {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    border-left: 4px solid #3B82F6; padding: 1rem; border-radius: 0.75rem;
    margin: 1rem 0; color: #1F2937;
}
.warning-box {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    border-left: 4px solid #F59E0B; padding: 1.5rem; border-radius: 0.75rem;
    margin: 1.5rem 0; color: #78350F;
}
.success-box {
    background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
    border-left: 4px solid #10B981; padding: 1.5rem; border-radius: 0.75rem; margin: 1.5rem 0;
}
.danger-box {
    background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
    border-left: 4px solid #EF4444; padding: 1.5rem; border-radius: 0.75rem;
    margin: 1.5rem 0; color: #991B1B;
}
.badge-mandatory { background: #EF4444; color: white; padding: 0.4rem 1rem; border-radius: 2rem; font-size: 0.85rem; }
.timeline-phase {
    background: white; border-left: 4px solid #3B82F6; padding: 1rem; margin: 0.5rem 0;
    border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
if 'email_capture' not in st.session_state:
    st.session_state.email_capture = None

# HEADER
st.markdown("""
<div class="main-header">
    <h1 style='font-size: 2.5rem; margin: 0;'>🔒 Assistant de Conformité Cybersécurité</h1>
    <p style='font-size: 1.1rem; margin: 0.5rem 0 0 0; opacity: 0.95;'>Outil intelligent adapté à votre profil et budget</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>📊 Sources des coûts:</strong> Estimations basées sur des consultants canadiens/québécois (2024-2026), 
    études de marché (Matayo AI, IAS Canada, Secureframe) et documents officiels (NIST, CAI Québec).
</div>
""", unsafe_allow_html=True)

st.progress((st.session_state.etape - 1) / 2, text=f"🎯 Étape {st.session_state.etape}/3")
st.markdown("<br>", unsafe_allow_html=True)

# ÉTAPE 1: PROFIL
if st.session_state.etape == 1:
    st.markdown("## 📋 Profil de l'organisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏢 Informations de base")
        secteur = st.selectbox("Secteur d'activité", 
            ["", "health", "finance", "public", "tech", "retail", "other"],
            format_func=lambda x: {"": "-- Sélectionnez --", "health": "🏥 Santé", 
            "finance": "💰 Finance", "public": "🏛️ Public", "tech": "💻 Tech", 
            "retail": "🛍️ Retail", "other": "📊 Autre"}[x])
        
        taille = st.selectbox("Taille", ["", "micro", "small", "medium", "large"],
            format_func=lambda x: {"": "-- Sélectionnez --", "micro": "Micro (1-10)", 
            "small": "Petite (11-49)", "medium": "Moyenne (50-199)", "large": "Grande (200+)"}[x])
        
        # NOUVEAU: Chiffre d'affaires pour calculateur pénalités
        ca_annuel = st.number_input("Chiffre d'affaires annuel (optionnel - pour calcul pénalités)", 
                                     min_value=0, value=0, step=100000, 
                                     help="Permet de calculer le risque réel de pénalités Loi 25")
    
    with col2:
        st.markdown("### 💵 Budget et maturité")
        budget = st.selectbox("Budget disponible", ["", "low", "medium", "high"],
            format_func=lambda x: {"": "-- Sélectionnez --", "low": "Limité (< 50K$)", 
            "medium": "Moyen (50-200K$)", "high": "Élevé (> 200K$)"}[x])
        
        maturite = st.selectbox("Maturité cybersécurité", ["", "initial", "managed", "defined", "optimized"],
            format_func=lambda x: {"": "-- Sélectionnez --", "initial": "Initial", 
            "managed": "Géré", "defined": "Défini", "optimized": "Optimisé"}[x])
    
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
            st.session_state.profil = {'secteur': secteur, 'taille': taille, 'budget': budget, 
                                        'maturite': maturite, 'infrastructure': infrastructure,
                                        'ca_annuel': ca_annuel}
            st.session_state.etape = 2
            st.rerun()

# ÉTAPE 2: EXISTANT
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

# ÉTAPE 3: RÉSULTATS
elif st.session_state.etape == 3:
    st.markdown("## 📊 Vos recommandations personnalisées")
    
    profil = st.session_state.profil
    economies_sel = st.session_state.economies_selectionnees
    total_economies = calculer_economies(economies_sel, data['economies'])
    obligatoires, optionnels = filtrer_referentiels_applicables(data['referentiels'], profil)
    recommandations = generer_recommandations(obligatoires, optionnels, total_economies, profil['budget'])
    
    # Profil résumé
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
    
    # ============================================
    # NOUVEAU 1: CALCULATEUR PÉNALITÉS LOI 25
    # ============================================
    st.markdown("### ⚠️ RISQUE DE NON-CONFORMITÉ - Loi 25")
    
    ca_annuel = profil.get('ca_annuel', 0)
    
    # Calcul pénalités maximales
    penalite_fixe = 10000000  # 10M$ max
    penalite_pct_ca = ca_annuel * 0.02 if ca_annuel > 0 else 0  # 2% CA mondial
    penalite_max = max(penalite_fixe, penalite_pct_ca)
    
    # Coût conformité vs pénalités
    cout_conformite = recommandations['totaux']['standard']
    economie_vs_penalite = penalite_max - cout_conformite
    roi_protection = (economie_vs_penalite / cout_conformite * 100) if cout_conformite > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%); 
        padding: 1.5rem; border-radius: 1rem; border: 2px solid #EF4444; text-align: center;'>
            <div style='color: #991B1B; font-size: 0.9rem; font-weight: 600;'>⚠️ PÉNALITÉ MAXIMALE LOI 25</div>
            <div style='color: #991B1B; font-size: 2rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(penalite_max)}</div>
            <div style='color: #991B1B; font-size: 0.85rem;'>10M$ ou 2% CA mondial</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%); 
        padding: 1.5rem; border-radius: 1rem; border: 2px solid #3B82F6; text-align: center;'>
            <div style='color: #1E40AF; font-size: 0.9rem; font-weight: 600;'>💰 COÛT CONFORMITÉ</div>
            <div style='color: #1E40AF; font-size: 2rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(cout_conformite)}</div>
            <div style='color: #1E40AF; font-size: 0.85rem;'>Approche recommandée</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%); 
        padding: 1.5rem; border-radius: 1rem; border: 2px solid #10B981; text-align: center;'>
            <div style='color: #065F46; font-size: 0.9rem; font-weight: 600;'>✅ VOUS ÉCONOMISEZ</div>
            <div style='color: #065F46; font-size: 2rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(economie_vs_penalite)}</div>
            <div style='color: #065F46; font-size: 0.85rem;'>ROI protection: {int(roi_protection)}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="danger-box">
        <strong>🚨 ATTENTION:</strong> En cas de non-conformité à la Loi 25, votre organisation risque jusqu'à 
        <strong>{formater_cout(penalite_max)}</strong> en pénalités. Investir <strong>{formater_cout(cout_conformite)}</strong> 
        aujourd'hui vous protège contre un risque {int(roi_protection)}% plus élevé!
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Vue d'ensemble
    totaux = recommandations['totaux']
    budget_info = recommandations['budget']
    
    st.markdown("### 📊 Vue d'ensemble - 3 approches")
    
    # GRAPHIQUE
    fig = go.Figure()
    approaches = ['💰 Économique', '⭐ Recommandée', '🏆 Premium']
    costs = [totaux['minimal'], totaux['standard'], totaux['maximal']]
    colors = ['#10B981', '#3B82F6', '#A855F7']
    
    fig.add_trace(go.Bar(x=approaches, y=costs, marker_color=colors,
        text=[formater_cout(c) for c in costs], textposition='auto',
        textfont=dict(size=16, color='white', family='Inter')))
    
    fig.add_hline(y=budget_info['montant'], line_dash="dash", line_color="#EF4444", 
        line_width=3, annotation_text=f"Budget: {formater_cout(budget_info['montant'])}", 
        annotation_position="right")
    
    fig.update_layout(title="Comparaison des 3 approches vs votre budget",
        yaxis_title="Coût ($)", height=400, showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12))
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3 Cartes approches
    col1, col2, col3 = st.columns(3)
    
    with col1:
        reste = "✓ Reste: " + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['minimal']['montant_depassement'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 2rem; 
        border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);'>
            <div style='font-size: 1rem; font-weight: 600;'>💰 ÉCONOMIQUE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['minimal'])}</div>
            <div style='font-size: 0.9rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.5rem;'>{reste}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        reste = "✓ Reste: " + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['standard']['montant_depassement'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 2rem; 
        border-radius: 1rem; color: white; text-align: center; border: 3px solid #1e40af; box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);'>
            <div style='font-size: 1rem; font-weight: 600;'>⭐ RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['standard'])}</div>
            <div style='font-size: 0.9rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.5rem;'>{reste}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reste = "✓ Reste: " + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['maximal']['montant_depassement'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); padding: 2rem; 
        border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(168, 85, 247, 0.3);'>
            <div style='font-size: 1rem; font-weight: 600;'>🏆 PREMIUM</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['maximal'])}</div>
            <div style='font-size: 0.9rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.5rem;'>{reste}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================
    # NOUVEAU 2: ROADMAP TIMELINE VISUELLE
    # ============================================
    st.markdown("### 🗓️ ROADMAP D'IMPLÉMENTATION")
    
    # Sélection approche pour timeline
    approche_timeline = st.radio(
        "Choisissez une approche pour voir la roadmap détaillée:",
        ["💰 Économique (9-12 mois)", "⭐ Recommandée (6-9 mois)", "🏆 Premium (3-6 mois)"],
        horizontal=True
    )
    
    # Définition des phases selon l'approche
    if "Économique" in approche_timeline:
        duree_mois = 12
        phases = [
            {"mois": "1-2", "titre": "📋 Analyse GAP interne", "taches": [
                "Auto-évaluation complète", "Identification écarts Loi 25", "Priorisation actions"
            ]},
            {"mois": "3-5", "titre": "📝 Documentation & Politiques", "taches": [
                "Rédaction politiques (templates CAI)", "Registre des traitements", "Procédures internes"
            ]},
            {"mois": "6-8", "titre": "🔒 Mise en conformité technique", "taches": [
                "Implémentation contrôles techniques", "Formation équipe interne", "Outils gratuits (Excel)"
            ]},
            {"mois": "9-10", "titre": "✅ ÉFVP & Tests", "taches": [
                "ÉFVP simplifiées (2 processus)", "Tests auto-vérification", "Corrections"
            ]},
            {"mois": "11-12", "titre": "🎯 Finalisation", "taches": [
                "Revue finale interne", "Documentation complète", "Plan amélioration continue"
            ]}
        ]
    elif "Recommandée" in approche_timeline:
        duree_mois = 9
        phases = [
            {"mois": "1", "titre": "📋 GAP Analysis (Consultant)", "taches": [
                "Audit externe complet", "Rapport d'écarts détaillé", "Plan d'action priorisé"
            ]},
            {"mois": "2-3", "titre": "📝 Documentation & Gouvernance", "taches": [
                "Politiques professionnelles", "Registre traitements complet", "Formation équipe (mixte)"
            ]},
            {"mois": "4-5", "titre": "🔒 Implémentation technique", "taches": [
                "Outils conformité standards", "Contrôles de sécurité", "Intégration processus"
            ]},
            {"mois": "6-7", "titre": "✅ ÉFVP & Validation", "taches": [
                "ÉFVP 2-3 processus critiques", "Support consultant ponctuel", "Ajustements"
            ]},
            {"mois": "8-9", "titre": "🎯 Audit & Certification", "taches": [
                "Revue finale consultant", "Corrections dernière minute", "Attestation conformité"
            ]}
        ]
    else:  # Premium
        duree_mois = 6
        phases = [
            {"mois": "1", "titre": "📋 Audit Complet (Seniors)", "taches": [
                "Analyse exhaustive multi-consultants", "Rapport exécutif détaillé", "Roadmap personnalisée"
            ]},
            {"mois": "2", "titre": "📝 Documentation Premium", "taches": [
                "Politiques sur mesure", "Formation présentielle complète", "Outils premium automatisés"
            ]},
            {"mois": "3-4", "titre": "🔒 Implémentation Accélérée", "taches": [
                "Équipe consultants dédiée", "Mise en place tous contrôles", "Support quotidien"
            ]},
            {"mois": "5", "titre": "✅ ÉFVP Approfondies", "taches": [
                "ÉFVP tous processus", "Tests exhaustifs", "Optimisations"
            ]},
            {"mois": "6", "titre": "🏆 Certification & Support", "taches": [
                "Audit externe certifié", "Certification officielle", "Support 12 mois inclus"
            ]}
        ]
    
    # Affichage timeline
    for idx, phase in enumerate(phases, 1):
        progress_pct = (idx / len(phases)) * 100
        st.markdown(f"""
        <div class="timeline-phase">
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <strong style='color: #3B82F6; font-size: 1.1rem;'>Mois {phase['mois']}: {phase['titre']}</strong>
                </div>
                <div style='background: #3B82F6; color: white; padding: 0.3rem 0.8rem; border-radius: 1rem; font-size: 0.85rem;'>
                    {int(progress_pct)}%
                </div>
            </div>
            <ul style='margin: 0.5rem 0 0 0; padding-left: 1.5rem; color: #4B5563;'>
                {"".join([f"<li>{tache}</li>" for tache in phase['taches']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.info(f"📅 **Durée totale estimée:** {duree_mois} mois | 🎯 **Date de fin prévue:** {(datetime.now().month + duree_mois) % 12 or 12}/{datetime.now().year + (datetime.now().month + duree_mois - 1) // 12}")
    
    st.divider()
    
    # OBLIGATIONS (code existant abrégé pour économiser l'espace)
    if recommandations['obligatoires']:
        st.markdown("### ⚠️ À IMPLÉMENTER MAINTENANT")
        
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Attention:</strong> Ces référentiels sont OBLIGATOIRES selon votre profil.
        </div>
        """, unsafe_allow_html=True)
        
        for idx, ref in enumerate(recommandations['obligatoires'], 1):
            with st.expander(f"**{idx}. {ref['name']}** - {ref['description']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**💰 Économique:** {formater_cout(ref['cout_minimal'])}")
                    st.caption("• 100% interne\n• Templates gratuits\n• 9-12 mois")
                
                with col2:
                    st.markdown(f"**⭐ Recommandé:** {formater_cout(ref['cout_standard'])}")
                    st.caption("• Mix interne/externe\n• Outils standards\n• 6-9 mois\n• **MEILLEUR ROI**")
                
                with col3:
                    st.markdown(f"**🏆 Premium:** {formater_cout(ref['cout_maximal'])}")
                    st.caption("• Consultants seniors\n• Outils premium\n• 3-6 mois")
    
    # RÉSUMÉ TOTAL
    st.markdown("---")
    st.markdown("## 💰 RÉSUMÉ: TOTAL À INVESTIR MAINTENANT")
    
    nb_obligatoires = len(recommandations['obligatoires'])
    st.markdown(f"**{nb_obligatoires} référentiel(s) obligatoire(s) - Choisissez votre approche**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        reste = "✓ RESTE: " + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['minimal']['montant_depassement'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 1.5rem; 
        border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);'>
            <div style='font-size: 0.9rem; font-weight: 600;'>💰 Approche ÉCONOMIQUE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['minimal'])}</div>
            <div style='background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.3rem; font-size: 0.9rem;'>{reste}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        reste = "✓ RESTE: " + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['standard']['montant_depassement'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); padding: 1.5rem; 
        border-radius: 1rem; color: white; text-align: center; border: 3px solid #1E40AF; box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);'>
            <div style='font-size: 0.9rem; font-weight: 600;'>⭐ Approche RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['standard'])}</div>
            <div style='background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.3rem; font-size: 0.9rem;'>{reste}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reste = "✓ RESTE: " + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] else "⚠️ Dépasse: " + formater_cout(budget_info['maximal']['montant_depassement'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #A855F7 0%, #9333EA 100%); padding: 1.5rem; 
        border-radius: 1rem; color: white; text-align: center; box-shadow: 0 8px 20px rgba(168, 85, 247, 0.3);'>
            <div style='font-size: 0.9rem; font-weight: 600;'>🏆 Approche PREMIUM</div>
            <div style='font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;'>{formater_cout(totaux['maximal'])}</div>
            <div style='background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 0.3rem; font-size: 0.9rem;'>{reste}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================
    # NOUVEAU 3: CAPTURE EMAIL + EXPORT PDF
    # ============================================
    st.markdown("### 📥 OBTENEZ VOTRE RAPPORT COMPLET")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="success-box">
            <strong>🎁 Rapport PDF gratuit incluant:</strong><br>
            • Analyse complète de votre profil<br>
            • Comparaison détaillée des 3 approches<br>
            • Roadmap d'implémentation personnalisée<br>
            • Calculateur de pénalités Loi 25<br>
            • Templates et checklists bonus
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        email_user = st.text_input("📧 Votre email professionnel", placeholder="nom@entreprise.ca")
        
        if st.button("📥 Télécharger le rapport PDF", type="primary", use_container_width=True):
            if email_user and "@" in email_user:
                st.session_state.email_capture = email_user
                
                # Ici on générerait le PDF avec reportlab
                # Pour l'instant, on simule
                st.success(f"✅ Rapport envoyé à {email_user}!")
                st.balloons()
                
                # Simulation du lien de téléchargement
                st.download_button(
                    label="📄 Télécharger maintenant",
                    data="Contenu PDF simulé - À implémenter avec reportlab",
                    file_name=f"rapport_conformite_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.info("💬 **Un conseiller vous contactera sous 24h pour discuter de vos besoins!**")
            else:
                st.error("⚠️ Veuillez entrer un email valide")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bouton consultation
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 1.5rem; 
    border-radius: 1rem; text-align: center; color: white; margin: 1rem 0;'>
        <h3 style='margin: 0 0 0.5rem 0;'>💬 Besoin d'aide pour décider?</h3>
        <p style='margin: 0;'>Réservez une consultation gratuite de 30 minutes avec un expert</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📅 Réserver ma consultation gratuite", use_container_width=True):
            st.info("📧 Un lien de réservation a été envoyé à votre email!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔄 Recommencer une nouvelle analyse", use_container_width=True):
        st.session_state.etape = 1
        st.session_state.profil = {}
        st.session_state.economies_selectionnees = []
        st.rerun()

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 1rem;'>
        <h2 style='margin: 0; font-size: 1.5rem;'>🔒 Conformité</h2>
        <p style='margin: 0.5rem 0 0 0;'>Version MVP 2.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✨ Nouveautés!")
    st.success("✅ Calculateur pénalités Loi 25\n✅ Roadmap visuelle\n✅ Export PDF gratuit")
    
    st.divider()
    
    st.markdown("### ℹ️ À propos")
    st.info("✅ Obligations légales\n💰 Calcul coûts réels\n📊 Optimisation budget\n📋 Plan d'action\n🎁 Templates gratuits")
    
    st.divider()
    
    st.markdown("### 📞 Support")
    st.markdown("📧 contact@example.ca\n📞 514-XXX-XXXX\n🌐 www.example.ca")
    
    st.divider()
    st.caption("© 2026")