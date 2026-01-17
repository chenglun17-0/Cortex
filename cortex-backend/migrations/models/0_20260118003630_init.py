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
    "priority" VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    "branch_name" VARCHAR(255),
    "deadline" DATE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "assignee_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_tasks_status_449504" ON "tasks" ("status");
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
    "wxoL9XT50rlhlg6yCxw2+w8t7R/XLP4HXDTGKw=="
)
