-- =========================================================
-- Fix for name_token in restaurants table
-- =========================================================

-- First, drop the unique constraint if it exists
ALTER TABLE public.restaurants 
  DROP CONSTRAINT IF EXISTS restaurants_name_token_key;

-- Make name_token nullable temporarily
ALTER TABLE public.restaurants 
  ALTER COLUMN name_token DROP NOT NULL;

-- Create a function to generate a URL-friendly slug
CREATE OR REPLACE FUNCTION generate_slug("name" text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT regexp_replace(
    regexp_replace(
      lower(trim("name")),
      '[^a-z0-9]+', '-', 'g'
    ),
    '^-|-$', '', 'g'
  );
$$;

-- Update existing rows with generated slugs
UPDATE public.restaurants 
SET name_token = generate_slug(name) 
WHERE name_token IS NULL;

-- Add a unique index on name_token
CREATE UNIQUE INDEX IF NOT EXISTS idx_restaurants_name_token 
  ON public.restaurants (name_token);

-- Create a trigger to automatically set name_token on insert/update
CREATE OR REPLACE FUNCTION set_restaurant_name_token()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.name_token IS NULL OR NEW.name_token = '' THEN
    NEW.name_token := generate_slug(NEW.name);
  END IF;
  RETURN NEW;
END;
$$;

-- Create the trigger
DROP TRIGGER IF EXISTS trg_restaurants_name_token ON public.restaurants;
CREATE TRIGGER trg_restaurants_name_token
BEFORE INSERT OR UPDATE OF name ON public.restaurants
FOR EACH ROW
EXECUTE FUNCTION set_restaurant_name_token();

-- Make name_token required again
ALTER TABLE public.restaurants 
  ALTER COLUMN name_token SET NOT NULL;
