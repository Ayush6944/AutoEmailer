import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_remaining_companies():
    """Check companies that still need emails sent."""
    try:
        # Connect to companies database
        with sqlite3.connect('data/companies.db') as conn:
            cursor = conn.cursor()
            
            # Get total count of companies
            cursor.execute("SELECT COUNT(*) FROM companies")
            total_companies = cursor.fetchone()[0]
            
            # Get count of companies that have been sent emails
            cursor.execute("SELECT COUNT(*) FROM companies WHERE sent_timestamp IS NOT NULL")
            sent_companies = cursor.fetchone()[0]
            
            # Get remaining companies
            cursor.execute("""
                SELECT id, company_name, hr_email
                FROM companies
                WHERE sent_timestamp IS NULL
                ORDER BY id
                LIMIT 10
            """)
            next_companies = cursor.fetchall()
            
            # Print summary
            print("\n=== Email Campaign Status ===")
            print(f"Total companies in database: {total_companies}")
            print(f"Companies sent emails: {sent_companies}")
            print(f"Companies remaining: {total_companies - sent_companies}")
            
            if next_companies:
                print("\nNext 10 companies to receive emails:")
                for company in next_companies:
                    print(f"\nID: {company[0]}")
                    print(f"Company: {company[1]}")
                    print(f"Email: {company[2]}")
            
    except Exception as e:
        logger.error(f"Error checking remaining companies: {str(e)}")
        raise

if __name__ == '__main__':
    check_remaining_companies() 