from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "task_comments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "author_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "task_id" INT NOT NULL REFERENCES "tasks" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_task_comments_task_id" ON "task_comments" ("task_id");
CREATE INDEX IF NOT EXISTS "idx_task_comments_created_at" ON "task_comments" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_task_comments_task_created_id" ON "task_comments" ("task_id", "created_at" DESC, "id" DESC);
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "task_comments";
"""


MODELS_STATE = "eJztW22P2jgQ/ison/akXtXldtvVfaPAXlHLUm3Tu6pVFRlikpTETh1HLK3472ebvDhvbAKBDWy+tIvHk9iPZyaex57fioN1aHsvJ8QAyPoFqIWR8nfnt4KAA9kfufIXHQW4bizlDRRMbaGApZ5CAqYeJWBGmXAObA+yJh16M2K5wcuQb9u8Ec9YRwsZcZOPrJ8+1Cg2IDUhYYJv31mzhXT4AL3wp7vQ5ha09cS4LZ2/W7RrdOWKthGit6Ijf9tUm2Hbd1Dc2V1RE6Oot4UobzUgggRQyB9Pic+Hz0cXTDec0WakcZfNECUdHc6Bb1NpuiUxmDEYGX5sNJ6YoMHf8mf38urN1c1fr69uWBcxkqjlzXozvXjuG0WBwJ2qrIUcULDpIWCMcRP/Z5Drm4DkQxf2T4HHhpwGL4RqG3phw+Hgc8CDZkNkUJP9vHz1agtY//bu++969xes1x98MphZ8cbG7wJRdyNbr7kZzhcSoLxhCmaLJSC6lpDEULsE/4Az6mXhfhto3r6/h3bkcymIA8/8uHlKCbQDKLeAHftnPWivQ2sJW4NRsPYYBt+DZE8MPrNHnBYA3D5wFxdZTFbkdJ10C0DAEKPm7+ZvSllEThiXjKU4gst22QbvNnife/CWg5E8sgyQKnwosMGU2k54Pll0yoNPHX5R+Zgdz/tpy6hdjHtfBKDOKpB8mNz9E3aXUO5/mLxNgTsjkE9fAzSL7YBJqOXAfHyTmil49UD1ZfhHPcZbN9oKm4M+QfYq/ggWoj8aDz+pvfHHxBIMeuqQS7oJ+MPWi9cpO48e0vlvpL7r8J+dr5O7oUAQe9Qg4o1xP/WrwscEfIo1hJca0CUfDltDYJKfcFffcWGTmu3CPunCZrZmbGsAd1vXpGYN69qs6NigZQynvdVB5aRcq7S7ytF8fKvViPWrZ7MlYbhkE6wInqTyjFDLZMP5hpgF8hYTaBnoPVwJPEdsZADN8raoBbRU4+AsSgBZMwHLKPXJczP2xyaKcnm/96nfGwyVrEXWgOLJpc8Z9CQ/y4etDB/jQGcKiWdabj2UzFg8r5l7llLMDAXeYk8oVPaIE0NgT2omY09ZAMcArVTM/63XQY/OZ2zxTzFyLUU/hfMg3G7Y7jAU/8AWYj8ThCgmAu4F5NvqkJMKfDxajEDKKcRARE2CfcOUdaR1yA0OrF3LILsuQ7EFHl5MtMUh4FG6TR5mvazbt/AV/NEcKuV7S8QdlogLDLp63pRQbNPhhvEcyShU0i2SSjulAU+xijVnT1KILombpPGcQNuSPElhfM8df/lDwwbtzNK7/qRjPZ4u+d4xs6UGAyd5VtVs6ZDnliJXyNlLhTlE8RYqSlTa48qmhbNtuyRqUbvSeWWkcKgDy9o/CIkTy+71dYkTS9ar8MRSyNoTy6OdWLJvAfVzMvhiE401jnaorqiTwUSpzUjLnKp3iw/Vu5kzdYFAFS8P+h8PwDlki0ZggzF0iYWJRVdVcJR1jhcwlfFwMPo8bjCWU8I2eKZW9bJMSu1AEfOgV2YO9AECum2hHCw51VH09Yl1trEcp/YR4iRFe+nleZBB7aWXs1jY9tLLuV56AZ5nGQjCarRjSusZXdtome6WtG0caRu64/GI2+Zec0mFpiZxtwLbHO42xLyYu43Kf1rutmlR7cUW7pYvW9UMWtaph5A4OIqJ9Pm6DBVxXUxFXGeoCOgAy64CYaRwivgdpGLHBJ7J7w6x4LjEJMebi8HMUT3Ng4XL7k0ZYLs3xcByWUtcnGF+2xIXZ7qwGeLCBh7VbGxYaIelzSi39EVbs3OSNEZbfXK46pMyZRS8GCN1l3vfSoqTAjfhxG1NiZ9LyjIQjlZc0iDTqK22JK9iYr8akz3YxaaVmUhTSVeayDU5yQoT6VJkurwkyVnWUGES2UKKT1v/D1dHeH0="
