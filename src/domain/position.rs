use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Position {
    pub id: i32,
    pub title: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PositionResponse {
    pub title: String,
}

impl From<Position> for PositionResponse {
    fn from(position: Position) -> Self {
        Self {
            title: position.title,
        }
    }
}
