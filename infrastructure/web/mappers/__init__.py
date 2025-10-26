"""DTO mappers - convert between domain entities and HTTP DTOs.

Note: Most response DTOs use Pydantic's from_attributes=True config,
which allows them to work directly with both ORM models and domain entities.

These mappers are provided for cases where custom conversion logic is needed.
"""

# Future: Add custom DTO mappers here if needed
# For now, Pydantic's from_attributes handles most conversions automatically
