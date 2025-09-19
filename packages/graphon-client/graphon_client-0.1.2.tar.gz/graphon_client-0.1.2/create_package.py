#!/usr/bin/env python3
"""
Complete script to create and publish a PyPI package from graphon_client.py
Run this script in the directory containing your graphon_client.py file.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and handle errors"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result

def create_package_structure():
    """Create the package directory structure"""
    print("Creating package structure...")
    
    # Create directories
    os.makedirs("graphon_client", exist_ok=True)
    
    # Move the main file into the package directory and create __init__.py
    if os.path.exists("graphon_client.py"):
        shutil.copy("graphon_client.py", "graphon_client/client.py")
    else:
        print("Error: graphon_client.py not found in current directory!")
        sys.exit(1)

def create_init_file():
    """Create __init__.py for the package"""
    init_content = '''"""
Graphon Client - A Python client library for the Graphon API
"""

from .client import GraphonClient

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ["GraphonClient"]
'''
    
    with open("graphon_client/__init__.py", "w") as f:
        f.write(init_content)

def create_setup_py():
    """Create setup.py file"""
    setup_content = '''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="graphon-client",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python client library for the Graphon API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/graphon-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="graphon api client video indexing",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/graphon-client/issues",
        "Source": "https://github.com/yourusername/graphon-client",
    },
)
'''
    
    with open("setup.py", "w") as f:
        f.write(setup_content)

def create_pyproject_toml():
    """Create pyproject.toml file (modern Python packaging)"""
    pyproject_content = '''[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "graphon-client"
version = "0.1.0"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
description = "A Python client library for the Graphon API"
readme = "README.md"
requires-python = ">=3.7"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "requests>=2.25.0",
]

[project.urls]
"Homepage" = "https://github.com/yourusername/graphon-client"
"Bug Reports" = "https://github.com/yourusername/graphon-client/issues"
"Source" = "https://github.com/yourusername/graphon-client"
'''
    
    with open("pyproject.toml", "w") as f:
        f.write(pyproject_content)

def create_readme():
    """Create README.md file"""
    readme_content = '''# Graphon Client

A Python client library for interacting with the Graphon API for video indexing and querying.

## Installation

```bash
pip install graphon-client
```

## Usage

```python
from graphon_client import GraphonClient

# Initialize the client
client = GraphonClient(token="your-api-token")

# Index a video file
job_id = client.index("path/to/your/video.mp4")

# Wait for indexing to complete
client.wait_for_completion(job_id)

# Query the indexed video
result = client.query(job_id, "What topics are discussed in this video?")
print(result)
```

## API Reference

### GraphonClient

#### `__init__(token: str)`
Initialize the client with your API token.

#### `index(video_file_path: str, show_progress: bool = True) -> str`
Upload and index a video file. Returns a job ID.

#### `get_status(job_id: str) -> dict`
Get the current status of an indexing job.

#### `query(job_id: str, query_text: str) -> dict`
Query a completed index with a text question.

#### `wait_for_completion(job_id: str, poll_interval: int = 10)`
Wait for an indexing job to complete, polling at regular intervals.

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License
'''
    
    with open("README.md", "w") as f:
        f.write(readme_content)

def create_license():
    """Create MIT License file"""
    license_content = '''MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
    
    with open("LICENSE", "w") as f:
        f.write(license_content)

def create_manifest():
    """Create MANIFEST.in file"""
    manifest_content = '''include README.md
include LICENSE
include pyproject.toml
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
'''
    
    with open("MANIFEST.in", "w") as f:
        f.write(manifest_content)

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/
'''
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)

def install_build_tools():
    """Install required build tools"""
    print("Installing/upgrading build tools...")
    run_command("python -m pip install --upgrade pip setuptools wheel twine build")

def build_package():
    """Build the package"""
    print("Building package...")
    run_command("python -m build")

def upload_to_pypi():
    """Upload to PyPI"""
    print("\n" + "="*50)
    print("READY TO UPLOAD TO PYPI")
    print("="*50)
    print("\nBefore uploading, please:")
    print("1. Update the version, author, email, and URLs in setup.py and pyproject.toml")
    print("2. Make sure you have a PyPI account at https://pypi.org/")
    print("3. Create an API token at https://pypi.org/manage/account/token/")
    print("4. Review the README.md and other files")
    
    upload = input("\nDo you want to upload to PyPI now? (y/N): ").lower().strip()
    
    if upload == 'y':
        print("\nUploading to PyPI...")
        print("You'll be prompted for your PyPI credentials or API token.")
        run_command("python -m twine upload dist/*")
        print("\n✅ Package uploaded successfully!")
        print("You can install it with: pip install graphon-client")
    else:
        print("\nTo upload later, run:")
        print("python -m twine upload dist/*")

def main():
    """Main function to orchestrate the package creation"""
    print("🚀 Creating PyPI package from graphon_client.py")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("graphon_client.py"):
        print("❌ Error: graphon_client.py not found in current directory!")
        print("Please run this script in the same directory as your graphon_client.py file.")
        sys.exit(1)
    
    # Create package structure and files
    create_package_structure()
    create_init_file()
    create_setup_py()
    create_pyproject_toml()
    create_readme()
    create_license()
    create_manifest()
    create_gitignore()
    
    # Install build tools and build package
    install_build_tools()
    build_package()
    
    print("\n✅ Package structure created successfully!")
    print("\nFiles created:")
    for file in ["graphon_client/", "setup.py", "pyproject.toml", "README.md", "LICENSE", "MANIFEST.in", ".gitignore"]:
        if os.path.exists(file):
            print(f"  ✓ {file}")
    
    print(f"\nBuild files created in dist/:")
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            print(f"  ✓ dist/{file}")
    
    # Option to upload
    upload_to_pypi()

if __name__ == "__main__":
    main()