from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tasks" ADD "type" VARCHAR(20) NOT NULL DEFAULT 'feature';
        CREATE INDEX IF NOT EXISTS "idx_tasks_type_d859d7" ON "tasks" ("type");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_tasks_type_d859d7";
        ALTER TABLE "tasks" DROP COLUMN "type";"""


MODELS_STATE = (
    "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"
)
