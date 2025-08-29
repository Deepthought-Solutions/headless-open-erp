"""refactor_contact_to_lead_model

Revision ID: ec1fad755e19
Revises: f43562ccdfe8
Create Date: 2025-08-02 01:29:09.309303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec1fad755e19'
down_revision: Union[str, Sequence[str], None] = 'f43562ccdfe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create new tables and columns
    contacts_new_table = op.create_table('contacts_new',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True)
    )

    # Create enum tables
    lead_statuses_table = op.create_table('lead_statuses',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )
    lead_urgencies_table = op.create_table('lead_urgencies',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )
    recommended_packs_table = op.create_table('recommended_packs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )

    # Populate enum tables
    op.bulk_insert(lead_statuses_table,
        [
            {'name': 'nouveau'},
            {'name': 'à rappeler'},
            {'name': 'relancé'},
            {'name': 'proposition envoyée'},
            {'name': 'gagné'},
            {'name': 'perdu'}
        ]
    )
    op.bulk_insert(lead_urgencies_table,
        [
            {'name': 'immédiat'},
            {'name': 'ce mois'},
            {'name': 'moyen terme'}
        ]
    )
    op.bulk_insert(recommended_packs_table,
        [
            {'name': 'conformité'},
            {'name': 'confiance'},
            {'name': 'croissance'}
        ]
    )

    leads_table = op.create_table('leads',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('submission_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('estimated_users', sa.Integer(), nullable=True),
        sa.Column('problem_summary', sa.Text(), nullable=True),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('recommended_pack_id', sa.Integer(), nullable=True),
        sa.Column('maturity_score', sa.Integer(), nullable=True),
        sa.Column('urgency_id', sa.Integer(), nullable=True),
        sa.Column('status_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts_new.id'], ),
        sa.ForeignKeyConstraint(['recommended_pack_id'], ['recommended_packs.id'], ),
        sa.ForeignKeyConstraint(['urgency_id'], ['lead_urgencies.id'], ),
        sa.ForeignKeyConstraint(['status_id'], ['lead_statuses.id'], )
    )

    op.create_table('lead_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lead_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lead_positions',
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id']),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id']),
        sa.PrimaryKeyConstraint('lead_id', 'position_id')
    )
    op.create_table('lead_concerns',
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('concern_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id']),
        sa.ForeignKeyConstraint(['concern_id'], ['concerns.id']),
        sa.PrimaryKeyConstraint('lead_id', 'concern_id')
    )

    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('size', sa.Integer(), nullable=True))

    # Step 2: Data migration
    op.execute('UPDATE companies SET size = employees')

    op.execute("""
        INSERT INTO contacts_new (name, email, phone, created_at)
        SELECT name, email, phone, MIN(created_at)
        FROM contacts
        GROUP BY email, name, phone
    """)

    op.execute("""
        INSERT INTO leads (id, submission_date, problem_summary, contact_id, company_id, status_id)
        SELECT c.id, c.created_at, c.message, cn.id, c.company_id, ls.id
        FROM contacts c
        JOIN contacts_new cn ON c.email = cn.email
        CROSS JOIN lead_statuses ls WHERE ls.name = 'nouveau'
    """)

    op.execute("""
        INSERT INTO lead_positions (lead_id, position_id)
        SELECT contact_id, position_id FROM contact_positions
    """)
    op.execute("""
        INSERT INTO lead_concerns (lead_id, concern_id)
        SELECT contact_id, concern_id FROM contact_concerns
    """)

    # Step 3: Drop old tables and columns
    op.drop_table('contact_positions')
    op.drop_table('contact_concerns')
    op.drop_table('contacts')
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.drop_column('employees')

    # Step 4: Rename contacts_new to contacts
    op.rename_table('contacts_new', 'contacts')
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_leads_contact_id_contacts', 'contacts', ['contact_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('employees', sa.Integer(), nullable=True))

    op.execute('UPDATE companies SET employees = size')

    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.drop_column('size')

    op.rename_table('contacts', 'contacts_temp')

    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, index=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('conscent', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('newsletter', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('sector_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'])
    )

    op.create_table('contact_positions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('contact_id', sa.Integer, sa.ForeignKey('contacts.id')),
        sa.Column('position_id', sa.Integer, sa.ForeignKey('positions.id'))
    )
    op.create_table('contact_concerns',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('contact_id', sa.Integer, sa.ForeignKey('contacts.id')),
        sa.Column('concern_id', sa.Integer, sa.ForeignKey('concerns.id'))
    )

    op.execute("""
        INSERT INTO contacts (id, name, email, phone, message, company_id, created_at)
        SELECT l.id, ct.name, ct.email, ct.phone, l.problem_summary, l.company_id, l.submission_date
        FROM leads l
        JOIN contacts_temp ct ON l.contact_id = ct.id
    """)
    op.execute("""
        INSERT INTO contact_positions (contact_id, position_id)
        SELECT lead_id, position_id FROM lead_positions
    """)
    op.execute("""
        INSERT INTO contact_concerns (contact_id, concern_id)
        SELECT lead_id, concern_id FROM lead_concerns
    """)

    op.drop_table('contacts_temp')
    op.drop_table('lead_positions')
    op.drop_table('lead_concerns')
    op.drop_table('lead_attachments')
    op.drop_table('lead_history')
    op.drop_table('leads')
    op.drop_table('lead_statuses')
    op.drop_table('lead_urgencies')
    op.drop_table('recommended_packs')
