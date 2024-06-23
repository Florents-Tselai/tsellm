PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE [prompts] (
   [prompt] TEXT
);
INSERT INTO prompts VALUES('hello world!');
INSERT INTO prompts VALUES('how are you?');
INSERT INTO prompts VALUES('is this real life?');
INSERT INTO prompts VALUES('1+1=?');
COMMIT;
