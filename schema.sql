-- Name characters: 50

CREATE TABLE Prof_M (
	id BIGSERIAL PRIMARY KEY,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL
);


CREATE TABLE Time_Block_M (
	name CHAR(1) PRIMARY KEY,
	start_time VARCHAR(25) NOT NULL,
	end_time VARCHAR(25) NOT NULL
);

CREATE TABLE Course_Section_S (
	section SMALLINT PRIMARY KEY,
	professor BIGINT REFERENCES Prof_M,
	course_name VARCHAR(4) NOT NULL,
	course_number SMALLINT NOT NULL,
	time_block CHAR(1) NOT NULL REFERENCES Time_Block_M,
	seat_cap SMALLINT,
	section_title VARCHAR(50)
);

CREATE TABLE Room_M (
	id SERIAL PRIMARY KEY,
	building VARCHAR(50) NOT NULL,
	room_num SMALLINT NOT NULL,
	feature_score INT -- Size of this field depends on # of entries in Room_Feature_M
);

CREATE TABLE Room_Feature_M (
	id SERIAL PRIMARY KEY,
	description_str VARCHAR(50) NOT NULL
);

CREATE TYPE PREF AS ENUM ( 'cannot', 'dislike', 'ok', 'like' );
CREATE TABLE Room_Prefs_S (
	section_num SMALLINT REFERENCES Course_Section_S,
	room_id INT REFERENCES Room_M,
	preference PREF NOT NULL
);
