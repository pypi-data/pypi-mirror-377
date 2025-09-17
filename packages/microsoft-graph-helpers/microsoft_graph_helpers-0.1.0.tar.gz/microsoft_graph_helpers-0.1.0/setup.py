from setuptools import setup, find_packages

setup(
    name='microsoft_graph_helpers',
    version='0.1.0',
    description='Helper functions for interacting with Microsoft Graph API',
    author='Lucas Krupinski',
    packages=find_packages(),
    install_requires=[
        'requests>=2.32.5'
    ],
    python_requires='>=3.12',
)
