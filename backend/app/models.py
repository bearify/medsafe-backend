
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,Boolean,Float


class Patient(Base):
    __tablename__ = "patients"

  
    id = Column(Integer, primary_key=True, index=True)

  
    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)

    conditions = Column(Text, nullable=True)

  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    medication_name = Column(String(100), nullable=False)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)

class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    allergy_name = Column(String(100), nullable=False)
    reaction = Column(String(200), nullable=True)
    severity = Column(String(50), nullable=True)

class ImpactHistory(Base):
    __tablename__ = "impact_history"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    impact_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, index=True)

    medication_a = Column(String(100), nullable=False)
    medication_b = Column(String(100), nullable=False)

    severity = Column(String(50), nullable=False)

    description = Column(Text, nullable=False)

    source = Column(String(255), nullable=True)

class HealthcareProvider(Base):
    __tablename__ = "healthcare_providers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    doctor_type = Column(String(100), nullable=False)
    hospital_name = Column(String(150), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    availability = Column(Boolean, default=False)


class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(String(10), primary_key=True, index=True)
    hospital_name = Column(String(150), nullable=False)
    area = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    departments = Column(Text, nullable=False)

    emergency_available = Column(Boolean, nullable=True)
    specialist_available = Column(Boolean, nullable=True)
    specialist_status = Column(String(50), nullable=True)

