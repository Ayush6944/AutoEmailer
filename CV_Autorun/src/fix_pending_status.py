"""
Fix pending status for companies that have been sent emails
"""

import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_pending_status():
    """Update status from 'pending' to 'sent' for companies that have sent_timestamp."""
    try:
        # Connect to database
        conn = sqlite3.connect('data/companies.db')
        cursor = conn.cursor()
        
        # Get count of companies to update
        cursor.execute("""
            SELECT COUNT(*) FROM companies 
            WHERE sent_timestamp IS NOT NULL 
            AND status = 'pending'
        """)
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("No companies found with pending status and sent_timestamp")
            return
        
        # Update companies
        cursor.execute("""
            UPDATE companies 
            SET status = 'sent'
            WHERE sent_timestamp IS NOT NULL 
            AND status = 'pending'
        """)
        
        # Commit changes
        conn.commit()
        
        logger.info(f"Successfully updated {count} companies from pending to sent status")
        
        # Show some examples of updated companies
        cursor.execute("""
            SELECT id, company_name, hr_email, sent_timestamp 
            FROM companies 
            WHERE status = 'sent'
            AND sent_timestamp IS NOT NULL
            ORDER BY id DESC
            LIMIT 5
        """)
        
        logger.info("\nLast 5 companies updated:")
        for row in cursor.fetchall():
            logger.info(f"ID: {row[0]}, Company: {row[1]}, Email: {row[2]}, Sent: {row[3]}")
        
    except Exception as e:
        logger.error(f"Error updating database: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_pending_status() 