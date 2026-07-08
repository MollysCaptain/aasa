"""
Validation rules for the 5-field intake form.
Returns (is_valid: bool, error_message: str) — error_message is "" when valid.
"""

def validate_intake(workflow: str, industry: str, org_size_key: str,
                     privacy_key: str, budget) -> tuple[bool, str]:
    if not workflow or not workflow.strip():
        return False, "Please select a target AI workflow."

    if not industry or not industry.strip():
        return False, "Please select an industry."

    if not org_size_key:
        return False, "Please select your organisation size."

    if privacy_key not in ("standard", "regulated"):
        return False, "Please choose a data-privacy posture."

    # Budget must be a real, non-negative number.
    try:
        budget_value = float(budget)
    except (TypeError, ValueError):
        return False, "Monthly budget must be a number."

    if budget_value <= 0:
        return False, "Monthly budget must be greater than zero."

    return True, ""
