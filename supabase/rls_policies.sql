-- =========================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =========================================================

-- Enable RLS on all tables
ALTER TABLE public.restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admins ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.waiters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.menu_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tabs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- =========================================================
-- Helper Functions for RLS
-- =========================================================

-- Check if user is an admin of a restaurant
CREATE OR REPLACE FUNCTION is_restaurant_admin(restaurant_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.admins 
    WHERE id = auth.uid() AND admins.restaurant_id = is_restaurant_admin.restaurant_id
  );
$$;

-- Check if user is a waiter at a restaurant
CREATE OR REPLACE FUNCTION is_restaurant_waiter(restaurant_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.waiters 
    WHERE id = auth.uid() 
    AND waiters.restaurant_id = is_restaurant_waiter.restaurant_id
    AND waiters.is_active = true
  );
$$;

-- Check if user is a customer with an active tab
CREATE OR REPLACE FUNCTION is_tab_customer(tab_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.tabs 
    WHERE id = is_tab_customer.tab_id 
    AND customer_id = auth.uid()
    AND status = 'active'::tab_status
  );
$$;

-- =========================================================
-- Restaurant Policies
-- =========================================================

-- Restaurants: Public read access
CREATE POLICY "Restaurants are viewable by everyone"
ON public.restaurants
FOR SELECT
USING (true);

-- Restaurants: Only admins can modify
CREATE POLICY "Only admins can manage restaurants"
ON public.restaurants
FOR ALL
USING (is_restaurant_admin(id));

-- =========================================================
-- Admin Policies
-- =========================================================

-- Admins: Can only see themselves and their restaurant's admins
CREATE POLICY "Admins can view their restaurant's admins"
ON public.admins
FOR SELECT
USING (
  restaurant_id IN (
    SELECT restaurant_id FROM public.admins 
    WHERE id = auth.uid()
  )
);

-- Admins: Can only be created by existing admins of the same restaurant
CREATE POLICY "Admins can manage their restaurant's admins"
ON public.admins
FOR ALL
USING (is_restaurant_admin(restaurant_id));

-- =========================================================
-- Waiter Policies
-- =========================================================

-- Waiters: Admins can manage all waiters in their restaurant
CREATE POLICY "Admins can manage their restaurant's waiters"
ON public.waiters
FOR ALL
USING (is_restaurant_admin(restaurant_id));

-- Waiters: Can view their own profile
CREATE POLICY "Waiters can view their own profile"
ON public.waiters
FOR SELECT
USING (id = auth.uid());

-- =========================================================
-- Menu Item Policies
-- =========================================================

-- Menu Items: Public read access
CREATE POLICY "Menu items are viewable by everyone"
ON public.menu_items
FOR SELECT
USING (true);

-- Menu Items: Only admins can modify
CREATE POLICY "Only admins can manage menu items"
ON public.menu_items
FOR ALL
USING (is_restaurant_admin(restaurant_id));

-- =========================================================
-- Tab Policies
-- =========================================================

-- Tabs: Customers can view their own active tabs
CREATE POLICY "Customers can view their own tabs"
ON public.tabs
FOR SELECT
USING (customer_id = auth.uid() AND status = 'active'::tab_status);

-- Tabs: Staff can view all tabs in their restaurant
CREATE POLICY "Restaurant staff can view all tabs"
ON public.tabs
FOR SELECT
USING (
  is_restaurant_admin(restaurant_id) 
  OR is_restaurant_waiter(restaurant_id)
);

-- Tabs: Only customers can create tabs
CREATE POLICY "Customers can create tabs"
ON public.tabs
FOR INSERT
WITH CHECK (customer_id = auth.uid());

-- Tabs: Only staff can update tab status
CREATE POLICY "Only staff can update tab status"
ON public.tabs
FOR UPDATE
USING (
  is_restaurant_admin(restaurant_id) 
  OR is_restaurant_waiter(restaurant_id)
);

-- =========================================================
-- Order Policies
-- =========================================================

-- Orders: Customers can view their own orders
CREATE POLICY "Customers can view their own orders"
ON public.orders
FOR SELECT
USING (
  tab_id IN (
    SELECT id FROM public.tabs 
    WHERE customer_id = auth.uid()
  )
);

-- Orders: Staff can view all orders in their restaurant
CREATE POLICY "Restaurant staff can view all orders"
ON public.orders
FOR SELECT
USING (
  tab_id IN (
    SELECT t.id FROM public.tabs t
    WHERE is_restaurant_admin(t.restaurant_id) 
    OR is_restaurant_waiter(t.restaurant_id)
  )
);

-- Orders: Only staff can create/update orders
CREATE POLICY "Only staff can manage orders"
ON public.orders
FOR ALL
USING (
  tab_id IN (
    SELECT t.id FROM public.tabs t
    WHERE is_restaurant_admin(t.restaurant_id) 
    OR is_restaurant_waiter(t.restaurant_id)
  )
);

-- =========================================================
-- Order Item Policies
-- =========================================================

-- Order Items: Inherit permissions from parent order
CREATE POLICY "Order item permissions inherit from order"
ON public.order_items
FOR ALL
USING (
  order_id IN (
    SELECT o.id FROM public.orders o
    JOIN public.tabs t ON o.tab_id = t.id
    WHERE t.customer_id = auth.uid()
    OR is_restaurant_admin(t.restaurant_id)
    OR is_restaurant_waiter(t.restaurant_id)
  )
);

-- =========================================================
-- Payment Policies
-- =========================================================

-- Payments: Customers can view their own payments
CREATE POLICY "Customers can view their own payments"
ON public.payments
FOR SELECT
USING (
  tab_id IN (
    SELECT id FROM public.tabs 
    WHERE customer_id = auth.uid()
  )
);

-- Payments: Staff can view all payments in their restaurant
CREATE POLICY "Restaurant staff can view all payments"
ON public.payments
FOR SELECT
USING (
  tab_id IN (
    SELECT t.id FROM public.tabs t
    WHERE is_restaurant_admin(t.restaurant_id) 
    OR is_restaurant_waiter(t.restaurant_id)
  )
);

-- Payments: Only staff can create/update payments
CREATE POLICY "Only staff can manage payments"
ON public.payments
FOR ALL
USING (
  tab_id IN (
    SELECT t.id FROM public.tabs t
    WHERE is_restaurant_admin(t.restaurant_id) 
    OR is_restaurant_waiter(t.restaurant_id)
  )
);

-- =========================================================
-- Message Policies
-- =========================================================

-- Messages: Customers can view messages in their tabs
CREATE POLICY "Customers can view their tab messages"
ON public.messages
FOR SELECT
USING (is_tab_customer(tab_id));

-- Messages: Staff can view messages in their restaurant's tabs
CREATE POLICY "Staff can view their restaurant's messages"
ON public.messages
FOR SELECT
USING (
  tab_id IN (
    SELECT t.id FROM public.tabs t
    WHERE is_restaurant_admin(t.restaurant_id) 
    OR is_restaurant_waiter(t.restaurant_id)
  )
);

-- Messages: Customers can send messages to their tabs
CREATE POLICY "Customers can send messages to their tabs"
ON public.messages
FOR INSERT
WITH CHECK (
  sender_type = 'customer'::message_sender 
  AND sender_id = auth.uid()
  AND is_tab_customer(tab_id)
);

-- Messages: Staff can send messages to any tab in their restaurant
CREATE POLICY "Staff can send messages to their restaurant's tabs"
ON public.messages
FOR INSERT
WITH CHECK (
  (sender_type = 'waiter'::message_sender OR sender_type = 'admin'::message_sender)
  AND sender_id = auth.uid()
  AND tab_id IN (
    SELECT t.id FROM public.tabs t
    WHERE is_restaurant_admin(t.restaurant_id) 
    OR is_restaurant_waiter(t.restaurant_id)
  )
);
