import traceback
import sys
try:
    import sqlalchemy
    print('SQLAlchemy version:', sqlalchemy.__version__)
except Exception:
    traceback.print_exc()
    sys.exit(1)
print('Import ok')
