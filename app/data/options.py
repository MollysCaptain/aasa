"""
Static and derived dropdown option lists for the intake form.
Org sizes are our own taxonomy (no such field exists in the case dataset).
Industries / workflows are derived from the real dataset — see Card 2.1
Step 0 (scripts/validate_use_cases.py, scripts/normalize_domains.py) in
13-Build-Guide-Epic2-Retrieval-v1.md. Re-run the snippet in Card 1.2 Step 3
of 12-Build-Guide-Epic1-Intake-v1.md and update these two lists if the
underlying data ever changes.
"""

ORG_SIZES = {
    "solo": "Solo / Pre-seed (1–4 people)",
    "startup": "Startup (5–20 people)",
    "smb": "Small–Medium Business (21–200 people)",
    "mid": "Mid-Market (201–1,000 people)",
    "ent": "Enterprise (1,000+ people)",
}

PRIVACY_POSTURES = {
    "standard": "Standard",
    "regulated": "Regulated (HIPAA / GDPR / financial data)",
}

# Derived from data/use-cases.csv's real 'Use Case Industry' column
# (24 real values; "Any industry" added by hand as a "no preference" option).
INDUSTRIES = ["Any industry"] + [
    "Agriculture",
    "Automotive",
    "Cross-Industry",
    "Cybersecurity",
    "Education",
    "Energy & Utilities",
    "Financial Services",
    "Government & Public Sector",
    "Healthcare",
    "Hospitality & Travel",
    "Legal & Compliance",
    "Manufacturing",
    "Marketing & Advertising",
    "Media, Entertainment & Sports",
    "Nonprofit & NGO",
    "Other",
    "Professional Services",
    "Real Estate & Construction",
    "Robotics",
    "Robotics & Automation",
    "Technology",
    "Telecommunications",
    "Transportation & Logistics",
    "Retail & E-commerce",
]

# Derived from data/use-cases.csv's 'Use Case Domain (Canonical)' column,
# produced by scripts/normalize_domains.py against data/domain_mapping.json
# (18 canonical values, collapsed from 59 raw "Use Case Domain" strings;
# "Any workflow" added by hand as a "no preference" option).
WORKFLOWS = ["Any workflow"] + [
    "Content & Creative",
    "CX & Personalization",
    "Customer Service",
    "Data & Analytics",
    "Facilities & EHS",
    "Finance",
    "HR",
    "IT & Platform",
    "Legal & Compliance",
    "Marketing",
    "Operations & Supply Chain",
    "Process Automation & RPA",
    "Procurement",
    "R&D & Engineering",
    "Risk & Compliance",
    "Sales",
    "Security & Cyber",
    "Training & L&D",
]

