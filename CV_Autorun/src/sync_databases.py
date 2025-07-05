import sqlite3
import logging
import pandas as pd
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sync_databases():
    """Sync companies.db and email_tracking.db by matching companies by name and email."""
    try:
        # Connect to both databases
        with sqlite3.connect('data/companies.db') as companies_conn, \
             sqlite3.connect('data/email_tracking.db') as tracking_conn:
            
            companies_cursor = companies_conn.cursor()
            tracking_cursor = tracking_conn.cursor()
            
            # 1. Get all sent companies from companies.db
            companies_cursor.execute("""
                SELECT id, company_name, hr_email, sent_timestamp, status, error_message
                FROM companies
                WHERE sent_timestamp IS NOT NULL
            """)
            sent_companies = pd.DataFrame(companies_cursor.fetchall(), 
                                       columns=['id', 'company_name', 'hr_email', 'sent_timestamp', 'status', 'error_message'])
            
            # 2. Get all companies from email_tracking.db
            tracking_cursor.execute("""
                SELECT id, company_id, company_name, hr_email, sent_date, status, error_message
                FROM sent_emails
            """)
            tracked_companies = pd.DataFrame(tracking_cursor.fetchall(),
                                          columns=['tracking_id', 'company_id', 'company_name', 'hr_email', 'sent_date', 'status', 'error_message'])
            
            # 3. Match companies by name and email
            logger.info("Matching companies between databases...")
            matches = []
            for _, sent_company in sent_companies.iterrows():
                # Find matching company in tracking db
                match = tracked_companies[
                    (tracked_companies['company_name'].str.strip().str.lower() == sent_company['company_name'].strip().lower()) &
                    (tracked_companies['hr_email'].str.strip().str.lower() == sent_company['hr_email'].strip().lower())
                ]
                
                if not match.empty:
                    matches.append({
                        'companies_id': sent_company['id'],
                        'tracking_id': match.iloc[0]['tracking_id'],
                        'company_name': sent_company['company_name'],
                        'hr_email': sent_company['hr_email'],
                        'sent_timestamp': sent_company['sent_timestamp'],
                        'status': sent_company['status'],
                        'error_message': sent_company['error_message']
                    })
            
            # 4. Update email_tracking.db with correct data
            logger.info("Updating email_tracking.db...")
            for match in matches:
                tracking_cursor.execute("""
                    UPDATE sent_emails
                    SET sent_date = ?, status = ?, error_message = ?
                    WHERE id = ?
                """, (match['sent_timestamp'], match['status'], match['error_message'], match['tracking_id']))
            
            tracking_conn.commit()
            
            # 5. Report results
            logger.info("Sync complete. Results:")
            print(f"\nTotal companies marked as sent in companies.db: {len(sent_companies)}")
            print(f"Total companies in email_tracking.db: {len(tracked_companies)}")
            print(f"Successfully matched and updated: {len(matches)}")
            
            # Show unmatched companies
            unmatched_sent = sent_companies[~sent_companies['id'].isin([m['companies_id'] for m in matches])]
            if not unmatched_sent.empty:
                print("\nCompanies in companies.db not found in tracking.db:")
                print(unmatched_sent[['company_name', 'hr_email', 'sent_timestamp']].to_string())
            
            unmatched_tracked = tracked_companies[~tracked_companies['tracking_id'].isin([m['tracking_id'] for m in matches])]
            if not unmatched_tracked.empty:
                print("\nCompanies in tracking.db not found in companies.db:")
                print(unmatched_tracked[['company_name', 'hr_email', 'sent_date']].to_string())
            
    except Exception as e:
        logger.error(f"Error syncing databases: {str(e)}")
        raise

if __name__ == '__main__':
    sync_databases() 