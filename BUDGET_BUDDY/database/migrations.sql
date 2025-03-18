# ⚡ Database Migrations: Updates database schema when needed
ALTER TABLE transactions ADD COLUMN transaction_status ENUM('pending', 'completed') DEFAULT 'completed';
