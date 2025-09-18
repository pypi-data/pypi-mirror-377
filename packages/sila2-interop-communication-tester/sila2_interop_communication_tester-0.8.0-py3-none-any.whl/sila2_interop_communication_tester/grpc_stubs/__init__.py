import pathlib
import sys

# Allow compiled proto files to find non-relative imports in this folder
sys.path.append(str(pathlib.Path(__file__).parent))
