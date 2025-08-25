import os
from supabase import create_client, Client as SupabaseClient
from typing import Optional, Dict, Any, List, Union
from .config import Config

class SupabaseManager:
    _instance = None
    _client: Optional[SupabaseClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        ""Initialize the Supabase client."""
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Supabase URL and Key must be set in environment variables")
        
        self._client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    @property
    def client(self) -> SupabaseClient:
        ""Get the Supabase client instance."""
        if self._client is None:
            self._initialize()
        return self._client
    
    # Auth Methods
    def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None):
        ""Sign up a new user."""
        return self.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata or {}
            }
        })
    
    def sign_in(self, email: str, password: str):
        ""Sign in a user with email and password."""
        return self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    
    def sign_out(self):
        ""Sign out the current user."""
        return self.client.auth.sign_out()
    
    def get_session(self):
        ""Get the current session."""
        return self.client.auth.get_session()
    
    # Database Methods
    def from_table(self, table_name: str):
        ""Get a query builder for a specific table."""
        return self.client.table(table_name)
    
    def insert(self, table: str, data: Union[Dict, List[Dict]]) -> Dict:
        ""Insert data into a table."""
        return self.client.table(table).insert(data).execute()
    
    def select(self, table: str, columns: str = "*", **filters) -> Dict:
        ""Select data from a table with optional filters."""
        query = self.client.table(table).select(columns)
        
        for key, value in filters.items():
            query = query.eq(key, value)
            
        return query.execute()
    
    def update(self, table: str, data: Dict, **filters) -> Dict:
        ""Update data in a table with optional filters."""
        query = self.client.table(table).update(data)
        
        for key, value in filters.items():
            query = query.eq(key, value)
            
        return query.execute()
    
    def delete(self, table: str, **filters) -> Dict:
        ""Delete data from a table with optional filters."""
        query = self.client.table(table).delete()
        
        for key, value in filters.items():
            query = query.eq(key, value)
            
        return query.execute()
    
    # Realtime
    def on(self, event: str, callback, table: str = None, **filters):
        ""Subscribe to realtime changes."""
        subscription = self.client.channel('realtime')
        
        if table:
            subscription = subscription.on(
                'postgres_changes',
                {
                    'event': event,
                    'schema': 'public',
                    'table': table,
                    **filters
                },
                callback
            )
        else:
            subscription = subscription.on(
                'broadcast',
                {'event': event},
                callback
            )
        
        subscription.subscribe()
        return subscription

# Singleton instance
supabase = SupabaseManager()
