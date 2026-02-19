"""
Module de calcul des coûts et recommandations
"""

def formater_cout(montant):
    """Formate un montant en $ CAD"""
    return f"{montant:,.0f} $".replace(',', ' ')


def calculer_economies(economies_selectionnees, economies_data):
    """
    Calcule le total des économies basé sur les éléments sélectionnés
    
    Args:
        economies_selectionnees: Liste des clés d'économies sélectionnées
        economies_data: Dictionnaire complet des économies disponibles
        
    Returns:
        int: Total des économies en $
    """
    total = 0
    for key in economies_selectionnees:
        if key in economies_data:
            total += economies_data[key]['economie']
    return total


def calculer_couts_referentiel(ref_data, total_economies):
    """
    Calcule les 3 variantes de coûts pour un référentiel
    
    Args:
        ref_data: Dictionnaire des données du référentiel
        total_economies: Total des économies calculées
        
    Returns:
        dict: Coûts minimal, standard, maximal + économies
    """
    base_cost = ref_data['baseCost']
    
    # Calculer les économies proportionnelles
    proportion = base_cost / 60000  # Référence Loi 25
    economies = min(total_economies * proportion, base_cost * 0.65)
    
    # Coût standard (après économies)
    cout_standard = base_cost - economies
    
    # Coût minimal (45% du standard = approche économique)
    cout_minimal = cout_standard * 0.45
    
    # Coût maximal (115% du coût de base = approche premium)
    cout_maximal = base_cost * 1.15
    
    return {
        'baseCost': base_cost,
        'economies': economies,
        'cout_minimal': cout_minimal,
        'cout_standard': cout_standard,
        'cout_maximal': cout_maximal,
        'economie_pct': round((economies / base_cost) * 100) if base_cost > 0 else 0
    }


def filtrer_referentiels_applicables(referentiels, profil):
    """
    Filtre les référentiels applicables selon le profil
    
    Args:
        referentiels: Dictionnaire de tous les référentiels
        profil: Dictionnaire avec secteur, infra, etc.
        
    Returns:
        tuple: (obligatoires, optionnels)
    """
    obligatoires = []
    optionnels = []
    
    has_cloud = 'cloud' in profil.get('infrastructure', []) or 'hybrid' in profil.get('infrastructure', [])
    secteur = profil.get('secteur', '')
    
    for ref_id, ref_data in referentiels.items():
        # Vérifier secteur
        if 'all' not in ref_data['sectors'] and secteur not in ref_data['sectors']:
            continue
            
        # Vérifier cloud
        if ref_data.get('cloud', False) and not has_cloud:
            continue
            
        # Ajouter aux listes appropriées
        if ref_data.get('mandatory', False):
            obligatoires.append({**ref_data, 'id': ref_id})
        else:
            optionnels.append({**ref_data, 'id': ref_id})
    
    return obligatoires, optionnels


def calculer_budget_restant(cout, budget_total):
    """
    Calcule le budget restant
    
    Args:
        cout: Coût total
        budget_total: Budget disponible
        
    Returns:
        dict: reste, depasse (bool), montant_depassement
    """
    reste = budget_total - cout
    depasse = reste < 0
    
    return {
        'reste': abs(reste),
        'depasse': depasse,
        'montant_depassement': abs(reste) if depasse else 0
    }


def generer_recommandations(obligatoires, optionnels, total_economies, budget):
    """
    Génère les recommandations complètes avec tous les calculs
    
    Args:
        obligatoires: Liste des référentiels obligatoires
        optionnels: Liste des référentiels optionnels
        total_economies: Total des économies
        budget: Budget total disponible
        
    Returns:
        dict: Recommandations complètes structurées
    """
    budget_limites = {
        'low': 50000,
        'medium': 200000,
        'high': 1000000
    }
    
    budget_montant = budget_limites.get(budget, 50000)
    
    # Calculer pour chaque obligatoire
    obligatoires_couts = []
    for ref in obligatoires:
        couts = calculer_couts_referentiel(ref, total_economies)
        obligatoires_couts.append({
            **ref,
            **couts
        })
    
    # Calculer totaux
    total_minimal = sum(r['cout_minimal'] for r in obligatoires_couts)
    total_standard = sum(r['cout_standard'] for r in obligatoires_couts)
    total_maximal = sum(r['cout_maximal'] for r in obligatoires_couts)
    
    # Budget restant pour chaque approche
    budget_minimal = calculer_budget_restant(total_minimal, budget_montant)
    budget_standard = calculer_budget_restant(total_standard, budget_montant)
    budget_maximal = calculer_budget_restant(total_maximal, budget_montant)
    
    # Calculer pour optionnels
    optionnels_couts = []
    for ref in optionnels:
        couts = calculer_couts_referentiel(ref, total_economies)
        optionnels_couts.append({
            **ref,
            **couts
        })
    
    return {
        'obligatoires': obligatoires_couts,
        'optionnels': optionnels_couts,
        'totaux': {
            'minimal': total_minimal,
            'standard': total_standard,
            'maximal': total_maximal
        },
        'budget': {
            'montant': budget_montant,
            'minimal': budget_minimal,
            'standard': budget_standard,
            'maximal': budget_maximal
        },
        'economies_totales': total_economies
    }
