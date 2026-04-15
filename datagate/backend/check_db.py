from app.db.session import SessionLocal
from app.models.service import Service

def check_services():
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        print(f"Total services found: {len(services)}")
        for s in services:
            print(f"- ID: {s.id}, Name: {s.name}, Type: {s.service_type}, URL: {s.connection_url}")
    finally:
        db.close()

if __name__ == "__main__":
    check_services()
