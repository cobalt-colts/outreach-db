-- Permission level 1 is admin; permission level 0 is a standard user.
-- Swap existing values so current users retain their roles.
BEGIN;
UPDATE users
SET permission_level = CASE permission_level
    WHEN 0 THEN 1
    WHEN 1 THEN 0
    ELSE permission_level
END;
COMMIT;
