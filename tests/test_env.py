import importlib
import sys


def test_python_version():
    assert sys.version_info[:2] in [(3, 11), (3, 12)]


def test_required_packages_import():
    for name in ["pdfplumber", "fitz", "pandas", "numpy", "sklearn", "shap", "jsonschema"]:
        importlib.import_module(name)
