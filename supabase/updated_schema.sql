-- =========================================================
-- Billo MVP – Enhanced Supabase SQL Schema
-- =========================================================

-- ---------- Extensions ----------
create extension if not exists pgcrypto;
create extension if not exists "uuid-ossp";

-- ---------- Enums ----------
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tab_status') THEN
    CREATE TYPE tab_status AS ENUM ('active', 'closed');
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'order_status') THEN
    CREATE TYPE order_status AS ENUM ('pending', 'preparing', 'ready', 'completed', 'cancelled', 'rejected');
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
    CREATE TYPE payment_status AS ENUM ('pending', 'confirmed', 'failed');
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_method') THEN
    CREATE TYPE payment_method AS ENUM ('cash', 'mpesa', 'airtel');
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_sender') THEN
    CREATE TYPE message_sender AS ENUM ('customer', 'waiter', 'admin');
  END IF;
END $$;

-- ---------- Helper: Africa/Nairobi business day ----------
CREATE OR REPLACE FUNCTION app_business_day(ts timestamptz DEFAULT now())
RETURNS date
LANGUAGE sql
STABLE
AS $$
  SELECT (timezone('Africa/Nairobi', ts))::date;
$$;

-- ---------- Helper: updated_at trigger ----------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- =========================================================
-- Core Tables with Realtime
-- =========================================================

-- Restaurants (public readable)
CREATE TABLE IF NOT EXISTS public.restaurants (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name             TEXT NOT NULL,
  name_token       TEXT UNIQUE NOT NULL,            -- Used for permanent URLs
  county           TEXT,
  location         TEXT,
  business_hours   JSONB,                           -- Stored as JSON config
  qr_code_url      TEXT,                            -- Supabase Storage URL of QR image
  is_active        BOOLEAN DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable realtime for restaurants table
ALTER PUBLICATION supabase_realtime ADD TABLE public.restaurants;

-- Admins (link auth user -> restaurant + PIN)
CREATE TABLE IF NOT EXISTS public.admins (
  id             UUID PRIMARY KEY,                  -- auth.users.id
  restaurant_id  UUID NOT NULL REFERENCES public.restaurants(id) ON DELETE CASCADE,
  admin_pin      TEXT NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (id, restaurant_id)
);

-- Waiters (auth user accounts; PIN enforced at app level)
CREATE TABLE IF NOT EXISTS public.waiters (
  id             UUID PRIMARY KEY,                  -- auth.users.id
  restaurant_id  UUID NOT NULL REFERENCES public.restaurants(id) ON DELETE CASCADE,
  name           TEXT NOT NULL,
  pin            TEXT NOT NULL,
  is_active      BOOLEAN NOT NULL DEFAULT TRUE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Menu Items (public readable)
CREATE TABLE IF NOT EXISTS public.menu_items (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  restaurant_id  UUID NOT NULL REFERENCES public.restaurants(id) ON DELETE CASCADE,
  name           TEXT NOT NULL,
  description    TEXT,
  price          NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  category       TEXT,
  is_available   BOOLEAN NOT NULL DEFAULT TRUE,
  image_url      TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable realtime for menu items
ALTER PUBLICATION supabase_realtime ADD TABLE public.menu_items;

-- Tabs (customer sessions)
CREATE TABLE IF NOT EXISTS public.tabs (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  restaurant_id  UUID NOT NULL REFERENCES public.restaurants(id) ON DELETE CASCADE,
  customer_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  tab_number     INTEGER NOT NULL,
  status         tab_status DEFAULT 'active',
  notes          TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (restaurant_id, tab_number)
);

-- Enable realtime for tabs
ALTER PUBLICATION supabase_realtime ADD TABLE public.tabs;

-- Orders
CREATE TABLE IF NOT EXISTS public.orders (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tab_id         UUID NOT NULL REFERENCES public.tabs(id) ON DELETE CASCADE,
  waiter_id      UUID REFERENCES public.waiters(id) ON DELETE SET NULL,
  status         order_status DEFAULT 'pending',
  notes          TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable realtime for orders
ALTER PUBLICATION supabase_realtime ADD TABLE public.orders;

-- Order Items
CREATE TABLE IF NOT EXISTS public.order_items (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id       UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
  menu_item_id   UUID NOT NULL REFERENCES public.menu_items(id) ON DELETE CASCADE,
  quantity       INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
  price          NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  notes          TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Payments
CREATE TABLE IF NOT EXISTS public.payments (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tab_id         UUID NOT NULL REFERENCES public.tabs(id) ON DELETE CASCADE,
  amount         NUMERIC(10,2) NOT NULL CHECK (amount > 0),
  method         payment_method NOT NULL,
  status         payment_status DEFAULT 'pending',
  reference      TEXT,
  phone_number   TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable realtime for payments
ALTER PUBLICATION supabase_realtime ADD TABLE public.payments;

-- Messages (chat between customer and staff)
CREATE TABLE IF NOT EXISTS public.messages (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tab_id         UUID NOT NULL REFERENCES public.tabs(id) ON DELETE CASCADE,
  sender_type    message_sender NOT NULL,
  sender_id      UUID NOT NULL,  -- Could be customer_id or waiter_id
  message        TEXT NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable realtime for messages
ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;

-- =========================================================
-- Indexes for Performance
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_restaurants_name_token ON public.restaurants(name_token);
CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant ON public.menu_items(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_tabs_restaurant ON public.tabs(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_tabs_customer ON public.tabs(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_tab ON public.orders(tab_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON public.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_tab ON public.payments(tab_id);
CREATE INDEX IF NOT EXISTS idx_messages_tab ON public.messages(tab_id);

-- =========================================================
-- Triggers for updated_at
-- =========================================================
DO $$
DECLARE
    t text;
    tables text[] := ARRAY['restaurants', 'admins', 'waiters', 'menu_items', 'tabs', 'orders', 'order_items', 'payments'];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trg_%s_updated_at ON public.%I', t, t);
        EXECUTE format('CREATE TRIGGER trg_%s_updated_at
                        BEFORE UPDATE ON public.%I
                        FOR EACH ROW EXECUTE FUNCTION set_updated_at()',
                        t, t);
    END LOOP;
END;
$$;
