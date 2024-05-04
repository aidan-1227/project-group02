DROP TABLE IF EXISTS GoatDam CASCADE;
CREATE TABLE GoatDam (
        animal_id INTEGER PRIMARY KEY,
        tag VARCHAR(16) UNIQUE,
        sex VARCHAR(20),
        dob TIMESTAMP,
        dam VARCHAR(16)
);

INSERT INTO GoatDam (animal_id, tag, sex, dob, dam)
SELECT animal_id, tag, sex, dob, dam
FROM Animal;

UPDATE GoatDam
SET dam = NULL
WHERE dam NOT IN (
        SELECT tag FROM GoatDam
);

ALTER TABLE GoatDam
ADD CONSTRAINT DamFK
FOREIGN KEY (dam)
REFERENCES GoatDam(tag);

DROP TABLE IF EXISTS Weights CASCADE;
CREATE TABLE Weights (
        session_id INT NOT NULL,
        animal_id INT NOT NULL,
	tag VARCHAR(16),
	dob TIMESTAMP,
        when_measured TIMESTAMP NOT NULL,
        weight VARCHAR(20) NOT NULL default '',
        PRIMARY KEY(session_id, animal_id, when_measured)
);

INSERT INTO Weights (session_id, animal_id, when_measured, weight)
SELECT sat.session_id, sat.animal_id, sat.when_measured, sat.alpha_value AS weight
FROM SessionAnimalTrait AS sat
WHERE sat.trait_code = 53 AND sat.alpha_value != '';

UPDATE weights AS w
SET tag = a.tag
FROM animal AS a
WHERE a.animal_id = w.animal_id;

UPDATE weights AS w
SET dob = a.dob
FROM animal AS a
WHERE a.animal_id = w.animal_id;
