use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Concern {
    pub id: i32,
    pub label: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ConcernResponse {
    pub label: Option<String>,
}

impl From<Concern> for ConcernResponse {
    fn from(concern: Concern) -> Self {
        Self {
            label: concern.label,
        }
    }
}
