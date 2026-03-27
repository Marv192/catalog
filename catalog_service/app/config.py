import os


DUMMY_DB_URL = 'postgresql+asyncpg://user:password@localhost:5432/testdb'
DATABASE_URL = os.getenv('DATABASE_URL', DUMMY_DB_URL)
MIGRATION_DATABASE_URL = os.getenv('MIGRATION_DATABASE_URL', DUMMY_DB_URL)

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'