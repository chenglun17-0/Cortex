from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "task_collaborators" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "task_id" INT NOT NULL REFERENCES "tasks" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_task_collab_task_use_2a9ee3" UNIQUE ("task_id", "user_id")
);
CREATE INDEX IF NOT EXISTS "idx_task_collaborators_task_id" ON "task_collaborators" ("task_id");
CREATE INDEX IF NOT EXISTS "idx_task_collaborators_user_id" ON "task_collaborators" ("user_id");
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "task_collaborators";
"""


MODELS_STATE = ""
