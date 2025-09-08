use thiserror::Error;

#[derive(Debug, Error)]
pub enum ApplicationError {
    #[error("Database error: {0}")]
    DatabaseError(#[from] sqlx::Error),
    #[error("Validation error: {0}")]
    ValidationError(String),
    #[error("Not found: {0}")]
    NotFound(String),
    #[error("An unexpected error occurred")]
    UnexpectedError,
}
