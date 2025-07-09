"""
Script to delete companies from the database based on various criteria
"""

import sqlite3
import pandas as pd
import logging
from typing import List, Optional
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(_name_)

class CompanyDeleter:
    def _init_(self, db_path: str = 'data/companies.db'):
        """Initialize with database path."""
        self.db_path = db_path
    
    def show_companies(self, limit: int = 10, status: Optional[str] = None) -> pd.DataFrame:
        """Show companies in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT id, company_name, hr_email, status, sent_timestamp
                    FROM companies
                """
                if status:
                    query += f" WHERE status = '{status}'"
                query += f" ORDER BY id LIMIT {limit}"
                
                df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            logger.error(f"Error showing companies: {str(e)}")
            return pd.DataFrame()
    
    def delete_by_id(self, company_id: int) -> bool:
        """Delete a company by its ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First check if company exists
                cursor.execute("SELECT company_name FROM companies WHERE id = ?", (company_id,))
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"Company with ID {company_id} not found")
                    return False
                
                company_name = result[0]
                cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
                conn.commit()
                
                logger.info(f"Successfully deleted company: {company_name} (ID: {company_id})")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting company by ID: {str(e)}")
            return False
    
    def delete_by_email(self, email: str) -> int:
        """Delete companies by email address."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First check how many companies have this email
                cursor.execute("SELECT COUNT(*) FROM companies WHERE hr_email = ?", (email,))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    logger.warning(f"No companies found with email: {email}")
                    return 0
                
                # Show what will be deleted
                cursor.execute("SELECT id, company_name FROM companies WHERE hr_email = ?", (email,))
                companies = cursor.fetchall()
                logger.info(f"Found {count} companies with email {email}:")
                for company_id, company_name in companies:
                    logger.info(f"  - {company_name} (ID: {company_id})")
                
                # Delete the companies
                cursor.execute("DELETE FROM companies WHERE hr_email = ?", (email,))
                conn.commit()
                
                logger.info(f"Successfully deleted {count} companies with email: {email}")
                return count
                
        except Exception as e:
            logger.error(f"Error deleting companies by email: {str(e)}")
            return 0
    
    def delete_by_company_name(self, company_name: str, exact_match: bool = False) -> int:
        """Delete companies by company name."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if exact_match:
                    query = "SELECT COUNT(*) FROM companies WHERE company_name = ?"
                    delete_query = "DELETE FROM companies WHERE company_name = ?"
                    param = (company_name,)
                else:
                    query = "SELECT COUNT(*) FROM companies WHERE company_name LIKE ?"
                    delete_query = "DELETE FROM companies WHERE company_name LIKE ?"
                    param = (f"%{company_name}%",)
                
                # First check how many companies match
                cursor.execute(query, param)
                count = cursor.fetchone()[0]
                
                if count == 0:
                    logger.warning(f"No companies found matching: {company_name}")
                    return 0
                
                # Show what will be deleted
                if exact_match:
                    cursor.execute("SELECT id, company_name FROM companies WHERE company_name = ?", param)
                else:
                    cursor.execute("SELECT id, company_name FROM companies WHERE company_name LIKE ?", param)
                
                companies = cursor.fetchall()
                logger.info(f"Found {count} companies matching '{company_name}':")
                for company_id, name in companies:
                    logger.info(f"  - {name} (ID: {company_id})")
                
                # Delete the companies
                cursor.execute(delete_query, param)
                conn.commit()
                
                logger.info(f"Successfully deleted {count} companies matching: {company_name}")
                return count
                
        except Exception as e:
            logger.error(f"Error deleting companies by name: {str(e)}")
            return 0
    
    def delete_by_status(self, status: str) -> int:
        """Delete companies by status (e.g., 'sent', 'pending', 'failed')."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First check how many companies have this status
                cursor.execute("SELECT COUNT(*) FROM companies WHERE status = ?", (status,))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    logger.warning(f"No companies found with status: {status}")
                    return 0
                
                # Show what will be deleted
                cursor.execute("SELECT id, company_name, hr_email FROM companies WHERE status = ?", (status,))
                companies = cursor.fetchall()
                logger.info(f"Found {count} companies with status '{status}':")
                for company_id, company_name, hr_email in companies:
                    logger.info(f"  - {company_name} (ID: {company_id}, Email: {hr_email})")
                
                # Delete the companies
                cursor.execute("DELETE FROM companies WHERE status = ?", (status,))
                conn.commit()
                
                logger.info(f"Successfully deleted {count} companies with status: {status}")
                return count
                
        except Exception as e:
            logger.error(f"Error deleting companies by status: {str(e)}")
            return 0
    
    def delete_sent_emails(self) -> int:
        """Delete all companies that have been sent emails."""
        return self.delete_by_status('sent')
    
    def delete_failed_emails(self) -> int:
        """Delete all companies that failed to send emails."""
        return self.delete_by_status('failed')
    
    def get_database_stats(self) -> dict:
        """Get statistics about the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total companies
                cursor.execute("SELECT COUNT(*) FROM companies")
                total = cursor.fetchone()[0]
                
                # Companies by status
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM companies 
                    GROUP BY status
                """)
                status_counts = dict(cursor.fetchall())
                
                # Companies with emails sent
                cursor.execute("SELECT COUNT(*) FROM companies WHERE sent_timestamp IS NOT NULL")
                sent_count = cursor.fetchone()[0]
                
                return {
                    'total_companies': total,
                    'status_counts': status_counts,
                    'sent_count': sent_count
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {}
    
    def delete_by_ids(self, ids: list) -> int:
        """Delete multiple companies by their IDs."""
        try:
            if not ids:
                logger.warning("No IDs provided for deletion.")
                return 0
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Show what will be deleted
                q_marks = ','.join(['?'] * len(ids))
                cursor.execute(f"SELECT id, company_name FROM companies WHERE id IN ({q_marks})", ids)
                companies = cursor.fetchall()
                if not companies:
                    logger.warning(f"No companies found with the provided IDs: {ids}")
                    return 0
                logger.info(f"Found {len(companies)} companies to delete:")
                for company_id, company_name in companies:
                    logger.info(f"  - {company_name} (ID: {company_id})")
                # Delete the companies
                cursor.execute(f"DELETE FROM companies WHERE id IN ({q_marks})", ids)
                conn.commit()
                logger.info(f"Successfully deleted {len(companies)} companies with IDs: {ids}")
                return len(companies)
        except Exception as e:
            logger.error(f"Error deleting companies by IDs: {str(e)}")
            return 0

def main():
    parser = argparse.ArgumentParser(description='Delete companies from the database')
    parser.add_argument('--show', action='store_true', help='Show companies in database')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--id', type=int, help='Delete company by ID')
    parser.add_argument('--email', type=str, help='Delete companies by email')
    parser.add_argument('--name', type=str, help='Delete companies by name (partial match)')
    parser.add_argument('--exact-name', type=str, help='Delete company by exact name')
    parser.add_argument('--status', type=str, help='Delete companies by status')
    parser.add_argument('--delete-sent', action='store_true', help='Delete all sent emails')
    parser.add_argument('--delete-failed', action='store_true', help='Delete all failed emails')
    parser.add_argument('--limit', type=int, default=10, help='Limit for showing companies')
    parser.add_argument('--ids', type=int, nargs='+', help='Delete multiple companies by IDs (space separated)')
    
    args = parser.parse_args()
    
    deleter = CompanyDeleter()
    
    if args.stats:
        stats = deleter.get_database_stats()
        print("\n=== Database Statistics ===")
        print(f"Total companies: {stats.get('total_companies', 0)}")
        print(f"Sent emails: {stats.get('sent_count', 0)}")
        print("\nStatus breakdown:")
        for status, count in stats.get('status_counts', {}).items():
            print(f"  {status}: {count}")
        return
    
    if args.show:
        print("\n=== Companies in Database ===")
        df = deleter.show_companies(limit=args.limit)
        if not df.empty:
            print(df.to_string(index=False))
        else:
            print("No companies found or error occurred")
        return
    
    if args.id:
        deleter.delete_by_id(args.id)
    elif args.email:
        deleter.delete_by_email(args.email)
    elif args.name:
        deleter.delete_by_company_name(args.name, exact_match=False)
    elif args.exact_name:
        deleter.delete_by_company_name(args.exact_name, exact_match=True)
    elif args.status:
        deleter.delete_by_status(args.status)
    elif args.delete_sent:
        deleter.delete_sent_emails()
    elif args.delete_failed:
        deleter.delete_failed_emails()
    elif args.ids:
        deleter.delete_by_ids(args.ids)
    else:
        print("No action specified. Use --help for usage information.")

if _name_ == "_main_":
    main()