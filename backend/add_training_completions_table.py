"""
Add training_completions table to track when employees complete training
"""
from database import db
from app import app
from models import TrainingCompletion

with app.app_context():
    # Create the training_completions table
    db.create_all()
    print("training_completions table created successfully!")
