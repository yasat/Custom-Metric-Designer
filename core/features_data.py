FEATURES = [
    {
        "name": "Status of Checking Account",
        "type": "categorical",
        "categories": [
            "< 0 DM",
            "0 <= ... < 200 DM",
            ">= 200 DM",
            "no checking account"
        ],
        "explanation": "Status of the applicant's existing checking account.",
    },
    {
        "name": "Duration in Month",
        "type": "numerical",
        "min": 4,
        "max": 72,
        "explanation": "Credit repayment duration in months.",
    },
    {
        "name": "Credit History",
        "type": "categorical",
        "categories": [
            "no credits taken / all paid back duly",
            "all credits at this bank paid back duly",
            "existing credits paid back duly till now",
            "delay in paying off in the past",
            "critical account / other credits exist (not at this bank)"
        ],
        "explanation": "History of the applicant’s credit repayment.",
    },
    {
        "name": "Purpose",
        "type": "categorical",
        "categories": [
            "car (new)",
            "car (used)",
            "furniture/equipment",
            "radio/television",
            "domestic appliances",
            "repairs",
            "education",
            "vacation",
            "retraining",
            "business",
            "others"
        ],
        "explanation": "Purpose of the requested loan.",
    },
    {
        "name": "Credit Amount",
        "type": "numerical",
        "min": 1,
        "max": 5,
        "explanation": "The total amount of credit requested.",
    },
    {
        "name": "Savings Account/Bonds",
        "type": "categorical",
        "categories": [
            "< 100 DM",
            "100 <= ... < 500 DM",
            "500 <= ... < 1000 DM",
            ">= 1000 DM",
            "unknown / no savings account"
        ],
        "explanation": "Savings account or bond ownership status.",
    },
    {
        "name": "Present Employment Since",
        "type": "categorical",
        "categories": [
            "unemployed",
            "< 1 year",
            "1 - 4 years",
            "4 - 7 years",
            ">= 7 years"
        ],
        "explanation": "Length of current employment.",
    },
    {
        "name": "Installment Rate as % of Disposable Income",
        "type": "numerical",
        "min": 1,
        "max": 4,
        "explanation": "Installment rate as a percentage of disposable income.",
    },
    {
        "name": "Personal Status and Sex",
        "type": "categorical",
        "categories": [
            "male - divorced/separated",
            "female - divorced/separated/married",
            "male - single",
            "male - married/widowed",
            "female - single"
        ],
        "explanation": "Gender and marital status of the applicant.",
    },
    {
        "name": "Other Debtors/Guarantors",
        "type": "categorical",
        "categories": [
            "none",
            "co-applicant",
            "guarantor"
        ],
        "explanation": "Other individuals responsible for the credit.",
    },
    {
        "name": "Present Residence Since",
        "type": "numerical",
        "min": 1,
        "max": 4,
        "explanation": "Years at current residence.",
    },
    {
        "name": "Property",
        "type": "categorical",
        "categories": [
            "real estate",
            "building society savings / life insurance",
            "car or other asset",
            "unknown / no property"
        ],
        "explanation": "Applicant’s owned property or collateral.",
    },
    {
        "name": "Age in Years",
        "type": "numerical",
        "min": 18,
        "max": 75,
        "explanation": "Age of the applicant.",
    },
    {
        "name": "Other Installment Plans",
        "type": "categorical",
        "categories": [
            "bank",
            "stores",
            "none"
        ],
        "explanation": "Presence of other installment payment obligations.",
    },
    {
        "name": "Housing",
        "type": "categorical",
        "categories": [
            "rent",
            "own",
            "for free"
        ],
        "explanation": "Housing situation of the applicant.",
    },
    {
        "name": "Number of Existing Credits at This Bank",
        "type": "numerical",
        "min": 0,
        "max": 4,
        "explanation": "Number of open credit lines with this bank.",
    },
    {
        "name": "Job",
        "type": "categorical",
        "categories": [
            "unemployed/unskilled - non-resident",
            "unskilled - resident",
            "skilled employee / official",
            "management / self-employed / highly qualified"
        ],
        "explanation": "Employment type of the applicant.",
    },
    {
        "name": "Dependents",
        "type": "numerical",
        "min": 0,
        "max": 2,
        "explanation": "Number of People Liable.",
    },
    {
        "name": "Telephone",
        "type": "categorical",
        "categories": [
            "none",
            "yes, registered under customer's name"
        ],
        "explanation": "Telephone ownership and registration.",
    },
    {
        "name": "Foreign Worker",
        "type": "categorical",
        "categories": [
            "yes",
            "no"
        ],
        "explanation": "Whether the applicant is a foreign worker.",
    }
]

FEATURE_CATEGORY_MAP = {
    "Status of Checking Account": {
        "< 0 DM": "A11",
        "0 <= ... < 200 DM": "A12",
        ">= 200 DM": "A13",
        "no checking account": "A14"
    },
    "Credit History": {
        "no credits taken / all paid back duly": "A30",
        "all credits at this bank paid back duly": "A31",
        "existing credits paid back duly till now": "A32",
        "delay in paying off in the past": "A33",
        "critical account / other credits exist (not at this bank)": "A34"
    },
    "Purpose": {
        "car (new)": "A40",
        "car (used)": "A41",
        "furniture/equipment": "A42",
        "radio/television": "A43",
        "domestic appliances": "A44",
        "repairs": "A45",
        "education": "A46",
        "vacation": "A47",
        "retraining": "A48",
        "business": "A49",
        "others": "A410"
    },
    "Savings Account/Bonds": {
        "< 100 DM": "A61",
        "100 <= ... < 500 DM": "A62",
        "500 <= ... < 1000 DM": "A63",
        ">= 1000 DM": "A64",
        "unknown / no savings account": "A65"
    },
    "Present Employment Since": {
        "unemployed": "A71",
        "< 1 year": "A72",
        "1 - 4 years": "A73",
        "4 - 7 years": "A74",
        ">= 7 years": "A75"
    },
    "Personal Status and Sex": {
        "male - divorced/separated": "A91",
        "female - divorced/separated/married": "A92",
        "male - single": "A93",
        "male - married/widowed": "A94",
        "female - single": "A95"
    },
    "Other Debtors/Guarantors": {
        "none": "A101",
        "co-applicant": "A102",
        "guarantor": "A103"
    },
    "Property": {
        "real estate": "A121",
        "building society savings / life insurance": "A122",
        "car or other asset": "A123",
        "unknown / no property": "A124"
    },
    "Other Installment Plans": {
        "bank": "A141",
        "stores": "A142",
        "none": "A143"
    },
    "Housing": {
        "rent": "A151",
        "own": "A152",
        "for free": "A153"
    },
    "Job": {
        "unemployed/unskilled - non-resident": "A171",
        "unskilled - resident": "A172",
        "skilled employee / official": "A173",
        "management / self-employed / highly qualified": "A174"
    },
    "Telephone": {
        "none": "A191",
        "yes, registered under customer's name": "A192"
    },
    "Foreign Worker": {
        "yes": "A201",
        "no": "A202"
    }
}
