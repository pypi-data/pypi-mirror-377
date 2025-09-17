from setuptools import setup, find_packages

setup(
    name='OSL_CGCD',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='Descripción de OSL_CGCD',
    author='Tu Nombre',
    author_email='tu.email@example.com',
    install_requires=[],
    python_requires='>=3.6',
)