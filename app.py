"""
Application Streamlit - Assistant de Conformité Cybersécurité
Version MVP Complète
"""

import streamlit as st
import json
import pandas as pd
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
.big-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1E40AF;
    margin-bottom: 0.5rem;
}
.subtitle {
    font-size: 1.2rem;
    color: #6B7280;
    margin-bottom: 2rem;
}
.info-box {
    background-color: #EFF6FF;
    border-left: 4px solid #3B82F6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.warning-box {
    background-color: #FEF3C7;
    border-left: 4px solid #F59E0B;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.success-box {
    background-color: #D1FAE5;
    border-left: 4px solid #10B981;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ==================== CHARGEMENT DONNÉES ====================
@st.cache_data
def charger_donnees():
    """Charge les données des référentiels depuis le JSON"""
    data_path = Path(__file__).parent / "data" / "referentiels.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Charger les données UNE FOIS au début
data = charger_donnees()

# ==================== INITIALISATION SESSION STATE ====================
if 'etape' not in st.session_state:
    st.session_state.etape = 1
if 'profil' not in st.session_state:
    st.session_state.profil = {}
if 'economies_selectionnees' not in st.session_state:
    st.session_state.economies_selectionnees = []

# ==================== HEADER ====================
st.markdown('<div class="big-title">🔒 Assistant de Conformité Cybersécurité</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Outil intelligent adapté à votre profil et budget</div>', unsafe_allow_html=True)

st.info("""
📊 **Sources des coûts:** Estimations basées sur des consultants canadiens/québécois (2024-2026), 
études de marché (Matayo AI, IAS Canada, Secureframe) et documents officiels (NIST, CAI Québec). 
Les coûts réels peuvent varier de ±30% selon votre contexte spécifique.
""")

# Barre de progression
progress = (st.session_state.etape - 1) / 2
st.progress(progress, text=f"Étape {st.session_state.etape}/3")

# ==================== ÉTAPE 1: PROFIL ====================
if st.session_state.etape == 1:
    st.header("📋 Étape 1: Profil de l'organisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        secteur = st.selectbox(
            "Secteur d'activité *",
            options=["", "health", "finance", "public", "tech", "retail", "other"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "health": "Santé",
                "finance": "Finance / Assurance",
                "public": "Secteur public",
                "tech": "Technologies / SaaS",
                "retail": "Commerce / Retail",
                "other": "Autre"
            }[x],
            key="secteur"
        )
        
        taille = st.selectbox(
            "Taille de l'organisation *",
            options=["", "micro", "small", "medium", "large"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "micro": "Micro (1-10 employés)",
                "small": "Petite (11-49 employés)",
                "medium": "Moyenne (50-199 employés)",
                "large": "Grande (200+ employés)"
            }[x],
            key="taille"
        )
        
        budget = st.selectbox(
            "Budget disponible pour la conformité *",
            options=["", "low", "medium", "high"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "low": "Limité (moins de 50 000$)",
                "medium": "Moyen (50 000$ - 200 000$)",
                "high": "Élevé (plus de 200 000$)"
            }[x],
            key="budget"
        )
    
    with col2:
        st.write("**Type d'infrastructure ***")
        infra_options = {
            "onprem": "Sur site (On-premise)",
            "cloud": "Cloud (AWS, Azure, GCP, etc.)",
            "hybrid": "Hybride (Mix cloud et sur site)"
        }
        
        infrastructure = []
        for key, label in infra_options.items():
            if st.checkbox(label, key=f"infra_{key}"):
                infrastructure.append(key)
        
        maturite = st.selectbox(
            "Niveau de maturité cybersécurité *",
            options=["", "initial", "managed", "defined", "optimized"],
            format_func=lambda x: {
                "": "-- Sélectionnez --",
                "initial": "Initial (peu ou pas de processus formels)",
                "managed": "Géré (quelques processus en place)",
                "defined": "Défini (processus documentés et suivis)",
                "optimized": "Optimisé (amélioration continue)"
            }[x],
            key="maturite"
        )
    
    st.divider()
    
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
    st.header("💡 Étape 2: Évaluation de l'existant")
    
    st.markdown("""
    <div class="info-box">
        <strong>💡 Astuce:</strong> Cochez tout ce que vous avez DÉJÀ en place pour réduire considérablement 
        les coûts d'implémentation! Chaque élément coché représente des économies substantielles.
    </div>
    """, unsafe_allow_html=True)
    
    # Organiser par catégorie
    economies_data = data['economies']
    
    gouvernance = {k: v for k, v in economies_data.items() if v['categorie'] == 'gouvernance'}
    securite = {k: v for k, v in economies_data.items() if v['categorie'] == 'securite'}
    processus = {k: v for k, v in economies_data.items() if v['categorie'] == 'processus'}
    
    economies_selectionnees = []
    
    # Gouvernance
    with st.expander("📋 **Gouvernance et Politiques**", expanded=True):
        for key, item in gouvernance.items():
            if st.checkbox(
                f"**{item['label']}**",
                help=f"{item['description']} | 💰 Économie: {formater_cout(item['economie'])}",
                key=f"eco_{key}"
            ):
                economies_selectionnees.append(key)
                st.caption(f"✅ Économie: {formater_cout(item['economie'])}")
    
    # Sécurité
    with st.expander("🔒 **Sécurité Technique**", expanded=True):
        for key, item in securite.items():
            if st.checkbox(
                f"**{item['label']}**",
                help=f"{item['description']} | 💰 Économie: {formater_cout(item['economie'])}",
                key=f"eco_{key}"
            ):
                economies_selectionnees.append(key)
                st.caption(f"✅ Économie: {formater_cout(item['economie'])}")
    
    # Processus
    with st.expander("⚙️ **Processus et Procédures**", expanded=True):
        for key, item in processus.items():
            if st.checkbox(
                f"**{item['label']}**",
                help=f"{item['description']} | 💰 Économie: {formater_cout(item['economie'])}",
                key=f"eco_{key}"
            ):
                economies_selectionnees.append(key)
                st.caption(f"✅ Économie: {formater_cout(item['economie'])}")
    
    # Calcul total
    total_economies = calculer_economies(economies_selectionnees, economies_data)
    
    # Affichage total
    st.divider()
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.metric("💰 Économies totales estimées", formater_cout(total_economies))
    with col2:
        st.metric("Éléments cochés", len(economies_selectionnees))
    with col3:
        pct = round((total_economies / 170000) * 100) if total_economies > 0 else 0
        st.metric("% du maximum", f"{pct}%")
    
    st.caption("💡 Économies maximales possibles: 170 000$ (si tous les éléments sont cochés)")
    
    st.divider()
    
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
    st.header("📊 Vos recommandations personnalisées")
    
    # Récupérer données
    profil = st.session_state.profil
    economies_sel = st.session_state.economies_selectionnees
    
    # Calculer économies
    total_economies = calculer_economies(economies_sel, data['economies'])
    
    # Filtrer référentiels
    obligatoires, optionnels = filtrer_referentiels_applicables(data['referentiels'], profil)
    
    # Générer recommandations
    recommandations = generer_recommandations(obligatoires, optionnels, total_economies, profil['budget'])
    
    # Afficher profil résumé
    st.subheader("📋 Votre profil")
    col1, col2, col3, col4 = st.columns(4)
    
    secteur_labels = {
        "health": "Santé", "finance": "Finance", "public": "Public",
        "tech": "Technologies", "retail": "Commerce", "other": "Autre"
    }
    taille_labels = {
        "micro": "Micro (1-10)", "small": "Petite (11-49)",
        "medium": "Moyenne (50-199)", "large": "Grande (200+)"
    }
    
    with col1:
        st.metric("Secteur", secteur_labels.get(profil['secteur'], profil['secteur']))
    with col2:
        st.metric("Taille", taille_labels.get(profil['taille'], profil['taille']))
    with col3:
        st.metric("Budget disponible", formater_cout(recommandations['budget']['montant']))
    with col4:
        st.metric("Économies réalisées", formater_cout(total_economies))
    
    st.divider()
    
    # Vue d'ensemble
    st.subheader("📊 Vue d'ensemble - 3 approches")
    
    st.markdown("""
    <div class="info-box">
        <strong>💡 Choisissez votre approche:</strong> Nous vous proposons 3 niveaux d'investissement selon vos besoins et contraintes.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    totaux = recommandations['totaux']
    budget_info = recommandations['budget']
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>💰 Approche ÉCONOMIQUE</div>
            <div style='font-size: 2rem; font-weight: bold;'>{formater_cout(totaux['minimal'])}</div>
            <div style='font-size: 0.8rem; margin-top: 0.5rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['minimal']['reste']) if not budget_info['minimal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['minimal']['montant_depassement'])}
            </div>
            <div style='font-size: 0.7rem; margin-top: 0.5rem; opacity: 0.9;'>Travail interne, templates gratuits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center; border: 3px solid #1e40af;'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>⭐ Approche RECOMMANDÉE</div>
            <div style='font-size: 2.5rem; font-weight: bold;'>{formater_cout(totaux['standard'])}</div>
            <div style='font-size: 0.8rem; margin-top: 0.5rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['standard']['reste']) if not budget_info['standard']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['standard']['montant_depassement'])}
            </div>
            <div style='font-size: 0.7rem; margin-top: 0.5rem; opacity: 0.9;'>Mix interne/externe, MEILLEUR ROI</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>🏆 Approche PREMIUM</div>
            <div style='font-size: 2rem; font-weight: bold;'>{formater_cout(totaux['maximal'])}</div>
            <div style='font-size: 0.8rem; margin-top: 0.5rem;'>
                {'✓ Reste: ' + formater_cout(budget_info['maximal']['reste']) if not budget_info['maximal']['depasse'] 
                 else '⚠️ Dépasse: ' + formater_cout(budget_info['maximal']['montant_depassement'])}
            </div>
            <div style='font-size: 0.7rem; margin-top: 0.5rem; opacity: 0.9;'>Consultants seniors, outils premium</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Obligations
    if recommandations['obligatoires']:
        st.subheader("⚠️ À IMPLÉMENTER MAINTENANT - Obligations légales")
        
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Attention:</strong> Ces référentiels sont OBLIGATOIRES selon votre profil. 
            Ne pas les implémenter expose votre organisation à des risques légaux et financiers importants.
        </div>
        """, unsafe_allow_html=True)
        
        for idx, ref in enumerate(recommandations['obligatoires'], 1):
            with st.expander(f"**{idx}. {ref['name']}** - {ref['description']}", expanded=True):
                
                # 3 colonnes pour les 3 approches
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**💰 ÉCONOMIQUE**")
                    st.metric("Coût", formater_cout(ref['cout_minimal']))
                    st.markdown("""
                    **✓ Ce qui EST inclus:**
                    - Travail 100% interne
                    - Templates gratuits
                    - Outils gratuits (Excel)
                    - Formation en ligne
                    - ÉFVP simplifiées
                    
                    **⚠️ Risque:** Plus de temps requis
                    """)
                
                with col2:
                    st.markdown("**⭐ RECOMMANDÉE**")
                    st.metric("Coût", formater_cout(ref['cout_standard']))
                    st.markdown("""
                    **✓ Ce qui EST inclus:**
                    - Consultant GAP analysis
                    - Mix 60% interne / 40% externe
                    - Outils standards
                    - Formation mixte
                    - ÉFVP 2-3 processus
                    - Documentation complète
                    
                    **✓ MEILLEUR ROI**
                    """)
                
                with col3:
                    st.markdown("**🏆 PREMIUM**")
                    st.metric("Coût", formater_cout(ref['cout_maximal']))
                    st.markdown("""
                    **✓ Ce qui EST inclus:**
                    - Consultants seniors
                    - Outils premium
                    - Formation sur mesure
                    - ÉFVP tous processus
                    - Audits externes
                    - Support 12 mois
                    
                    **→ Pour:** Grandes organisations
                    """)
                
                # Tableau comparatif
                st.markdown("##### 📊 Comparaison détaillée")
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
    
    # Optionnels
    if recommandations['optionnels']:
        st.divider()
        st.subheader("💡 Recommandations pour plus tard - Non obligatoires")
        
        st.markdown("""
        <div class="info-box">
            <strong>💡 Ces référentiels ne sont pas obligatoires</strong> mais fortement recommandés pour améliorer votre posture de sécurité.
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(2)
        for idx, ref in enumerate(recommandations['optionnels']):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style='background: #EFF6FF; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #3B82F6; margin-bottom: 1rem;'>
                        <h4 style='color: #1E40AF; margin: 0 0 0.5rem 0;'>{ref['name']}</h4>
                        <p style='color: #6B7280; font-size: 0.9rem; margin: 0 0 0.5rem 0;'>{ref['description']}</p>
                        <p style='font-size: 1.2rem; font-weight: bold; color: #3B82F6; margin: 0;'>
                            Coût: {formater_cout(ref['cout_standard'])}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Prochaines étapes
    st.divider()
    st.subheader("🎯 Prochaines étapes recommandées")
    
    st.markdown(f"""
    **1. Validation budgétaire** - Budget recommandé: **{formater_cout(totaux['standard'])}**
    
    **2. Sélection consultants** - Obtenir 2-3 soumissions
    
    **3. Planification** - Calendrier 6-9 mois
    
    **4. Formation équipe** - Former 1-2 personnes clés
    
    **5. Lancement** - Débuter par analyse GAP
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Recommencer", use_container_width=True):
            st.session_state.etape = 1
            st.session_state.profil = {}
            st.session_state.economies_selectionnees = []
            st.rerun()
    
    with col2:
        csv_data = pd.DataFrame(recommandations['obligatoires']).to_csv(index=False)
        st.download_button(
            label="📥 Télécharger rapport (CSV)",
            data=csv_data,
            file_name=f"recommandations_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 📊 Assistant Conformité")
    st.markdown("**Version MVP 1.0**")
    st.caption(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}")
    
    st.divider()
    
    st.markdown("### ℹ️ À propos")
    st.info("""
    Cet outil vous aide à:
    - ✅ Identifier obligations légales
    - 💰 Calculer coûts réels
    - 📊 Optimiser budget
    - 📋 Planifier implémentation
    """)
    
    st.divider()
    
    st.markdown("### 📞 Support")
    st.markdown("""
    📧 contact@votre-entreprise.ca  
    📞 514-XXX-XXXX  
    🌐 www.votre-site.ca
    """)
    
    st.divider()
    st.caption(f"© 2026 - Tous droits réservés")