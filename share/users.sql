CREATE TABLE IF NOT EXISTS users(
	id			INTEGER PRIMARY KEY,
	username    TEXT NOT NULL UNIQUE,
	email       TEXT NOT NULL UNIQUE,
  	password    TEXT NOT NULL,
	bio			TEXT
);

INSERT INTO users VALUES(1, 'asd', 'test@test.com', 'qwe', 'This is a bio');
INSERT INTO users VALUES(2, 'BrianFang2', 'brian.fang@csu.fullerton.edu', 'password', 'another bio');
INSERT INTO users VALUES(3, 'NathanTran17', 'ntran402@csu.fullerton.edu', 'abc1234', 'third bio');
INSERT INTO users VALUES(4, 'Ashkon', 'ashkon@csu.fullerton.edu', 'letmein', 'last bio');
INSERT INTO users VALUES(5, 'ProfAvery', 'ProfAvery@csu.fullerton.edu', 'password', 'Our cool professor!');

CREATE TABLE IF NOT EXISTS following(
	id				INTEGER PRIMARY KEY,
	users_id    	INTEGER NOT NULL,
	following_id  	INTEGER NOT NULL,

	FOREIGN KEY (users_id) REFERENCES users(id),
	FOREIGN KEY (following_id) REFERENCES users(id)
);

INSERT INTO following VALUES(1, '1', '2');
INSERT INTO following VALUES(2, '1', '3');
INSERT INTO following VALUES(3, '2', '1');
INSERT INTO following VALUES(4, '3', '2');

CREATE VIEW IF NOT EXISTS followingNames
AS
    SELECT users.username, friends.username as friendname
    FROM users, following, users AS friends
    WHERE
        users.id = following.users_id AND
        following.following_id = friends.id;