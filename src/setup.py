import setuptools

setuptools.setup(
    name='igcogito',
    version='1.0',
    description='',
    author='',
    author_email='example@evil.com',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ig_cogito = igcogito.main:console_entry',
            'ig_xml_to_xls = igcogito.main:xml_to_xls_console_entry'
        ]
    }
)
