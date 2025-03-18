# 📊 SQL Data Seeding : Inserts initial test data for development ((Insert Sample Data) )
INSERT INTO users (name, email, password_hash, role) VALUES
('Alice Doe', 'alice@example.com', 'hashed_password', 'client'),
('Bob Banker', 'bob@example.com', 'hashed_password', 'banker');

INSERT INTO accounts (user_id, balance, account_type) VALUES
(1, 1000.00, 'checking'),
(1, 500.00, 'savings');
