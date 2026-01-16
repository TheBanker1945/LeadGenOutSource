"""Handles CRUD operations for leads."""

import os
import sqlite3
from typing import Optional

from .db_manager import get_connection


class LeadRepository:
    """Repository class for lead CRUD operations."""

    def add_lead(self, data: dict, session_id: Optional[int] = None) -> bool:
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
            session_id: Optional scrape session ID to associate this lead with
        
        Returns:
            True if lead was added successfully, False if phone already exists.
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Add session_id to data if provided
        if session_id is not None:
            data['session_id'] = session_id
        
        try:
            if os.getenv("DATABASE_URL"):
                # PostgreSQL uses %s placeholders
                cursor.execute("""
                    INSERT INTO leads (
                        company_name, address, city, phone, website, 
                        niche, rating, operating_hours, session_id
                    )
                    VALUES (
                        %(company_name)s, %(address)s, %(city)s, %(phone)s, %(website)s,
                        %(niche)s, %(rating)s, %(operating_hours)s, %(session_id)s
                    )
                """, data)
            else:
                # SQLite uses :name placeholders
                cursor.execute("""
                    INSERT INTO leads (
                        company_name, address, city, phone, website, 
                        niche, rating, operating_hours, session_id
                    )
                    VALUES (
                        :company_name, :address, :city, :phone, :website,
                        :niche, :rating, :operating_hours, :session_id
                    )
                """, data)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except (sqlite3.IntegrityError, Exception) as e:
            # Phone number already exists - skip duplicate
            cursor.close()
            conn.close()
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
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, company_name, city, phone, website, niche, status, 
                   mockup_path, laptop_mockup_path, created_at
            FROM leads
            WHERE status = 'NEW'
        """
        
        params = []
        placeholder = '%s' if os.getenv("DATABASE_URL") else '?'
        
        # Add city filter if provided - match "Neighborhood, City" format
        if city:
            # Simple pattern: match anything ending with ", CityName"
            query += f" AND city LIKE {placeholder}"
            params.append(f"%, {city}")
        
        # Add niche filter if provided
        if niche:
            query += f" AND niche = {placeholder}"
            params.append(niche)
        
        query += " ORDER BY created_at ASC"
        
        if limit:
            query += f" LIMIT {int(limit)}"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results

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
        conn = get_connection()
        cursor = conn.cursor()
        placeholder = '%s' if os.getenv("DATABASE_URL") else '?'
        
        if mockup_path and laptop_mockup_path:
            cursor.execute(f"""
                UPDATE leads
                SET status = {placeholder}, mockup_path = {placeholder}, laptop_mockup_path = {placeholder}
                WHERE id = {placeholder}
            """, (status, mockup_path, laptop_mockup_path, lead_id))
        elif mockup_path:
            cursor.execute(f"""
                UPDATE leads
                SET status = {placeholder}, mockup_path = {placeholder}
                WHERE id = {placeholder}
            """, (status, mockup_path, lead_id))
        else:
            cursor.execute(f"""
                UPDATE leads
                SET status = {placeholder}
                WHERE id = {placeholder}
            """, (status, lead_id))
        
        conn.commit()
        cursor.close()
        conn.close()

    def get_all_leads(
        self,
        city: Optional[str] = None,
        niche: Optional[str] = None,
        session_id: Optional[int] = None
    ) -> list[dict]:
        """
        Returns all leads from the database.
        
        Args:
            city: Optional city filter. If provided, only returns leads from this city.
            niche: Optional niche filter. If provided, only returns leads for this niche.
            session_id: Optional session filter. If provided, only returns leads from this session.
        
        Returns:
            List of lead dictionaries with all fields.
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, company_name, address, city, phone, website, 
                   niche, rating, operating_hours, status,
                   mockup_path, laptop_mockup_path, session_id, created_at
            FROM leads
            WHERE 1=1
        """
        
        params = []
        placeholder = '%s' if os.getenv("DATABASE_URL") else '?'
        
        # Add city filter if provided - match "Neighborhood, City" format
        if city:
            # Simple pattern: match anything ending with ", CityName"
            query += f" AND city LIKE {placeholder}"
            params.append(f"%, {city}")
        
        # Add niche filter if provided
        if niche:
            query += f" AND niche = {placeholder}"
            params.append(niche)
        
        # Add session filter if provided
        if session_id:
            query += f" AND session_id = {placeholder}"
            params.append(session_id)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    
    def create_session(self, session_name: str, locations: list, niches: list, 
                       country: str = "", state: str = "") -> int:
        """
        Creates a new scrape session.
        
        Args:
            session_name: Name for this session
            locations: List of locations being scraped
            niches: List of niches being scraped
            country: Country being scraped
            state: State being scraped
        
        Returns:
            The ID of the created session
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        locations_str = ", ".join(locations)
        niches_str = ", ".join(niches)
        
        if os.getenv("DATABASE_URL"):
            cursor.execute("""
                INSERT INTO scrape_sessions (session_name, locations, niches, country, state, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (session_name, locations_str, niches_str, country, state, 'running'))
            session_id = cursor.fetchone()['id']
        else:
            cursor.execute("""
                INSERT INTO scrape_sessions (session_name, locations, niches, country, state, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_name, locations_str, niches_str, country, state, 'running'))
            session_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        return session_id
    
    def update_session(self, session_id: int, total_leads: int, status: str = 'completed'):
        """
        Updates a scrape session with final stats.
        
        Args:
            session_id: The session ID to update
            total_leads: Total number of leads scraped
            status: Final status ('completed', 'failed', 'stopped')
        """
        conn = get_connection()
        cursor = conn.cursor()
        placeholder = '%s' if os.getenv("DATABASE_URL") else '?'
        
        cursor.execute(f"""
            UPDATE scrape_sessions
            SET total_leads = {placeholder}, status = {placeholder}, completed_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder}
        """, (total_leads, status, session_id))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_all_sessions(self) -> list[dict]:
        """
        Returns all scrape sessions.
        
        Returns:
            List of session dictionaries
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_name, locations, niches, country, state,
                   total_leads, started_at, completed_at, status
            FROM scrape_sessions
            ORDER BY started_at DESC
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
