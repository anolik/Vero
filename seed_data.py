"""Textes pré-rédigés pour les 5 catégories de contenu.

Chaque catégorie a 3 variantes:
  1 = Professionnel (ton formel et institutionnel)
  2 = Chaleureux (ton personnel et accessible)
  3 = Concis (direct et efficace)

Catégories:
  biography      — Biographie / À propos
  services       — Services offerts
  client_approach — Approche client
  credentials    — Titres et accréditations
  legal          — Mentions légales et divulgations
"""

TEXT_TEMPLATES = [
    # ── Biographie / À propos ──────────────────────────────────────────
    {
        "category": "biography",
        "variant": 1,
        "title": "Biographie — Professionnel",
        "content": (
            "Fort d'une solide expérience dans le domaine des services financiers, "
            "je me consacre à accompagner mes clients dans l'atteinte de leurs objectifs "
            "financiers. Mon parcours m'a permis de développer une expertise approfondie "
            "en investissement dans les fonds communs de placement et en assurance de personnes. "
            "Je m'engage à offrir un service personnalisé, fondé sur une analyse rigoureuse "
            "et une compréhension fine des besoins de chaque client."
        ),
    },
    {
        "category": "biography",
        "variant": 2,
        "title": "Biographie — Chaleureux",
        "content": (
            "Passionné par les finances personnelles depuis toujours, j'ai choisi ce métier "
            "pour une raison simple : aider les gens à réaliser leurs rêves. Que ce soit pour "
            "planifier la retraite, protéger votre famille ou faire fructifier votre épargne, "
            "je suis là pour vous guider à chaque étape. Mon approche se veut humaine et "
            "accessible, parce que je crois que tout le monde mérite un accompagnement "
            "financier de qualité."
        ),
    },
    {
        "category": "biography",
        "variant": 3,
        "title": "Biographie — Concis",
        "content": (
            "Représentant en services financiers spécialisé en fonds communs de placement "
            "et en assurance de personnes. J'aide mes clients à protéger et faire croître "
            "leur patrimoine grâce à des solutions adaptées à leur réalité."
        ),
    },
    # ── Services offerts ────────────────────────────────────────────────
    {
        "category": "services",
        "variant": 1,
        "title": "Services — Professionnel",
        "content": (
            "Je propose une gamme complète de services financiers conçus pour répondre "
            "à l'ensemble de vos besoins :\n\n"
            "• Fonds communs de placement — Sélection et suivi de portefeuilles diversifiés "
            "adaptés à votre profil d'investisseur et à vos horizons de placement.\n"
            "• Assurance de personnes — Solutions d'assurance vie, invalidité et maladies "
            "graves pour protéger votre famille et votre patrimoine.\n"
            "• Planification financière — Élaboration de stratégies globales intégrant "
            "épargne, fiscalité et planification de la retraite.\n"
            "• Planification successorale — Conseils pour assurer un transfert de patrimoine "
            "efficace et conforme à vos volontés."
        ),
    },
    {
        "category": "services",
        "variant": 2,
        "title": "Services — Chaleureux",
        "content": (
            "Mon rôle, c'est de simplifier vos finances pour que vous puissiez vous "
            "concentrer sur ce qui compte vraiment. Voici comment je peux vous aider :\n\n"
            "Investir intelligemment — Je vous aide à choisir les fonds communs de placement "
            "qui correspondent à vos objectifs et à votre tolérance au risque.\n\n"
            "Protéger ceux que vous aimez — L'assurance vie et l'assurance invalidité, "
            "c'est la tranquillité d'esprit pour vous et votre famille.\n\n"
            "Planifier votre avenir — Ensemble, on bâtit un plan financier qui évolue "
            "avec vous, de l'épargne à la retraite.\n\n"
            "Chaque situation est unique, et c'est pour ça que je prends le temps de bien "
            "comprendre la vôtre."
        ),
    },
    {
        "category": "services",
        "variant": 3,
        "title": "Services — Concis",
        "content": (
            "Mes services :\n"
            "• Fonds communs de placement\n"
            "• Assurance vie et invalidité\n"
            "• Assurance maladies graves\n"
            "• Planification financière\n"
            "• Planification de la retraite\n"
            "• Planification successorale"
        ),
    },
    # ── Approche client ─────────────────────────────────────────────────
    {
        "category": "client_approach",
        "variant": 1,
        "title": "Approche client — Professionnel",
        "content": (
            "Ma philosophie repose sur une approche disciplinée et méthodique de la gestion "
            "financière. Chaque recommandation est le fruit d'une analyse rigoureuse de votre "
            "situation financière, de vos objectifs à court et long terme, et de votre tolérance "
            "au risque. Je privilégie la diversification et la constance, en m'appuyant sur "
            "des données probantes plutôt que sur les tendances du marché. La transparence "
            "et l'intégrité guident chacune de mes actions."
        ),
    },
    {
        "category": "client_approach",
        "variant": 2,
        "title": "Approche client — Chaleureux",
        "content": (
            "Pour moi, la relation avec mes clients va bien au-delà des chiffres. Je crois "
            "qu'un bon conseiller financier est d'abord quelqu'un qui écoute. C'est pourquoi "
            "je prends le temps de comprendre vos projets de vie, vos inquiétudes et vos "
            "aspirations avant de proposer quoi que ce soit. Mon objectif est de bâtir une "
            "relation de confiance durable où vous vous sentez en contrôle de votre avenir "
            "financier."
        ),
    },
    {
        "category": "client_approach",
        "variant": 3,
        "title": "Approche client — Concis",
        "content": (
            "Mon approche : écouter d'abord, conseiller ensuite. Je m'engage à fournir "
            "des recommandations claires, transparentes et adaptées à votre réalité "
            "financière. Pas de jargon inutile, pas de promesses irréalistes."
        ),
    },
    # ── Titres et accréditations ────────────────────────────────────────
    {
        "category": "credentials",
        "variant": 1,
        "title": "Accréditations — Professionnel",
        "content": (
            "Titres et certifications professionnelles :\n\n"
            "• Représentant en épargne collective inscrit auprès de l'Autorité des marchés "
            "financiers (AMF)\n"
            "• Représentant en assurance de personnes certifié par la Chambre de la sécurité "
            "financière (CSF)\n"
            "• [Nombre] années d'expérience dans le secteur des services financiers\n"
            "• Formation continue conforme aux exigences réglementaires de l'AMF et de la CSF\n\n"
            "Je maintiens les plus hauts standards de pratique professionnelle et respecte "
            "rigoureusement le code de déontologie de la Chambre de la sécurité financière."
        ),
    },
    {
        "category": "credentials",
        "variant": 2,
        "title": "Accréditations — Chaleureux",
        "content": (
            "Votre confiance est ma priorité, et mes qualifications sont là pour la soutenir. "
            "Je suis dûment inscrit auprès de l'Autorité des marchés financiers pour les "
            "fonds communs de placement, et certifié par la Chambre de la sécurité financière "
            "pour l'assurance de personnes.\n\n"
            "Avec [nombre] années dans le domaine, je continue de me perfectionner chaque "
            "année pour vous offrir les meilleurs conseils possibles. La formation continue, "
            "ce n'est pas juste une obligation pour moi — c'est une passion."
        ),
    },
    {
        "category": "credentials",
        "variant": 3,
        "title": "Accréditations — Concis",
        "content": (
            "• Inscrit à l'AMF — Épargne collective\n"
            "• Certifié CSF — Assurance de personnes\n"
            "• [Nombre] ans d'expérience\n"
            "• Formation continue à jour"
        ),
    },
    # ── Mentions légales et divulgations ────────────────────────────────
    {
        "category": "legal",
        "variant": 1,
        "title": "Mentions légales — Professionnel",
        "content": (
            "Les fonds communs de placement sont distribués par l'entremise de [Nom du cabinet], "
            "cabinet inscrit en épargne collective auprès de l'Autorité des marchés financiers "
            "du Québec. Les produits d'assurance de personnes sont offerts par l'entremise de "
            "[Nom du cabinet], cabinet inscrit en assurance de personnes.\n\n"
            "Les fonds communs de placement ne sont pas garantis, leur valeur fluctue "
            "fréquemment et les rendements passés ne sont pas indicatifs des rendements futurs. "
            "Les placements dans les fonds communs peuvent donner lieu à des commissions, "
            "des commissions de suivi, des frais de gestion et d'autres frais.\n\n"
            "Pour connaître les risques associés à un investissement, veuillez lire le "
            "prospectus du fonds avant d'investir.\n\n"
            "Responsable de la protection des renseignements personnels : "
            "[Prénom Nom], [courriel]"
        ),
    },
    {
        "category": "legal",
        "variant": 2,
        "title": "Mentions légales — Chaleureux",
        "content": (
            "En toute transparence, voici les informations importantes à connaître :\n\n"
            "Je suis rattaché à [Nom du cabinet], un cabinet dûment inscrit auprès de "
            "l'Autorité des marchés financiers pour les fonds communs de placement et "
            "l'assurance de personnes.\n\n"
            "Comme pour tout investissement, il est important de savoir que la valeur des "
            "fonds communs peut fluctuer et que les rendements passés ne garantissent pas "
            "les rendements futurs. C'est pour ça qu'on travaille ensemble pour choisir "
            "les solutions les mieux adaptées à votre situation.\n\n"
            "Pour toute question concernant la protection de vos renseignements personnels, "
            "n'hésitez pas à communiquer avec [Prénom Nom] à [courriel]."
        ),
    },
    {
        "category": "legal",
        "variant": 3,
        "title": "Mentions légales — Concis",
        "content": (
            "Cabinet : [Nom du cabinet] — inscrit à l'AMF (épargne collective et assurance "
            "de personnes).\n\n"
            "Les fonds communs ne sont pas garantis. Leur valeur fluctue. Les rendements "
            "passés ne préjugent pas des rendements futurs. Lisez le prospectus avant "
            "d'investir.\n\n"
            "Responsable vie privée : [Prénom Nom], [courriel]"
        ),
    },
]


def seed_text_templates(db) -> int:
    """Insert text templates into database. Returns count of inserted rows."""
    existing = db.execute("SELECT COUNT(*) FROM text_templates").fetchone()[0]
    if existing > 0:
        return 0

    for tpl in TEXT_TEMPLATES:
        db.execute(
            "INSERT INTO text_templates (category, variant, title, content) VALUES (?, ?, ?, ?)",
            (tpl["category"], tpl["variant"], tpl["title"], tpl["content"]),
        )
    db.commit()
    return len(TEXT_TEMPLATES)
