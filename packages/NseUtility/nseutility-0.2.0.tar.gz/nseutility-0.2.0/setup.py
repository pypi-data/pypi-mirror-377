from setuptools import setup, find_packages

setup(
    name="NseUtility",
    version="0.2.0",
    author="Prasad",
    description="A utility to fetch NSE India data",
    packages=find_packages(),
    install_requires=["pandas", "requests", "numpy", "feedparser", "urllib3", "gspread", "oauth2client", "google-auth", "schedule", "pytz", "beautifulsoup4"],
    python_requires=">=3.8",
)