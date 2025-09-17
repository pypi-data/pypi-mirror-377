from setuptools import setup, find_packages

setup(
    name="streamlit-cookie-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.20",
    ],
    author="Jason Kim",
    author_email="youremail@example.com",  # <-- replace
    description="A simple cookie/session manager for Streamlit apps",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jasonisdoing/streamlit-cookie-manager",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
)