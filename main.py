# pip install fastapi uvicorn
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional
import datetime
import uvicorn

app = FastAPI(title="Система записи пациентов к врачу (Вариант 8)")

# ===== Модели =====
class Doctor(BaseModel):
    id: int
    name: str
    specialty: str
    cabinet: str

class Appointment(BaseModel):
    id: int
    doctor_id: int
    patient_name: str
    date: datetime.date
    time: str
    comment: str = ""

# ===== “База данных” =====
doctors = [
    Doctor(id=1, name="Иванов И.И.", specialty="Терапевт", cabinet="101"),
    Doctor(id=2, name="Петров П.П.", specialty="Хирург", cabinet="202"),
    Doctor(id=3, name="Сидорова А.А.", specialty="Кардиолог", cabinet="303"),
]

appointments: List[Appointment] = []
next_appointment_id = 1

# ===== Простая система ролей =====
def get_user_role(x_user_role: Optional[str] = Header(None)) -> str:
    if x_user_role not in ["admin", "user"]:
        raise HTTPException(status_code=403, detail="Укажите заголовок X-User-Role: admin или user")
    return x_user_role

# ===== CRUD для записей =====

# CREATE — создать запись к врачу
@app.post("/appointments")
def create_appointment(
    doctor_id: int,
    patient_name: str,
    date: datetime.date,
    time: str,
    comment: Optional[str] = "",
    role: str = Depends(get_user_role)
):
    global next_appointment_id

    # Проверяем, есть ли врач
    doctor = next((d for d in doctors if d.id == doctor_id), None)
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")

    # Проверяем, не занято ли это время
    for a in appointments:
        if a.doctor_id == doctor_id and a.date == date and a.time == time:
            raise HTTPException(status_code=400, detail="Это время уже занято")

    appointment = Appointment(
        id=next_appointment_id,
        doctor_id=doctor_id,
        patient_name=patient_name,
        date=date,
        time=time,
        comment=comment
    )
    appointments.append(appointment)
    next_appointment_id += 1
    return {"message": "Запись успешно создана", "appointment": appointment}

# READ — все записи (только админ)
@app.get("/appointments")
def list_appointments(role: str = Depends(get_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Только админ может просматривать все записи")
    return appointments

# UPDATE — изменить запись (только админ)
@app.put("/appointments/{appointment_id}")
def update_appointment(
    appointment_id: int,
    date: datetime.date,
    time: str,
    comment: Optional[str] = "",
    role: str = Depends(get_user_role)
):
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Изменять может только админ")

    appointment.date = date
    appointment.time = time
    appointment.comment = comment
    return {"message": "Запись обновлена", "appointment": appointment}

# DELETE — удалить запись (только админ)
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, role: str = Depends(get_user_role)):
    appointment = next((a for a in appointments if a.id == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Удалять может только админ")

    appointments.remove(appointment)
    return {"message": "Запись удалена"}

# ADMIN — список врачей
@app.get("/doctors", include_in_schema=False)
def get_doctors():
    return doctors


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
