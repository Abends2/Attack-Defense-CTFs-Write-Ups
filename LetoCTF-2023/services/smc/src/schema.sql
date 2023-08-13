DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    personal_data TEXT NOT NULL
);

DROP TABLE IF EXISTS doctors;

CREATE TABLE doctors (
    id SERIAL,
    name TEXT NOT NULL UNIQUE,
    field TEXT NOT NULL
);

DROP TABLE IF EXISTS appointments;

CREATE TABLE appointments (
    id SERIAL,
    user_id INTEGER,
    doctor_name TEXT,
    fio TEXT NOT NULL,
    insurance_num TEXT NOT NULL,
    time TEXT NOT NULL
);

-- Do no change!
INSERT INTO doctors (name, field) VALUES ('Ryan Gosling', 'Drive');
INSERT INTO doctors (name, field) VALUES ('Timothy T. Fox', 'Urology');
INSERT INTO doctors (name, field) VALUES ('Jennifer H. Plante', 'Cardiology');
INSERT INTO doctors (name, field) VALUES ('Patricia P. Daniels', 'Dermatology');
INSERT INTO doctors (name, field) VALUES ('Theresa J. Pesina', 'Pediatrics');
INSERT INTO doctors (name, field) VALUES ('Betty W. Flemings', 'Psychiatry');
