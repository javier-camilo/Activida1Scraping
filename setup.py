from setuptools import setup, find_packages

setup(
    name='Scraping',
    version='0.0.1',
    author='Daniela Coronado, Camilo Olea',
    author_email= ['daniela.coronado@est.iudigital.edu.co', 'camilo.olea@est.iudigital.edu.co'],
    description='Web scraping project for IUDigital',
    py_modules=['Actividad1', 'Actividad2', 'Actividad3'],
    install_requires=[
        "pandas",
        "openpyxl",
        "requests",
        "beautifulsoup4"
    ]
)