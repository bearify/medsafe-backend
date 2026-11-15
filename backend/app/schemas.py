from pydantic import BaseModel
from typing import Optional

class PatientCreate(BaseModel):
    full_name: str
    age: Optional[int] = None
    conditions: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    full_name: str
    age: Optional[int] = None
    conditions: Optional[str] = None

    class Config:
        from_attributes = True

class MedicationCreate(BaseModel):
    patient_id: int
    medication_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None

class AllergyCreate(BaseModel):
    patient_id: int
    allergy_name: str
    reaction: Optional[str] = None
    severity: Optional[str] = None

class ImpactHistoryCreate(BaseModel):
    patient_id: int
    medication_id: int
    impact_type: str
    description: str

class DrugInteractionCreate(BaseModel):
    medication_a: str
    medication_b: str
    severity: str
    description: str
    source: str

class HealthcareProviderCreate(BaseModel):
    full_name: str
    doctor_type: str
    hospital_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability: bool = False


class HealthcareProviderResponse(BaseModel):
    id: int
    full_name: str
    doctor_type: str
    hospital_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability: bool

    class Config:
        from_attributes = True


class HospitalCreate(BaseModel):
    hospital_id: str
    hospital_name: str
    area: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    departments: str
    emergency_available: Optional[bool] = None
    specialist_available: Optional[bool] = None
    specialist_status: Optional[str] = None


class HospitalResponse(BaseModel):
    hospital_id: str
    hospital_name: str
    area: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    departments: str
    emergency_available: Optional[bool] = None
    specialist_available: Optional[bool] = None
    specialist_status: Optional[str] = None

    class Config:
        from_attributes = True
