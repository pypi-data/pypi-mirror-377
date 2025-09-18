from setuptools import setup, find_packages

setup(
    name="mclash",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "mclash": ["clash", "config.yaml", "Country.mmdb"]
    },
    entry_points={
        "console_scripts": [
            "mclash = mclash.__main__:main"
        ]
    },
)
