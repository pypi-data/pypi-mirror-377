from setuptools import setup

VERSION = "0.1.1"

setup(
    name="datasette-llm-sql-writer",
    description="Generate Datasette SQL queries using plain language and an LLM",
    author="Evan Jones",
    url="https://github.com/etjones/datasette-llm-sql-writer",
    license="Apache License, Version 2.0",
    version=VERSION,
    py_modules=["datasette_llm_sql_writer"],
    entry_points={"datasette": ["plugin_demos = datasette_plugin_demos"]},
    install_requires=["datasette"],
)
