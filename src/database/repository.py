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
            # Match city at the end (for "Neighborhood, City" format) or neighborhoods without suffix
            if city:
                if city == 'Toronto':
                    # Match "Neighborhood, Toronto" OR Toronto neighborhoods without suffix
                    toronto_hoods = "('Etobicoke','Scarborough','North York','Downtown','Yorkville','Entertainment District','Financial District','Junction Triangle','Kensington Market','The Annex','The Beaches','Leslieville','Liberty Village','Parkdale','Mimico','Weston')"
                    query += f" AND (city LIKE ? OR city IN {toronto_hoods})"
                    params.append(f"%,{city}")
                elif city == 'Calgary':
                    calgary_hoods = "('Beltline','Crescent Heights','Inglewood','Kensington','Sunalta','Bridgeland','East Village','Forest Lawn','Manchester','Ogden','Alyth/Bonnybrook','Acadia','Midnapore','Montgomery')"
                    query += f" AND (city LIKE ? OR city IN {calgary_hoods})"
                    params.append(f"%,{city}")
                elif city == 'Miami':
                    miami_hoods = "('Brickell','Coconut Grove','Edgewater','Wynwood','Little Havana','South Beach','Overtown','Little Haiti','Liberty City','Allapattah','West Little River','Doral','Hialeah','Medley','Opa-locka','Sweetwater')"
                    query += f" AND (city LIKE ? OR city IN {miami_hoods})"
                    params.append(f"%,{city}")
                elif city == 'New York':
                    ny_hoods = "('Sunset Park','Long Island City','Bushwick','Red Hook','Chinatown','The Garment District','Mott Haven','Astoria','DUMBO','Hunts Point','Jamaica','Washington Heights','East Harlem','Concourse')"
                    query += f" AND (city LIKE ? OR city IN {ny_hoods})"
                    params.append(f"%,{city}")
                else:
                    # Standard matching for other cities (case-insensitive with LIKE)
                    query += " AND (city LIKE ? OR city LIKE ?)"
                    params.append(f"%,{city}")
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
            # Match city at the end (for "Neighborhood, City" format) or neighborhoods without suffix
            if city:
                if city == 'Toronto':
                    # Match "Neighborhood, Toronto" OR Toronto neighborhoods without suffix
                    toronto_hoods = "('Etobicoke','Scarborough','North York','Downtown','Yorkville','Entertainment District','Financial District','Junction Triangle','Kensington Market','The Annex','The Beaches','Leslieville','Liberty Village','Parkdale','Mimico','Weston')"
                    query += f" AND (city LIKE ? OR city IN {toronto_hoods})"
                    params.append(f"%,{city}")
                elif city == 'Calgary':
                    calgary_hoods = "('Beltline','Crescent Heights','Inglewood','Kensington','Sunalta','Bridgeland','East Village','Forest Lawn','Manchester','Ogden','Alyth/Bonnybrook','Acadia','Midnapore','Montgomery')"
                    query += f" AND (city LIKE ? OR city IN {calgary_hoods})"
                    params.append(f"%,{city}")
                elif city == 'Miami':
                    miami_hoods = "('Brickell','Coconut Grove','Edgewater','Wynwood','Little Havana','South Beach','Overtown','Little Haiti','Liberty City','Allapattah','West Little River','Doral','Hialeah','Medley','Opa-locka','Sweetwater')"
                    query += f" AND (city LIKE ? OR city IN {miami_hoods})"
                    params.append(f"%,{city}")
                elif city == 'New York':
                    ny_hoods = "('Sunset Park','Long Island City','Bushwick','Red Hook','Chinatown','The Garment District','Mott Haven','Astoria','DUMBO','Hunts Point','Jamaica','Washington Heights','East Harlem','Concourse')"
                    query += f" AND (city LIKE ? OR city IN {ny_hoods})"
                    params.append(f"%,{city}")
                else:
                    # Standard matching for other cities (case-insensitive with LIKE)
                    query += " AND (city LIKE ? OR city LIKE ?)"
                    params.append(f"%,{city}")
                    params.append(f"%{city}%")
            
            # Add niche filter if provided
            if niche:
                query += " AND niche = ?"
                params.append(niche)
            
            query += " ORDER BY created_at DESC"
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
