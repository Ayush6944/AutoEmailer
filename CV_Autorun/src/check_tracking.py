import sqlite3
import logging
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_tracking_db():
    """Check email_tracking.db and its sent_emails table."""
    try:
        # Connect to email_tracking.db
        with sqlite3.connect('data/email_tracking.db') as conn:
            cursor = conn.cursor()
            
            # Check if sent_emails table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sent_emails'
            """)
            if not cursor.fetchone():
                logger.error("sent_emails table does not exist in email_tracking.db")
                return
            
            # Get all sent emails
            cursor.execute("""
                SELECT * FROM sent_emails
                ORDER BY sent_at DESC
            """)
            sent_emails = cursor.fetchall()
            
            if sent_emails:
                logger.info(f"Found {len(sent_emails)} sent emails in tracking database")
                
                # Convert to DataFrame for better viewing
                df = pd.DataFrame(sent_emails, columns=[
                    'id', 'company_id', 'hr_email', 'sent_at', 
                    'status', 'error_message'
                ])
                
                # Print summary
                print("\nEmail Tracking Summary:")
                print(f"Total emails tracked: {len(df)}")
                print(f"Successful emails: {len(df[df['status'] == 'success'])}")
                print(f"Failed emails: {len(df[df['status'] == 'failed'])}")
                
                # Check for duplicates
                duplicates = df[df.duplicated(['company_id', 'hr_email'], keep=False)]
                if not duplicates.empty:
                    print(f"\nFound {len(duplicates)} duplicate entries:")
                    print(duplicates.to_string(index=False))
                    
                    # Ask for cleanup
                    response = input("\nWould you like to clean up duplicates? (y/n): ")
                    if response.lower() == 'y':
                        # Keep only the most recent entry for each company
                        df = df.sort_values('sent_at').drop_duplicates(
                            ['company_id', 'hr_email'], 
                            keep='last'
                        )
                        
                        # Clear the table and insert cleaned data
                        cursor.execute("DELETE FROM sent_emails")
                        for _, row in df.iterrows():
                            cursor.execute("""
                                INSERT INTO sent_emails 
                                (company_id, hr_email, sent_at, status, error_message)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                row['company_id'], 
                                row['hr_email'], 
                                row['sent_at'], 
                                row['status'], 
                                row['error_message']
                            ))
                        
                        conn.commit()
                        logger.info("Cleaned up duplicate entries")
                
                # Show recent emails
                print("\nMost recent emails:")
                print(df.head(10).to_string(index=False))
                
            else:
                logger.info("No sent emails found in tracking database")
            
    except Exception as e:
        logger.error(f"Error checking tracking database: {str(e)}")
        raise

if __name__ == '__main__':
    check_tracking_db() 