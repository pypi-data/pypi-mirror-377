from setuptools import setup, find_packages

setup(
    name="mclash",
    version="1.2.1",
    packages=find_packages(),  # 确保能找到 mclash 包
    include_package_data=True,
    package_data={"mclash": ["clash", "config.yaml", "Country.mmdb"]},
    entry_points={"console_scripts": ["mclash = mclash.__main__:main"]},
    python_requires=">=3.6",
)
