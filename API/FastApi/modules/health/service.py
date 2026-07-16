import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from FastApi.modules.health.repository import (
    MedicalConditionRepository,
    MedicationRepository,
    SymptomRepository,
    VaccineRepository,
    VetVisitRepository,
    WeightRecordRepository,
)
from FastApi.modules.health.schemas import (
    MedicalConditionCreate,
    MedicalConditionResponse,
    MedicalConditionUpdate,
    MedicationCreate,
    MedicationResponse,
    MedicationUpdate,
    SymptomCreate,
    SymptomResponse,
    SymptomUpdate,
    VaccineCreate,
    VaccineResponse,
    VaccineUpdate,
    VetVisitCreate,
    VetVisitResponse,
    VetVisitUpdate,
    WeightRecordCreate,
    WeightRecordResponse,
    WeightRecordUpdate,
)


class WeightRecordService:
    def __init__(self, db: AsyncSession):
        self.repo = WeightRecordRepository(db)

    async def get_by_id(self, record_id: uuid.UUID) -> WeightRecordResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Weight record not found")
        return WeightRecordResponse.model_validate(record)

    async def get_by_pet_id(self, pet_id: uuid.UUID) -> list[WeightRecordResponse]:
        records = await self.repo.get_by_pet_id(pet_id)
        return [WeightRecordResponse.model_validate(record) for record in records]

    async def create(self, record_create: WeightRecordCreate) -> WeightRecordResponse:
        record = await self.repo.create(
            pet_id=record_create.pet_id,
            weight=record_create.weight,
            record_date=record_create.record_date,
            description=record_create.description,
        )
        return WeightRecordResponse.model_validate(record)

    async def update(self, record_id: uuid.UUID, record_update: WeightRecordUpdate) -> WeightRecordResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Weight record not found")
        fields = record_update.model_dump(exclude_unset=True)
        updated_record = await self.repo.update(record, **fields)
        return WeightRecordResponse.model_validate(updated_record)

    async def delete(self, record_id: uuid.UUID) -> None:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Weight record not found")
        await self.repo.delete(record)


class VaccineService:
    def __init__(self, db: AsyncSession):
        self.repo = VaccineRepository(db)

    async def get_by_id(self, record_id: uuid.UUID) -> VaccineResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vaccine record not found")
        return VaccineResponse.model_validate(record)
    
    async def get_by_pet_id(self, pet_id: uuid.UUID) -> list[VaccineResponse]:
        records = await self.repo.get_by_pet_id(pet_id)
        return [VaccineResponse.model_validate(record) for record in records]
    
    async def create(self, record_create: VaccineCreate) -> VaccineResponse:
        record = await self.repo.create(
            pet_id=record_create.pet_id,
            vaccine_name=record_create.vaccine_name,
            next_due_date=record_create.next_due_date,
            record_date=record_create.record_date,
            description=record_create.description
        )
        return VaccineResponse.model_validate(record)
    
    async def update(self, record_id: uuid.UUID, record_update: VaccineUpdate) -> VaccineResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vaccine record not found")
        fields = record_update.model_dump(exclude_unset=True)
        updated_record = await self.repo.update(record, **fields)
        return VaccineResponse.model_validate(updated_record)

    async def delete(self, record_id: uuid.UUID) -> None:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vaccine record not found")
        await self.repo.delete(record)


class MedicalConditionService:
    def __init__(self, db: AsyncSession):
        self.repo = MedicalConditionRepository(db)

    async def get_by_id(self, record_id: uuid.UUID) -> MedicalConditionResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical condition not found")
        return MedicalConditionResponse.model_validate(record)

    async def get_by_pet_id(self, pet_id: uuid.UUID) -> list[MedicalConditionResponse]:
        records = await self.repo.get_by_pet_id(pet_id)
        return [MedicalConditionResponse.model_validate(record) for record in records]

    async def create(self, record_create: MedicalConditionCreate) -> MedicalConditionResponse:
        record = await self.repo.create(
            pet_id=record_create.pet_id,
            condition_name=record_create.condition_name,
            treatment_plan=record_create.treatment_plan,
            record_date=record_create.record_date,
            description=record_create.description,
        )
        return MedicalConditionResponse.model_validate(record)

    async def update(
        self, record_id: uuid.UUID, record_update: MedicalConditionUpdate
    ) -> MedicalConditionResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical condition not found")
        fields = record_update.model_dump(exclude_unset=True)
        updated_record = await self.repo.update(record, **fields)
        return MedicalConditionResponse.model_validate(updated_record)

    async def delete(self, record_id: uuid.UUID) -> None:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medical condition not found")
        await self.repo.delete(record)


class MedicationService:
    def __init__(self, db: AsyncSession):
        self.repo = MedicationRepository(db)

    async def get_by_id(self, record_id: uuid.UUID) -> MedicationResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medication not found")
        return MedicationResponse.model_validate(record)

    async def get_by_pet_id(self, pet_id: uuid.UUID) -> list[MedicationResponse]:
        records = await self.repo.get_by_pet_id(pet_id)
        return [MedicationResponse.model_validate(record) for record in records]

    async def create(self, record_create: MedicationCreate) -> MedicationResponse:
        record = await self.repo.create(
            pet_id=record_create.pet_id,
            medication_name=record_create.medication_name,
            dosage=record_create.dosage,
            frequency=record_create.frequency,
            record_date=record_create.record_date,
            description=record_create.description,
        )
        return MedicationResponse.model_validate(record)

    async def update(self, record_id: uuid.UUID, record_update: MedicationUpdate) -> MedicationResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medication not found")
        fields = record_update.model_dump(exclude_unset=True)
        updated_record = await self.repo.update(record, **fields)
        return MedicationResponse.model_validate(updated_record)

    async def delete(self, record_id: uuid.UUID) -> None:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medication not found")
        await self.repo.delete(record)


class SymptomService:
    def __init__(self, db: AsyncSession):
        self.repo = SymptomRepository(db)

    async def get_by_id(self, record_id: uuid.UUID) -> SymptomResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Symptom not found")
        return SymptomResponse.model_validate(record)

    async def get_by_pet_id(self, pet_id: uuid.UUID) -> list[SymptomResponse]:
        records = await self.repo.get_by_pet_id(pet_id)
        return [SymptomResponse.model_validate(record) for record in records]

    async def create(self, record_create: SymptomCreate) -> SymptomResponse:
        record = await self.repo.create(
            pet_id=record_create.pet_id,
            symptom_name=record_create.symptom_name,
            severity=record_create.severity,
            notes=record_create.notes,
            record_date=record_create.record_date,
            description=record_create.description,
        )
        return SymptomResponse.model_validate(record)

    async def update(self, record_id: uuid.UUID, record_update: SymptomUpdate) -> SymptomResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Symptom not found")
        fields = record_update.model_dump(exclude_unset=True)
        updated_record = await self.repo.update(record, **fields)
        return SymptomResponse.model_validate(updated_record)

    async def delete(self, record_id: uuid.UUID) -> None:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Symptom not found")
        await self.repo.delete(record)


class VetVisitService:
    def __init__(self, db: AsyncSession):
        self.repo = VetVisitRepository(db)

    async def get_by_id(self, record_id: uuid.UUID) -> VetVisitResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vet visit not found")
        return VetVisitResponse.model_validate(record)

    async def get_by_pet_id(self, pet_id: uuid.UUID) -> list[VetVisitResponse]:
        records = await self.repo.get_by_pet_id(pet_id)
        return [VetVisitResponse.model_validate(record) for record in records]

    async def create(self, record_create: VetVisitCreate) -> VetVisitResponse:
        record = await self.repo.create(
            pet_id=record_create.pet_id,
            vet_name=record_create.vet_name,
            visit_reason=record_create.visit_reason,
            notes=record_create.notes,
            record_date=record_create.record_date,
            description=record_create.description,
        )
        return VetVisitResponse.model_validate(record)

    async def update(self, record_id: uuid.UUID, record_update: VetVisitUpdate) -> VetVisitResponse:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vet visit not found")
        fields = record_update.model_dump(exclude_unset=True)
        updated_record = await self.repo.update(record, **fields)
        return VetVisitResponse.model_validate(updated_record)

    async def delete(self, record_id: uuid.UUID) -> None:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vet visit not found")
        await self.repo.delete(record)