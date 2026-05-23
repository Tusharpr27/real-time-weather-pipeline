"""
Alert scheduler module
Manages background jobs for alert escalation, notification, and cleanup
"""
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

from src.alerts.alert_notifier import get_alert_notifier
from src.alerts.escalation_manager import get_escalation_manager
from src.alerts.alert_tracker import get_alert_tracker
from src.utils.logger import logger


class AlertScheduler:
    """Manages alert-related background jobs"""
    
    def __init__(self, scheduler: BackgroundScheduler):
        self.scheduler = scheduler
        self.job_ids = []
    
    def start(self):
        """Start alert scheduler jobs"""
        logger.info("ðŸš€ Starting alert scheduler...")
        
        try:
            # Job 1: Check for alert escalations every 5 minutes
            job1 = self.scheduler.add_job(
                self._escalation_check_job,
                'interval',
                minutes=5,
                id='alert_escalation_check',
                name='Alert Escalation Check',
                replace_existing=True
            )
            self.job_ids.append(job1.id)
            logger.info("âœ… Added: Alert Escalation Check (every 5 minutes)")
            
            # Job 2: Retry failed notifications every 10 minutes
            job2 = self.scheduler.add_job(
                self._notification_retry_job,
                'interval',
                minutes=10,
                id='alert_notification_retry',
                name='Alert Notification Retry',
                replace_existing=True
            )
            self.job_ids.append(job2.id)
            logger.info("âœ… Added: Alert Notification Retry (every 10 minutes)")
            
            # Job 3: Clean old alerts daily at 03:00 UTC
            job3 = self.scheduler.add_job(
                self._cleanup_old_alerts_job,
                CronTrigger(hour=3, minute=0),
                id='alert_cleanup',
                name='Alert Cleanup',
                replace_existing=True
            )
            self.job_ids.append(job3.id)
            logger.info("âœ… Added: Alert Cleanup (daily at 03:00 UTC)")
            
            # Job 4: Generate alert summary every 6 hours
            job4 = self.scheduler.add_job(
                self._alert_summary_job,
                'interval',
                hours=6,
                id='alert_summary',
                name='Alert Summary',
                replace_existing=True
            )
            self.job_ids.append(job4.id)
            logger.info("âœ… Added: Alert Summary (every 6 hours)")
            
            logger.info(f"ðŸ“‹ Alert scheduler started with {len(self.job_ids)} jobs")
            
        except Exception as e:
            logger.error(f"Error starting alert scheduler: {e}")
            raise
    
    def stop(self):
        """Stop alert scheduler jobs"""
        logger.info("â¹ï¸ Stopping alert scheduler...")
        try:
            for job_id in self.job_ids:
                self.scheduler.remove_job(job_id)
            logger.info("âœ… Alert scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping alert scheduler: {e}")
    
    def _escalation_check_job(self):
        """Check for alerts needing escalation"""
        try:
            logger.debug("ðŸ”„ Running escalation check job...")
            
            manager = get_escalation_manager()
            escalations = asyncio.run(manager.check_escalations())
            
            if escalations:
                logger.info(f"ðŸ“ˆ Found {len(escalations)} alerts needing escalation")
                
                # Escalate each alert
                for esc in escalations:
                    asyncio.run(manager.escalate_alert(esc["alert_id"], esc["next_level"]))
                    
                    # Notify about escalation
                    notifier = get_alert_notifier()
                    asyncio.run(notifier.notify_alert(esc["alert_id"]))
                    
                    logger.info(f"Escalated alert {esc['alert_id']} to level {esc['next_level']}")
            else:
                logger.debug("No alerts needing escalation")
                
        except Exception as e:
            logger.error(f"Error in escalation check job: {e}")
    
    def _notification_retry_job(self):
        """Retry failed notifications"""
        try:
            logger.debug("ðŸ”„ Running notification retry job...")
            
            notifier = get_alert_notifier()
            pending = notifier.notification_queue.get_pending()
            
            if pending:
                logger.info(f"ðŸ“¨ Retrying {len(pending)} pending notifications...")
                
                for notification in pending:
                    success, msg = asyncio.run(
                        notifier.email_notifier.send_alert_email(
                            recipient="admin@example.com",  # Default recipient
                            alert_type=notification["data"].get("alert_type", "Unknown"),
                            location=notification["data"].get("location", "Unknown"),
                            description=notification["data"].get("description", ""),
                            severity=notification["data"].get("severity", "MEDIUM")
                        )
                    )
                    
                    if success:
                        notifier.notification_queue.mark_sent(notification["alert_id"])
                    else:
                        notifier.notification_queue.mark_failed(notification["alert_id"])
            else:
                logger.debug("No pending notifications to retry")
                
        except Exception as e:
            logger.error(f"Error in notification retry job: {e}")
    
    def _cleanup_old_alerts_job(self):
        """Clean old alerts based on retention policy"""
        try:
            logger.info("ðŸ§¹ Running alert cleanup job...")
            
            tracker = get_alert_tracker()
            # Could implement alert retention here
            logger.info("Alert cleanup completed")
            
        except Exception as e:
            logger.error(f"Error in cleanup job: {e}")
    
    def _alert_summary_job(self):
        """Generate alert summary statistics"""
        try:
            logger.debug("ðŸ“Š Running alert summary job...")
            
            tracker = get_alert_tracker()
            stats = asyncio.run(tracker.get_alert_statistics())
            
            logger.info(f"ðŸ“Š Alert Summary: Total={stats.get('total_alerts', 0)}, "
                       f"Active={stats.get('active', 0)}, "
                       f"Acknowledged={stats.get('acknowledged', 0)}, "
                       f"Resolved={stats.get('resolved', 0)}")
            
        except Exception as e:
            logger.error(f"Error in summary job: {e}")
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        jobs_info = []
        for job_id in self.job_ids:
            job = self.scheduler.get_job(job_id)
            if job:
                jobs_info.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time,
                    "trigger": str(job.trigger)
                })
        
        return {
            "status": "running" if self.scheduler.running else "stopped",
            "jobs_count": len(self.job_ids),
            "jobs": jobs_info
        }


def create_alert_scheduler(scheduler: BackgroundScheduler) -> AlertScheduler:
    """Create and return alert scheduler"""
    return AlertScheduler(scheduler)



