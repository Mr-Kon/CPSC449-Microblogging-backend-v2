CREATE TABLE IF NOT EXISTS posts (
    id          INTEGER PRIMARY KEY,
    username    TEXT NOT NULL,
    text        TEXT NOT NULL,
    timestamp   INTEGER DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO posts(username, text) VALUES('asd', 'first post');
INSERT INTO posts(username, text) VALUES('BrianFang2', 'second post');
INSERT INTO posts(username, text) VALUES('NathanTran17', 'blue post');
INSERT INTO posts(username, text) VALUES('Ashkon', 'red post');
INSERT INTO posts(username, text) VALUES('asd', 'retweet: ');

