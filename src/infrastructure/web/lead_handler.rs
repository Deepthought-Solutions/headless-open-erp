use crate::{
    application::lead_service::LeadService,
    domain::lead::{LeadRequest, LeadResponse},
    infrastructure::web::error::AppError,
};
use axum::{extract::State, http::StatusCode, Json};
use std::sync::Arc;

pub async fn create_lead(
    State(lead_service): State<Arc<LeadService>>,
    Json(payload): Json<LeadRequest>,
) -> Result<(StatusCode, Json<LeadResponse>), AppError> {
    let lead_response = lead_service
        .create_lead(payload.lead, payload.altcha, payload.visitor_id)
        .await?;

    Ok((StatusCode::CREATED, Json(lead_response)))
}
