import argparse
import logging
import json
from datetime import datetime
from data_manager import DataManager
from email_engine import EmailEngine
from template_manager import TemplateManager
from tracker import EmailTracker
import os
import time
import signal
import sys
from typing import Dict, Any
import sqlite3

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('campaign.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json."""
    try:
        config_path = 'config.json'
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        # Validate required email settings
        if 'email' not in config:
            raise ValueError("Missing 'email' section in configuration")
            
        email_config = config['email']
        required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password']
        missing_fields = [field for field in required_fields if field not in email_config]
        
        if missing_fields:
            raise ValueError(f"Missing required email configuration fields: {', '.join(missing_fields)}")
            
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def save_progress(last_processed_id: int):
    """Save the last processed company ID to a progress file."""
    try:
        with open('campaign_progress.json', 'w') as f:
            json.dump({'last_processed_id': last_processed_id}, f)
    except Exception as e:
        logger.error(f"Error saving progress: {str(e)}")

def load_progress() -> int:
    """Load the last processed company ID from the progress file."""
    try:
        if os.path.exists('campaign_progress.json'):
            with open('campaign_progress.json', 'r') as f:
                return json.load(f).get('last_processed_id', 0)
    except Exception as e:
        logger.error(f"Error loading progress: {str(e)}")
    return 0

def signal_handler(signum, frame):
    """Handle signals to gracefully stop the campaign."""
    logger.info("\nReceived signal to stop. Saving progress...")
    sys.exit(0)

def run_campaign(resume_path: str, batch_size: int = 50, daily_limit: int = 500, background: bool = False):
    """Run the email campaign with rate limiting and error handling."""
    data_manager = None
    email_tracker = None
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize managers
        data_manager = DataManager()
        email_tracker = EmailTracker()  # Initialize email tracker
        config = load_config()
        email_engine = EmailEngine(config['email'])
        template_manager = TemplateManager()
        
        # Verify resume exists
        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume not found at {resume_path}")
        
        # Load template
        template = template_manager.get_template('job_inquiry')
        # Add resume to template attachments
        template['attachments'] = [resume_path]
        
        # Get companies to process
        companies = data_manager.get_unsent_companies(limit=daily_limit)
        total_companies = len(companies)
        logger.info(f"Starting campaign for {total_companies} companies")
        
        # Load progress
        last_processed_id = load_progress()
        if last_processed_id > 0:
            logger.info(f"Resuming from company ID {last_processed_id}")
            companies = [c for c in companies if c['id'] > last_processed_id]
            logger.info(f"Remaining companies to process: {len(companies)}")
        
        # Process companies in batches
        processed_count = 0
        current_batch = []  # Keep track of current batch for cleanup
        
        for i in range(0, len(companies), batch_size):
            try:
                batch = companies[i:i + batch_size]
                current_batch = batch  # Update current batch
                emails = []
                
                for company in batch:
                    try:
                        # Prepare email content
                        email_body = template_manager.format_template(
                            template,
                            company_name=company['company_name'],
                            hr_email=company['hr_email'],
                            hr_name="HR Manager",
                            position=company.get('position', 'Software Engineer')
                        )
                        
                        # Add to batch
                        emails.append({
                            'to_email': company['hr_email'],
                            'subject': f"Application for {company.get('position', 'Software Engineer')} at {company['company_name']}",
                            'content': email_body,
                            'company_id': company['id'],
                            'company_name': company['company_name'],
                            'hr_email': company['hr_email'],
                            'position': company.get('position', 'Software Engineer')
                        })
                        
                    except Exception as e:
                        logger.error(f"Error preparing email for company {company['company_name']}: {e}")
                        # Update both databases on failure
                        data_manager.mark_email_sent(company['id'], status='failed', error_message=str(e))
                        email_tracker.mark_email_sent(company['id'], status='failed', error_message=str(e))
                        save_progress(company['id'])
                        processed_count += 1
                
                if emails:
                    # Send emails in batch
                    results = email_engine.send_batch(emails, template)
                    
                    # Update both databases with results
                    for result in results:
                        company_id = result['company_id']
                        success = result['success']
                        error = result.get('error')
                        
                        # Update companies.db
                        data_manager.mark_email_sent(
                            company_id,
                            status='sent' if success else 'failed',
                            error_message=None if success else error
                        )
                        
                        # Update email_tracking.db
                        email_tracker.mark_email_sent(
                            company_id,
                            status='sent' if success else 'failed',
                            error_message=None if success else error
                        )
                        
                        # Save progress after each email
                        save_progress(company_id)
                        processed_count += 1
                        
                        # Log progress
                        logger.info(f"Progress: {processed_count}/{total_companies} companies processed")
                
                # Add delay between batches
                if i + batch_size < len(companies):
                    time.sleep(email_engine.batch_delay)
                    
            except KeyboardInterrupt:
                logger.info("\nCampaign interrupted by user. Cleaning up current batch...")
                # Update status for any remaining companies in current batch
                for company in current_batch:
                    if company['id'] > last_processed_id:
                        data_manager.mark_email_sent(company['id'], status='pending')
                        email_tracker.mark_email_sent(company['id'], status='pending')
                
                logger.info(f"Processed {processed_count} out of {total_companies} companies.")
                logger.info(f"Last processed company ID: {load_progress()}")
                logger.info("You can resume the campaign later by running the script again.")
                sys.exit(0)
        
        logger.info(f"Campaign completed. Sent {processed_count} emails.")
        
        # Save final progress and exit
        if processed_count > 0:
            save_progress(companies[-1]['id'] if companies else last_processed_id)
            
            # Final verification of database updates
            logger.info("Verifying database updates...")
            for company in companies:
                if company['id'] > last_processed_id:
                    # Verify in companies.db
                    with sqlite3.connect('data/companies.db') as conn:
                        cursor = conn.execute("""
                            SELECT status, sent_timestamp 
                            FROM companies 
                            WHERE id = ?
                        """, (company['id'],))
                        result = cursor.fetchone()
                        if result:
                            logger.info(f"Companies DB - ID {company['id']}: status={result[0]}, sent={result[1]}")
                    
                    # Verify in email_tracking.db
                    with sqlite3.connect('data/email_tracking.db') as conn:
                        cursor = conn.execute("""
                            SELECT status, sent_date 
                            FROM sent_emails 
                            WHERE company_id = ?
                        """, (company['id'],))
                        result = cursor.fetchone()
                        if result:
                            logger.info(f"Tracking DB - ID {company['id']}: status={result[0]}, sent={result[1]}")
        
        # Exit with success code
        logger.info("Campaign completed successfully. Exiting...")
        if background:
            # In background mode, ensure all database connections are closed
            if data_manager:
                data_manager.close()
            if email_tracker:
                email_tracker.close()
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("\nCampaign interrupted by user. Cleaning up...")
        # Update status for any remaining companies in current batch
        if current_batch:
            for company in current_batch:
                if company['id'] > last_processed_id:
                    data_manager.mark_email_sent(company['id'], status='pending')
                    email_tracker.mark_email_sent(company['id'], status='pending')
        
        logger.info(f"Last processed company ID: {load_progress()}")
        logger.info("You can resume the campaign later by running the script again.")
        if background:
            # In background mode, ensure all database connections are closed
            if data_manager:
                data_manager.close()
            if email_tracker:
                email_tracker.close()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running campaign: {str(e)}")
        if background:
            # In background mode, ensure all database connections are closed
            if data_manager:
                data_manager.close()
            if email_tracker:
                email_tracker.close()
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run email campaign')
    parser.add_argument('--resume', required=True, help='Path to resume file')
    parser.add_argument('--batch-size', type=int, default=50, help='Number of emails to send in each batch')
    parser.add_argument('--daily-limit', type=int, default=500, help='Maximum number of emails to send per day')
    parser.add_argument('--background', action='store_true', help='Run in background mode')
    args = parser.parse_args()
    
    if args.background:
        # Detach from terminal
        pid = os.fork()
        if pid > 0:
            print(f"Campaign started in background with PID {pid}")
            sys.exit(0)
    
    run_campaign(args.resume, args.batch_size, args.daily_limit, args.background) 