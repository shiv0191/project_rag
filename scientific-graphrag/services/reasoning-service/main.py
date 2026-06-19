"""
Reasoning Services - Phase 10, 11, 12

Scientific Reasoning Engine
Reference Range Engine
Confidence Engine
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import json

from shared.utils.logger import setup_logging
from shared.schemas.models import ReferenceRangeCheckResult, ReferenceRange, Finding, Evidence

logger = setup_logging(__name__)


class ReferenceRangeEngine:
    """Phase 11: Reference Range Engine
    
    Manages reference ranges for different properties
    Compares values against ranges
    Flags abnormal values
    """
    
    def __init__(self):
        """Initialize reference range engine"""
        self.reference_ranges = self._load_default_ranges()
    
    def _load_default_ranges(self) -> Dict[str, ReferenceRange]:
        """Load default reference ranges"""
        ranges = {
            "Ferritin": ReferenceRange(
                property_name="Ferritin",
                unit="ng/mL",
                min_value=30.0,
                max_value=300.0,
                status="normal"
            ),
            "Hemoglobin": ReferenceRange(
                property_name="Hemoglobin",
                unit="g/dL",
                min_value=13.5,
                max_value=17.5,
                status="normal"
            ),
            "Hematocrit": ReferenceRange(
                property_name="Hematocrit",
                unit="%",
                min_value=41.0,
                max_value=53.0,
                status="normal"
            ),
            "WBC": ReferenceRange(
                property_name="WBC",
                unit="K/uL",
                min_value=4.5,
                max_value=11.0,
                status="normal"
            ),
            "Platelets": ReferenceRange(
                property_name="Platelets",
                unit="K/uL",
                min_value=150.0,
                max_value=400.0,
                status="normal"
            )
        }
        logger.info(f"Loaded {len(ranges)} reference ranges")
        return ranges
    
    def register_range(self, property_name: str, range_obj: ReferenceRange):
        """Register a reference range"""
        self.reference_ranges[property_name] = range_obj
        logger.info(f"Registered range for {property_name}")
    
    def check_value(
        self,
        property_name: str,
        value: float,
        unit: str = None
    ) -> ReferenceRangeCheckResult:
        """Check if a value is within reference range"""
        
        if property_name not in self.reference_ranges:
            logger.warning(f"No reference range found for {property_name}")
            return ReferenceRangeCheckResult(
                property_name=property_name,
                value=value,
                unit=unit or "unknown",
                reference_range=None,
                status="unknown"
            )
        
        ref_range = self.reference_ranges[property_name]
        
        if value < ref_range.min_value:
            status = "LOW"
        elif value > ref_range.max_value:
            status = "HIGH"
        else:
            status = "NORMAL"
        
        result = ReferenceRangeCheckResult(
            property_name=property_name,
            value=value,
            unit=unit or ref_range.unit,
            reference_range=ref_range,
            status=status
        )
        
        logger.info(f"Checked {property_name}: {value} -> {status}")
        return result
    
    def check_batch(
        self,
        measurements: Dict[str, float]
    ) -> List[ReferenceRangeCheckResult]:
        """Check multiple measurements"""
        results = []
        for property_name, value in measurements.items():
            result = self.check_value(property_name, value)
            results.append(result)
        
        logger.info(f"Checked {len(measurements)} measurements")
        return results


class ScientificReasoningEngine:
    """Phase 10: Scientific Reasoning Engine
    
    Generates findings based on measurements and evidence
    Compares values with reference ranges
    Explains evidence
    """
    
    def __init__(self):
        """Initialize reasoning engine"""
        self.reference_engine = ReferenceRangeEngine()
        self.clinical_rules = self._load_clinical_rules()
    
    def _load_clinical_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load clinical reasoning rules"""
        rules = {
            "anemia": [
                {
                    "name": "Iron Deficiency Anemia",
                    "conditions": [
                        {"metric": "Ferritin", "operator": "<", "value": 30},
                        {"metric": "Hemoglobin", "operator": "<", "value": 13.5}
                    ],
                    "confidence": 0.85
                },
                {
                    "name": "Vitamin B12 Deficiency",
                    "conditions": [
                        {"metric": "Hemoglobin", "operator": "<", "value": 12},
                        {"metric": "Ferritin", "operator": ">", "value": 100}
                    ],
                    "confidence": 0.75
                }
            ],
            "infection": [
                {
                    "name": "Possible Bacterial Infection",
                    "conditions": [
                        {"metric": "WBC", "operator": ">", "value": 11}
                    ],
                    "confidence": 0.70
                }
            ]
        }
        logger.info(f"Loaded {sum(len(v) for v in rules.values())} clinical rules")
        return rules
    
    def generate_findings(
        self,
        measurements: Dict[str, float],
        evidence_docs: List[Evidence] = None
    ) -> List[Finding]:
        """Generate findings from measurements"""
        
        findings = []
        
        # Check reference ranges
        range_checks = self.reference_engine.check_batch(measurements)
        abnormal_checks = [c for c in range_checks if c.status != "NORMAL"]
        
        if not abnormal_checks:
            return findings
        
        # Apply clinical rules
        for category, rules in self.clinical_rules.items():
            for rule in rules:
                if self._check_rule(rule, measurements):
                    finding = Finding(
                        finding_statement=rule["name"],
                        confidence=rule["confidence"],
                        evidence=evidence_docs or []
                    )
                    findings.append(finding)
        
        logger.info(f"Generated {len(findings)} findings")
        return findings
    
    def _check_rule(self, rule: Dict[str, Any], measurements: Dict[str, float]) -> bool:
        """Check if a rule applies"""
        for condition in rule["conditions"]:
            metric = condition["metric"]
            operator = condition["operator"]
            value = condition["value"]
            
            if metric not in measurements:
                return False
            
            measured_value = measurements[metric]
            
            if operator == "<" and not measured_value < value:
                return False
            elif operator == ">" and not measured_value > value:
                return False
            elif operator == "=" and not measured_value == value:
                return False
        
        return True
    
    def explain_finding(self, finding: Finding) -> str:
        """Generate explanation for a finding"""
        explanation = f"Finding: {finding.finding_statement}\n"
        explanation += f"Confidence: {finding.confidence:.2%}\n"
        explanation += f"Evidence sources: {len(finding.evidence)}\n"
        
        for idx, evidence in enumerate(finding.evidence, 1):
            explanation += f"\n  [{idx}] {evidence.source_document.content[:100]}...\n"
        
        return explanation


class ConfidenceEngine:
    """Phase 12: Confidence Engine
    
    Generates confidence scores based on:
    - Retrieval score
    - Reranker score
    - Graph evidence score
    """
    
    def __init__(self):
        """Initialize confidence engine"""
        self.weights = {
            "retrieval": 0.4,
            "reranker": 0.35,
            "graph": 0.25
        }
    
    def set_weights(self, weights: Dict[str, float]):
        """Set confidence score weights"""
        total = sum(weights.values())
        self.weights = {k: v/total for k, v in weights.items()}
        logger.info(f"Updated confidence weights: {self.weights}")
    
    def calculate_confidence(
        self,
        retrieval_score: float = 0.0,
        reranker_score: float = 0.0,
        graph_score: float = 0.0,
        source_count: int = 0
    ) -> float:
        """Calculate overall confidence score"""
        
        # Normalize scores to 0-1
        retrieval_score = max(0, min(1, retrieval_score))
        reranker_score = max(0, min(1, reranker_score))
        graph_score = max(0, min(1, graph_score))
        
        # Calculate weighted score
        confidence = (
            retrieval_score * self.weights["retrieval"] +
            reranker_score * self.weights["reranker"] +
            graph_score * self.weights["graph"]
        )
        
        # Apply source count boost (diminishing returns)
        if source_count > 0:
            source_boost = min(0.1, source_count * 0.02)  # Max 0.1 boost
            confidence = min(1.0, confidence + source_boost)
        
        return round(confidence, 3)
    
    def adjust_for_contradiction(self, confidence: float, contradiction_count: int) -> float:
        """Adjust confidence for contradictory evidence"""
        penalty = min(0.3, contradiction_count * 0.1)  # Max 0.3 penalty
        adjusted = max(0, confidence - penalty)
        return round(adjusted, 3)


# FastAPI app for reasoning service
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Reasoning Service", version="1.0.0")

reference_engine = ReferenceRangeEngine()
reasoning_engine = ScientificReasoningEngine()
confidence_engine = ConfidenceEngine()


class CheckValueRequest(BaseModel):
    property_name: str
    value: float
    unit: Optional[str] = None


class GenerateFindingsRequest(BaseModel):
    measurements: Dict[str, float]


@app.post("/check-value")
async def check_value(request: CheckValueRequest):
    """Check a value against reference range"""
    try:
        result = reference_engine.check_value(
            request.property_name,
            request.value,
            request.unit
        )
        
        return {
            "status": "success",
            "property": request.property_name,
            "value": request.value,
            "reference_status": result.status,
            "reference_range": {
                "min": result.reference_range.min_value if result.reference_range else None,
                "max": result.reference_range.max_value if result.reference_range else None
            }
        }
    except Exception as e:
        logger.error(f"Error checking value: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/generate-findings")
async def generate_findings(request: GenerateFindingsRequest):
    """Generate findings from measurements"""
    try:
        findings = reasoning_engine.generate_findings(request.measurements)
        
        return {
            "status": "success",
            "measurements": request.measurements,
            "findings": [
                {
                    "statement": f.finding_statement,
                    "confidence": f.confidence,
                    "evidence_count": len(f.evidence)
                }
                for f in findings
            ]
        }
    except Exception as e:
        logger.error(f"Error generating findings: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/calculate-confidence")
async def calculate_confidence(
    retrieval_score: float = 0.0,
    reranker_score: float = 0.0,
    graph_score: float = 0.0,
    source_count: int = 0
):
    """Calculate confidence score"""
    try:
        confidence = confidence_engine.calculate_confidence(
            retrieval_score,
            reranker_score,
            graph_score,
            source_count
        )
        
        return {
            "status": "success",
            "confidence": confidence,
            "breakdown": {
                "retrieval": retrieval_score,
                "reranker": reranker_score,
                "graph": graph_score
            }
        }
    except Exception as e:
        logger.error(f"Error calculating confidence: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "reasoning-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
