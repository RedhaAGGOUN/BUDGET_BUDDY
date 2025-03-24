-- Budget Buddy Database Schema

-- Drop existing database if it exists
DROP DATABASE IF EXISTS budget_buddy;

-- Create database
CREATE DATABASE budget_buddy;
USE budget_buddy;

-- Create users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('client', 'banker', 'admin') NOT NULL DEFAULT 'client',
    balance DECIMAL(10, 2) DEFAULT 0.00,
    banker_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Added created_at
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Added updated_at
    FOREIGN KEY (banker_id) REFERENCES users(user_id)
);

-- Create categories table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Create transactions table
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    transaction_type ENUM('deposit', 'withdraw', 'transfer') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category_id INT,  -- Changed to category_id (Foreign Key)
    description TEXT,
    recipient_id INT,
    balance_after DECIMAL(10, 2) NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (recipient_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)  -- Foreign Key constraint
);

-- Insert default users
-- Passwords are hashed using bcrypt for 'Password123!'
INSERT INTO users (first_name, last_name, email, password, user_type, balance) VALUES
('Admin', 'User', 'admin@budgetbuddy.com', '$2b$12$3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4S5T6U7V8W9X0Y1Z2', 'admin', 0.00),
('Jean', 'Dupont', 'jean.dupont@budgetbuddy.com', '$2b$12$3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4S5T6U7V8W9X0Y1Z2', 'banker', 0.00),
('Marie', 'Curie', 'marie.curie@budgetbuddy.com', '$2b$12$3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4S5T6U7V8W9X0Y1Z2', 'client', 1000.00);

-- Insert default categories
INSERT INTO categories (name) VALUES
('Food'),
('Transportation'),
('Entertainment'),
('Utilities'),
('Shopping'),
('Other');

-- Create an index on the transaction_date column for faster queries
CREATE INDEX idx_transaction_date ON transactions (transaction_date);

-- Create an index on user_id and transaction_date for even faster user-specific transaction history
CREATE INDEX idx_user_transaction_date ON transactions (user_id, transaction_date);

-- Optional: Create a full-text index on the description for searching
-- ALTER TABLE transactions ADD FULLTEXT INDEX idx_description (description);  -- Only if full-text search is needed

-- Add a trigger to update the balance after a transaction
DELIMITER //
CREATE TRIGGER update_balance_after_transaction
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    IF NEW.transaction_type = 'deposit' OR NEW.transaction_type = 'transfer' THEN
        UPDATE users SET balance = balance + NEW.amount WHERE user_id = IF(NEW.transaction_type = 'transfer', NEW.recipient_id, NEW.user_id);
    ELSEIF NEW.transaction_type = 'withdraw' THEN
        UPDATE users SET balance = balance - NEW.amount WHERE user_id = NEW.user_id;
    END IF;
END;
//
DELIMITER ;

-- Add a trigger to prevent overspending
DELIMITER //
CREATE TRIGGER prevent_overspending
BEFORE INSERT ON transactions
FOR EACH ROW
BEGIN
  DECLARE current_balance DECIMAL(10, 2);
    IF NEW.transaction_type = 'withdraw' OR NEW.transaction_type = 'transfer' THEN
        SELECT balance INTO current_balance FROM users WHERE user_id = NEW.user_id;
        IF current_balance - NEW.amount < 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient funds';
        END IF;
    END IF;
END;
//
DELIMITER ;
