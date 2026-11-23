-- Executed by Datasette Lite (?sql=) before any ?csv= import, so the CSV rows
-- land in a table with proper types and a primary key instead of the
-- all-TEXT table that a plain CSV import would create.
CREATE TABLE cities (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  voivodeship TEXT NOT NULL,
  population INTEGER,
  latitude REAL,
  longitude REAL
);
CREATE INDEX idx_cities_voivodeship ON cities (voivodeship);
