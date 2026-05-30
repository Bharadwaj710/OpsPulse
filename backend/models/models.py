from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True) # Use Supabase Auth ID
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    avatar_url = db.Column(db.String, nullable=True)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'admin' | 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String, default='Pending') # Pending, In Progress, Completed
    created_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    product_image_url = db.Column(db.Text, nullable=True)
    revision_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tasks')

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    action = db.Column(db.String, nullable=False)
    performed_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    # Phase 2: Audit log extensions (preserving existing name and columns)
    entity_type = db.Column(db.String(50), default='task')
    old_value = db.Column(db.JSON, nullable=True)
    new_value = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GeneratedImage(db.Model):
    __tablename__ = 'generated_images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    generated_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=True) # Matches users.id (UUID internally but String in SQLAlchemy)
    image_type = db.Column(db.String(50), nullable=False)
    angle = db.Column(db.String(20), nullable=True)
    image_url = db.Column(db.Text, nullable=False)
    prompt_used = db.Column(db.Text, nullable=True)
    metadata_ = db.Column('metadata', db.JSON, nullable=True) # Alias to avoid python keyword
    is_final = db.Column(db.Boolean, default=False)
    job_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GenerationJob(db.Model):
    __tablename__ = 'generation_jobs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)