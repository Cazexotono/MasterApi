### Unofficial master API for Skymp
REST API for monitoring [SkyMP](https://github.com/skyrim-multiplayer/skymp) servers and authorizing clients 

#### Requirements
- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) 
- openssl
- PostgreSQL
- Redis

#### Quick start
Initialize a local copy of the repository
```
git clone https://github.com/Cazexotono/MasterApi.git
cd MasterApi
uv sync
```
Generate or place RSA keys:
```
cd secret
openssl genrsa -out rsa_private 4096
openssl rsa -in rsa_private -pubout -out rsa_public
cd ..
```
Configure connections to PostgreSQL and Redis. To do this, create a .env file in the root of the project and add the following environment variables to it:
```
API__DATABASE__DB_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
API__REDIS__CACHE_URL=redis://localhost:6379/0
```
The database is migrated using a alembic.
```
uv run alembic upgrade head
```
