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

def verify_sync():
    """Verify the synchronization between companies.db and email_tracking.db."""
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
                ORDER BY sent_timestamp DESC
            """)
            sent_companies = pd.DataFrame(companies_cursor.fetchall(), 
                                       columns=['id', 'company_name', 'hr_email', 'sent_timestamp', 'status', 'error_message'])
            
            # 2. Get all companies from email_tracking.db
            tracking_cursor.execute("""
                SELECT id, company_id, company_name, hr_email, sent_date, status, error_message, is_followup
                FROM sent_emails
                ORDER BY sent_date DESC
            """)
            tracked_companies = pd.DataFrame(tracking_cursor.fetchall(),
                                          columns=['tracking_id', 'company_id', 'company_name', 'hr_email', 'sent_date', 'status', 'error_message', 'is_followup'])
            
            # 3. Print summary
            print("\n=== Database Synchronization Report ===")
            print(f"\nTotal companies marked as sent in companies.db: {len(sent_companies)}")
            print(f"Total companies in email_tracking.db: {len(tracked_companies)}")
            
            # 4. Check for any discrepancies
            discrepancies = []
            for _, sent_company in sent_companies.iterrows():
                match = tracked_companies[
                    (tracked_companies['company_name'].str.strip().str.lower() == sent_company['company_name'].strip().lower()) &
                    (tracked_companies['hr_email'].str.strip().str.lower() == sent_company['hr_email'].strip().lower())
                ]
                
                if match.empty:
                    discrepancies.append({
                        'type': 'missing_in_tracking',
                        'company_name': sent_company['company_name'],
                        'hr_email': sent_company['hr_email'],
                        'sent_timestamp': sent_company['sent_timestamp']
                    })
                elif match.iloc[0]['sent_date'] != sent_company['sent_timestamp']:
                    discrepancies.append({
                        'type': 'timestamp_mismatch',
                        'company_name': sent_company['company_name'],
                        'hr_email': sent_company['hr_email'],
                        'companies_timestamp': sent_company['sent_timestamp'],
                        'tracking_timestamp': match.iloc[0]['sent_date']
                    })
            
            # 5. Report discrepancies
            if discrepancies:
                print("\nFound discrepancies:")
                for disc in discrepancies:
                    if disc['type'] == 'missing_in_tracking':
                        print(f"\nCompany missing in tracking.db:")
                        print(f"Name: {disc['company_name']}")
                        print(f"Email: {disc['hr_email']}")
                        print(f"Sent at: {disc['sent_timestamp']}")
                    else:
                        print(f"\nTimestamp mismatch for company:")
                        print(f"Name: {disc['company_name']}")
                        print(f"Email: {disc['hr_email']}")
                        print(f"Companies.db timestamp: {disc['companies_timestamp']}")
                        print(f"Tracking.db timestamp: {disc['tracking_timestamp']}")
            else:
                print("\nNo discrepancies found! Databases are fully synchronized.")
            
            # 6. Show recent activity
            print("\n=== Recent Activity ===")
            print("\nMost recent emails sent (companies.db):")
            recent_companies = sent_companies.head(5)
            for _, company in recent_companies.iterrows():
                print(f"\nCompany: {company['company_name']}")
                print(f"Email: {company['hr_email']}")
                print(f"Sent at: {company['sent_timestamp']}")
                print(f"Status: {company['status']}")
            
            print("\nMost recent emails tracked (email_tracking.db):")
            recent_tracked = tracked_companies.head(5)
            for _, company in recent_tracked.iterrows():
                print(f"\nCompany: {company['company_name']}")
                print(f"Email: {company['hr_email']}")
                print(f"Sent at: {company['sent_date']}")
                print(f"Status: {company['status']}")
                print(f"Follow-up: {company['is_followup']}")
            
    except Exception as e:
        logger.error(f"Error verifying sync: {str(e)}")
        raise

if __name__ == '__main__':
    verify_sync() 