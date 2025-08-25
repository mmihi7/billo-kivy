-- Function to listen for tab updates for a specific user
CREATE OR REPLACE FUNCTION listen_to_tab_updates(user_id_param UUID)
RETURNS SETOF tabs AS $$
BEGIN
    -- Return all tabs for the user
    RETURN QUERY
    SELECT * FROM tabs
    WHERE customer_id = user_id_param
    ORDER BY updated_at DESC;
    
    -- Notify about changes to the user's tabs
    EXECUTE format('LISTEN "user_%s_tab_updates"', user_id_param);
    
    -- Keep the connection alive
    LOOP
        PERFORM pg_sleep(0.1);
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger function to notify about tab changes
CREATE OR REPLACE FUNCTION notify_tab_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Notify about the change
    PERFORM pg_notify(
        'tab_changes',
        json_build_object(
            'event', TG_OP,
            'table', TG_TABLE_NAME,
            'record', row_to_json(NEW)
        )::text
    );
    
    -- Notify the specific user about the change to their tab
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        PERFORM pg_notify(
            format('user_%s_tab_updates', NEW.customer_id),
            json_build_object(
                'event', TG_OP,
                'table', TG_TABLE_NAME,
                'record', row_to_json(NEW)
            )::text
        );
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM pg_notify(
            format('user_%s_tab_updates', OLD.customer_id),
            json_build_object(
                'event', TG_OP,
                'table', TG_TABLE_NAME,
                'record', row_to_json(OLD)
            )::text
        );
    END IF;
    
    -- Return the appropriate record
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for tab changes
DROP TRIGGER IF EXISTS tab_changes_trigger ON tabs;
CREATE TRIGGER tab_changes_trigger
AFTER INSERT OR UPDATE OR DELETE ON tabs
FOR EACH ROW EXECUTE FUNCTION notify_tab_changes();

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION listen_to_tab_updates(UUID) TO anon, authenticated;
GRANT SELECT ON TABLE tabs TO anon, authenticated;
