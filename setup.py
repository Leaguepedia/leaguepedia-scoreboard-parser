import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="leaguepedia-scoreboard-parser",
    version="0.1.21",
    author="RheingoldRiver",
    author_email="river.esports@gmail.com",
    description="Parser for Leaguepedia scoreboards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leaguepedia/leaguepedia-scoreboard-parser",
    packages=setuptools.find_packages(),
    python_requires='>=3.9',
    install_requires=[]
)
