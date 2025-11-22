"""
Pattern Detector for Guardian Crisis Detection System

Detects crisis patterns in user messages including:
- Suicidal ideation (direct, passive, with timeline)
- Self-harm
- Domestic violence
- Mental health distress
- Youth-specific crises
- Cultural contexts (Māori, rural)
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class PatternDetector:
    """Detects crisis patterns in text messages."""

    def __init__(self, patterns_file: Optional[str] = None):
        """Initialize pattern detector with pattern definitions.

        Args:
            patterns_file: Path to JSON file containing pattern definitions
        """
        if patterns_file is None:
            # Default to patterns file in data directory
            patterns_file = Path(__file__).parent.parent / "data" / "crisis_patterns.json"

        with open(patterns_file, 'r', encoding='utf-8') as f:
            self.patterns = json.load(f)

    def detect(self, message: str, context: Optional[List[str]] = None) -> Dict:
        """Detect crisis patterns in a message.

        Args:
            message: The user's message to analyze
            context: Optional list of previous messages for context

        Returns:
            Dict containing:
                - detected_patterns: List of pattern matches
                - risk_level: Overall risk level
                - categories: List of crisis categories detected
                - indicators: Specific indicators found
        """
        detected = {
            "detected_patterns": [],
            "categories": set(),
            "indicators": {},
            "false_positive_check": self._check_false_positives(message)
        }

        # Check for false positives first
        if detected["false_positive_check"]["is_false_positive"]:
            detected["risk_level"] = "LOW"
            detected["categories"] = list(detected["categories"])
            return detected

        # Check each category of patterns
        self._check_suicide_patterns(message, detected)
        self._check_self_harm_patterns(message, detected)
        self._check_domestic_violence_patterns(message, detected)
        self._check_child_abuse_patterns(message, detected)
        self._check_substance_abuse_patterns(message, detected)
        self._check_eating_disorder_patterns(message, detected)
        self._check_mental_health_patterns(message, detected)
        self._check_psychotic_patterns(message, detected)
        self._check_youth_patterns(message, detected)
        self._check_cultural_patterns(message, detected)

        # Determine overall risk level
        detected["risk_level"] = self._determine_risk_level(detected["detected_patterns"])

        # Convert set to list for JSON serialization
        detected["categories"] = list(detected["categories"])

        return detected

    def _check_false_positives(self, message: str) -> Dict:
        """Check if message is a false positive (figure of speech, joke, etc.)"""
        false_pos = self.patterns.get("false_positives", {})

        result = {
            "is_false_positive": False,
            "reason": None,
            "confidence": 0.0
        }

        # Check figures of speech
        figures = false_pos.get("figures_of_speech", {})
        for pattern in figures.get("patterns", []):
            if re.search(pattern, message):
                result["is_false_positive"] = True
                result["reason"] = "figure_of_speech"
                result["confidence"] = 0.9
                return result

        # Check for humor indicators
        humor_indicators = figures.get("indicators", {}).get("humor", [])
        for indicator in humor_indicators:
            if indicator in message:
                # Check if also contains crisis keywords
                has_crisis_keyword = any(
                    keyword in message.lower()
                    for keyword in ["kill", "die", "suicide", "end it"]
                )
                if has_crisis_keyword:
                    # Humor emoji + crisis keyword might be deflection
                    result["is_false_positive"] = False
                    result["reason"] = "possible_deflection"
                    result["confidence"] = 0.5
                else:
                    result["is_false_positive"] = True
                    result["reason"] = "humor"
                    result["confidence"] = 0.8
                return result

        # Check hyperbole with coping
        hyperbole = false_pos.get("hyperbole_with_coping", {})
        for pattern in hyperbole.get("patterns", []):
            if re.search(pattern, message):
                result["is_false_positive"] = True
                result["reason"] = "coping_stated"
                result["confidence"] = 0.9
                return result

        return result

    def _check_suicide_patterns(self, message: str, detected: Dict):
        """Check for suicide ideation patterns."""
        suicide_patterns = self.patterns.get("suicide_ideation", {})

        for category, config in suicide_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "suicide_ideation",
                        "subcategory": category,
                        "severity": config.get("severity", "CRITICAL"),
                        "matched_text": match.group(0),
                        "description": config.get("description", ""),
                        "action": config.get("action", "")
                    })
                    detected["categories"].add("suicide_ideation")

                    # Check for timeline indicators (escalates severity)
                    if category == "with_timeline":
                        detected["indicators"]["imminent_timeline"] = True
                    elif category == "plan_and_means":
                        detected["indicators"]["has_means"] = True
                        detected["indicators"]["has_plan"] = True

    def _check_self_harm_patterns(self, message: str, detected: Dict):
        """Check for self-harm patterns."""
        self_harm_patterns = self.patterns.get("self_harm", {})

        for category, config in self_harm_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "self_harm",
                        "subcategory": category,
                        "severity": config.get("severity", "CRITICAL"),
                        "matched_text": match.group(0),
                        "medical_risk": config.get("medical_risk", "")
                    })
                    detected["categories"].add("self_harm")

    def _check_domestic_violence_patterns(self, message: str, detected: Dict):
        """Check for domestic violence patterns."""
        dv_patterns = self.patterns.get("domestic_violence", {})

        for category, config in dv_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "domestic_violence",
                        "subcategory": category,
                        "severity": config.get("severity", "CRITICAL"),
                        "matched_text": match.group(0),
                        "description": config.get("description", "")
                    })
                    detected["categories"].add("domestic_violence")

                    # Flag specific high-risk indicators
                    if "lethality_indicators" in config:
                        for risk_type, indicators in config["lethality_indicators"].items():
                            for indicator in indicators:
                                if indicator.lower() in message.lower():
                                    detected["indicators"][f"dv_{risk_type}"] = True

    def _check_child_abuse_patterns(self, message: str, detected: Dict):
        """Check for child abuse disclosure patterns."""
        child_patterns = self.patterns.get("child_abuse", {})

        for category, config in child_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "child_abuse",
                        "subcategory": category,
                        "severity": config.get("severity", "CRITICAL"),
                        "matched_text": match.group(0),
                        "action": config.get("action", "")
                    })
                    detected["categories"].add("child_abuse")
                    detected["indicators"]["minor_involved"] = True

    def _check_substance_abuse_patterns(self, message: str, detected: Dict):
        """Check for substance abuse patterns."""
        substance_patterns = self.patterns.get("substance_abuse", {})

        for category, config in substance_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    severity = config.get("severity", "HIGH")
                    detected["detected_patterns"].append({
                        "category": "substance_abuse",
                        "subcategory": category,
                        "severity": severity,
                        "matched_text": match.group(0)
                    })
                    detected["categories"].add("substance_abuse")

                    if category == "overdose_signs":
                        detected["indicators"]["possible_overdose"] = True

    def _check_eating_disorder_patterns(self, message: str, detected: Dict):
        """Check for eating disorder patterns."""
        ed_patterns = self.patterns.get("eating_disorders", {})

        for category, config in ed_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "eating_disorder",
                        "subcategory": category,
                        "severity": config.get("severity", "HIGH"),
                        "matched_text": match.group(0),
                        "medical_risk": config.get("medical_risk", "")
                    })
                    detected["categories"].add("eating_disorder")

    def _check_mental_health_patterns(self, message: str, detected: Dict):
        """Check for general mental health distress patterns."""
        mh_patterns = self.patterns.get("mental_health_distress", {})

        for category, config in mh_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "mental_health_distress",
                        "subcategory": category,
                        "severity": config.get("severity", "HIGH"),
                        "matched_text": match.group(0)
                    })
                    detected["categories"].add("mental_health_distress")

    def _check_psychotic_patterns(self, message: str, detected: Dict):
        """Check for psychotic symptoms (hallucinations, delusions)."""
        psychotic_patterns = self.patterns.get("psychotic_symptoms", {})

        for category, config in psychotic_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "psychotic_symptoms",
                        "subcategory": category,
                        "severity": config.get("severity", "CRITICAL"),
                        "matched_text": match.group(0),
                        "action": config.get("action", "")
                    })
                    detected["categories"].add("psychotic_symptoms")
                    detected["indicators"]["psychotic_symptoms"] = True

    def _check_youth_patterns(self, message: str, detected: Dict):
        """Check for youth-specific crisis patterns."""
        youth_patterns = self.patterns.get("youth_specific", {})

        for category, config in youth_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "youth_specific",
                        "subcategory": category,
                        "severity": config.get("severity", "HIGH"),
                        "matched_text": match.group(0)
                    })
                    detected["categories"].add("youth_specific")
                    detected["indicators"]["youth"] = True

        # Check for age indicators
        age_pattern = r"\bi'?m (\d{1,2})\b"
        age_match = re.search(age_pattern, message, re.IGNORECASE)
        if age_match:
            age = int(age_match.group(1))
            if age < 25:
                detected["indicators"]["age"] = age
                if age < 18:
                    detected["indicators"]["minor"] = True

    def _check_cultural_patterns(self, message: str, detected: Dict):
        """Check for cultural context patterns (Māori, rural, etc.)."""
        cultural_patterns = self.patterns.get("cultural_contexts", {})

        for category, config in cultural_patterns.items():
            for pattern in config.get("patterns", []):
                match = re.search(pattern, message)
                if match:
                    detected["detected_patterns"].append({
                        "category": "cultural_context",
                        "subcategory": category,
                        "severity": config.get("severity", "varies"),
                        "matched_text": match.group(0)
                    })
                    detected["categories"].add(f"cultural_{category}")
                    detected["indicators"][f"cultural_{category}"] = True

    def _determine_risk_level(self, detected_patterns: List[Dict]) -> str:
        """Determine overall risk level from detected patterns.

        Risk levels:
        - CRITICAL: Immediate danger, requires emergency response
        - HIGH: Significant risk, requires crisis intervention
        - MEDIUM: Moderate concern, offer resources
        - LOW: No immediate risk
        """
        if not detected_patterns:
            return "LOW"

        # Check highest severity
        severities = [p.get("severity", "LOW") for p in detected_patterns]

        if "CRITICAL" in severities:
            return "CRITICAL"
        elif "HIGH" in severities:
            return "HIGH"
        elif "MEDIUM" in severities:
            return "MEDIUM"
        else:
            return "LOW"

    def extract_age(self, message: str) -> Optional[int]:
        """Extract age from message if mentioned."""
        age_patterns = [
            r"\bi'?m (\d{1,2})( years old)?\b",
            r"\bi am (\d{1,2})( years old)?\b",
            r"\b(\d{1,2})( years old| yo|y/o)\b"
        ]

        for pattern in age_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 5 <= age <= 100:  # Reasonable age range
                    return age

        return None
