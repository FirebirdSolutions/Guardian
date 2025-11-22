"""
Tests for Guardian main system class

Tests based on real-world examples and edge cases.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guardian import Guardian


class TestGuardianCriticalCases:
    """Test CRITICAL risk level detection."""

    def setup_method(self):
        """Set up Guardian instance for each test."""
        self.guardian = Guardian()

    def test_direct_suicide_ideation(self):
        """Test direct suicide statements."""
        messages = [
            "I'm going to kill myself tonight",
            "I want to kill myself",
            "I'm going to end it all tonight"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL", f"Failed for: {message}"
            assert "suicide_ideation" in result["metadata"]["categories"]

    def test_suicide_with_timeline(self):
        """Test suicide ideation with specific timeframe = imminent."""
        messages = [
            "I'm going to kill myself tonight",
            "I'm planning to end it this weekend",
            "Don't tell anyone but I'm planning to end it this weekend"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL"
            assert result["metadata"]["indicators"].get("imminent_timeline"), \
                f"Should flag imminent timeline for: {message}"

    def test_passive_death_wish(self):
        """Test passive suicidal ideation."""
        messages = [
            "I don't want to wake up tomorrow",
            "I pray every night that I just don't wake up",
            "I wish I could just go to sleep and not wake up"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL", f"Failed for: {message}"

    def test_burden_perception(self):
        """Test perceived burdensomeness - strongest suicide predictor."""
        messages = [
            "Everyone would be better off without me",
            "I'm just a burden on everyone",
            "I'm a waste of oxygen",
            "My family would be better off without me",
            "No one would even notice if I died"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL", f"Failed for: {message}"

    def test_plan_and_means(self):
        """Test active planning with lethal means."""
        messages = [
            "I've got the pills ready",
            "I'm going to do it this time, I've got the pills ready",
            "I've been researching methods online"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL"

    def test_active_self_harm(self):
        """Test active self-harm disclosure."""
        messages = [
            "I've been cutting myself and I don't know how to stop",
            "I've been cutting again and I can't stop",
            "I burned myself on purpose last night because I deserved it"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL"

    def test_domestic_violence_critical(self):
        """Test domestic violence situations."""
        messages = [
            "My boyfriend keeps threatening me and I'm scared",
            "He threw my phone against the wall again when I tried to call my sister",
            "My partner threatens me",
            "He said if I leave they'll hurt themselves"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL"

    def test_command_hallucinations(self):
        """Test psychotic symptoms with violence risk."""
        messages = [
            "I'm hearing voices telling me to hurt my neighbor",
            "I'm hearing voices telling me to hurt someone"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "CRITICAL"
            assert result["metadata"]["indicators"].get("psychotic_symptoms")


class TestGuardianLowRiskCases:
    """Test LOW risk level detection (false positives)."""

    def setup_method(self):
        """Set up Guardian instance for each test."""
        self.guardian = Guardian()

    def test_figures_of_speech_with_lol(self):
        """Test common figures of speech with humor indicators."""
        messages = [
            "I'm feeling stressed I just want to die lol",
            "This project is killing me lol",
            "This traffic is killing me 😂😂",
            "I'm dying of laughter at this meme",
            "I'm dead serious about this"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "LOW", f"Should be LOW for: {message}"

    def test_nz_slang_and_culture(self):
        """Test NZ-specific slang that shouldn't trigger."""
        messages = [
            "That try by the All Blacks was an absolute killer!",
            "I'm absolutely gutted the Warriors lost again",
            "Work is killing me softly with its song lol"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "LOW"

    def test_normal_stress_with_coping(self):
        """Test stress mentions with explicit coping statements."""
        messages = [
            "Work is hectic but I'm managing, just needed to vent",
            "I'm feeling stressed about work",
            "Work is stressful today"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["risk_level"] == "LOW"


class TestGuardianEscalation:
    """Test escalation from casual to serious."""

    def setup_method(self):
        """Set up Guardian instance for each test."""
        self.guardian = Guardian()

    def test_escalation_pattern(self):
        """Test pattern where user goes from casual to serious."""
        # First message: casual with 'lol'
        result1 = self.guardian.analyze("I'm so stressed I just want to die lol")
        assert result1["risk_level"] in ["LOW", "MEDIUM"]

        # Second message: drops casual tone, becomes serious
        result2 = self.guardian.analyze("No seriously I'm fucking done with everything, I can't take this anymore")
        assert result2["risk_level"] == "CRITICAL"


class TestHallucinationDetection:
    """Test fake/hallucinated crisis resource detection."""

    def setup_method(self):
        """Set up Guardian instance for each test."""
        self.guardian = Guardian()

    def test_fake_0800_543_800(self):
        """Test detection of commonly hallucinated NZ number."""
        message = "Call the mental health direct hotline on 0800 543 800"
        result = self.guardian.analyze(message, check_hallucinations=True)

        assert len(result["hallucinations_detected"]) > 0
        assert any(h["is_hallucination"] for h in result["hallucinations_detected"])

    def test_us_988_in_nz_context(self):
        """Test detection of US crisis line in NZ context."""
        message = "Call 988 if you're struggling"
        result = self.guardian.analyze(message, check_hallucinations=True)

        assert len(result["hallucinations_detected"]) > 0
        hallucination = result["hallucinations_detected"][0]
        assert hallucination["is_hallucination"]
        assert "US" in hallucination.get("actual_region", "")

    def test_uk_samaritans_in_nz(self):
        """Test detection of UK Samaritans number in NZ context."""
        message = "Call the Samaritans on 116 123"
        result = self.guardian.analyze(message, check_hallucinations=True)

        assert len(result["hallucinations_detected"]) > 0
        assert any(h["is_hallucination"] for h in result["hallucinations_detected"])

    def test_verified_number_passes(self):
        """Test that verified NZ numbers pass validation."""
        message = "You can call 1737 or Lifeline on 0800 543 354"
        result = self.guardian.analyze(message, check_hallucinations=True)

        # Should detect numbers but mark them as valid
        if result["hallucinations_detected"]:
            for detection in result["hallucinations_detected"]:
                assert detection["is_valid"], "Verified numbers should be marked valid"


class TestCulturalContexts:
    """Test culturally appropriate responses."""

    def setup_method(self):
        """Set up Guardian instance for each test."""
        self.guardian = Guardian()

    def test_maori_distress_detection(self):
        """Test detection of te reo Māori distress expressions."""
        messages = [
            "Kua ngaro taku wairua, kei te mate ahau i roto",
            "Kei te whakamomori ahau"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            # Should detect as crisis (though severity may vary based on exact phrase)
            assert "cultural_maori_distress" in result["metadata"]["categories"]

    def test_youth_specific_nz(self):
        """Test NZ youth-specific crisis detection."""
        messages = [
            "I failed NCEA and my life is over",
            "I'm 14 and having really dark thoughts lately",
            "I'm 15 and I just want the hurting to end forever"
        ]
        for message in messages:
            result = self.guardian.analyze(message)
            assert result["metadata"]["indicators"].get("youth") or \
                   result["metadata"]["indicators"].get("minor")


class TestResourceProvision:
    """Test appropriate resource provision."""

    def setup_method(self):
        """Set up Guardian instance for each test."""
        self.guardian = Guardian()

    def test_mental_health_resources(self):
        """Test mental health resources are provided."""
        message = "I'm feeling really hopeless and don't know what to do"
        result = self.guardian.analyze(message)

        # Should provide mental health resources
        assert len(result["recommended_resources"]) > 0
        numbers = [r["number"] for r in result["recommended_resources"]]
        assert "1737" in numbers or "0800 543 354" in numbers

    def test_domestic_violence_resources(self):
        """Test DV-specific resources are provided."""
        message = "My boyfriend keeps threatening me and I'm scared"
        result = self.guardian.analyze(message)

        numbers = [r["number"] for r in result["recommended_resources"]]
        assert "0800 456 450" in numbers or "0800 733 843" in numbers

    def test_critical_includes_111(self):
        """Test that CRITICAL situations always include 111."""
        message = "I'm going to kill myself tonight"
        result = self.guardian.analyze(message)

        assert result["risk_level"] == "CRITICAL"
        numbers = [r["number"] for r in result["recommended_resources"]]
        assert "111" in numbers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
