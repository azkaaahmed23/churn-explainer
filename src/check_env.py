"""Phase 0 environment check. Run this right after `pip install -r requirements.txt`.

If `shap` fails to import on Python 3.13, recreate the venv with Python 3.12:
    py -3.12 -m venv venv
"""
import importlib
import sys

PACKAGES = ["pandas", "numpy", "scipy", "sklearn", "shap", "joblib", "matplotlib", "streamlit"]

print(f"Python {sys.version.split()[0]}")
failed = []
for name in PACKAGES:
    try:
        mod = importlib.import_module(name)
        print(f"  OK    {name:<12} {getattr(mod, '__version__', '')}")
    except Exception as exc:  # noqa: BLE001
        failed.append(name)
        print(f"  FAIL  {name:<12} {type(exc).__name__}: {exc}")

if failed:
    print(f"\nProblem packages: {', '.join(failed)}")
    sys.exit(1)
print("\nAll good. Environment is ready.")
