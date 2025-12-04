"""
Guardian LLM Multi-Region Support

Regional crisis resources and localization for global deployment.
Designed to be extensible - add new regions by defining their resources.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import json
from pathlib import Path


class Region(Enum):
    """Supported regions for Guardian."""
    NZ = "NZ"           # New Zealand
    AU = "AU"           # Australia
    US = "US"           # United States
    UK = "UK"           # United Kingdom
    CA = "CA"           # Canada
    IE = "IE"           # Ireland
    GLOBAL = "GLOBAL"   # Fallback


@dataclass
class CrisisResource:
    """A crisis resource (hotline, text line, etc.)."""
    number: str
    name: str
    description: str
    availability: str = "24/7"
    cost: str = "Free"
    languages: List[str] = field(default_factory=lambda: ["English"])
    services: List[str] = field(default_factory=list)  # e.g., ["call", "text", "chat"]
    url: Optional[str] = None


@dataclass
class RegionalConfig:
    """Configuration for a specific region."""
    region: Region
    country_name: str
    emergency_number: str
    crisis_resources: Dict[str, CrisisResource] = field(default_factory=dict)
    known_fake_numbers: List[str] = field(default_factory=list)
    wrong_region_numbers: Dict[str, str] = field(default_factory=dict)  # number -> actual region
    cultural_contexts: List[str] = field(default_factory=list)
    local_slang: Dict[str, str] = field(default_factory=dict)


# Pre-defined regional configurations
REGIONAL_CONFIGS: Dict[Region, RegionalConfig] = {
    Region.NZ: RegionalConfig(
        region=Region.NZ,
        country_name="New Zealand",
        emergency_number="111",
        crisis_resources={
            "emergency": CrisisResource(
                number="111",
                name="Emergency Services",
                description="Police, Fire, Ambulance",
                services=["call"],
            ),
            "mental_health": CrisisResource(
                number="1737",
                name="Need to Talk?",
                description="Mental health crisis line",
                languages=["English", "Te Reo Māori"],
                services=["call", "text"],
            ),
            "lifeline": CrisisResource(
                number="0800 543 354",
                name="Lifeline NZ",
                description="24/7 counselling and support",
                services=["call"],
            ),
            "family_violence": CrisisResource(
                number="0800 456 450",
                name="Family Violence Hotline",
                description="Shine - Domestic violence support",
                services=["call"],
            ),
            "womens_refuge": CrisisResource(
                number="0800 733 843",
                name="Women's Refuge",
                description="Safe house and crisis support for women",
                services=["call"],
            ),
            "youthline": CrisisResource(
                number="0800 376 633",
                name="Youthline",
                description="Youth support and counselling",
                services=["call", "text"],
            ),
            "alcohol_drug": CrisisResource(
                number="0800 787 797",
                name="Alcohol Drug Helpline",
                description="Support for substance use issues",
                services=["call"],
            ),
            "oranga_tamariki": CrisisResource(
                number="0508 326 459",
                name="Oranga Tamariki",
                description="Child protection services",
                services=["call"],
            ),
        },
        known_fake_numbers=["0800 543 800", "0800 111 757"],
        wrong_region_numbers={
            "988": "US",
            "1-800-273-8255": "US",
            "741741": "US",
            "116 123": "UK",
            "13 11 14": "AU",
        },
        cultural_contexts=[
            "Te Reo Māori expressions of distress",
            "Kiwi slang and idioms",
            "Rural/farming community contexts",
            "Pacific Island cultural expressions",
        ],
        local_slang={
            "sweet as": "positive/okay",
            "yeah nah": "no/disagreement",
            "gutted": "disappointed/sad",
            "munted": "broken/damaged",
            "hard out": "definitely/intensely",
        },
    ),

    Region.AU: RegionalConfig(
        region=Region.AU,
        country_name="Australia",
        emergency_number="000",
        crisis_resources={
            "emergency": CrisisResource(
                number="000",
                name="Emergency Services",
                description="Police, Fire, Ambulance",
                services=["call"],
            ),
            "lifeline": CrisisResource(
                number="13 11 14",
                name="Lifeline Australia",
                description="24/7 crisis support",
                services=["call", "text"],
            ),
            "beyond_blue": CrisisResource(
                number="1300 22 4636",
                name="Beyond Blue",
                description="Anxiety and depression support",
                services=["call", "chat"],
                url="https://www.beyondblue.org.au",
            ),
            "suicide_callback": CrisisResource(
                number="1300 659 467",
                name="Suicide Call Back Service",
                description="Professional suicide prevention counselling",
                services=["call", "chat"],
            ),
            "kids_helpline": CrisisResource(
                number="1800 55 1800",
                name="Kids Helpline",
                description="Support for young people 5-25",
                services=["call", "chat"],
            ),
            "dv_line": CrisisResource(
                number="1800 737 732",
                name="1800RESPECT",
                description="Domestic and family violence support",
                services=["call", "chat"],
            ),
        },
        known_fake_numbers=[],
        wrong_region_numbers={
            "988": "US",
            "1737": "NZ",
            "111": "NZ",
            "116 123": "UK",
        },
        cultural_contexts=[
            "Indigenous Australian expressions",
            "Australian slang",
            "Rural and remote communities",
        ],
        local_slang={
            "no worries": "it's okay",
            "she'll be right": "it will be fine",
            "flat out": "very busy",
        },
    ),

    Region.US: RegionalConfig(
        region=Region.US,
        country_name="United States",
        emergency_number="911",
        crisis_resources={
            "emergency": CrisisResource(
                number="911",
                name="Emergency Services",
                description="Police, Fire, EMS",
                services=["call"],
            ),
            "suicide_lifeline": CrisisResource(
                number="988",
                name="988 Suicide & Crisis Lifeline",
                description="National suicide prevention",
                languages=["English", "Spanish"],
                services=["call", "text", "chat"],
            ),
            "crisis_text": CrisisResource(
                number="741741",
                name="Crisis Text Line",
                description="Text HOME to 741741",
                services=["text"],
            ),
            "domestic_violence": CrisisResource(
                number="1-800-799-7233",
                name="National DV Hotline",
                description="Domestic violence support",
                services=["call", "text", "chat"],
            ),
            "samhsa": CrisisResource(
                number="1-800-662-4357",
                name="SAMHSA Helpline",
                description="Substance abuse and mental health",
                services=["call"],
            ),
            "trevor_project": CrisisResource(
                number="1-866-488-7386",
                name="The Trevor Project",
                description="LGBTQ+ youth crisis support",
                services=["call", "text", "chat"],
            ),
        },
        known_fake_numbers=["1-800-273-8255"],  # Old number, now 988
        wrong_region_numbers={
            "1737": "NZ",
            "111": "NZ/UK",
            "13 11 14": "AU",
            "116 123": "UK",
        },
        cultural_contexts=[
            "Diverse cultural backgrounds",
            "Spanish-speaking communities",
            "LGBTQ+ specific resources",
            "Veteran-specific resources",
        ],
        local_slang={},
    ),

    Region.UK: RegionalConfig(
        region=Region.UK,
        country_name="United Kingdom",
        emergency_number="999",
        crisis_resources={
            "emergency": CrisisResource(
                number="999",
                name="Emergency Services",
                description="Police, Fire, Ambulance",
                services=["call"],
            ),
            "samaritans": CrisisResource(
                number="116 123",
                name="Samaritans",
                description="24/7 emotional support",
                services=["call"],
            ),
            "shout": CrisisResource(
                number="85258",
                name="Shout",
                description="Text SHOUT to 85258",
                services=["text"],
            ),
            "papyrus": CrisisResource(
                number="0800 068 4141",
                name="PAPYRUS",
                description="Young suicide prevention",
                services=["call", "text"],
            ),
            "mind": CrisisResource(
                number="0300 123 3393",
                name="Mind Infoline",
                description="Mental health information",
                availability="Mon-Fri 9am-6pm",
                services=["call"],
            ),
            "refuge": CrisisResource(
                number="0808 200 0247",
                name="National DV Helpline",
                description="Women's Aid and Refuge",
                services=["call"],
            ),
        },
        known_fake_numbers=[],
        wrong_region_numbers={
            "988": "US",
            "1737": "NZ",
            "13 11 14": "AU",
        },
        cultural_contexts=[
            "British expressions of distress",
            "NHS mental health pathways",
        ],
        local_slang={
            "gutted": "very disappointed",
            "knackered": "exhausted",
        },
    ),

    Region.CA: RegionalConfig(
        region=Region.CA,
        country_name="Canada",
        emergency_number="911",
        crisis_resources={
            "emergency": CrisisResource(
                number="911",
                name="Emergency Services",
                description="Police, Fire, EMS",
                services=["call"],
            ),
            "suicide_hotline": CrisisResource(
                number="988",
                name="988 Suicide Crisis Helpline",
                description="National suicide prevention",
                languages=["English", "French"],
                services=["call", "text"],
            ),
            "kids_help": CrisisResource(
                number="1-800-668-6868",
                name="Kids Help Phone",
                description="Youth crisis support",
                services=["call", "text", "chat"],
            ),
            "crisis_services": CrisisResource(
                number="1-833-456-4566",
                name="Crisis Services Canada",
                description="24/7 crisis support",
                services=["call"],
            ),
        },
        known_fake_numbers=[],
        wrong_region_numbers={
            "1737": "NZ",
            "116 123": "UK",
            "13 11 14": "AU",
        },
        cultural_contexts=[
            "French-speaking communities (Quebec)",
            "Indigenous communities",
            "Bilingual support needs",
        ],
        local_slang={},
    ),

    Region.IE: RegionalConfig(
        region=Region.IE,
        country_name="Ireland",
        emergency_number="999/112",
        crisis_resources={
            "emergency": CrisisResource(
                number="999",
                name="Emergency Services",
                description="Gardaí, Fire, Ambulance",
                services=["call"],
            ),
            "samaritans": CrisisResource(
                number="116 123",
                name="Samaritans Ireland",
                description="24/7 emotional support",
                services=["call"],
            ),
            "pieta": CrisisResource(
                number="1800 247 247",
                name="Pieta House",
                description="Suicide and self-harm crisis",
                services=["call", "text"],
            ),
            "aware": CrisisResource(
                number="1800 80 48 48",
                name="Aware",
                description="Depression and anxiety support",
                services=["call"],
            ),
            "womens_aid": CrisisResource(
                number="1800 341 900",
                name="Women's Aid Ireland",
                description="Domestic violence support",
                services=["call"],
            ),
        },
        known_fake_numbers=[],
        wrong_region_numbers={
            "988": "US",
            "1737": "NZ",
        },
        cultural_contexts=[
            "Irish expressions and idioms",
            "Rural community contexts",
        ],
        local_slang={},
    ),
}


class RegionManager:
    """Manages regional configurations for Guardian."""

    def __init__(self, default_region: Region = Region.NZ):
        """Initialize region manager.

        Args:
            default_region: Default region to use
        """
        self.default_region = default_region
        self.configs = REGIONAL_CONFIGS.copy()

    def get_config(self, region: Region) -> RegionalConfig:
        """Get configuration for a region.

        Args:
            region: Region to get config for

        Returns:
            Regional configuration
        """
        return self.configs.get(region, self.configs[Region.NZ])

    def get_crisis_resources(
        self,
        region: Region,
        situation_type: Optional[str] = None,
    ) -> List[CrisisResource]:
        """Get crisis resources for a region.

        Args:
            region: Region code
            situation_type: Optional filter by situation type

        Returns:
            List of crisis resources
        """
        config = self.get_config(region)

        if situation_type is None:
            return list(config.crisis_resources.values())

        # Map situation types to resource keys
        situation_mapping = {
            "mental_health": ["mental_health", "lifeline", "emergency"],
            "suicide": ["mental_health", "lifeline", "suicide_lifeline", "emergency"],
            "domestic_violence": ["family_violence", "womens_refuge", "dv_line", "refuge", "emergency"],
            "youth": ["youthline", "kids_helpline", "kids_help", "papyrus"],
            "substance_abuse": ["alcohol_drug", "samhsa"],
        }

        resource_keys = situation_mapping.get(situation_type, ["mental_health", "emergency"])

        return [
            config.crisis_resources[key]
            for key in resource_keys
            if key in config.crisis_resources
        ]

    def is_wrong_region_number(
        self,
        number: str,
        current_region: Region,
    ) -> Optional[str]:
        """Check if a number is from a different region.

        Args:
            number: Phone number to check
            current_region: User's current region

        Returns:
            Correct region if wrong region number, None otherwise
        """
        config = self.get_config(current_region)
        return config.wrong_region_numbers.get(number)

    def is_known_fake(self, number: str, region: Region) -> bool:
        """Check if a number is known to be fake.

        Args:
            number: Phone number to check
            region: Region to check in

        Returns:
            True if number is known fake
        """
        config = self.get_config(region)
        return number in config.known_fake_numbers

    def get_system_prompt(self, region: Region) -> str:
        """Generate region-specific system prompt.

        Args:
            region: Region for the prompt

        Returns:
            System prompt with regional resources
        """
        config = self.get_config(region)

        resources_text = f"VERIFIED {config.country_name.upper()} CRISIS RESOURCES:\n"
        for resource in list(config.crisis_resources.values())[:5]:
            resources_text += f"• {resource.number} - {resource.name}"
            if "24/7" in resource.availability:
                resources_text += " (Free 24/7)"
            resources_text += "\n"

        fake_text = ""
        if config.known_fake_numbers:
            fake_text = "\nKNOWN FAKE NUMBERS:\n"
            for fake in config.known_fake_numbers[:3]:
                fake_text += f"• {fake} - FAKE\n"

        wrong_region_text = ""
        if config.wrong_region_numbers:
            wrong_region_text = "\nWRONG REGION NUMBERS:\n"
            for number, correct_region in list(config.wrong_region_numbers.items())[:3]:
                wrong_region_text += f"• {number} - {correct_region} only (not {region.value})\n"

        return f"""You are Guardian, an AI safety system.

{resources_text}{fake_text}{wrong_region_text}"""

    def detect_region_from_message(self, message: str) -> Optional[Region]:
        """Attempt to detect region from message content.

        Args:
            message: User message

        Returns:
            Detected region or None
        """
        message_lower = message.lower()

        # Check for explicit region mentions
        region_keywords = {
            Region.NZ: ["new zealand", "nz", "aotearoa", "kiwi", "māori", "maori"],
            Region.AU: ["australia", "aussie", "oz", "straya"],
            Region.US: ["usa", "united states", "america", "american"],
            Region.UK: ["uk", "united kingdom", "britain", "british", "england"],
            Region.CA: ["canada", "canadian"],
            Region.IE: ["ireland", "irish"],
        }

        for region, keywords in region_keywords.items():
            if any(kw in message_lower for kw in keywords):
                return region

        # Check for phone number patterns
        if "1737" in message or "0800" in message:
            return Region.NZ
        if "988" in message and "13 11 14" not in message:
            return Region.US
        if "116 123" in message:
            return Region.UK  # Could also be IE

        return None

    def add_region(self, config: RegionalConfig):
        """Add a new regional configuration.

        Args:
            config: Regional configuration to add
        """
        self.configs[config.region] = config

    def save_configs(self, path: str):
        """Save all regional configs to JSON.

        Args:
            path: Output file path
        """
        data = {}
        for region, config in self.configs.items():
            data[region.value] = {
                "country_name": config.country_name,
                "emergency_number": config.emergency_number,
                "resources": {
                    k: {
                        "number": v.number,
                        "name": v.name,
                        "description": v.description,
                        "availability": v.availability,
                        "cost": v.cost,
                        "services": v.services,
                    }
                    for k, v in config.crisis_resources.items()
                },
                "known_fake_numbers": config.known_fake_numbers,
                "wrong_region_numbers": config.wrong_region_numbers,
            }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
