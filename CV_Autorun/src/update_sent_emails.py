import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_sent_emails(last_id: int):
    """Update the database to mark all companies up to last_id as sent."""
    try:
        # Connect to database
        conn = sqlite3.connect('data/companies.db')
        cursor = conn.cursor()
        
        # Get count of companies to update
        cursor.execute("""
            SELECT COUNT(*) FROM companies 
            WHERE id <= ? AND sent_timestamp IS NULL
        """, (last_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info(f"No companies found to update up to ID {last_id}")
            return
        
        # Update companies
        cursor.execute("""
            UPDATE companies 
            SET sent_timestamp = ?,
                status = 'sent'
            WHERE id <= ? AND sent_timestamp IS NULL
        """, (datetime.now().isoformat(), last_id))
        
        # Commit changes
        conn.commit()
        
        logger.info(f"Successfully marked {count} companies as sent up to ID {last_id}")
        
        # Show some examples of updated companies
        cursor.execute("""
            SELECT id, company_name, hr_email 
            FROM companies 
            WHERE id <= ? AND sent_timestamp IS NOT NULL
            ORDER BY id DESC
            LIMIT 5
        """, (last_id,))
        
        logger.info("\nLast 5 companies marked as sent:")
        for row in cursor.fetchall():
            logger.info(f"ID: {row[0]}, Company: {row[1]}, Email: {row[2]}")
        
    except Exception as e:
        logger.error(f"Error updating database: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Update all companies up to ID 0
    update_sent_emails(0) 