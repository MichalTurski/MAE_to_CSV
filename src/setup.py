import setuptools

setuptools.setup(
    name='igcogito',
    version='1.0',
    description='',
    author='',
    author_email='example@evil.com',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['ig_cogito = igcogito.main:console_entry']
    }
)
