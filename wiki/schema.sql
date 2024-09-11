/* https://stackoverflow.com/questions/57519302/postgresql-ltree-query-to-get-comment-threads-nested-json-array-and-build-html-f 
   http://www.postgresonline.com/article_pfriendly/173.html */

-- SELECT nlevel(node_path) AS depth, id, pid, title, node_path FROM pages ORDER BY node_path;
-- 01052023 В users_table добавлен gid для группирования пользователей.

DROP TABLE IF EXISTS users_table;
DROP TABLE IF EXISTS pages;

CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE users_table (
                id int primary key generated always as identity,
                gid int,
                username text unique not null,
                password text not null
);

CREATE TABLE pages (
                id int primary key generated always as identity,
                pid int REFERENCES pages,
                author_id int,
                created timestamp default current_timestamp,
                title text,
                content text,
                node_path LTREE
);

CREATE INDEX pages_node_path_idx ON pages USING GIST (node_path);
CREATE INDEX pages_pid_idx ON pages (pid);


CREATE OR REPLACE FUNCTION get_calculated_node_path(param_id integer)
  RETURNS ltree AS
$$
SELECT CASE WHEN p.pid IS NULL THEN p.id::text::ltree 
            ELSE get_calculated_node_path(p.pid)  || p.id::text END
    FROM pages As p
    WHERE p.id = $1;
$$
  LANGUAGE sql;


CREATE OR REPLACE FUNCTION trig_update_node_path() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'UPDATE' THEN
        IF (COALESCE(OLD.pid,0) != COALESCE(NEW.pid,0)  OR  NEW.id != OLD.id) THEN
            -- update all nodes that are children of this one including this one
            UPDATE pages SET node_path = get_calculated_node_path(id) 
                WHERE OLD.node_path  @> pages.node_path;
        END IF;
  ELSIF TG_OP = 'INSERT' THEN
        UPDATE pages SET node_path = get_calculated_node_path(NEW.id) WHERE pages.id = NEW.id;
  END IF;

  RETURN NEW;
END
$$ LANGUAGE 'plpgsql' VOLATILE;


CREATE TRIGGER trig01_update_node_path AFTER INSERT OR UPDATE OF id, pid
   ON pages FOR EACH ROW
   EXECUTE PROCEDURE trig_update_node_path();
