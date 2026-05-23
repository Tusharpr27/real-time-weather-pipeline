"""
Delete a test alert from the database.
Usage: cd backend && .\venv\Scripts\python.exe scripts\delete_test_alert.py [alert_id]
"""
import sys

sys.path.insert(0, '.')

from src.database.database import create_session
from src.database.models import Alert


def delete_alert(alert_id: int = 1):
    db = create_session()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            print(f"Alert id={alert_id} not found")
            return False

        db.delete(alert)
        db.commit()
        print(f"Deleted alert id={alert_id}")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting alert: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    aid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    delete_alert(aid)
