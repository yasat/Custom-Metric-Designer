FEATURES = [
    {
        "name": "Checking Account",
        "type": "categorical",
        "categories": ["< 0 DM", "0 - 200 DM", "> 200 DM", "no account"],
        "explanation": "Status of the applicant's checking account balance.",
    },
    {
        "name": "Duration",
        "type": "numerical",
        "min": 4,
        "max": 72,
        "explanation": "Credit repayment duration in months.",
    },
    {
        "name": "Credit History",
        "type": "categorical",
        "categories": [
            "no credits taken",
            "all paid back duly",
            "existing credits paid",
            "delay in payments",
            "critical account"
        ],
        "explanation": "History of the applicant's credit behavior.",
    },
    {
        "name": "Purpose",
        "type": "categorical",
        "categories": [
            "car (new)",
            "car (used)",
            "furniture/equipment",
            "radio/TV",
            "education",
            "retraining",
            "business",
            "other"
        ],
        "explanation": "Reason for taking the credit.",
    },
    {
        "name": "Credit Amount",
        "type": "numerical",
        "min": 250,
        "max": 20000,
        "explanation": "The amount of money the applicant wants to borrow.",
    },
    {
        "name": "Savings Account/Bonds",
        "type": "categorical",
        "categories": [
            "< 100 DM",
            "100 - 500 DM",
            "500 - 1000 DM",
            "> 1000 DM",
            "unknown/none"
        ],
        "explanation": "Status of savings account or bonds.",
    },
    {
        "name": "Present Employment Since",
        "type": "categorical",
        "categories": [
            "unemployed",
            "< 1 year",
            "1 - 4 years",
            "4 - 7 years",
            "> 7 years"
        ],
        "explanation": "Number of years the applicant has been employed.",
    },
    {
        "name": "Instalment Rate",
        "type": "numerical",
        "min": 1,
        "max": 4,
        "explanation": "Monthly instalment as % of disposable income.",
    },
    {
        "name": "Personal Status",
        "type": "categorical",
        "categories": [
            "male-divorced/separated",
            "male-single",
            "male-married",
            "female-divorced/separated/married"
        ],
        "explanation": "Applicant's marital status and gender.",
    },
    {
        "name": "Other Debtors",
        "type": "categorical",
        "categories": [
            "none",
            "co-applicant",
            "guarantor"
        ],
        "explanation": "Other people responsible for the credit.",
    },
    {
        "name": "Present Residence",
        "type": "numerical",
        "min": 1,
        "max": 4,
        "explanation": "Number of years at current residence.",
    },
    {
        "name": "Property",
        "type": "categorical",
        "categories": [
            "real estate",
            "insurance",
            "car/other",
            "unknown"
        ],
        "explanation": "Applicant's owned property used as collateral.",
    },
    {
        "name": "Age",
        "type": "numerical",
        "min": 18,
        "max": 75,
        "explanation": "Applicant's age in years.",
    },
    {
        "name": "Other Instalment Plans",
        "type": "categorical",
        "categories": [
            "bank",
            "stores",
            "none"
        ],
        "explanation": "Other concurrent instalment plans the applicant may have.",
    },
    {
        "name": "Housing",
        "type": "categorical",
        "categories": [
            "rent",
            "own",
            "for free"
        ],
        "explanation": "Applicant's housing status.",
    },
    {
        "name": "Existing Credits",
        "type": "numerical",
        "min": 1,
        "max": 4,
        "explanation": "Number of credits the applicant has with this bank.",
    },
    {
        "name": "Job",
        "type": "categorical",
        "categories": [
            "unemployed/unskilled",
            "unskilled-resident",
            "skilled",
            "highly qualified"
        ],
        "explanation": "Applicant's occupation type.",
    },
    {
        "name": "Dependents",
        "type": "numerical",
        "min": 0,
        "max": 2,
        "explanation": "Number of dependents supported by the applicant.",
    },
    {
        "name": "Telephone",
        "type": "categorical",
        "categories": [
            "none",
            "yes, registered"
        ],
        "explanation": "Whether applicant has a registered telephone.",
    },
    {
        "name": "Foreign Worker",
        "type": "categorical",
        "categories": [
            "yes",
            "no"
        ],
        "explanation": "Whether applicant is a foreign worker.",
    },
]
