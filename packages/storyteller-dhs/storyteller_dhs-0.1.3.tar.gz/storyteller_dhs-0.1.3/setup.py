from setuptools import setup, find_packages
from _version import __version__
from pathlib import Path

# Read README.md for PyPI description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="storyteller-dhs",
    version=__version__,
    author="kofiyatech",
    author_email="kofiya.technologies@gmail.com",
    description="Storyteller-DHS: Explore and analyze DHS (Demographic and Health Surveys) datasets with an intuitive interface and CLI tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Ensures README.md renders correctly
    url="https://github.com/kofiyatech/storyteller-DHS-database-viewer",  # Update if repo URL is different
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "storyteller": [
            "metadata.yaml",
            "assets/*",
            "templates/*",
        ],
    },
    install_requires=[
        "click",
        "datasette",
        "sqlite-utils",
        "Jinja2",
        "pandas",
    ],  # TODO - Update for new dependencies
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "storyteller=storyteller.cli:storyteller",
            "enable_fts=storyteller.cli:enable_fts",
        ],
    },  # TODO - Update for new CLI commands
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",  # Update if different
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Database :: Front-Ends",
    ],
    keywords="dhs, storyteller, datasette, demographics, health, survey, analysis",
)
