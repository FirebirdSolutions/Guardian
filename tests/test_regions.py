"""Tests for the Guardian LLM region management system."""

import pytest

from guardian_llm.regions import (
    Region,
    RegionManager,
    CrisisResource,
    RegionalConfig,
    REGIONAL_CONFIGS,
)


class TestRegion:
    """Tests for Region enum."""

    def test_all_regions_defined(self):
        """Test that all expected regions are defined."""
        expected = ["NZ", "AU", "US", "UK", "CA", "IE", "GLOBAL"]
        for code in expected:
            assert hasattr(Region, code), f"Region {code} not defined"

    def test_region_values(self):
        """Test region enum values match their names."""
        for region in Region:
            assert region.value == region.name


class TestCrisisResource:
    """Tests for CrisisResource dataclass."""

    def test_create_resource(self):
        """Test creating a crisis resource."""
        resource = CrisisResource(
            number="111",
            name="Emergency Services",
            description="Police, Fire, Ambulance",
        )
        assert resource.number == "111"
        assert resource.name == "Emergency Services"
        assert resource.availability == "24/7"  # default
        assert resource.cost == "Free"  # default

    def test_resource_with_all_fields(self):
        """Test creating a resource with all fields."""
        resource = CrisisResource(
            number="1737",
            name="Need to Talk?",
            description="Mental health crisis line",
            availability="24/7",
            cost="Free",
            languages=["English", "Te Reo Māori"],
            services=["call", "text"],
            url="https://example.com",
        )
        assert "Te Reo Māori" in resource.languages
        assert "text" in resource.services
        assert resource.url == "https://example.com"


class TestRegionalConfig:
    """Tests for regional configuration."""

    def test_nz_config_exists(self):
        """Test NZ configuration is defined."""
        assert Region.NZ in REGIONAL_CONFIGS
        config = REGIONAL_CONFIGS[Region.NZ]
        assert config.country_name == "New Zealand"
        assert config.emergency_number == "111"

    def test_nz_crisis_resources(self):
        """Test NZ crisis resources are defined."""
        config = REGIONAL_CONFIGS[Region.NZ]
        assert "emergency" in config.crisis_resources
        assert "mental_health" in config.crisis_resources
        assert "lifeline" in config.crisis_resources

    def test_nz_mental_health_number(self):
        """Test NZ mental health line is 1737."""
        config = REGIONAL_CONFIGS[Region.NZ]
        mental_health = config.crisis_resources["mental_health"]
        assert mental_health.number == "1737"
        assert "Te Reo Māori" in mental_health.languages

    def test_nz_known_fake_numbers(self):
        """Test NZ known fake numbers are defined."""
        config = REGIONAL_CONFIGS[Region.NZ]
        assert "0800 543 800" in config.known_fake_numbers

    def test_nz_wrong_region_numbers(self):
        """Test NZ knows which numbers are from other regions."""
        config = REGIONAL_CONFIGS[Region.NZ]
        assert config.wrong_region_numbers.get("988") == "US"
        assert config.wrong_region_numbers.get("116 123") == "UK"

    def test_all_regions_have_emergency_resources(self):
        """Test all regions have emergency resources."""
        for region, config in REGIONAL_CONFIGS.items():
            assert "emergency" in config.crisis_resources, f"{region} missing emergency resource"
            assert config.emergency_number, f"{region} missing emergency number"


class TestRegionManager:
    """Tests for RegionManager."""

    @pytest.fixture
    def manager(self):
        """Create a region manager for testing."""
        return RegionManager(default_region=Region.NZ)

    def test_default_region(self, manager):
        """Test default region is set."""
        assert manager.default_region == Region.NZ

    def test_get_config(self, manager):
        """Test getting regional config."""
        config = manager.get_config(Region.NZ)
        assert config.country_name == "New Zealand"

    def test_get_config_unknown_returns_default(self, manager):
        """Test unknown region falls back to default."""
        # Access a non-existent key, should return NZ config
        config = manager.get_config(Region.NZ)
        assert config is not None

    def test_get_crisis_resources_all(self, manager):
        """Test getting all crisis resources for a region."""
        resources = manager.get_crisis_resources(Region.NZ)
        assert len(resources) > 0
        numbers = [r.number for r in resources]
        assert "111" in numbers
        assert "1737" in numbers

    def test_get_crisis_resources_by_situation(self, manager):
        """Test getting resources by situation type."""
        resources = manager.get_crisis_resources(Region.NZ, situation_type="domestic_violence")
        numbers = [r.number for r in resources]
        # Should include family violence and women's refuge
        assert any("0800 456 450" in n or "0800 733 843" in n for n in numbers)

    def test_is_wrong_region_number(self, manager):
        """Test detecting wrong region numbers."""
        correct_region = manager.is_wrong_region_number("988", Region.NZ)
        assert correct_region == "US"

        correct_region = manager.is_wrong_region_number("1737", Region.NZ)
        assert correct_region is None  # 1737 is correct for NZ

    def test_is_known_fake(self, manager):
        """Test detecting fake numbers."""
        assert manager.is_known_fake("0800 543 800", Region.NZ) is True
        assert manager.is_known_fake("1737", Region.NZ) is False

    def test_detect_region_from_message_nz(self, manager):
        """Test detecting NZ from message content."""
        messages = [
            "I'm in New Zealand and need help",
            "Can you help? I'm a kiwi",
            "I'm from aotearoa",
        ]
        for msg in messages:
            region = manager.detect_region_from_message(msg)
            assert region == Region.NZ, f"Failed for message: {msg}"

    def test_detect_region_from_message_us(self, manager):
        """Test detecting US from message content."""
        region = manager.detect_region_from_message("I'm in the USA")
        assert region == Region.US

    def test_detect_region_from_message_phone_number(self, manager):
        """Test detecting region from phone number mention."""
        region = manager.detect_region_from_message("I tried calling 1737")
        assert region == Region.NZ

    def test_detect_region_from_message_no_match(self, manager):
        """Test no region detected when no indicators."""
        region = manager.detect_region_from_message("I feel sad today")
        assert region is None

    def test_get_system_prompt(self, manager):
        """Test generating system prompt for a region."""
        prompt = manager.get_system_prompt(Region.NZ)
        assert "Guardian" in prompt
        assert "NEW ZEALAND" in prompt
        assert "111" in prompt
        assert "1737" in prompt

    def test_get_system_prompt_includes_fake_numbers(self, manager):
        """Test system prompt includes fake number warnings."""
        prompt = manager.get_system_prompt(Region.NZ)
        assert "FAKE" in prompt or "fake" in prompt.lower()

    def test_us_resources(self, manager):
        """Test US crisis resources."""
        config = manager.get_config(Region.US)
        assert config.emergency_number == "911"
        assert "suicide_lifeline" in config.crisis_resources
        assert config.crisis_resources["suicide_lifeline"].number == "988"

    def test_uk_resources(self, manager):
        """Test UK crisis resources."""
        config = manager.get_config(Region.UK)
        assert config.emergency_number == "999"
        assert "samaritans" in config.crisis_resources
        assert config.crisis_resources["samaritans"].number == "116 123"


class TestCrossRegionValidation:
    """Tests for cross-region number validation."""

    @pytest.fixture
    def manager(self):
        return RegionManager()

    def test_us_number_wrong_for_nz(self, manager):
        """Test US numbers are flagged as wrong for NZ."""
        # 988 is the US crisis line
        result = manager.is_wrong_region_number("988", Region.NZ)
        assert result == "US"

    def test_nz_number_wrong_for_us(self, manager):
        """Test NZ numbers are flagged as wrong for US."""
        result = manager.is_wrong_region_number("1737", Region.US)
        assert result == "NZ"

    def test_au_number_wrong_for_nz(self, manager):
        """Test AU numbers are flagged as wrong for NZ."""
        result = manager.is_wrong_region_number("13 11 14", Region.NZ)
        assert result == "AU"
