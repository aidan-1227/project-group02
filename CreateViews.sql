CREATE OR REPLACE VIEW GoatFamilyTree AS
WITH RECURSIVE Familytree AS (
	SELECT tag, animal_id, dam
	FROM GoatDam
	WHERE dam = '12086'

	UNION ALL

	SELECT g.tag, g.animal_id, g.dam
	FROM GoatDam g
	INNER JOIN Familytree ft on g.dam = ft.tag
)
SELECT * FROM Familytree;

CREATE OR REPLACE VIEW GoatBirthCohort AS 
	SELECT tag, animal_id, dob
	FROM GoatDam
	WHERE dob > '01-01-2017' AND dob < '01-01-2018';

CREATE OR REPLACE VIEW TotalHerd AS 
	SELECT tag, animal_id
	FROM GoatDam;

CREATE OR REPLACE VIEW GetWeight AS
	SELECT * FROM Weights
	WHERE animal_id = 1897;
