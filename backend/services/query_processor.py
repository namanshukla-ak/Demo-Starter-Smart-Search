"""
Query processing service for natural language interpretation
"""
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from backend.models.schemas import QueryClassification, AssessmentType
from backend.services.database_service import DatabaseService

class QueryProcessor:
    """Service for processing natural language queries"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        
        # Keywords mapping for intent classification
        self.symptom_keywords = [
            "headache", "nausea", "dizziness", "confusion", "memory", 
            "emotional", "symptom", "symptoms", "pain", "score"
        ]
        
        self.reaction_time_keywords = [
            "reaction", "time", "speed", "cognitive", "response", 
            "accuracy", "performance", "test"
        ]
        
        self.aggregation_keywords = {
            "average": ["average", "avg", "mean"],
            "maximum": ["max", "maximum", "highest", "worst"],
            "minimum": ["min", "minimum", "lowest", "best"],
            "count": ["count", "number", "how many"],
            "list": ["list", "show", "display", "who"]
        }
        
        self.time_patterns = {
            "last_week": ["last week", "past week"],
            "last_month": ["last month", "past month"],
            "last_30_days": ["last 30 days", "past 30 days"],
            "today": ["today", "today's"],
            "yesterday": ["yesterday"]
        }
    
    def classify_query(self, question: str) -> QueryClassification:
        """Classify the natural language query"""
        question_lower = question.lower()
        
        # Determine modules
        modules = []
        if any(keyword in question_lower for keyword in self.symptom_keywords):
            modules.append(AssessmentType.SYMPTOM_CHECKLIST)
        if any(keyword in question_lower for keyword in self.reaction_time_keywords):
            modules.append(AssessmentType.REACTION_TIME)
        
        # If no specific module detected, include both
        if not modules:
            modules = [AssessmentType.SYMPTOM_CHECKLIST, AssessmentType.REACTION_TIME]
        
        # Determine intent
        intent = self._determine_intent(question_lower)
        
        # Extract metrics
        metrics = self._extract_metrics(question_lower, modules)
        
        # Extract time range
        time_range = self._extract_time_range(question_lower)
        
        # Extract filters
        filters = self._extract_filters(question_lower)
        
        return QueryClassification(
            intent=intent,
            modules=modules,
            metrics=metrics,
            filters=filters,
            time_range=time_range,
            confidence=0.8  # TODO: Implement actual confidence calculation
        )
    
    def _determine_intent(self, question: str) -> str:
        """Determine the main intent of the query"""
        for intent, keywords in self.aggregation_keywords.items():
            if any(keyword in question for keyword in keywords):
                return intent
        
        # Default intent based on common patterns
        if "compare" in question or "vs" in question:
            return "compare"
        elif "trend" in question or "over time" in question:
            return "trend"
        elif "alert" in question or "concern" in question:
            return "alert"
        else:
            return "summary"
    
    def _extract_metrics(self, question: str, modules: List[AssessmentType]) -> List[str]:
        """Extract specific metrics to calculate"""
        metrics = []
        
        if AssessmentType.SYMPTOM_CHECKLIST in modules:
            if "headache" in question:
                metrics.append("headache_severity")
            if "total" in question and "score" in question:
                metrics.append("total_symptom_score")
            if not metrics:  # Default symptom metrics
                metrics.extend(["total_symptom_score", "headache_severity"])
        
        if AssessmentType.REACTION_TIME in modules:
            if "accuracy" in question:
                metrics.append("accuracy_percentage")
            if "reaction" in question and "time" in question:
                metrics.append("average_reaction_time")
            if not any("reaction" in m for m in metrics):  # Default reaction time metrics
                metrics.append("average_reaction_time")
        
        return metrics
    
    def _extract_time_range(self, question: str) -> Optional[Dict[str, str]]:
        """Extract time range from the question"""
        for period, patterns in self.time_patterns.items():
            if any(pattern in question for pattern in patterns):
                return {"period": period}
        
        # Look for specific date patterns
        date_pattern = r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b'
        dates = re.findall(date_pattern, question)
        if dates:
            return {"custom_dates": dates}
        
        return None
    
    def _extract_filters(self, question: str) -> Dict[str, Any]:
        """Extract filters like team, player names, etc."""
        filters = {}
        
        # Look for team names (LSU, Tigers, etc.)
        team_pattern = r'\b(LSU|Tigers|[A-Z][a-z]+ [A-Z][a-z]+)\b'
        teams = re.findall(team_pattern, question)
        if teams:
            filters["team"] = teams[0]
        
        # Look for severity thresholds
        if "severe" in question:
            filters["min_severity"] = 4
        elif "moderate" in question:
            filters["min_severity"] = 2
        
        return filters
    
    def process_query(self, question: str, user_id: Optional[str] = None, 
                     team_id: Optional[str] = None) -> Dict[str, Any]:
        """Process the complete query and return results"""
        
        # Classify the query
        classification = self.classify_query(question)
        
        # Convert time range to datetime objects
        date_range = self._convert_time_range(classification.time_range)
        
        # Fetch data based on classification
        results = []
        
        if AssessmentType.SYMPTOM_CHECKLIST in classification.modules:
            symptom_data = self.db_service.get_symptom_data(
                team_id=team_id or classification.filters.get("team"),
                date_from=date_range.get("start"),
                date_to=date_range.get("end")
            )
            if symptom_data:
                symptom_metrics = self.db_service.calculate_symptom_metrics(symptom_data)
                results.append({
                    "module": "symptom_checklist",
                    "data": symptom_metrics,
                    "count": len(symptom_data)
                })
        
        if AssessmentType.REACTION_TIME in classification.modules:
            reaction_data = self.db_service.get_reaction_time_data(
                team_id=team_id or classification.filters.get("team"),
                date_from=date_range.get("start"),
                date_to=date_range.get("end")
            )
            if reaction_data:
                reaction_metrics = self.db_service.calculate_reaction_time_metrics(reaction_data)
                results.append({
                    "module": "reaction_time",
                    "data": reaction_metrics,
                    "count": len(reaction_data)
                })
        
        # Generate natural language response
        response = self._generate_response(classification, results)
        
        return {
            "answer": response,
            "confidence": classification.confidence,
            "source_modules": [r["module"] for r in results],
            "metadata": {
                "classification": classification.dict(),
                "results": results,
                "query_type": classification.intent
            }
        }
    
    def _convert_time_range(self, time_range: Optional[Dict[str, str]]) -> Dict[str, Optional[datetime]]:
        """Convert time range strings to datetime objects"""
        if not time_range:
            return {"start": None, "end": None}
        
        now = datetime.now()
        
        if "period" in time_range:
            period = time_range["period"]
            if period == "last_week":
                return {"start": now - timedelta(weeks=1), "end": now}
            elif period == "last_month":
                return {"start": now - timedelta(days=30), "end": now}
            elif period == "last_30_days":
                return {"start": now - timedelta(days=30), "end": now}
            elif period == "today":
                return {"start": now.replace(hour=0, minute=0, second=0), "end": now}
            elif period == "yesterday":
                yesterday = now - timedelta(days=1)
                return {
                    "start": yesterday.replace(hour=0, minute=0, second=0),
                    "end": yesterday.replace(hour=23, minute=59, second=59)
                }
        
        return {"start": None, "end": None}
    
    def _generate_response(self, classification: QueryClassification, results: List[Dict]) -> str:
        """Generate natural language response from results"""
        if not results:
            return "I couldn't find any data matching your query. Please try with different criteria."
        
        response_parts = []
        
        for result in results:
            module = result["module"]
            data = result["data"]
            count = result["count"]
            
            if module == "symptom_checklist":
                response_parts.append(
                    f"Based on {count} symptom assessments, the average total symptom score is "
                    f"{data.get('avg_total_symptom_score', 0):.1f}. "
                    f"Average headache severity is {data.get('avg_headache_severity', 0):.1f} out of 6."
                )
            elif module == "reaction_time":
                response_parts.append(
                    f"Based on {count} reaction time tests, the average reaction time is "
                    f"{data.get('avg_reaction_time', 0):.0f}ms with an average accuracy of "
                    f"{data.get('avg_accuracy', 0):.1f}%."
                )
        
        # Add summary based on intent
        if classification.intent == "alert" and results:
            response_parts.append("\n\nThis data may require clinical attention if values are significantly elevated from baseline.")
        
        return " ".join(response_parts)
