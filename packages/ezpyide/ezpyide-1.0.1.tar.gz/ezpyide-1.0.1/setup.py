from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# načítanie README
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="ezpyide",             # názov balíka
    version="1.0.1",            # verzia
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.0.0",
        "streamlit_ace>=0.1.0"
    ],
    entry_points={
        "console_scripts": [
            "ezpy = ezpy.__main__:main",
        ],
    },
    long_description=long_description,      # pridanie README
    long_description_content_type="text/markdown",  # formát markdown
    author="Denis Varga",
    description="Web IDE for Python using Streamlit and Ace Editor",
    url="https://github.com/DenisVargaeu/ezpyide",  # ak máš GitHub repo
)
