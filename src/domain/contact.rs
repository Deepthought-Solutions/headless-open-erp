use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Contact {
    pub id: i32,
    pub name: String,
    pub email: String,
    pub phone: Option<String>,
    pub job_title: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ContactResponse {
    pub id: i32,
    pub name: String,
    pub email: String,
    pub phone: Option<String>,
    pub job_title: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl From<Contact> for ContactResponse {
    fn from(contact: Contact) -> Self {
        Self {
            id: contact.id,
            name: contact.name,
            email: contact.email,
            phone: contact.phone,
            job_title: contact.job_title,
            created_at: contact.created_at,
            updated_at: contact.updated_at,
        }
    }
}
