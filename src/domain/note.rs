use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Note {
    pub id: i32,
    pub note: String,
    pub created_at: DateTime<Utc>,
    pub author_name: String,
    pub lead_id: i32,
    pub reason_id: i32,
}

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct NoteReason {
    pub id: i32,
    pub name: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct NoteReasonResponse {
    pub name: String,
}

impl From<NoteReason> for NoteReasonResponse {
    fn from(reason: NoteReason) -> Self {
        Self { name: reason.name }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct NoteResponse {
    pub id: i32,
    pub note: String,
    pub created_at: DateTime<Utc>,
    pub author_name: String,
    pub reason: NoteReasonResponse,
}

#[derive(Debug, Deserialize)]
pub struct NoteCreateRequest {
    pub note: String,
    pub reason: String,
    #[serde(default)]
    pub send_to_contact: bool,
    #[serde(default)]
    pub send_to_recipients: Vec<String>,
}
