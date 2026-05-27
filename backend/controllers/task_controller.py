from flask import request
from services.task_service import TaskService
from utils.responses import api_response

class TaskController:
    @staticmethod
    def create_task():
        data = request.get_json()
        if not data or 'title' not in data:
            return api_response(False, "Title is required", status_code=400)
        
        try:
            task = TaskService.create_task(data, request.user_id)
            return api_response(True, "Task created successfully", {
                "id": task.id, 
                "title": task.title, 
                "status": task.status
            }, 201)
        except Exception as e:
            return api_response(False, str(e), status_code=500)

    @staticmethod
    def get_tasks():
        try:
            tasks = TaskService.get_user_tasks(request.user_id)
            data = [{
                "id": t.id, 
                "title": t.title, 
                "description": t.description,
                "status": t.status, 
                "created_by": t.created_by,
                "created_by_name": t.creator.name if t.creator else "Unknown",
                "assigned_to": t.assigned_to,
                "assigned_to_name": t.assignee.name if t.assignee else "Unassigned",
                "created_at": t.created_at
            } for t in tasks]
            return api_response(True, "Tasks fetched successfully", data)
        except Exception as e:
            return api_response(False, str(e), status_code=500)

    @staticmethod
    def update_status():
        data = request.get_json()
        task_id = request.json.get('id')
        status = request.json.get('status')
        
        if not task_id or not status:
            return api_response(False, "Task ID and status are required", status_code=400)
            
        valid_statuses = {'Pending', 'In Progress', 'Completed'}
        if status not in valid_statuses:
            return api_response(False, f"Invalid status. Must be one of {list(valid_statuses)}", status_code=400)
            
        try:
            task = TaskService.update_task_status(task_id, status, request.user_id)
            if not task:
                return api_response(False, "Task not found", status_code=404)
            return api_response(True, "Status updated successfully", {"id": task.id, "status": task.status})
        except PermissionError as pe:
            return api_response(False, str(pe), status_code=403)
        except Exception as e:
            return api_response(False, str(e), status_code=500)

    @staticmethod
    def delete_task(task_id):
        try:
            success = TaskService.delete_task(task_id, request.user_id)
            if success is None:
                return api_response(False, "Task not found", status_code=404)
            return api_response(True, "Task deleted successfully")
        except PermissionError as pe:
            return api_response(False, str(pe), status_code=403)
        except Exception as e:
            return api_response(False, str(e), status_code=500)

    @staticmethod
    def update_task(task_id):
        data = request.get_json()
        if not data:
            return api_response(False, "Data is required", status_code=400)
        
        try:
            task = TaskService.update_task(task_id, data, request.user_id)
            if not task:
                return api_response(False, "Task not found", status_code=404)
            return api_response(True, "Task updated successfully", {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "assigned_to": task.assigned_to
            })
        except PermissionError as pe:
            return api_response(False, str(pe), status_code=403)
        except Exception as e:
            return api_response(False, str(e), status_code=500)

    @staticmethod
    def get_activities():
        try:
            from models.models import Task, User
            logs = TaskService.get_activities(request.user_id)
            data = []
            for log in logs:
                task = Task.query.get(log.task_id)
                user = User.query.get(log.performed_by)
                data.append({
                    "id": log.id,
                    "task_id": log.task_id,
                    "task_title": task.title if task else "Deleted Task",
                    "action": log.action,
                    "performed_by": log.performed_by,
                    "performed_by_name": user.name if user else "Unknown",
                    "created_at": log.created_at
                })
            return api_response(True, "Activity logs fetched successfully", data)
        except Exception as e:
            return api_response(False, str(e), status_code=500)