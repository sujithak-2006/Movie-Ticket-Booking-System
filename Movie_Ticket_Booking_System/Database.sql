-- 1. Start Fresh: Drop everything safely in correct order of dependency
DROP DATABASE IF EXISTS movie_booking;
CREATE DATABASE movie_booking;
USE movie_booking;

-- 2. Create the structural Schema tables
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_name VARCHAR(100) NOT NULL,
    genre VARCHAR(50),
    language VARCHAR(50),
    duration VARCHAR(20),
    price INT NOT NULL,
    poster_url VARCHAR(500)
);

-- ✅ UPDATED: Added show_date and price metrics so the Admin completely controls showtimes
CREATE TABLE shows (
    show_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT,
    show_date DATE NOT NULL,
    show_time VARCHAR(20) NOT NULL,
    price INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);

-- ✅ FIXED: Connected bookings table directly to our fresh relational shows table layout
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    movie_id INT,
    show_id INT,
    show_time VARCHAR(20),
    seat_numbers VARCHAR(100),
    amount INT,
    status VARCHAR(20) DEFAULT 'Confirmed',
    booking_date VARCHAR(50), -- ✅ FIXED: Changed to flexible text string to hold raw calendar values safely
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (show_id) REFERENCES shows(show_id) ON DELETE SET NULL
);

-- ✅ FIXED: Added missing user mapping constraint to prevent orphan data entries
CREATE TABLE recent_searches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    query VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Populate movies table with data AND image filenames mapped to match your static assets folder
INSERT INTO movies (movie_name, genre, language, duration, price, poster_url) VALUES
('Leo', 'Action', 'Tamil', '2h 44m', 180, 'leo.jpg'),
('Dragon', 'Comedy', 'Tamil', '2h 30m', 150, 'dragon.jpg'),
('Amaran', 'Action', 'Tamil', '2h 40m', 180, 'amaran.jpg'),
('Vidamuyarchi', 'Thriller', 'Tamil', '2h 45m', 200, 'vidamuyarchi.jpg'),
('Avengers Endgame', 'Action', 'English', '3h 02m', 250, 'avengers endgame.jpg'),
('Interstellar', 'Sci-Fi', 'English', '2h 49m', 220, 'interstellar.jpg'),
('Batman', 'Action', 'English', '2h 56m', 210, 'batman.jpg'),
('Joker', 'Thriller', 'English', '2h 02m', 200, 'joker.jpg'),
('Oppenheimer', 'Thriller', 'English', '3h 00m', 240, 'oppenheimer.jpg'),
('The Conjuring', 'Horror', 'English', '1h 52m', 180, 'the conjuring.jpg'),
('Home Alone', 'Comedy', 'English', '1h 43m', 160, 'home alone.jpg'),
('Jumanji', 'Comedy', 'English', '1h 59m', 190, 'jumanji.jpg'),
('Don', 'Comedy', 'Tamil', '2h 43m', 180, 'don.jpg'),
('Annabelle', 'Horror', 'English', '1h 39m', 180, 'annabelle.jpg'),
('The Nun', 'Horror', 'English', '1h 36m', 180, 'the nun.jpg'),
('Demonte Colony', 'Horror', 'Tamil', '2h 00m', 180, 'Demonte Colony.jpg'),
('Inception', 'Sci-Fi', 'English', '2h 28m', 220, 'inception.jpg'),
('The Martian', 'Sci-Fi', 'English', '2h 24m', 220, 'the martian.jpg'),
('Avatar', 'Sci-Fi', 'English', '2h 42m', 250, 'avatar.jpg'),
('Titanic', 'Romance', 'English', '3h 14m', 220, 'titanic.jpg'),
('La La Land', 'Romance', 'English', '2h 08m', 190, 'la la land.jpg'),
('Me Before You', 'Romance', 'English', '1h 50m', 180, 'me before you.jpg'),
('Sita Ramam', 'Romance', 'Telugu', '2h 43m', 200, 'sita ramam.jpg');

-- 4. Verify structural entries look great
SELECT * FROM movies;
SELECT * FROM shows;
SELECT * FROM users;
SELECT * FROM bookings;