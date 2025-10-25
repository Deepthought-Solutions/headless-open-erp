# Architecture Refactoring Guide: Moving to True Clean Architecture

## Executive Summary

This document outlines how to fix the architectural violations identified in the current codebase and migrate to a true Clean Architecture implementation. The current system is an ORM-first layered architecture masquerading as Clean Architecture.

**Estimated Effort:** Large (4-6 weeks for complete refactoring)
**Risk Level:** High (requires touching most of the codebase)
**Recommended Approach:** Incremental migration with feature flagging

---

## Critical Issues to Fix

### 1. **Domain Layer Depends on Infrastructure** 🔴 CRITICAL

**Current State:**
```python
# domain/orm.py:7
from infrastructure.database import Base
```

**The Problem:** Domain imports infrastructure, inverting the dependency rule.

**Solution:**

#### Step 1: Create Pure Domain Entities

Create new directory: `domain/entities/`

```python
# domain/entities/lead.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Lead:
    """Pure domain entity - no framework dependencies"""
    id: Optional[int]
    submission_date: datetime
    estimated_users: Optional[int]
    problem_summary: Optional[str]
    maturity_score: Optional[int]

    # Value objects (not IDs)
    contact: 'Contact'
    company: 'Company'
    status: 'LeadStatus'
    urgency: 'LeadUrgency'
    recommended_pack: Optional['RecommendedPack']
    positions: List['Position']
    concerns: List['Concern']

    def calculate_potential_score(self) -> int:
        """Business logic in domain entity"""
        score = 0

        if self.company and self.company.size:
            if self.company.size > 1000:
                score += 3
            elif self.company.size > 250:
                score += 2
            else:
                score += 1

        if self.urgency and self.urgency.name == "immédiat":
            score += 3
        elif self.urgency and self.urgency.name == "ce mois":
            score += 2

        if self.contact and self.contact.job_title:
            executive_roles = {'ceo', 'cto', 'manager', 'director'}
            if any(role in self.contact.job_title.lower() for role in executive_roles):
                score += 2

        return score

@dataclass
class Contact:
    id: Optional[int]
    name: str
    email: str
    phone: Optional[str]
    job_title: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Company:
    id: Optional[int]
    name: str
    size: Optional[int]

# ... etc for other entities
```

#### Step 2: Create Repository Interfaces in Domain

```python
# domain/repositories/lead_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.lead import Lead

class LeadRepository(ABC):
    """Abstract repository - domain defines interface, infrastructure implements"""

    @abstractmethod
    def save(self, lead: Lead) -> Lead:
        """Persist a lead"""
        pass

    @abstractmethod
    def find_by_id(self, lead_id: int) -> Optional[Lead]:
        """Find lead by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[Lead]:
        """Get all leads"""
        pass

    @abstractmethod
    def update(self, lead: Lead) -> Lead:
        """Update existing lead"""
        pass

class ContactRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional['Contact']:
        pass

    @abstractmethod
    def save(self, contact: 'Contact') -> 'Contact':
        pass

# ... etc
```

#### Step 3: Move ORM Models to Infrastructure

```python
# infrastructure/persistence/models/lead_model.py
from sqlalchemy import Column, Integer, String, DateTime, func, Text, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database import Base

class LeadModel(Base):
    """ORM Model - infrastructure concern"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    submission_date = Column(DateTime(timezone=True), server_default=func.now())
    estimated_users = Column(Integer, nullable=True)
    problem_summary = Column(Text, nullable=True)

    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # ... rest of ORM definition

    contact = relationship("ContactModel", back_populates="leads")
    company = relationship("CompanyModel", back_populates="leads")
    # ... etc
```

#### Step 4: Create Mappers

```python
# infrastructure/persistence/mappers/lead_mapper.py
from domain.entities.lead import Lead, Contact, Company
from infrastructure.persistence.models.lead_model import LeadModel, ContactModel, CompanyModel

class LeadMapper:
    """Maps between domain entities and ORM models"""

    @staticmethod
    def to_domain(model: LeadModel) -> Lead:
        """Convert ORM model to domain entity"""
        return Lead(
            id=model.id,
            submission_date=model.submission_date,
            estimated_users=model.estimated_users,
            problem_summary=model.problem_summary,
            maturity_score=model.maturity_score,
            contact=ContactMapper.to_domain(model.contact),
            company=CompanyMapper.to_domain(model.company),
            status=LeadStatusMapper.to_domain(model.status),
            urgency=LeadUrgencyMapper.to_domain(model.urgency),
            recommended_pack=RecommendedPackMapper.to_domain(model.recommended_pack) if model.recommended_pack else None,
            positions=[PositionMapper.to_domain(p) for p in model.positions],
            concerns=[ConcernMapper.to_domain(c) for c in model.concerns]
        )

    @staticmethod
    def to_model(entity: Lead) -> LeadModel:
        """Convert domain entity to ORM model"""
        model = LeadModel(
            id=entity.id,
            submission_date=entity.submission_date,
            estimated_users=entity.estimated_users,
            problem_summary=entity.problem_summary,
            maturity_score=entity.maturity_score
        )
        # Note: relationships handled separately in repository
        return model
```

#### Step 5: Implement Repository in Infrastructure

```python
# infrastructure/persistence/repositories/sqlalchemy_lead_repository.py
from sqlalchemy.orm import Session, joinedload
from domain.repositories.lead_repository import LeadRepository
from domain.entities.lead import Lead
from infrastructure.persistence.models.lead_model import LeadModel
from infrastructure.persistence.mappers.lead_mapper import LeadMapper

class SqlAlchemyLeadRepository(LeadRepository):
    """Concrete implementation using SQLAlchemy"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, lead: Lead) -> Lead:
        model = LeadMapper.to_model(lead)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return LeadMapper.to_domain(model)

    def find_by_id(self, lead_id: int) -> Optional[Lead]:
        model = self._session.query(LeadModel).options(
            joinedload(LeadModel.contact),
            joinedload(LeadModel.company),
            joinedload(LeadModel.status),
            joinedload(LeadModel.urgency),
            joinedload(LeadModel.recommended_pack),
            joinedload(LeadModel.positions),
            joinedload(LeadModel.concerns)
        ).filter(LeadModel.id == lead_id).one_or_none()

        return LeadMapper.to_domain(model) if model else None

    def find_all(self) -> List[Lead]:
        models = self._session.query(LeadModel).options(
            joinedload(LeadModel.contact),
            joinedload(LeadModel.company),
            joinedload(LeadModel.status),
            joinedload(LeadModel.urgency),
            joinedload(LeadModel.recommended_pack),
            joinedload(LeadModel.positions),
            joinedload(LeadModel.concerns)
        ).all()

        return [LeadMapper.to_domain(m) for m in models]

    def update(self, lead: Lead) -> Lead:
        model = self._session.query(LeadModel).filter(
            LeadModel.id == lead.id
        ).one_or_none()

        if not model:
            raise ValueError(f"Lead {lead.id} not found")

        # Update fields
        model.problem_summary = lead.problem_summary
        model.estimated_users = lead.estimated_users
        # ... etc

        self._session.commit()
        self._session.refresh(model)
        return LeadMapper.to_domain(model)
```

---

### 2. **Remove Pydantic from Domain Layer** 🟠 HIGH

**Current State:**
```python
# domain/contact.py
from pydantic import BaseModel, EmailStr
```

**The Problem:** Pydantic is a web framework concern. Domain should be framework-agnostic.

**Solution:**

#### Step 1: Move Request/Response DTOs to Infrastructure

```python
# infrastructure/web/dtos/lead_dto.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class LeadPayloadDTO(BaseModel):
    """HTTP Request DTO - infrastructure concern"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company_name: str
    company_size: Optional[int] = None
    positions: List[str]
    concerns: List[str]
    problem_summary: Optional[str] = None
    estimated_users: Optional[int] = None
    urgency: str
    conscent: bool

class LeadRequestDTO(BaseModel):
    lead: LeadPayloadDTO
    altcha: str

class LeadResponseDTO(BaseModel):
    id: int
    submission_date: datetime
    status: str
    urgency: str
    # ... etc

    class Config:
        from_attributes = True
```

#### Step 2: Create DTO Mappers

```python
# infrastructure/web/mappers/lead_dto_mapper.py
from domain.entities.lead import Lead
from infrastructure.web.dtos.lead_dto import LeadResponseDTO

class LeadDTOMapper:
    @staticmethod
    def to_response_dto(entity: Lead) -> LeadResponseDTO:
        """Convert domain entity to HTTP response DTO"""
        return LeadResponseDTO(
            id=entity.id,
            submission_date=entity.submission_date,
            status=entity.status.name,
            urgency=entity.urgency.name,
            # ... etc
        )
```

---

### 3. **Implement Domain Services for Business Logic** 🟠 HIGH

**Current Problem:** Business logic scattered across application services and ORM models.

**Solution:**

```python
# domain/services/lead_scoring_service.py
from domain.entities.lead import Lead
from domain.value_objects.lead_payload import LeadPayload

class LeadScoringService:
    """Domain service for lead scoring business logic"""

    def calculate_maturity_score(self, payload: LeadPayload) -> int:
        """Pure business logic - no dependencies"""
        score = 0

        if payload.company_size and payload.company_size > 100:
            score += 1
        if payload.estimated_users and payload.estimated_users > 50:
            score += 1
        if len(payload.concerns) > 2:
            score += 1
        if payload.job_title and any(
            role in payload.job_title.lower()
            for role in ['manager', 'director', 'cto', 'ceo']
        ):
            score += 1

        return min(score, 5)

    def recommend_pack(self, concerns: List[str]) -> str:
        """Business rule for pack recommendation"""
        if any("confiance" in c.lower() for c in concerns):
            return "confiance"
        elif any("croissance" in c.lower() for c in concerns):
            return "croissance"
        return "conformité"
```

---

### 4. **Refactor Application Services** 🟠 HIGH

**Current Problem:** Services do everything - data access, business logic, orchestration.

**Solution:**

```python
# application/use_cases/create_lead_use_case.py
from domain.repositories.lead_repository import LeadRepository
from domain.repositories.contact_repository import ContactRepository
from domain.repositories.company_repository import CompanyRepository
from domain.services.lead_scoring_service import LeadScoringService
from domain.entities.lead import Lead
from domain.value_objects.lead_payload import LeadPayload

class CreateLeadUseCase:
    """Application service - orchestrates use case"""

    def __init__(
        self,
        lead_repository: LeadRepository,
        contact_repository: ContactRepository,
        company_repository: CompanyRepository,
        scoring_service: LeadScoringService
    ):
        # Depends on abstractions (repository interfaces)
        self._lead_repo = lead_repository
        self._contact_repo = contact_repository
        self._company_repo = company_repository
        self._scoring_service = scoring_service

    def execute(self, payload: LeadPayload) -> Lead:
        """Execute use case - pure orchestration"""

        # Get or create contact
        contact = self._contact_repo.find_by_email(payload.email)
        if not contact:
            contact = Contact(
                id=None,
                name=payload.name,
                email=payload.email,
                phone=payload.phone,
                job_title=payload.job_title,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            contact = self._contact_repo.save(contact)

        # Get or create company
        company = self._company_repo.find_by_name(payload.company_name)
        if not company:
            company = Company(
                id=None,
                name=payload.company_name,
                size=payload.company_size
            )
            company = self._company_repo.save(company)

        # Use domain service for scoring
        maturity_score = self._scoring_service.calculate_maturity_score(payload)
        recommended_pack = self._scoring_service.recommend_pack(payload.concerns)

        # Create domain entity
        lead = Lead(
            id=None,
            submission_date=datetime.now(),
            estimated_users=payload.estimated_users,
            problem_summary=payload.problem_summary,
            maturity_score=maturity_score,
            contact=contact,
            company=company,
            status=LeadStatus(name="nouveau"),
            urgency=LeadUrgency(name=payload.urgency),
            recommended_pack=RecommendedPack(name=recommended_pack),
            positions=[],
            concerns=[]
        )

        # Save via repository
        return self._lead_repo.save(lead)
```

---

### 5. **Fix FastAPI Dependencies** 🟡 MEDIUM

**Current Problem:** Direct instantiation of services with SQLAlchemy sessions.

**Solution:**

```python
# infrastructure/web/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal
from domain.repositories.lead_repository import LeadRepository
from infrastructure.persistence.repositories.sqlalchemy_lead_repository import SqlAlchemyLeadRepository
from application.use_cases.create_lead_use_case import CreateLeadUseCase
from domain.services.lead_scoring_service import LeadScoringService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_lead_repository(db: Session = Depends(get_db)) -> LeadRepository:
    """Return repository interface, hide implementation"""
    return SqlAlchemyLeadRepository(db)

def get_contact_repository(db: Session = Depends(get_db)) -> ContactRepository:
    return SqlAlchemyContactRepository(db)

def get_company_repository(db: Session = Depends(get_db)) -> CompanyRepository:
    return SqlAlchemyCompanyRepository(db)

def get_lead_scoring_service() -> LeadScoringService:
    """Domain service - no dependencies"""
    return LeadScoringService()

def get_create_lead_use_case(
    lead_repo: LeadRepository = Depends(get_lead_repository),
    contact_repo: ContactRepository = Depends(get_contact_repository),
    company_repo: CompanyRepository = Depends(get_company_repository),
    scoring_service: LeadScoringService = Depends(get_lead_scoring_service)
) -> CreateLeadUseCase:
    return CreateLeadUseCase(lead_repo, contact_repo, company_repo, scoring_service)
```

```python
# infrastructure/web/app.py (updated)
from infrastructure.web.dtos.lead_dto import LeadRequestDTO, LeadResponseDTO
from infrastructure.web.mappers.lead_dto_mapper import LeadDTOMapper
from application.use_cases.create_lead_use_case import CreateLeadUseCase

@app.post("/lead/", response_model=LeadResponseDTO)
async def create_lead(
    lead_request: LeadRequestDTO,
    use_case: CreateLeadUseCase = Depends(get_create_lead_use_case),
    email_notification_service: EmailNotificationService = Depends(get_email_notification_service)
):
    verify_altcha_solution(lead_request.altcha)

    try:
        # Convert DTO to domain value object
        payload = LeadPayload.from_dto(lead_request.lead)

        # Execute use case
        lead = use_case.execute(payload)

        # Send notification
        try:
            email_notification_service.send_lead_notification_email(
                MAIL_SENDER,
                MAIL_RECIPIENT,
                lead
            )
        except Exception as e:
            logger.exception("Mail notification failed")

        # Convert domain entity to response DTO
        return LeadDTOMapper.to_response_dto(lead)

    except Exception as e:
        logger.exception("Error creating lead")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Migration Strategy

### Phase 1: Preparation (Week 1)
1. Create new directory structure
2. Set up domain entities (parallel to existing ORM models)
3. Write unit tests for domain entities
4. Create repository interfaces

### Phase 2: Infrastructure (Week 2-3)
1. Move ORM models to `infrastructure/persistence/models/`
2. Create mappers between domain and ORM
3. Implement repositories in infrastructure
4. Update database module imports

### Phase 3: Application Layer (Week 3-4)
1. Create use cases
2. Create domain services
3. Write unit tests for use cases (using mock repositories)

### Phase 4: Web Layer (Week 4-5)
1. Move Pydantic DTOs to `infrastructure/web/dtos/`
2. Create DTO mappers
3. Update FastAPI dependencies
4. Update endpoints to use use cases

### Phase 5: Testing & Cleanup (Week 5-6)
1. Update all integration tests
2. Remove old service files
3. Remove old domain files
4. Update documentation

### Phase 6: Validation
1. Run full test suite
2. Manual testing
3. Code review

---

## New Directory Structure

```
headless-open-erp/
├── domain/
│   ├── entities/              # Pure domain entities
│   │   ├── lead.py
│   │   ├── contact.py
│   │   ├── company.py
│   │   └── ...
│   ├── value_objects/         # Immutable value objects
│   │   ├── lead_payload.py
│   │   └── ...
│   ├── repositories/          # Repository interfaces (abstractions)
│   │   ├── lead_repository.py
│   │   ├── contact_repository.py
│   │   └── ...
│   ├── services/              # Domain services (business logic)
│   │   ├── lead_scoring_service.py
│   │   └── ...
│   └── exceptions/            # Domain exceptions
│       └── ...
├── application/
│   └── use_cases/             # Application services (orchestration)
│       ├── create_lead_use_case.py
│       ├── get_lead_use_case.py
│       ├── create_note_use_case.py
│       └── ...
├── infrastructure/
│   ├── persistence/
│   │   ├── models/            # ORM models (was domain/orm.py)
│   │   │   ├── lead_model.py
│   │   │   ├── contact_model.py
│   │   │   └── ...
│   │   ├── repositories/      # Repository implementations
│   │   │   ├── sqlalchemy_lead_repository.py
│   │   │   ├── sqlalchemy_contact_repository.py
│   │   │   └── ...
│   │   └── mappers/           # Entity ↔ ORM mappers
│   │       ├── lead_mapper.py
│   │       └── ...
│   ├── web/
│   │   ├── app.py             # FastAPI application
│   │   ├── dependencies.py    # Dependency injection
│   │   ├── dtos/              # Request/Response DTOs (was domain/contact.py)
│   │   │   ├── lead_dto.py
│   │   │   ├── note_dto.py
│   │   │   └── ...
│   │   ├── mappers/           # Entity ↔ DTO mappers
│   │   │   ├── lead_dto_mapper.py
│   │   │   └── ...
│   │   └── auth.py
│   ├── mail/
│   │   └── sender.py
│   └── database.py
├── migrations/
└── tests/
    ├── unit/
    │   ├── domain/            # Test pure domain logic
    │   └── application/       # Test use cases with mocks
    └── integration/           # Test with real database
```

---

## Benefits of This Refactoring

### 1. **Testability**
- Domain logic testable without database
- Use cases testable with mock repositories
- Fast unit tests

### 2. **Maintainability**
- Clear separation of concerns
- Business rules in one place (domain)
- Easy to find and modify code

### 3. **Flexibility**
- Can swap database (SQLAlchemy → MongoDB)
- Can swap web framework (FastAPI → Flask)
- Can add GraphQL API without touching domain

### 4. **Independence**
- Domain has zero dependencies
- Can reuse domain in CLI tools, background jobs, etc.

### 5. **Dependency Rule Compliance**
```
Domain (no dependencies)
   ↑
Application (depends on domain abstractions only)
   ↑
Infrastructure (depends on everything, implements abstractions)
```

---

## Incremental Approach (Minimal Risk)

If full refactoring is too risky, use the **Strangler Fig Pattern**:

### Step 1: Add New Structure Alongside Old
- Keep existing `domain/orm.py`
- Add new `domain/entities/` in parallel
- New features use new structure
- Old features keep using old structure

### Step 2: Migrate One Entity at a Time
- Start with simplest entity (e.g., `Fingerprint`)
- Create entity → mapper → repository → use case
- Update endpoints
- Test thoroughly
- Repeat for next entity

### Step 3: Gradual Deprecation
- Once all features migrated, remove old code
- Update documentation
- Celebrate 🎉

---

## Testing Strategy

### Unit Tests (Fast, Isolated)
```python
# tests/unit/domain/test_lead.py
def test_calculate_potential_score_large_company():
    lead = Lead(
        company=Company(name="BigCorp", size=1500),
        urgency=LeadUrgency(name="immédiat"),
        contact=Contact(job_title="CEO", ...),
        # ...
    )

    assert lead.calculate_potential_score() == 8  # 3 + 3 + 2

# tests/unit/application/test_create_lead_use_case.py
def test_create_lead_with_new_contact():
    # Mock repositories
    lead_repo = Mock(LeadRepository)
    contact_repo = Mock(ContactRepository)
    contact_repo.find_by_email.return_value = None

    use_case = CreateLeadUseCase(lead_repo, contact_repo, ...)
    result = use_case.execute(payload)

    contact_repo.save.assert_called_once()
```

### Integration Tests (Slower, With Database)
```python
# tests/integration/test_create_lead_endpoint.py
def test_create_lead_endpoint(client, db_session):
    response = client.post("/lead/", json={...})
    assert response.status_code == 200

    # Verify in database
    lead = db_session.query(LeadModel).first()
    assert lead.contact.email == "test@example.com"
```

---

## Conclusion

The current architecture has the **form** of Clean Architecture (three layers) but not the **substance** (dependency rule violated, domain coupled to infrastructure).

**Recommendation:**
- For new projects: Start with proper Clean Architecture
- For this project: Use incremental migration (Strangler Fig)
- Start with one entity to prove the pattern works
- Gradually migrate remaining entities

**ROI:**
- Short term: More code, more complexity
- Long term: Easier testing, easier changes, framework independence

The choice depends on project goals and team capacity.
