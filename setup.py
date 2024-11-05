from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in gross_profit_by_sales_invoice/__init__.py
from gross_profit_by_sales_invoice import __version__ as version

setup(
	name="gross_profit_by_sales_invoice",
	version=version,
	description=" Gross Profit By Sales Invoice",
	author="Peter Maged",
	author_email="eng.peter.maged@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
