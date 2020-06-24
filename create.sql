CREATE TABLE books (
    ISBN VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    stars FLOAT DEFAULT NULL,
    review_count INTEGER DEFAULT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    firstname VARCHAR,
    lastname VARCHAR
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    text VARCHAR NOT NULL,
    stars INTEGER NOT NULL,
    date DATE NOT NULL,
    book_id VARCHAR REFERENCES books,
    user_id INTEGER REFERENCES users
);
