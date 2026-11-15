from fastapi import FastAPI
from sqlalchemy import text
from app import models
from app.database import Base, engine

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas import HealthcareProviderResponse, PatientCreate, PatientResponse

from app.schemas import MedicationCreate
from app.schemas import AllergyCreate

from app.schemas import ImpactHistoryCreate
from fastapi import FastAPI, Depends, HTTPException

from app.schemas import  DrugInteractionCreate

from itertools import combinations

from app.schemas import HealthcareProviderCreate
from app.schemas import HealthcareProviderResponse

from app.schemas import HospitalCreate
from app.schemas import HospitalResponse

import math

Base.metadata.create_all(bind=engine)

app = FastAPI(
	title="MEDSAFE API",
	description="Healthcare Management and Emergency Assistance System",
	version="1.0.0"
)


@app.get("/")
def home():
	return {
		"message": "Welcome to MEDSAFE!",
		"status": "Backend is running"
	}


@app.get("/health")
def health_check():
	return {
		"status": "healthy",
		"application": "MEDSAFE"
	}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate straight-line distance in kilometres."""

    earth_radius = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c

@app.get("/hospitals",
         response_model=list[HospitalResponse])
def get_hospitals(db: Session = Depends(get_db)):
    return db.query(models.Hospital).all()


@app.get("/database-check")
def database_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "message": "Database connected successfully!"
    }




@app.post("/patients", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    new_patient = models.Patient(
        full_name=patient.full_name,
        age=patient.age,
        conditions=patient.conditions
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


@app.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()

    if patient is None:
        return {"message": "Patient not found"}

    return patient

@app.post("/medications")
def add_medication(
    medication: MedicationCreate,
    db: Session = Depends(get_db)
):
    new_medication = models.Medication(
        patient_id=medication.patient_id,
        medication_name=medication.medication_name,
        dosage=medication.dosage,
        frequency=medication.frequency
    )

    db.add(new_medication)
    db.commit()
    db.refresh(new_medication)

    return new_medication


@app.get("/medications/{patient_id}")
def get_medications(
    patient_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Medication).filter(
        models.Medication.patient_id == patient_id
    ).all()

@app.post("/allergies")
def add_allergy(
    allergy: AllergyCreate,
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == allergy.patient_id
    ).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_allergy = models.Allergy(
        patient_id=allergy.patient_id,
        allergy_name=allergy.allergy_name,
        reaction=allergy.reaction,
        severity=allergy.severity
    )

    db.add(new_allergy)
    db.commit()
    db.refresh(new_allergy)

    return new_allergy


@app.get("/allergies/{patient_id}")
def get_allergies(
    patient_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Allergy).filter(
        models.Allergy.patient_id == patient_id
    ).all()

@app.post("/impact-history")
def add_impact(
    impact: ImpactHistoryCreate,
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == impact.patient_id
    ).first()

    medication = db.query(models.Medication).filter(
        models.Medication.id == impact.medication_id,
        models.Medication.patient_id == impact.patient_id
    ).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    if medication is None:
        raise HTTPException(
            status_code=404,
            detail="Medication not found for this patient"
        )

    new_impact = models.ImpactHistory(
        patient_id=impact.patient_id,
        medication_id=impact.medication_id,
        impact_type=impact.impact_type,
        description=impact.description
    )

    db.add(new_impact)
    db.commit()
    db.refresh(new_impact)

    return new_impact


@app.get("/impact-history/{patient_id}")
def get_impact_history(
    patient_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.ImpactHistory).filter(
        models.ImpactHistory.patient_id == patient_id
    ).all()

@app.post("/drug-interactions")
def add_interaction(
    interaction: DrugInteractionCreate,
    db: Session = Depends(get_db)
):
    new_interaction = models.DrugInteraction(
        medication_a=interaction.medication_a,
        medication_b=interaction.medication_b,
        severity=interaction.severity,
        description=interaction.description,
        source=interaction.source
    )

    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    return new_interaction

@app.get("/drug-interactions")
def get_interactions(db: Session = Depends(get_db)):
    return db.query(models.DrugInteraction).all()

@app.get("/check-interactions/{patient_id}")
def check_interactions(
    patient_id: int,
    db: Session = Depends(get_db)
):
    # Find patient
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Get patient's medications
    medications = db.query(models.Medication).filter(
        models.Medication.patient_id == patient_id
    ).all()

    # Get interaction records
    interactions = db.query(models.DrugInteraction).all()

    results = []

    # Compare every medication pair
    for med1, med2 in combinations(medications, 2):

        name1 = med1.medication_name.strip().casefold()
        name2 = med2.medication_name.strip().casefold()

        for interaction in interactions:

            drug_a = interaction.medication_a.strip().casefold()
            drug_b = interaction.medication_b.strip().casefold()

            if {name1, name2} == {drug_a, drug_b}:
                results.append({
                    "medication_a": interaction.medication_a,
                    "medication_b": interaction.medication_b,
                    "severity": interaction.severity,
                    "description": interaction.description,
                    "source": interaction.source
                })

    return {
        "patient_id": patient_id,
        "medications_checked": [
            med.medication_name for med in medications
        ],
        "potential_interactions": results,
        "message": (
            "No matching records in the local interaction database."
            if not results
            else "Potential interaction records found. "
                 "Professional review is required."
        ),
        "note": "Absence of a matching record does not establish "
                "that the medication combination is safe."
    }

@app.get("/check-allergies/{patient_id}")
def check_allergies(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    medications = db.query(models.Medication).filter(
        models.Medication.patient_id == patient_id
    ).all()

    allergies = db.query(models.Allergy).filter(
        models.Allergy.patient_id == patient_id
    ).all()

    results = []

    for medication in medications:
        for allergy in allergies:
            if (
                medication.medication_name.strip().casefold()
                == allergy.allergy_name.strip().casefold()
            ):
                results.append({
                    "medication": medication.medication_name,
                    "allergy": allergy.allergy_name,
                    "reaction": allergy.reaction,
                    "severity": allergy.severity
                })

    return {
        "patient_id": patient_id,
        "potential_matches": results,
        "note": "No matching names does not rule out an allergy. "
                "Professional review is required."
    }

@app.get("/patient-summary/{patient_id}")
def patient_summary(
    patient_id: int,
    db: Session = Depends(get_db)
):
    # Find patient
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Get medications
    medications = db.query(models.Medication).filter(
        models.Medication.patient_id == patient_id
    ).all()

    # Get allergies
    allergies = db.query(models.Allergy).filter(
        models.Allergy.patient_id == patient_id
    ).all()

    # Get impact history
    impacts = db.query(models.ImpactHistory).filter(
        models.ImpactHistory.patient_id == patient_id
    ).all()

    # Get potential interaction matches
    interaction_check = check_interactions(patient_id, db)

    # Get potential allergy matches
    allergy_check = check_allergies(patient_id, db)

    return {
        "patient": {
            "id": patient.id,
            "full_name": patient.full_name,
            "age": patient.age,
            "conditions": patient.conditions
        },
        "medications": [
            {
                "id": med.id,
                "name": med.medication_name,
                "dosage": med.dosage,
                "frequency": med.frequency
            }
            for med in medications
        ],
        "allergies": [
            {
                "name": allergy.allergy_name,
                "reaction": allergy.reaction,
                "severity": allergy.severity
            }
            for allergy in allergies
        ],
        "impact_history": [
            {
                "medication_id": impact.medication_id,
                "impact_type": impact.impact_type,
                "description": impact.description
            }
            for impact in impacts
        ],
        "potential_interactions": interaction_check[
            "potential_interactions"
        ],
        "potential_allergy_matches": allergy_check[
            "potential_matches"
        ],
        "safety_note": (
            "This is an educational decision-support summary. "
            "Missing matches do not establish that a medication is safe. "
            "Professional review is required."
        )
    }

@app.post("/healthcare-providers", response_model=HealthcareProviderResponse)
def create_healthcare_provider(
    provider: HealthcareProviderCreate,
    db: Session = Depends(get_db)
):
    new_provider = models.HealthcareProvider(**provider.model_dump())

    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)

    return new_provider

@app.get("/healthcare-providers",
         response_model=list[HealthcareProviderResponse])
def get_healthcare_providers(
    doctor_type: str = None,
    availability: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.HealthcareProvider)

    if doctor_type:
        query = query.filter(
            models.HealthcareProvider.doctor_type.ilike(
                f"%{doctor_type}%"
            )
        )

    if availability is not None:
        query = query.filter(
            models.HealthcareProvider.availability == availability
        )

    return query.all()


@app.get("/healthcare-providers/{provider_id}", response_model=HealthcareProviderResponse)
def get_healthcare_provider(
    provider_id: int,
    db: Session = Depends(get_db)
):
    provider = db.query(models.HealthcareProvider).filter(
        models.HealthcareProvider.id == provider_id
    ).first()

    if provider is None:
        raise HTTPException(
            status_code=404,
            detail="Healthcare provider not found"
        )

    return provider


@app.post("/hospitals")
def create_hospital(
    hospital: HospitalCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(models.Hospital).filter(
        models.Hospital.hospital_id == hospital.hospital_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Hospital already exists"
        )

    new_hospital = models.Hospital(**hospital.model_dump())

    db.add(new_hospital)
    db.commit()
    db.refresh(new_hospital)

    return new_hospital


@app.get("/hospitals",
         response_model=list[HospitalResponse])
def get_hospitals(db: Session = Depends(get_db)):
    return db.query(models.Hospital).all()


@app.get("/hospitals/{hospital_id}",
         response_model=HospitalResponse)
def get_hospital(
    hospital_id: str,
    db: Session = Depends(get_db)
):
    hospital = db.query(models.Hospital).filter(
        models.Hospital.hospital_id == hospital_id
    ).first()

    if hospital is None:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    return hospital


@app.post("/import-hospitals")
def import_hospitals(
    hospitals: list[HospitalCreate],
    db: Session = Depends(get_db)
):
    inserted = 0
    skipped = 0

    for hospital in hospitals:
        existing = db.query(models.Hospital).filter(
            models.Hospital.hospital_id == hospital.hospital_id
        ).first()

        if existing:
            skipped += 1
            continue

        new_hospital = models.Hospital(**hospital.model_dump())
        db.add(new_hospital)
        inserted += 1

    db.commit()

    return {
        "message": "Hospital import completed",
        "inserted": inserted,
        "skipped": skipped
    }

@app.get("/recommend-hospitals")
def recommend_hospitals(
    department: str,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):

    # Validate user coordinates
    if not -90 <= latitude <= 90:
        raise HTTPException(
            status_code=400,
            detail="Invalid latitude"
        )

    if not -180 <= longitude <= 180:
        raise HTTPException(
            status_code=400,
            detail="Invalid longitude"
        )

    # Get hospitals from PostgreSQL
    hospitals = db.query(models.Hospital).all()

    recommended = []

    # Filter hospitals by department
    for hospital in hospitals:

        departments = [
            d.strip().lower()
            for d in hospital.departments.split(";")
        ]

        if department.strip().lower() in departments:

            distance = calculate_distance(
                latitude,
                longitude,
                hospital.latitude,
                hospital.longitude
            )

            recommended.append({
                "hospital_id": hospital.hospital_id,
                "hospital_name": hospital.hospital_name,
                "area": hospital.area,
                "address": hospital.address,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude,
                "departments": hospital.departments,
                "emergency_available": hospital.emergency_available,
                "specialist_available": hospital.specialist_available,
                "specialist_status": hospital.specialist_status,
                "distance_km": round(distance, 2)
            })

    # Sort nearest hospitals first
    recommended.sort(
        key=lambda hospital: hospital["distance_km"]
    )

    return {
        "selected_department": department,
        "total_recommended": len(recommended),
        "hospitals": recommended
    }