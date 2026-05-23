"""
Advanced filtering system
Supports complex queries with multiple conditions and operators
"""
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from datetime import datetime, date
from sqlalchemy import and_, or_, not_, Column, String, Integer, Float, DateTime
from sqlalchemy.orm import Query

from src.utils.logger import logger


class FilterOperator(str, Enum):
    """Filter comparison operators"""
    EQ = "eq"           # Equal
    NEQ = "neq"         # Not equal
    GT = "gt"           # Greater than
    GTE = "gte"         # Greater than or equal
    LT = "lt"           # Less than
    LTE = "lte"         # Less than or equal
    IN = "in"           # In list
    NIN = "nin"         # Not in list
    CONTAINS = "contains"  # String contains
    STARTSWITH = "startswith"  # Starts with
    ENDSWITH = "endswith"      # Ends with
    BETWEEN = "between"        # Between range
    EXISTS = "exists"          # Field exists/not null


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions"""
    AND = "and"
    OR = "or"
    NOT = "not"


class FilterCondition:
    """Single filter condition"""
    
    def __init__(self, 
                 field: str,
                 operator: FilterOperator,
                 value: Any = None):
        self.field = field
        self.operator = operator
        self.value = value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value
        }


class FilterGroup:
    """Group of conditions with logical operator"""
    
    def __init__(self, logical_op: LogicalOperator = LogicalOperator.AND):
        self.logical_op = logical_op
        self.conditions: List[Union[FilterCondition, 'FilterGroup']] = []
    
    def add_condition(self, condition: FilterCondition):
        """Add a condition"""
        self.conditions.append(condition)
    
    def add_group(self, group: 'FilterGroup'):
        """Add a nested group"""
        self.conditions.append(group)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "operator": self.logical_op,
            "conditions": [
                c.to_dict() if isinstance(c, FilterCondition) else c.to_dict()
                for c in self.conditions
            ]
        }


class AdvancedFilter:
    """Advanced query filter builder"""
    
    def __init__(self):
        self.root_group = FilterGroup()
        self.current_group = self.root_group
        self.field_types: Dict[str, type] = {}
        self.date_fields: List[str] = []
    
    def register_field(self, field_name: str, field_type: type, is_date: bool = False):
        """Register a field type for validation"""
        self.field_types[field_name] = field_type
        if is_date:
            self.date_fields.append(field_name)
    
    def add_condition(self,
                     field: str,
                     operator: FilterOperator,
                     value: Any = None) -> 'AdvancedFilter':
        """Add a filter condition"""
        condition = FilterCondition(field, operator, value)
        self.current_group.add_condition(condition)
        return self
    
    def start_group(self, logical_op: LogicalOperator = LogicalOperator.AND) -> 'AdvancedFilter':
        """Start a new condition group"""
        new_group = FilterGroup(logical_op)
        self.current_group.add_group(new_group)
        self.current_group = new_group
        return self
    
    def end_group(self) -> 'AdvancedFilter':
        """End current group (go back to parent)"""
        # This would need reference to parent group
        # Simplified for now
        return self
    
    def build_query(self, query: Query, model_class: type) -> Query:
        """
        Build SQLAlchemy query from filters
        
        Args:
            query: Base query
            model_class: SQLAlchemy model class
            
        Returns:
            Filtered query
        """
        try:
            clauses = self._build_clauses(self.root_group, model_class)
            
            if clauses:
                query = query.filter(clauses)
            
            logger.debug(f"Built query with filters")
            return query
            
        except Exception as e:
            logger.error(f"Error building query: {e}")
            return query
    
    def _build_clauses(self, group: FilterGroup, model_class: type):
        """Build SQL clauses from condition group"""
        clauses = []
        
        for item in group.conditions:
            if isinstance(item, FilterCondition):
                clause = self._build_clause(item, model_class)
                if clause is not None:
                    clauses.append(clause)
            elif isinstance(item, FilterGroup):
                clause = self._build_clauses(item, model_class)
                if clause is not None:
                    clauses.append(clause)
        
        if not clauses:
            return None
        
        if group.logical_op == LogicalOperator.AND:
            return and_(*clauses)
        elif group.logical_op == LogicalOperator.OR:
            return or_(*clauses)
        else:
            return not_(or_(*clauses))
    
    def _build_clause(self, condition: FilterCondition, model_class: type):
        """Build single SQL clause"""
        try:
            field = getattr(model_class, condition.field, None)
            if field is None:
                logger.warning(f"Field {condition.field} not found on model")
                return None
            
            operator = condition.operator
            value = condition.value
            
            # Build clause based on operator
            if operator == FilterOperator.EQ:
                return field == value
            elif operator == FilterOperator.NEQ:
                return field != value
            elif operator == FilterOperator.GT:
                return field > value
            elif operator == FilterOperator.GTE:
                return field >= value
            elif operator == FilterOperator.LT:
                return field < value
            elif operator == FilterOperator.LTE:
                return field <= value
            elif operator == FilterOperator.IN:
                return field.in_(value)
            elif operator == FilterOperator.NIN:
                return ~field.in_(value)
            elif operator == FilterOperator.CONTAINS:
                return field.contains(value)
            elif operator == FilterOperator.STARTSWITH:
                return field.startswith(value)
            elif operator == FilterOperator.ENDSWITH:
                return field.endswith(value)
            elif operator == FilterOperator.BETWEEN:
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    return field.between(value[0], value[1])
            elif operator == FilterOperator.EXISTS:
                return field.isnot(None) if value else field.is_(None)
            
            return None
            
        except Exception as e:
            logger.error(f"Error building clause for {condition.field}: {e}")
            return None
    
    def to_dict(self) -> Dict:
        """Convert filter to dictionary"""
        return self.root_group.to_dict()
    
    def to_json_string(self) -> str:
        """Convert filter to JSON string"""
        import json
        return json.dumps(self.to_dict())


class FilterParser:
    """Parse filter definitions from dictionaries/JSON"""
    
    @staticmethod
    def from_dict(filter_dict: Dict) -> AdvancedFilter:
        """Parse filter from dictionary"""
        filter_obj = AdvancedFilter()
        
        # Parse the filter definition
        if "conditions" in filter_dict:
            FilterParser._parse_group(filter_obj.root_group, filter_dict)
        
        return filter_obj
    
    @staticmethod
    def _parse_group(group: FilterGroup, group_dict: Dict):
        """Parse condition group"""
        if "operator" in group_dict:
            group.logical_op = LogicalOperator(group_dict["operator"])
        
        for item in group_dict.get("conditions", []):
            if "operator" in item and "conditions" in item:
                # Nested group
                new_group = FilterGroup()
                FilterParser._parse_group(new_group, item)
                group.add_group(new_group)
            elif "field" in item:
                # Condition
                condition = FilterCondition(
                    field=item["field"],
                    operator=FilterOperator(item["operator"]),
                    value=item.get("value")
                )
                group.add_condition(condition)


# Example usage helper
def create_filter_example() -> Dict:
    """Create example filter structure"""
    return {
        "operator": "and",
        "conditions": [
            {
                "field": "severity",
                "operator": "eq",
                "value": "HIGH"
            },
            {
                "operator": "or",
                "conditions": [
                    {
                        "field": "location_id",
                        "operator": "in",
                        "value": [1, 2, 3]
                    },
                    {
                        "field": "created_at",
                        "operator": "between",
                        "value": ["2026-04-01", "2026-04-02"]
                    }
                ]
            }
        ]
    }
