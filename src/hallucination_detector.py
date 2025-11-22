"""
Hallucination Detector for Guardian Crisis Detection System

Detects and corrects hallucinated or wrong-region crisis resources,
preventing users from calling fake or non-functional numbers.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class HallucinationDetector:
    """Detects fake/hallucinated crisis resources in messages."""

    def __init__(self, fake_resources_file: Optional[str] = None,
                 real_resources_file: Optional[str] = None):
        """Initialize hallucination detector.

        Args:
            fake_resources_file: Path to JSON file containing known fake numbers
            real_resources_file: Path to JSON file containing verified real numbers
        """
        if fake_resources_file is None:
            fake_resources_file = Path(__file__).parent.parent / "data" / "known_fake_resources.json"
        if real_resources_file is None:
            real_resources_file = Path(__file__).parent.parent / "data" / "nz_crisis_resources.json"

        with open(fake_resources_file, 'r', encoding='utf-8') as f:
            self.fake_resources = json.load(f)

        with open(real_resources_file, 'r', encoding='utf-8') as f:
            self.real_resources = json.load(f)

    def check_resource(self, resource: str, resource_type: str = "phone") -> Dict:
        """Check if a resource (phone number, text code, URL) is real or fake.

        Args:
            resource: The resource to check (e.g., "0800 543 800")
            resource_type: Type of resource ("phone", "text", "url")

        Returns:
            Dict containing:
                - is_valid: bool
                - is_hallucination: bool
                - details: str explaining the issue
                - correction: str with correct resource if available
                - severity: "critical", "high", "medium", or "low"
        """
        # Normalize the resource (remove spaces, dashes, etc.)
        normalized = self._normalize_phone(resource) if resource_type == "phone" else resource

        # Check against known fake numbers
        fake_check = self._check_against_fakes(normalized, resource)
        if fake_check:
            return fake_check

        # Check if it's a wrong-region number
        region_check = self._check_wrong_region(normalized, resource)
        if region_check:
            return region_check

        # Check if it's a real verified number
        real_check = self._check_against_real(normalized)
        if real_check:
            return {
                "is_valid": True,
                "is_hallucination": False,
                "details": f"Verified NZ resource: {real_check['name']}",
                "resource_info": real_check,
                "severity": "none"
            }

        # Unknown number - flag for manual verification
        return {
            "is_valid": False,
            "is_hallucination": True,
            "details": "Unknown resource - not in verified database. Please verify before using.",
            "correction": "Use verified resources: 111 (emergency), 1737 (mental health), or 0800 543 354 (Lifeline)",
            "severity": "high"
        }

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number by removing spaces, dashes, etc."""
        # Remove common separators
        normalized = re.sub(r'[\s\-\(\)]+', '', phone)
        # Remove country code if present
        normalized = re.sub(r'^\+?64', '', normalized)
        # Remove leading 0 for comparison
        normalized = normalized.lstrip('0')
        return normalized

    def _check_against_fakes(self, normalized: str, original: str) -> Optional[Dict]:
        """Check if number matches known fake numbers."""
        fake_numbers = self.fake_resources.get("fake_numbers", {})

        for fake_id, fake_data in fake_numbers.items():
            fake_number = fake_data["number"]
            fake_normalized = self._normalize_phone(fake_number)

            if normalized == fake_normalized or original == fake_number:
                return {
                    "is_valid": False,
                    "is_hallucination": True,
                    "details": fake_data.get("description", "Known fake number"),
                    "correction": fake_data.get("correction", "Use verified NZ resources"),
                    "severity": fake_data.get("severity", "critical"),
                    "notes": fake_data.get("notes", "")
                }

        return None

    def _check_wrong_region(self, normalized: str, original: str) -> Optional[Dict]:
        """Check if number is from wrong region (US, UK, AU, etc.)."""
        wrong_region = self.fake_resources.get("wrong_region_numbers", {})

        for region_id, region_data in wrong_region.items():
            region_number = region_data["number"]
            region_normalized = self._normalize_phone(region_number)

            # Also check formatted variants if they exist
            formatted_variants = region_data.get("formatted_variants", [])
            all_variants = [region_number] + formatted_variants

            if (normalized == region_normalized or
                original == region_number or
                original in all_variants):
                return {
                    "is_valid": False,
                    "is_hallucination": True,
                    "details": region_data.get("description", "Wrong region"),
                    "correction": region_data.get("correction", "Use NZ resources"),
                    "severity": region_data.get("severity", "critical"),
                    "actual_region": region_data.get("actual_region", ""),
                    "notes": region_data.get("notes", "")
                }

        return None

    def _check_against_real(self, normalized: str) -> Optional[Dict]:
        """Check if number matches verified real resources."""
        verified = self.real_resources.get("verified_resources", {})

        for resource_id, resource_data in verified.items():
            if "number" in resource_data:
                real_number = resource_data["number"]
                real_normalized = self._normalize_phone(real_number)

                if normalized == real_normalized:
                    return resource_data

        return None

    def scan_message(self, message: str) -> List[Dict]:
        """Scan message for any phone numbers or resources and check them.

        Args:
            message: The message to scan

        Returns:
            List of dicts, each containing check results for found resources
        """
        results = []

        # Find phone numbers in message
        phone_patterns = [
            r'\b0800\s?\d{3}\s?\d{3,4}\b',  # 0800 numbers
            r'\b\d{4}\b',  # 4-digit numbers (like 1737)
            r'\b0\d{1,2}\s?\d{3}\s?\d{3,4}\b',  # Other NZ formats
            r'\b1-?800-?\d{3}-?\d{4}\b',  # US 1-800 format
            r'\b\d{3}\b(?=\s|$)',  # 3-digit (like 988, 111)
            r'\b\d{6}\b',  # 6-digit (like 741741)
            r'\b116\s?123\b'  # UK Samaritans
        ]

        for pattern in phone_patterns:
            matches = re.finditer(pattern, message)
            for match in matches:
                number = match.group(0)
                check_result = self.check_resource(number, "phone")
                check_result["found_number"] = number
                check_result["position"] = match.span()
                results.append(check_result)

        return results

    def generate_correction_message(self, check_result: Dict) -> str:
        """Generate user-friendly correction message.

        Args:
            check_result: Result from check_resource()

        Returns:
            User-friendly correction message
        """
        if check_result["is_valid"]:
            return f"✓ {check_result['details']}"

        severity = check_result.get("severity", "high")
        found_number = check_result.get("found_number", "that number")

        if severity == "critical":
            message = f"⚠️ WARNING: {found_number} is {check_result['details']}\n\n"
            message += f"✓ CORRECT: {check_result.get('correction', 'Use verified NZ resources')}"

            if "notes" in check_result and check_result["notes"]:
                message += f"\n\nNote: {check_result['notes']}"

            return message
        else:
            return f"⚠️ {check_result['details']}\n{check_result.get('correction', '')}"

    def get_verified_alternatives(self, situation_type: str = "mental_health") -> List[Dict]:
        """Get verified alternative resources for a situation.

        Args:
            situation_type: Type of crisis (e.g., "mental_health", "domestic_violence")

        Returns:
            List of verified resources appropriate for the situation
        """
        routing = self.real_resources.get("situation_routing", {})
        numbers = routing.get(situation_type, ["1737", "111"])

        verified = self.real_resources.get("verified_resources", {})
        alternatives = []

        for resource_id, resource_data in verified.items():
            if "number" in resource_data and resource_data["number"] in numbers:
                alternatives.append(resource_data)

        return alternatives
