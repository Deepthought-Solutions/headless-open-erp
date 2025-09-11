use super::{
    company::{Company, CompanyResponse},
    concern::{Concern, ConcernResponse},
    contact::{Contact, ContactResponse},
    position::{Position, PositionResponse},
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

// Database Models

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct LeadStatus {
    pub id: i32,
    pub name: String,
}

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct LeadUrgency {
    pub id: i32,
    pub name: String,
}

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct RecommendedPack {
    pub id: i32,
    pub name: String,
}

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct Lead {
    pub id: i32,
    pub submission_date: DateTime<Utc>,
    pub estimated_users: Option<i32>,
    pub problem_summary: Option<String>,
    pub contact_id: i32,
    pub company_id: i32,
    pub recommended_pack_id: Option<i32>,
    pub maturity_score: Option<i32>,
    pub urgency_id: Option<i32>,
    pub status_id: i32,
    pub fingerprint_visitor_id: Option<String>,
    pub altcha_solution: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct LeadPosition {
    pub lead_id: i32,
    pub position_id: i32,
}

#[derive(Debug, Clone, FromRow, Serialize, Deserialize)]
pub struct LeadConcern {
    pub lead_id: i32,
    pub concern_id: i32,
}

// Request Models

#[derive(Debug, Serialize, Deserialize)]
pub struct LeadPayload {
    pub name: String,
    pub email: String,
    pub phone: Option<String>,
    pub job_title: Option<String>,
    pub company_name: String,
    pub company_size: Option<i32>,
    pub positions: Vec<String>,
    pub concerns: Vec<String>,
    pub problem_summary: Option<String>,
    pub estimated_users: Option<i32>,
    pub urgency: String,
    pub conscent: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LeadRequest {
    pub lead: LeadPayload,
    pub altcha: String,
    #[serde(rename = "visitorId")]
    pub visitor_id: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct LeadUpdateRequest {
    pub name: Option<String>,
    pub email: Option<String>,
    pub phone: Option<String>,
    pub job_title: Option<String>,
    pub company_name: Option<String>,
    pub company_size: Option<i32>,
    pub positions: Option<Vec<String>>,
    pub concerns: Option<Vec<String>>,
    pub problem_summary: Option<String>,
    pub estimated_users: Option<i32>,
    pub urgency: Option<String>,
    pub conscent: Option<bool>,
    pub altcha: String,
    #[serde(rename = "visitorId")]
    pub visitor_id: String,
}

// Response Models

#[derive(Debug, Serialize, Deserialize)]
pub struct LeadStatusResponse {
    pub name: String,
}
impl From<LeadStatus> for LeadStatusResponse {
    fn from(status: LeadStatus) -> Self {
        Self { name: status.name }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LeadUrgencyResponse {
    pub name: String,
}
impl From<LeadUrgency> for LeadUrgencyResponse {
    fn from(urgency: LeadUrgency) -> Self {
        Self { name: urgency.name }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RecommendedPackResponse {
    pub name: String,
}
impl From<RecommendedPack> for RecommendedPackResponse {
    fn from(pack: RecommendedPack) -> Self {
        Self { name: pack.name }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LeadResponse {
    pub id: i32,
    pub submission_date: DateTime<Utc>,
    pub status: LeadStatusResponse,
    pub urgency: LeadUrgencyResponse,
    pub recommended_pack: Option<RecommendedPackResponse>,
    pub maturity_score: Option<i32>,
    pub potential_score: Option<i32>,
    pub estimated_users: Option<i32>,
    pub problem_summary: Option<String>,
    pub contact: ContactResponse,
    pub company: CompanyResponse,
    pub positions: Vec<PositionResponse>,
    pub concerns: Vec<ConcernResponse>,
}

// This is not a direct mapping from a single struct, so it will be constructed in the service layer.
// We still need a way to calculate potential_score. We can create a helper function or a method.

pub fn calculate_potential_score(
    company: &Company,
    urgency: &LeadUrgency,
    contact: &Contact,
) -> i32 {
    let mut score = 0;
    if let Some(size) = company.size {
        if size > 1000 {
            score += 3;
        } else if size > 250 {
            score += 2;
        } else {
            score += 1;
        }
    }

    if urgency.name == "immédiat" {
        score += 3;
    } else if urgency.name == "ce mois" {
        score += 2;
    }

    if let Some(job_title) = &contact.job_title {
        let title = job_title.to_lowercase();
        if title.contains("ceo")
            || title.contains("cto")
            || title.contains("manager")
            || title.contains("director")
        {
            score += 2;
        }
    }

    score
}
