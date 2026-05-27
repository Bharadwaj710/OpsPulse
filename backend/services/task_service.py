from models.models import db, Task, ActivityLog, User
from datetime import datetime
from services.email_service import EmailService

class TaskService:
    @staticmethod
    def create_task(data, user_id):
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status='Pending',
            created_by=user_id,
            assigned_to=data.get('assigned_to')
        )
        db.session.add(task)
        db.session.commit()
        
        # Log the activity
        log = ActivityLog(task_id=task.id, action="Task Created", performed_by=user_id)
        db.session.add(log)
        db.session.commit()
        
        # Send Email Notification if assigned
        if task.assigned_to:
            assignee = db.session.get(User, task.assigned_to)
            assigner = db.session.get(User, user_id)
            if assignee and assignee.email:
                assigner_name = assigner.name if assigner else "A team member"
                EmailService.send_task_assigned_email(assignee.email, task.title, assigner_name)
        
        return task

    @staticmethod
    def get_user_tasks(user_id):
        # Get tasks created by user OR assigned to user
        return Task.query.filter(
            (Task.created_by == user_id) | (Task.assigned_to == user_id)
        ).order_by(Task.created_at.desc()).all()

    @staticmethod
    def update_task_status(task_id, status, user_id):
        task = db.session.get(Task, task_id)
        if not task:
            return None
        
        # Verify access: either created_by or assigned_to must match user_id
        created_by_str = str(task.created_by) if task.created_by else None
        assigned_to_str = str(task.assigned_to) if task.assigned_to else None
        user_id_str = str(user_id) if user_id else None
        
        if created_by_str != user_id_str and assigned_to_str != user_id_str:
            raise PermissionError("You do not have access to update this task")
        
        old_status = task.status
        task.status = status
        if status == 'Completed':
            task.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        log = ActivityLog(task_id=task.id, action=f"Status changed to {status}", performed_by=user_id)
        db.session.add(log)
        db.session.commit()
        
        # Send Email Notification if completed and status actually changed
        if status == 'Completed' and old_status != 'Completed':
            completer = db.session.get(User, user_id)
            completer_name = completer.name if completer else "A team member"
            
            # Notify creator
            creator = db.session.get(User, task.created_by)
            if creator and creator.email and created_by_str != user_id_str:
                EmailService.send_task_completed_email(creator.email, task.title, completer_name)
                
            # Notify assignee if different from completer
            if assigned_to_str and assigned_to_str != user_id_str and assigned_to_str != created_by_str:
                assignee = db.session.get(User, task.assigned_to)
                if assignee and assignee.email:
                    EmailService.send_task_completed_email(assignee.email, task.title, completer_name)
        
        return task

    @staticmethod
    def delete_task(task_id, user_id):
        task = db.session.get(Task, task_id)
        if not task:
            return None
        
        created_by_str = str(task.created_by) if task.created_by else None
        user_id_str = str(user_id) if user_id else None
        if created_by_str != user_id_str:
            raise PermissionError("Only the creator can delete this task")
        
        # Delete related activity logs
        ActivityLog.query.filter_by(task_id=task_id).delete()
        
        db.session.delete(task)
        db.session.commit()
        return True

    @staticmethod
    def update_task(task_id, data, user_id):
        task = db.session.get(Task, task_id)
        if not task:
            return None
        
        created_by_str = str(task.created_by) if task.created_by else None
        user_id_str = str(user_id) if user_id else None
        if created_by_str != user_id_str:
            raise PermissionError("Only the creator can edit this task")
        
        old_assignee = task.assigned_to
        old_assignee_str = str(old_assignee) if old_assignee else None
        
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        
        assigned_to = data.get('assigned_to')
        if assigned_to == 'unassigned' or not assigned_to:
            task.assigned_to = None
        else:
            task.assigned_to = assigned_to
            
        db.session.commit()
        
        log = ActivityLog(task_id=task.id, action="Task Updated", performed_by=user_id)
        db.session.add(log)
        db.session.commit()
        
        # Send Email Notification if assignee changed
        assigned_to_str = str(task.assigned_to) if task.assigned_to else None
        if assigned_to_str and assigned_to_str != old_assignee_str:
            assignee = db.session.get(User, task.assigned_to)
            assigner = db.session.get(User, user_id)
            if assignee and assignee.email:
                assigner_name = assigner.name if assigner else "A team member"
                EmailService.send_task_assigned_email(assignee.email, task.title, assigner_name)
                
        return task

    @staticmethod
    def get_activities(user_id):
        tasks = Task.query.filter(
            (Task.created_by == user_id) | (Task.assigned_to == user_id)
        ).all()
        task_ids = [t.id for t in tasks]
        if not task_ids:
            return []
        
        logs = ActivityLog.query.filter(
            ActivityLog.task_id.in_(task_ids)
        ).order_by(ActivityLog.created_at.desc()).limit(50).all()
        return logs