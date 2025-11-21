-- Initialize databases for microservices
CREATE DATABASE auth_db;
CREATE DATABASE emails_db;
CREATE DATABASE resumes_db;
CREATE DATABASE analysis_db;

-- Create users for each service (dev environment)
CREATE USER auth_user WITH PASSWORD 'auth_dev_password';
CREATE USER email_user WITH PASSWORD 'email_dev_password';
CREATE USER resume_user WITH PASSWORD 'resume_dev_password';
CREATE USER analysis_user WITH PASSWORD 'analysis_dev_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;
GRANT ALL PRIVILEGES ON DATABASE emails_db TO email_user;
GRANT ALL PRIVILEGES ON DATABASE resumes_db TO resume_user;
GRANT ALL PRIVILEGES ON DATABASE analysis_db TO analysis_user;

-- Grant schema privileges (needed for table creation)
\c auth_db;
GRANT ALL ON SCHEMA public TO auth_user;

\c emails_db;
GRANT ALL ON SCHEMA public TO email_user;

\c resumes_db;
GRANT ALL ON SCHEMA public TO resume_user;

\c analysis_db;
GRANT ALL ON SCHEMA public TO analysis_user;
