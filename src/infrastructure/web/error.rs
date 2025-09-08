use crate::application::error::ApplicationError;
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

pub struct AppError(ApplicationError);

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, error_message) = match self.0 {
            ApplicationError::DatabaseError(ref e) => (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()),
            ApplicationError::ValidationError(ref msg) => (StatusCode::BAD_REQUEST, msg.to_string()),
            ApplicationError::NotFound(ref msg) => (StatusCode::NOT_FOUND, msg.to_string()),
            ApplicationError::UnexpectedError => (StatusCode::INTERNAL_SERVER_ERROR, "An unexpected error occurred".to_string()),
        };

        let body = Json(json!({ "error": error_message }));
        (status, body).into_response()
    }
}

impl From<ApplicationError> for AppError {
    fn from(error: ApplicationError) -> Self {
        AppError(error)
    }
}
