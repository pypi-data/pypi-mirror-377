# zt_privacy_lib package
"""
ZT Privacy Library - PII Detection and Anonymization

This library provides robust PII detection and anonymization capabilities
using GLiNER and Presidio models.

Main API Functions:
    - get_anonymize_prompt_strict_gliner: Stable API with detection_only parameter support

API Contract Guarantee:
    The 'detection_only: bool = False' parameter is supported and stable
    in all versions >= 0.1.3 of zt-privacy-lib
"""

__version__ = "0.1.3"
__api_version__ = "1.0"

# Explicitly document supported parameters for main API functions
SUPPORTED_PARAMETERS = {
    "get_anonymize_prompt_strict_gliner": [
        "form_data",
        "detection_only"  # bool, default=False - guaranteed stable API
    ]
}
