use headless_api::{
    application::lead_service::LeadService,
    domain::lead::{LeadRequest, LeadPayload, LeadResponse},
};
use axum::{
    routing::post,
    Router,
};
use sqlx::postgres::PgPoolOptions;
use std::{net::SocketAddr, sync::Arc};
use tower_http::cors::{Any, CorsLayer};
use reqwest::StatusCode;

async fn spawn_app() -> SocketAddr {
    dotenv::dotenv().ok();
    let database_url = std::env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPoolOptions::new()
        .max_connections(1)
        .connect(&database_url)
        .await
        .expect("Failed to create pool.");

    // Seed the database
    sqlx::query!("INSERT INTO lead_statuses (name) VALUES ('nouveau') ON CONFLICT (name) DO NOTHING")
        .execute(&pool)
        .await
        .unwrap();
    sqlx::query!("INSERT INTO lead_urgencies (name) VALUES ('ce mois') ON CONFLICT (name) DO NOTHING")
        .execute(&pool)
        .await
        .unwrap();
    sqlx::query!("INSERT INTO recommended_packs (name) VALUES ('conformité') ON CONFLICT (name) DO NOTHING")
        .execute(&pool)
        .await
        .unwrap();
    sqlx::query!("INSERT INTO recommended_packs (name) VALUES ('confiance') ON CONFLICT (name) DO NOTHING")
        .execute(&pool)
        .await
        .unwrap();
    sqlx::query!("INSERT INTO recommended_packs (name) VALUES ('croissance') ON CONFLICT (name) DO NOTHING")
        .execute(&pool)
        .await
        .unwrap();
    sqlx::query!(
        "INSERT INTO fingerprints (\"visitorId\", components) VALUES ($1, '{}') ON CONFLICT (\"visitorId\") DO NOTHING",
        "dummy_visitor_id"
    )
    .execute(&pool)
    .await
    .unwrap();

    let lead_service = Arc::new(LeadService::new(pool.clone()));

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/leads", post(headless_api::infrastructure::web::lead_handler::create_lead))
        .with_state(lead_service)
        .layer(cors);

    let addr = SocketAddr::from(([127, 0, 0, 1], 0));
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    let local_addr = listener.local_addr().unwrap();

    tokio::spawn(async move {
        axum::serve(listener, app.into_make_service()).await.unwrap();
    });

    local_addr
}

#[tokio::test]
async fn test_create_lead_success() {
    let addr = spawn_app().await;
    let client = reqwest::Client::new();

    let payload = LeadPayload {
        name: "Test User".to_string(),
        email: "test.user@example.com".to_string(),
        phone: Some("1234567890".to_string()),
        job_title: Some("Developer".to_string()),
        company_name: "Test Inc.".to_string(),
        company_size: Some(50),
        positions: vec!["Developer".to_string(), "Manager".to_string()],
        concerns: vec!["confiance".to_string(), "sécurité".to_string()],
        problem_summary: Some("This is a test problem".to_string()),
        estimated_users: Some(100),
        urgency: "ce mois".to_string(),
        conscent: true,
    };

    let request = LeadRequest {
        lead: payload,
        altcha: "dummy_altcha_solution".to_string(),
        visitor_id: Some("dummy_visitor_id".to_string()),
    };

    let response = client
        .post(format!("http://{}/leads", addr))
        .json(&request)
        .send()
        .await
        .expect("Failed to execute request.");

    let status = response.status();
    if status != StatusCode::CREATED {
        let body = response.text().await.unwrap();
        panic!("Request failed with status code {}: {}", status, body);
    }

    let lead_response: LeadResponse = response.json().await.unwrap();
    assert_eq!(lead_response.contact.name, "Test User");
    assert_eq!(lead_response.company.name, "Test Inc.");
    assert_eq!(lead_response.urgency.name, "ce mois");
}
