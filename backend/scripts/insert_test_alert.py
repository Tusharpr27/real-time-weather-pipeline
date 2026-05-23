"""
Insert a test alert into the database.
Run from project root: `cd backend; .\venv\Scripts\python.exe scripts\insert_test_alert.py`
"""
import sys
from datetime import datetime

sys.path.insert(0, '.')

from src.database.database import create_session
from src.database.models import Alert

def insert_alert(location_id=1):
    db = create_session()
    try:
        alert = Alert(
            location_id=location_id,
            alert_type='temp_high',
            severity='HIGH',
            message='Test alert injected by assistant',
            metric_name='temperature',
            metric_value=42.5,
            threshold_value=35.0,
            status='active',
            triggered_at=datetime.utcnow()
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        print(f"Inserted alert id={alert.id}")
        return alert.id
    except Exception as e:
        db.rollback()
        print(f"Error inserting alert: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    insert_alert()
