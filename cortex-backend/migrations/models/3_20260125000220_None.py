from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "organizations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_organizatio_name_75f36f" ON "organizations" ("name");
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(128) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login_at" TIMESTAMPTZ,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "organization_id" INT REFERENCES "organizations" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_users_usernam_266d85" ON "users" ("username");
CREATE INDEX IF NOT EXISTS "idx_users_email_133a6f" ON "users" ("email");
CREATE TABLE IF NOT EXISTS "projects" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "organization_id" INT REFERENCES "organizations" ("id") ON DELETE CASCADE,
    "owner_id" INT REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_projects_name_7b5b92" ON "projects" ("name");
CREATE TABLE IF NOT EXISTS "project_members" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_project_mem_project_1c5e7a" UNIQUE ("project_id", "user_id")
);
CREATE TABLE IF NOT EXISTS "tasks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "status" VARCHAR(20) NOT NULL DEFAULT 'TODO',
    "type" VARCHAR(20) NOT NULL DEFAULT 'feature',
    "priority" VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    "branch_name" VARCHAR(255),
    "deadline" DATE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "assignee_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tasks_status_449504" ON "tasks" ("status");
CREATE INDEX IF NOT EXISTS "idx_tasks_type_d859d7" ON "tasks" ("type");
CREATE INDEX IF NOT EXISTS "idx_tasks_branch__0ea182" ON "tasks" ("branch_name");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)
