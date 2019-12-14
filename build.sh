cd src
python setup.py sdist
pip install dist/*
rm -rf dist/
rm -rf *egg-info/
