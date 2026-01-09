"""Handles CRUD operations for leads."""

import sqlite3
from typing import Optional

from .db_manager import get_connection


class LeadRepository:
    """Repository class for lead CRUD operations."""

    def add_lead(self, data: dict) -> bool:
        """
        Adds a new lead to the database.
        
        Args:
            data: Dictionary containing lead fields:
                  - company_name (required)
                  - address (optional)
                  - city (optional)
                  - phone (optional, but should be unique)
                  - website (optional)
                  - niche (optional)
                  - rating (optional)
                  - operating_hours (optional)
        
        Returns:
            True if lead was added successfully, False if phone already exists.
        """
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO leads (
                        company_name, address, city, phone, website, 
                        niche, rating, operating_hours
                    )
                    VALUES (
                        :company_name, :address, :city, :phone, :website,
                        :niche, :rating, :operating_hours
                    )
                """, data)
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Phone number already exists - skip duplicate
            return False

    def get_pending_mockups(
        self, 
        limit: Optional[int] = None,
        city: Optional[str] = None,
        niche: Optional[str] = None
    ) -> list[dict]:
        """
        Returns leads with status 'NEW' that need mockups generated.
        
        Args:
            limit: Optional maximum number of leads to return.
                   Use this to test with a small batch first.
            city: Optional city filter. If provided, only returns leads from this city.
            niche: Optional niche filter. If provided, only returns leads for this niche.
        
        Returns:
            List of lead dictionaries.
        """
        with get_connection() as conn:
            query = """
                SELECT id, company_name, city, phone, website, niche, status, 
                       mockup_path, laptop_mockup_path, created_at
                FROM leads
                WHERE status = 'NEW'
            """
            
            params = []
            
            # Add city filter if provided
            if city:
                query += " AND city LIKE ?"
                params.append(f"%{city}%")
            
            # Add niche filter if provided
            if niche:
                query += " AND niche = ?"
                params.append(niche)
            
            query += " ORDER BY created_at ASC"
            
            if limit:
                query += f" LIMIT {int(limit)}"
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_status(
        self, 
        lead_id: int, 
        status: str, 
        mockup_path: Optional[str] = None,
        laptop_mockup_path: Optional[str] = None
    ) -> None:
        """
        Updates the status and optionally the mockup paths for a lead.
        
        Args:
            lead_id: The ID of the lead to update.
            status: The new status value.
            mockup_path: Optional path to the screenshot mockup.
            laptop_mockup_path: Optional path to the laptop frame mockup.
        """
        with get_connection() as conn:
            if mockup_path and laptop_mockup_path:
                conn.execute("""
                    UPDATE leads
                    SET status = ?, mockup_path = ?, laptop_mockup_path = ?
                    WHERE id = ?
                """, (status, mockup_path, laptop_mockup_path, lead_id))
            elif mockup_path:
                conn.execute("""
                    UPDATE leads
                    SET status = ?, mockup_path = ?
                    WHERE id = ?
                """, (status, mockup_path, lead_id))
            else:
                conn.execute("""
                    UPDATE leads
                    SET status = ?
                    WHERE id = ?
                """, (status, lead_id))
            conn.commit()

    def get_all_leads(
        self,
        city: Optional[str] = None,
        niche: Optional[str] = None
    ) -> list[dict]:
        """
        Returns all leads from the database.
        
        Args:
            city: Optional city filter. If provided, only returns leads from this city.
            niche: Optional niche filter. If provided, only returns leads for this niche.
        
        Returns:
            List of lead dictionaries with all fields.
        """
        with get_connection() as conn:
            query = """
                SELECT id, company_name, address, city, phone, website, 
                       niche, rating, operating_hours, status,
                       mockup_path, laptop_mockup_path, created_at
                FROM leads
                WHERE 1=1
            """
            
            params = []
            
            # Add city filter if provided
            if city:
                query += " AND city LIKE ?"
                params.append(f"%{city}%")
            
            # Add niche filter if provided
            if niche:
                query += " AND niche = ?"
                params.append(niche)
            
            query += " ORDER BY created_at DESC"
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
