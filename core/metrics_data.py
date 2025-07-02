METRICS = [
    {
        "id": "demographic_parity",
        "name": "Demographic Parity",
        "category": "Group",
        "explanation": "Applicants, regardless of group (e.g., Male or Female), should have the same chance of receiving a Good Credit prediction.",
    },
    {
        "id": "equal_opportunity",
        "name": "Equal Opportunity",
        "category": "Group",
        "explanation": "Applicants with real good credit, regardless of group, should have the same chance of receiving a Good Credit prediction.",
    },
    {
        "id": "predictive_equality",
        "name": "Predictive Equality",
        "category": "Group",
        "explanation": "Applicants with real bad credit, regardless of group, should have the same chance of receiving a Good Credit prediction.",
    },
    {
        "id": "outcome_test",
        "name": "Outcome Test",
        "category": "Group",
        "explanation": "Among applicants predicted as Good Credit, the probability of actually having good credit should be the same across groups.",
    },
    {
        "id": "equalized_odds",
        "name": "Equalized Odds",
        "category": "Group",
        "explanation": "Combines both Equal Opportunity and Predictive Equality for fairness.",
    },
    {
        "id": "conditional_statistical_parity",
        "name": "Conditional Statistical Parity",
        "category": "Group",
        "explanation": "Applicants with the same conditions (e.g., Job, Credit History, Savings) should have equal chances of a good prediction, regardless of group.",
    },
    {
        "id": "counterfactual_fairness",
        "name": "Counterfactual Fairness",
        "category": "Individual",
        "explanation": "Changing group attributes (e.g., Age, Gender) should not change the model prediction if everything else remains the same.",
    },
    {
        "id": "consistency",
        "name": "Consistency",
        "category": "Individual",
        "explanation": "Similar individuals should receive similar prediction outcomes from the model.",
    },
]