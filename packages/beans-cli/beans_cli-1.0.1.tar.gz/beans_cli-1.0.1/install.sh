python3 -m build
twine upload dist/*
pip install beans-cli --break-system-packages --upgrade