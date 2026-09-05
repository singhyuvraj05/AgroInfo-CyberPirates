# MySQL setup

The backend expects a MySQL database named `agroinfo`. For a local
development database, run:

```sql
CREATE DATABASE agroinfo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'agroinfo'@'localhost' IDENTIFIED BY 'change-this-password';
GRANT ALL PRIVILEGES ON agroinfo.* TO 'agroinfo'@'localhost';
FLUSH PRIVILEGES;
```

Set the matching SQLAlchemy URL in `backend/.env`. The FastAPI application
creates the initial `farms` table and one demo record when it starts.
