# 📦 Publishing and Integrating a Python Package in Open edX (Tutor)

This guide provides step-by-step instructions to **build**, **publish**, and **integrate** a custom Python package into an Open edX deployment using **Tutor**.

---

## 1. Build the Package

First, install the required tools and build your package:

```bash
pip install --upgrade build twine
rm -rf dist build *.egg-info
python3 -m build

2. Test Upload to TestPyPI
Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    your-package-name

3. Real Release to PyPI
python3 -m twine upload dist/*

4. Enable Package in Open edX

Ensure the backend is enabled.

Add the package name to openedx_extra_pip_requirements via plugin.

5. Rebuild Open edX Image
tutor images build openedx

6. Launch Open edX
tutor local launch



Here’s a step-by-step way to test if your package nextere_oauth is installed and accessible properly in your Open edX Tutor environment:

Enter the LMS container shell:

tutor local exec lms bash


This opens a bash shell inside the LMS container. You’re now inside the same environment where Open edX runs.

Open the Django shell:

python manage.py lms shell


This launches a Python shell with Django settings loaded. Any installed apps and packages will be importable here.

Test importing your package:

from nextere_oauth.auth_backend import NextereOIDCBackend


If there’s no error, the package is installed and recognized by Python/Django.

If you get an ImportError, check:

The package is installed in the LMS container (pip list can help).

The Python path includes your package location.

The INSTALLED_APPS and environment variables are correctly set if needed.

(Optional) You can also quickly instantiate the class to confirm it’s fully usable:

backend = NextereOIDCBackend()
print(backend)


If this prints an object reference without error, everything is correctly installed and working.
