"""
Простой клиент для системы записи пациентов к врачу.

Примеры:
  python client.py list admin
  python client.py create user 2 Иван 2025-11-01 10:00 "Болит спина"
  python client.py get user 1
  python client.py update admin 1 2025-11-02 11:00 "Перенос визита"
  python client.py delete admin 1

Перед запуском: сервер должен быть запущен (python main.py)
"""
import sys, requests

API = "http://127.0.0.1:8000"

def print_resp(r):
    print("Status:", r.status_code)
    try:
        print(r.json())
    except:
        print(r.text)

def create(role, doctor_id, patient_name, date, time, comment=""):
    headers = {"X-User-Role": role}
    params = {
        "doctor_id": int(doctor_id),
        "patient_name": patient_name,
        "date": date,
        "time": time,
        "comment": comment
    }
    r = requests.post(f"{API}/appointments", params=params, headers=headers)
    print_resp(r)

def list_appointments(role):
    headers = {"X-User-Role": role}
    r = requests.get(f"{API}/appointments", headers=headers)
    print_resp(r)

def get_appointment(role, appointment_id):
    headers = {"X-User-Role": role}
    r = requests.get(f"{API}/appointments/{appointment_id}", headers=headers)
    print_resp(r)

def update_appointment(role, appointment_id, date, time, comment=""):
    headers = {"X-User-Role": role}
    params = {"date": date, "time": time, "comment": comment}
    r = requests.put(f"{API}/appointments/{appointment_id}", params=params, headers=headers)
    print_resp(r)

def delete_appointment(role, appointment_id):
    headers = {"X-User-Role": role}
    r = requests.delete(f"{API}/appointments/{appointment_id}", headers=headers)
    print_resp(r)

def usage():
    print(__doc__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]
    try:
        if cmd == "create":
            _, _, role, doctor_id, patient_name, date, time, *comment = sys.argv
            comment = " ".join(comment)
            create(role, doctor_id, patient_name, date, time, comment)

        elif cmd == "list":
            _, _, role = sys.argv
            list_appointments(role)

        elif cmd == "get":
            _, _, role, appointment_id = sys.argv
            get_appointment(role, appointment_id)

        elif cmd == "update":
            _, _, role, appointment_id, date, time, *comment = sys.argv
            comment = " ".join(comment)
            update_appointment(role, appointment_id, date, time, comment)

        elif cmd == "delete":
            _, _, role, appointment_id = sys.argv
            delete_appointment(role, appointment_id)

        else:
            usage()
    except Exception as e:
        print("Error:", e)
