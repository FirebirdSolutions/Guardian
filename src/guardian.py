"""
Guardian - AI Safety System for Crisis Detection and Resource Provision

Main system class that coordinates pattern detection, hallucination checking,
and crisis resource provision for New Zealand.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .pattern_detector import PatternDetector
from .hallucination_detector import HallucinationDetector


class Guardian:
    """Main Guardian safety system class."""

    def __init__(self,
                 patterns_file: Optional[str] = None,
                 resources_file: Optional[str] = None,
                 fake_resources_file: Optional[str] = None):
        """Initialize Guardian system.

        Args:
            patterns_file: Path to crisis patterns JSON
            resources_file: Path to verified resources JSON
            fake_resources_file: Path to known fake resources JSON
        """
        # Initialize components
        self.pattern_detector = PatternDetector(patterns_file)
        self.hallucination_detector = HallucinationDetector(fake_resources_file, resources_file)

        # Load resources
        if resources_file is None:
            resources_file = Path(__file__).parent.parent / "data" / "nz_crisis_resources.json"

        with open(resources_file, 'r', encoding='utf-8') as f:
            self.resources = json.load(f)

        # Initialize conversation history (for context tracking)
        self.conversation_history = []

    def analyze(self, message: str, check_hallucinations: bool = True) -> Dict:
        """Analyze a user message for crisis indicators and hallucinated resources.

        Args:
            message: The user's message to analyze
            check_hallucinations: Whether to check for hallucinated phone numbers

        Returns:
            Dict containing:
                - risk_level: CRITICAL, HIGH, MEDIUM, or LOW
                - patterns_detected: List of crisis patterns found
                - hallucinations_detected: List of fake/wrong resources found
                - recommended_resources: List of appropriate resources to provide
                - intervention_message: Suggested response message
                - escalation_required: Whether human escalation is needed
        """
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "risk_level": "LOW",
            "patterns_detected": [],
            "hallucinations_detected": [],
            "recommended_resources": [],
            "intervention_message": "",
            "escalation_required": False,
            "metadata": {}
        }

        # 1. Check for hallucinated resources first (CRITICAL if in crisis)
        if check_hallucinations:
            hallucinations = self.hallucination_detector.scan_message(message)
            if hallucinations:
                result["hallucinations_detected"] = hallucinations
                # If fake numbers found, this is critical
                if any(h["is_hallucination"] for h in hallucinations):
                    result["intervention_message"] = self._generate_hallucination_warning(hallucinations)
                    result["risk_level"] = "CRITICAL"
                    result["escalation_required"] = True

        # 2. Detect crisis patterns
        pattern_analysis = self.pattern_detector.detect(message, self.conversation_history)
        result["patterns_detected"] = pattern_analysis["detected_patterns"]
        result["risk_level"] = pattern_analysis["risk_level"]
        result["metadata"]["categories"] = pattern_analysis["categories"]
        result["metadata"]["indicators"] = pattern_analysis["indicators"]

        # 3. Determine appropriate resources
        result["recommended_resources"] = self._get_appropriate_resources(pattern_analysis)

        # 4. Generate intervention message
        if not result["intervention_message"]:  # Don't override hallucination warning
            result["intervention_message"] = self._generate_intervention_message(
                result["risk_level"],
                result["patterns_detected"],
                result["recommended_resources"],
                pattern_analysis["indicators"]
            )

        # 5. Determine if escalation required
        result["escalation_required"] = self._requires_escalation(
            result["risk_level"],
            pattern_analysis["indicators"]
        )

        # 6. Add to conversation history
        self.conversation_history.append({
            "message": message,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _get_appropriate_resources(self, pattern_analysis: Dict) -> List[Dict]:
        """Determine appropriate resources based on detected patterns."""
        resources = []
        categories = pattern_analysis.get("categories", [])
        indicators = pattern_analysis.get("indicators", {})

        # Map categories to situation types
        situation_types = set()

        if "suicide_ideation" in categories or "self_harm" in categories:
            situation_types.add("suicide_ideation")
        if "domestic_violence" in categories:
            situation_types.add("domestic_violence")
        if "substance_abuse" in categories:
            situation_types.add("substance_abuse")
        if "eating_disorder" in categories:
            situation_types.add("eating_disorder")
        if "child_abuse" in categories:
            situation_types.add("child_abuse")
        if "youth_specific" in categories or indicators.get("youth"):
            situation_types.add("youth_crisis")
        if "psychotic_symptoms" in categories:
            situation_types.add("immediate_danger")
        if "cultural_maori_distress" in categories:
            situation_types.add("cultural_maori")

        # Get resources for each situation type
        situation_routing = self.resources.get("situation_routing", {})
        verified_resources = self.resources.get("verified_resources", {})

        resource_numbers = set()
        for situation in situation_types:
            numbers = situation_routing.get(situation, [])
            resource_numbers.update(numbers)

        # If no specific situation, default to mental health
        if not resource_numbers:
            resource_numbers.update(["1737", "0800 543 354", "111"])

        # Build resource list
        for resource_id, resource_data in verified_resources.items():
            if "number" in resource_data:
                if resource_data["number"] in resource_numbers:
                    resources.append({
                        "number": resource_data["number"],
                        "name": resource_data.get("name", ""),
                        "description": resource_data.get("description", ""),
                        "availability": resource_data.get("availability", ""),
                        "cost": resource_data.get("cost", "")
                    })

        # Always ensure 111 is available for CRITICAL situations
        if pattern_analysis.get("risk_level") == "CRITICAL":
            has_111 = any(r["number"] == "111" for r in resources)
            if not has_111:
                resources.insert(0, {
                    "number": "111",
                    "name": "Emergency Services",
                    "description": "Police, Fire, Ambulance",
                    "availability": "24/7",
                    "cost": "Free"
                })

        return resources

    def _generate_intervention_message(self,
                                      risk_level: str,
                                      patterns: List[Dict],
                                      resources: List[Dict],
                                      indicators: Dict) -> str:
        """Generate appropriate intervention message."""
        if risk_level == "LOW":
            return "No immediate crisis detected. Continue monitoring."

        message = ""

        # CRITICAL situations
        if risk_level == "CRITICAL":
            # Check for imminent danger
            if indicators.get("imminent_timeline") or indicators.get("has_means"):
                message = "⚠️ IMMEDIATE DANGER DETECTED\n\n"
                message += "Please reach out RIGHT NOW:\n"
            elif indicators.get("possible_overdose"):
                message = "🚨 MEDICAL EMERGENCY\n\n"
                message += "Call 111 for ambulance immediately:\n"
            elif indicators.get("psychotic_symptoms"):
                message = "🚨 MEDICAL EMERGENCY\n\n"
                message += "This requires immediate medical attention:\n"
            else:
                message = "⚠️ CRISIS INTERVENTION NEEDED\n\n"
                message += "Verified crisis resources:\n"

        # HIGH risk
        elif risk_level == "HIGH":
            message = "Support available 24/7:\n"

        # MEDIUM risk
        elif risk_level == "MEDIUM":
            message = "Resources that may help:\n"

        # Add resources
        for resource in resources[:3]:  # Top 3 most relevant
            message += f"\n• {resource['number']} - {resource['name']}"
            if resource.get('cost') == 'Free':
                message += " (Free)"
            if resource.get('availability'):
                if '24/7' in resource['availability']:
                    message += " - 24/7"

        # Add special notes for specific situations
        if indicators.get("minor"):
            message += "\n\n📱 Youth services available - Youthline: 0800 376 633 or text 234"

        if indicators.get("cultural_maori_distress"):
            message += "\n\n🌿 Kaupapa Māori support available"

        if risk_level == "CRITICAL":
            message += "\n\nYou don't have to face this alone. Please reach out."

        return message

    def _generate_hallucination_warning(self, hallucinations: List[Dict]) -> str:
        """Generate warning message for hallucinated resources."""
        message = "⚠️ RESOURCE VERIFICATION ALERT\n\n"

        for hallucination in hallucinations:
            if hallucination["is_hallucination"]:
                found_number = hallucination.get("found_number", "That number")
                message += f"❌ {found_number} - {hallucination['details']}\n\n"

                if "correction" in hallucination:
                    message += f"✓ CORRECT: {hallucination['correction']}\n\n"

        message += "Always verify crisis resources from official sources."
        return message

    def _requires_escalation(self, risk_level: str, indicators: Dict) -> bool:
        """Determine if situation requires human escalation."""
        if risk_level == "CRITICAL":
            return True

        # Specific indicators that always require escalation
        critical_indicators = [
            "imminent_timeline",
            "has_means",
            "possible_overdose",
            "psychotic_symptoms",
            "minor_involved",
            "dv_lethal_threat"
        ]

        for indicator in critical_indicators:
            if indicators.get(indicator):
                return True

        return False

    def get_crisis_resources(self, region: str = "NZ",
                            situation_type: str = "mental_health") -> List[Dict]:
        """Get crisis resources for a specific region and situation.

        Args:
            region: Region code (currently only "NZ" supported)
            situation_type: Type of crisis (e.g., "mental_health", "domestic_violence")

        Returns:
            List of appropriate crisis resources
        """
        if region != "NZ":
            return []

        situation_routing = self.resources.get("situation_routing", {})
        numbers = situation_routing.get(situation_type, ["1737", "111"])

        verified_resources = self.resources.get("verified_resources", {})
        resources = []

        for resource_id, resource_data in verified_resources.items():
            if "number" in resource_data and resource_data["number"] in numbers:
                resources.append(resource_data)

        return resources

    def log_incident(self, incident_data: Dict) -> Dict:
        """Log a crisis incident for monitoring and analysis.

        Args:
            incident_data: Dict containing incident information

        Returns:
            Dict with incident_id and confirmation
        """
        incident = {
            "incident_id": datetime.utcnow().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.utcnow().isoformat(),
            **incident_data
        }

        # In a real implementation, this would write to a database or log file
        # For now, just return the incident record
        return {
            "incident_id": incident["incident_id"],
            "logged": True,
            "timestamp": incident["timestamp"]
        }

    def check_hallucination(self, resource: str, resource_type: str = "phone") -> Dict:
        """Check if a resource is hallucinated/fake.

        Args:
            resource: The resource to check (phone number, etc.)
            resource_type: Type of resource ("phone", "text", "url")

        Returns:
            Dict with verification results
        """
        return self.hallucination_detector.check_resource(resource, resource_type)

    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
