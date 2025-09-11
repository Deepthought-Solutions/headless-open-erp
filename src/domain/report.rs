use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Report {
    pub id: i32,
    #[sqlx(rename = "visitorId")]
    pub visitor_id: String,
    pub page: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Deserialize)]
pub struct ReportRequest {
    pub altcha: String,
    #[serde(rename = "visitorId")]
    pub visitor_id: String,
    pub page: String,
}
