"""
xpSHACL Architecture
--------------------
This module defines the core data structures used throughout the xpSHACL system,
including constraint violations, justification trees, and context information.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# --- Enums ---
class ViolationType(Enum):
    """Enumeration of different types of SHACL violations."""

    CARDINALITY = "cardinality"
    VALUE_TYPE = "value_type"
    VALUE_RANGE = "value_range"
    PATTERN = "pattern"
    PROPERTY_PAIR = "property_pair"
    LOGICAL = "logical"
    OTHER = "other"


# --- Basic Type Aliases ---
NodeId = str
ShapeId = str


# --- Data Classes ---
@dataclass
class ConstraintViolation:
    """
    Represents a SHACL constraint violation.
    Captures detailed information about the violation for building explanations.
    """

    focus_node: NodeId
    shape_id: ShapeId
    constraint_id: str
    violation_type: ViolationType
    property_path: Optional[str] = None
    value: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None
    context: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert ConstraintViolation to a dictionary."""
        return {
            "focus_node": self.focus_node,
            "shape_id": self.shape_id,
            "constraint_id": self.constraint_id,
            "violation_type": self.violation_type.value,  # Serialize Enum value
            "property_path": self.property_path,
            "value": self.value,
            "message": self.message,
            "severity": self.severity,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create a ConstraintViolation from a dictionary."""
        violation_type_value = data.get("violation_type")
        violation_type = (
            ViolationType(violation_type_value) if violation_type_value else None
        )
        return cls(
            focus_node=data["focus_node"],
            shape_id=data["shape_id"],
            constraint_id=data["constraint_id"],
            violation_type=violation_type,
            property_path=data.get("property_path"),
            value=data.get("value"),
            message=data.get("message"),
            severity=data.get("severity"),
            context=data.get("context", {}),
        )


@dataclass
class JustificationNode:
    """Represents a node in a justification tree."""

    statement: str
    type: str  # e.g., "conclusion", "premise", "observation", "inference", "error"
    evidence: Optional[str] = None  # Optional evidence supporting the node
    children: List["JustificationNode"] = field(default_factory=list)

    def add_child(self, child: "JustificationNode"):
        """Adds a child node to this node."""
        self.children.append(child)

    def to_dict(self) -> Dict:
        """Convert node and its children to a dictionary"""
        return {
            "statement": self.statement,
            "type": self.type,
            "evidence": self.evidence,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create a JustificationNode from a dictionary."""
        return cls(
            statement=data["statement"],
            type=data["type"],
            evidence=data.get("evidence"),
            children=[
                cls.from_dict(child)
                for child in data.get(
                    "children",
                )
            ],
        )


@dataclass
class JustificationTree:
    """Represents a logical justification tree for a SHACL violation."""

    root: JustificationNode
    violation: ConstraintViolation

    def to_dict(self) -> Dict:
        """Convert the entire tree to a dictionary"""
        return {
            "violation": self.violation.to_dict(),
            "justification": self.root.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create a JustificationTree from a dictionary."""
        return cls(
            violation=ConstraintViolation.from_dict(data["violation"]),
            justification=JustificationNode.from_dict(data["justification"]),
        )


@dataclass
class DomainContext:
    """
    Captures contextual information relevant to a SHACL violation.
    This information is used to enrich the explanations generated by the LLM.
    """

    ontology_fragments: List[str] = field(default_factory=list)
    shape_documentation: List[str] = field(default_factory=list)
    similar_cases: List[Dict] = field(default_factory=list)
    domain_rules: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert DomainContext to a dictionary."""
        return {
            "ontology_fragments": self.ontology_fragments,
            "shape_documentation": self.shape_documentation,
            "similar_cases": self.similar_cases,
            "domain_rules": self.domain_rules,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create a DomainContext from a dictionary."""
        return cls(
            ontology_fragments=data.get(
                "ontology_fragments",
            ),
            shape_documentation=data.get(
                "shape_documentation",
            ),
            similar_cases=data.get(
                "similar_cases",
            ),
            domain_rules=data.get(
                "domain_rules",
            ),
        )


@dataclass
class ExplanationOutput:
    """
    Represents the full output of the xpSHACL explanation system for a
    single violation.
    """

    natural_language_explanation: str
    correction_suggestions: Optional[str] = None
    violation: Optional[ConstraintViolation] = None
    justification_tree: Optional[JustificationTree] = None
    retrieved_context: Optional[DomainContext] = None
    provided_by_model: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to a dictionary for JSON output"""
        return {
            "violation": self.violation.to_dict() if self.violation else None,
            "justification_tree": (
                self.justification_tree.to_dict() if self.justification_tree else None
            ),
            "retrieved_context": (
                self.retrieved_context.to_dict() if self.retrieved_context else None
            ),
            "natural_language_explanation": self.natural_language_explanation,
            "correction_suggestions": self.correction_suggestions,
            "provided_by_model": self.provided_by_model,
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create an ExplanationOutput from a dictionary."""
        return cls(
            natural_language_explanation=data["natural_language_explanation"],
            correction_suggestions=data.get(
                "correction_suggestions",
            ),
            violation=(
                ConstraintViolation.from_dict(data["violation"])
                if data.get("violation")
                else None
            ),
            justification_tree=(
                JustificationTree.from_dict(data["justification_tree"])
                if data.get("justification_tree")
                else None
            ),
            retrieved_context=(
                DomainContext.from_dict(data["retrieved_context"])
                if data.get("retrieved_context")
                else None
            ),
            provided_by_model=data["provided_by_model"],
        )
