use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Fingerprint {
    #[sqlx(rename = "visitorId")]
    pub visitor_id: String,
    pub components: Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Deserialize)]
pub struct FingerprintRequest {
    pub altcha: String,
    #[serde(rename = "visitorId")]
    pub visitor_id: String,
    pub components: Value,
}
