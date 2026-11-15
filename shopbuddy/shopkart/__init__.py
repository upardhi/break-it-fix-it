"""Shared fake store used by every ShopBuddy agent."""

import os

# Trust the operating system's certificates (needed on networks or PCs whose
# security software re-signs HTTPS traffic; harmless everywhere else).
try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

# Change the model without editing code:  set SHOPBUDDY_MODEL=gemini-2.5-flash
MODEL = os.environ.get("SHOPBUDDY_MODEL", "gemini-flash-latest")
