use crate::{
    application::error::ApplicationError,
    domain::{
        company::{Company, CompanyResponse},
        concern::{Concern, ConcernResponse},
        contact::{Contact, ContactResponse},
        lead::*,
        position::{Position, PositionResponse},
    },
};
use sqlx::PgPool;
use tracing::{info, error};

pub struct LeadService {
    pool: PgPool,
}

impl LeadService {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    fn calculate_maturity_score(&self, payload: &LeadPayload) -> i32 {
        let mut score = 0;
        if let Some(company_size) = payload.company_size {
            if company_size > 100 {
                score += 1;
            }
        }
        if let Some(estimated_users) = payload.estimated_users {
            if estimated_users > 50 {
                score += 1;
            }
        }
        if payload.concerns.len() > 2 {
            score += 1;
        }
        if let Some(job_title) = &payload.job_title {
            let title = job_title.to_lowercase();
            if title.contains("manager")
                || title.contains("director")
                || title.contains("cto")
                || title.contains("ceo")
            {
                score += 1;
            }
        }
        score.min(5)
    }

    pub async fn create_lead(
        &self,
        lead_payload: LeadPayload,
        altcha: String,
        visitor_id: Option<String>,
    ) -> Result<LeadResponse, ApplicationError> {
        info!("Starting create_lead transaction");
        let mut tx = self.pool.begin().await?;

        info!("Fetching contact");
        let contact = sqlx::query_as!(
            Contact,
            "SELECT * FROM contacts WHERE email = $1",
            &lead_payload.email
        )
        .fetch_optional(&mut *tx)
        .await?;

        let contact = if let Some(mut contact) = contact {
            info!("Updating existing contact");
            contact.name = lead_payload.name.clone();
            contact.phone = lead_payload.phone.as_ref().map(|s| s.to_string());
            contact.job_title = lead_payload.job_title.as_ref().map(|s| s.to_string());
            sqlx::query!(
                "UPDATE contacts SET name = $1, phone = $2, job_title = $3, updated_at = NOW() WHERE id = $4",
                contact.name,
                contact.phone,
                contact.job_title,
                contact.id
            )
            .execute(&mut *tx)
            .await?;
            contact
        } else {
            info!("Creating new contact");
            sqlx::query_as!(
                Contact,
                "INSERT INTO contacts (name, email, phone, job_title) VALUES ($1, $2, $3, $4) RETURNING *",
                lead_payload.name,
                lead_payload.email,
                lead_payload.phone,
                lead_payload.job_title
            )
            .fetch_one(&mut *tx)
            .await?
        };

        info!("Fetching company");
        let company = sqlx::query_as!(
            Company,
            "SELECT * FROM companies WHERE name = $1",
            &lead_payload.company_name
        )
        .fetch_optional(&mut *tx)
        .await?;

        let company = if let Some(mut company) = company {
            info!("Updating existing company");
            company.size = lead_payload.company_size;
            sqlx::query!(
                "UPDATE companies SET size = $1 WHERE id = $2",
                company.size,
                company.id
            )
            .execute(&mut *tx)
            .await?;
            company
        } else {
            info!("Creating new company");
            sqlx::query_as!(
                Company,
                "INSERT INTO companies (name, size) VALUES ($1, $2) RETURNING *",
                lead_payload.company_name,
                lead_payload.company_size
            )
            .fetch_one(&mut *tx)
            .await?
        };

        let maturity_score = self.calculate_maturity_score(&lead_payload);

        let pack_name = if lead_payload.concerns.iter().any(|c| c.contains("confiance")) {
            "confiance"
        } else if lead_payload.concerns.iter().any(|c| c.contains("croissance")) {
            "croissance"
        } else {
            "conformité"
        };
        info!("Fetching recommended pack");
        let recommended_pack = sqlx::query_as!(
            RecommendedPack,
            "SELECT * FROM recommended_packs WHERE name = $1",
            pack_name
        )
        .fetch_one(&mut *tx)
        .await?;

        info!("Fetching urgency");
        let urgency = sqlx::query_as!(
            LeadUrgency,
            "SELECT * FROM lead_urgencies WHERE name = $1",
            &lead_payload.urgency
        )
        .fetch_one(&mut *tx)
        .await?;

        info!("Fetching status");
        let status = sqlx::query_as!(
            LeadStatus,
            "SELECT * FROM lead_statuses WHERE name = 'nouveau'"
        )
        .fetch_one(&mut *tx)
        .await?;

        info!("Creating lead");
        let lead = sqlx::query_as!(
            Lead,
            r#"
            INSERT INTO leads (
                contact_id, company_id, problem_summary, estimated_users, urgency_id,
                status_id, maturity_score, recommended_pack_id, altcha_solution,
                fingerprint_visitor_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING *
            "#,
            contact.id,
            company.id,
            lead_payload.problem_summary,
            lead_payload.estimated_users,
            urgency.id,
            status.id,
            maturity_score,
            recommended_pack.id,
            altcha,
            visitor_id
        )
        .fetch_one(&mut *tx)
        .await.map_err(|e| {
            error!("Failed to create lead: {}", e);
            e
        })?;

        let mut positions = Vec::new();
        for position_title in &lead_payload.positions {
            info!("Fetching position: {}", position_title);
            let position = sqlx::query_as!(
                Position,
                "SELECT * FROM positions WHERE title = $1",
                position_title
            )
            .fetch_optional(&mut *tx)
            .await?;

            let position = if let Some(position) = position {
                position
            } else {
                info!("Creating new position: {}", position_title);
                sqlx::query_as!(
                    Position,
                    "INSERT INTO positions (title) VALUES ($1) RETURNING *",
                    position_title
                )
                .fetch_one(&mut *tx)
                .await?
            };

            info!("Linking position to lead");
            sqlx::query!(
                "INSERT INTO lead_positions (lead_id, position_id) VALUES ($1, $2)",
                lead.id,
                position.id
            )
            .execute(&mut *tx)
            .await?;
            positions.push(position);
        }

        let mut concerns = Vec::new();
        for concern_label in &lead_payload.concerns {
            info!("Fetching concern: {}", concern_label);
            let concern = sqlx::query_as!(
                Concern,
                "SELECT * FROM concerns WHERE label = $1",
                concern_label
            )
            .fetch_optional(&mut *tx)
            .await?;

            let concern = if let Some(concern) = concern {
                concern
            } else {
                info!("Creating new concern: {}", concern_label);
                sqlx::query_as!(
                    Concern,
                    "INSERT INTO concerns (label) VALUES ($1) RETURNING *",
                    concern_label
                )
                .fetch_one(&mut *tx)
                .await?
            };

            info!("Linking concern to lead");
            sqlx::query!(
                "INSERT INTO lead_concerns (lead_id, concern_id) VALUES ($1, $2)",
                lead.id,
                concern.id
            )
            .execute(&mut *tx)
            .await?;
            concerns.push(concern);
        }

        let potential_score = calculate_potential_score(&company, &urgency, &contact);

        info!("Committing transaction");
        tx.commit().await?;

        let response = LeadResponse {
            id: lead.id,
            submission_date: lead.submission_date,
            status: status.into(),
            urgency: urgency.into(),
            recommended_pack: Some(recommended_pack.into()),
            maturity_score: Some(lead.maturity_score.unwrap_or(0)),
            potential_score: Some(potential_score),
            estimated_users: lead.estimated_users,
            problem_summary: lead.problem_summary,
            contact: contact.into(),
            company: company.into(),
            positions: positions.into_iter().map(|p| p.into()).collect(),
            concerns: concerns.into_iter().map(|c| c.into()).collect(),
        };

        Ok(response)
    }
}
