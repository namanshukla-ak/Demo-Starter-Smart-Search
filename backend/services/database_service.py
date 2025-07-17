"""
Database service for Neurologix Smart Search POV
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any, Optional
import boto3
import json
from datetime import datetime
from config.settings import get_settings, get_database_url, get_aws_config
from backend.models.schemas import SymptomData, ReactionTimeData, Patient

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = create_engine(get_database_url())
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize AWS clients
        aws_config = get_aws_config()
        self.s3_client = boto3.client('s3', **aws_config)
        self.opensearch_client = None  # Initialize when needed
    
    def get_db_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def get_patients_by_team(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all patients for a specific team"""
        with self.get_db_session() as db:
            query = text("""
                SELECT patient_id, name, team_id, age, position, created_at, updated_at
                FROM patients 
                WHERE team_id = :team_id
            """)
            result = db.execute(query, {"team_id": team_id})
            return [dict(row._mapping) for row in result]
    
    def get_symptom_data(self, patient_id: Optional[str] = None, 
                        team_id: Optional[str] = None,
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get symptom assessment data with filters"""
        with self.get_db_session() as db:
            base_query = """
                SELECT s.*, p.name as patient_name, p.team_id
                FROM symptom_assessments s
                JOIN patients p ON s.patient_id = p.patient_id
                WHERE 1=1
            """
            params = {}
            
            if patient_id:
                base_query += " AND s.patient_id = :patient_id"
                params["patient_id"] = patient_id
            
            if team_id:
                base_query += " AND p.team_id = :team_id"
                params["team_id"] = team_id
            
            if date_from:
                base_query += " AND s.assessment_date >= :date_from"
                params["date_from"] = date_from
            
            if date_to:
                base_query += " AND s.assessment_date <= :date_to"
                params["date_to"] = date_to
            
            base_query += " ORDER BY s.assessment_date DESC"
            
            result = db.execute(text(base_query), params)
            return [dict(row._mapping) for row in result]
    
    def get_reaction_time_data(self, patient_id: Optional[str] = None,
                              team_id: Optional[str] = None,
                              date_from: Optional[datetime] = None,
                              date_to: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get reaction time test data with filters"""
        with self.get_db_session() as db:
            base_query = """
                SELECT r.*, p.name as patient_name, p.team_id
                FROM reaction_time_tests r
                JOIN patients p ON r.patient_id = p.patient_id
                WHERE 1=1
            """
            params = {}
            
            if patient_id:
                base_query += " AND r.patient_id = :patient_id"
                params["patient_id"] = patient_id
            
            if team_id:
                base_query += " AND p.team_id = :team_id"
                params["team_id"] = team_id
            
            if date_from:
                base_query += " AND r.assessment_date >= :date_from"
                params["date_from"] = date_from
            
            if date_to:
                base_query += " AND r.assessment_date <= :date_to"
                params["date_to"] = date_to
            
            base_query += " ORDER BY r.assessment_date DESC"
            
            result = db.execute(text(base_query), params)
            return [dict(row._mapping) for row in result]
    
    def get_s3_assessment_data(self, patient_id: str, assessment_type: str) -> Dict[str, Any]:
        """Get detailed assessment data from S3"""
        try:
            s3_key = f"assessments/{patient_id}/{assessment_type}/latest.json"
            response = self.s3_client.get_object(
                Bucket=self.settings.aws_s3_bucket,
                Key=s3_key
            )
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except Exception as e:
            print(f"Error fetching S3 data: {e}")
            return {}
    
    def calculate_symptom_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate symptom-related metrics"""
        if not data:
            return {}
        
        total_scores = [row['total_symptom_score'] for row in data]
        headache_scores = [row['headache_severity'] for row in data]
        
        return {
            "avg_total_symptom_score": sum(total_scores) / len(total_scores),
            "max_total_symptom_score": max(total_scores),
            "avg_headache_severity": sum(headache_scores) / len(headache_scores),
            "patient_count": len(set(row['patient_id'] for row in data)),
            "assessment_count": len(data)
        }
    
    def calculate_reaction_time_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate reaction time-related metrics"""
        if not data:
            return {}
        
        avg_times = [row['average_reaction_time'] for row in data]
        accuracies = [row['accuracy_percentage'] for row in data]
        
        return {
            "avg_reaction_time": sum(avg_times) / len(avg_times),
            "max_reaction_time": max(avg_times),
            "min_reaction_time": min(avg_times),
            "avg_accuracy": sum(accuracies) / len(accuracies),
            "patient_count": len(set(row['patient_id'] for row in data)),
            "test_count": len(data)
        }
