from setuptools import setup, find_packages

setup(name='hnt_sap_fornecedor_library',
    version='0.0.1',
    license='MIT License',
    author='Pepe',
    maintainer='Pepe',
    keywords='Dados do fornecedor SAP',
    description=u'Lib para ler dados do fornecedor.',
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={'hnt_sap_gui': ['common/*', 'fornecedor/*']},
    install_requires=[
    'python-dotenv',
    'robotframework-sapguilibrary',
    ])