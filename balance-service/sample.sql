-- Sample data for the Balance Service


CREATE TABLE IF NOT EXISTS balances (
    user_id INT NOT NULL,
    asset VARCHAR(10) NOT NULL,
    amount FLOAT NOT NULL,
    PRIMARY KEY (user_id, asset)
);


-- Assuming each user has a unique user_id and different balances for each asset

INSERT INTO balances (user_id, asset, amount) VALUES
(1, 'USDT', 1000.00),  -- User 1 starts with 1000 USDT
(1, 'ADA', 500.00),    -- User 1 also has 500 ADA
(2, 'USDT', 500.00),   -- User 2 starts with 500 USDT
(2, 'ADA', 100.00),    -- User 2 has 100 ADA
(3, 'BTC', 2.00),      -- User 3 has 2 BTC
(3, 'ETH', 10.00),     -- User 3 has 10 ETH
(4, 'USDT', 250.00),   -- User 4 starts with 250 USDT
(4, 'ETH', 5.00),      -- User 4 has 5 ETH
(5, 'BTC', 1.50),      -- User 5 has 1.5 BTC
(5, 'ADA', 300.00);    -- User 5 has 300 ADA
