from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in entre_theme/__init__.py
from entre_theme import __version__ as version

setup(
	name="entre_theme",
	version=version,
	description="A non-destructive ERPNext theme app by Entretech",
	author="Entretech",
	author_email="hello@entretech.pt",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
