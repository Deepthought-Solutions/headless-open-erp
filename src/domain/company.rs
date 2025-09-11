use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Company {
    pub id: i32,
    pub name: String,
    pub size: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CompanyResponse {
    pub name: String,
    pub size: Option<i32>,
}

impl From<Company> for CompanyResponse {
    fn from(company: Company) -> Self {
        Self {
            name: company.name,
            size: company.size,
        }
    }
}
