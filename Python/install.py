import subprocess
import sys

packages = [
    "graphviz"
]

for package in packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])