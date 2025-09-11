-- V1__initial.sql

CREATE TABLE lead_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE lead_urgencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE recommended_packs (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    phone VARCHAR,
    job_title VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    size INTEGER
);

CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    title VARCHAR UNIQUE NOT NULL
);

CREATE TABLE sectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE
);

CREATE TABLE concerns (
    id SERIAL PRIMARY KEY,
    label VARCHAR UNIQUE
);

CREATE TABLE fingerprints (
    "visitorId" VARCHAR PRIMARY KEY,
    components JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    submission_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    estimated_users INTEGER,
    problem_summary TEXT,
    contact_id INTEGER NOT NULL REFERENCES contacts(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    recommended_pack_id INTEGER REFERENCES recommended_packs(id),
    maturity_score INTEGER,
    urgency_id INTEGER REFERENCES lead_urgencies(id),
    status_id INTEGER NOT NULL REFERENCES lead_statuses(id),
    fingerprint_visitor_id VARCHAR REFERENCES fingerprints("visitorId"),
    altcha_solution VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE lead_positions (
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    position_id INTEGER NOT NULL REFERENCES positions(id),
    PRIMARY KEY (lead_id, position_id)
);

CREATE TABLE lead_concerns (
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    concern_id INTEGER NOT NULL REFERENCES concerns(id),
    PRIMARY KEY (lead_id, concern_id)
);

CREATE TABLE lead_attachments (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    file_name VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE lead_history (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    action VARCHAR NOT NULL,
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE lead_modification_logs (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    field_name VARCHAR NOT NULL,
    old_value VARCHAR,
    new_value VARCHAR,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE note_reasons (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    author_name VARCHAR NOT NULL,
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    reason_id INTEGER NOT NULL REFERENCES note_reasons(id)
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    "visitorId" VARCHAR NOT NULL REFERENCES fingerprints("visitorId"),
    page VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
