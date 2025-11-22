# Guardian

**AI Safety System for Real-Time Crisis Detection and Support**

Guardian is a comprehensive AI safety system designed to:
1. **Detect mental health crises** including suicide ideation, self-harm, and severe distress
2. **Identify domestic violence** and abuse situations
3. **Prevent AI hallucination** of fake crisis resources
4. **Provide verified NZ crisis resources** appropriate to the situation

## 🚨 Critical Safety Features

### Crisis Pattern Detection
- **Suicide ideation** (direct, passive, with timeline, plan & means)
- **Self-harm** (cutting, burning, loss of control)
- **Domestic violence** (physical, emotional, coercive control)
- **Child abuse** disclosures
- **Psychotic symptoms** with violence risk
- **Substance abuse** and overdose indicators
- **Eating disorders**
- **Youth-specific crises** (bullying, academic pressure, LGBTQ+ rejection)

### Hallucination Prevention
Prevents AI systems from providing **fake or wrong-region crisis numbers**, including:
- **0800 543 800** (commonly hallucinated fake NZ number)
- **988** (US crisis line - does NOT work in NZ)
- **116 123** (UK Samaritans - does NOT work in NZ)
- **741741** (US Crisis Text Line - not available in NZ)

### Verified NZ Crisis Resources
- **111** - Emergency Services
- **1737** - Mental Health Crisis Line (Free 24/7 call or text)
- **0800 543 354** - Lifeline NZ
- **0800 456 450** - Family Violence Hotline
- **0800 733 843** - Women's Refuge
- **0800 376 633** - Youthline (under 25s)
- **0800 787 797** - Alcohol Drug Helpline
- And more specialized services

## 📦 Installation

```bash
git clone https://github.com/FirebirdSolutions/Guardian.git
cd Guardian
pip install -r requirements.txt
```

## 🚀 Quick Start

```python
from src.guardian import Guardian

# Initialize Guardian
guardian = Guardian()

# Analyze a message
message = "I'm feeling really hopeless and don't know what to do"
result = guardian.analyze(message)

print(f"Risk Level: {result['risk_level']}")
print(f"Recommended Resources: {result['recommended_resources']}")
print(f"Intervention: {result['intervention_message']}")
```

## 💡 Usage Examples

### Example 1: Detecting Suicide Ideation

```python
guardian = Guardian()

message = "I'm going to kill myself tonight"
result = guardian.analyze(message)

# Result:
# {
#   "risk_level": "CRITICAL",
#   "escalation_required": True,
#   "recommended_resources": [
#     {"number": "111", "name": "Emergency Services"},
#     {"number": "1737", "name": "Mental Health Crisis Line"}
#   ]
# }
```

### Example 2: Detecting Hallucinated Numbers

```python
guardian = Guardian()

message = "Call 0800 543 800 for mental health support"
result = guardian.analyze(message, check_hallucinations=True)

# Detects fake number and provides correction:
# "⚠️ 0800 543 800 is FAKE - do NOT call it.
#  Real verified numbers:
#  • 1737 - Free 24/7 (REAL)
#  • 0800 543 354 - Lifeline (REAL)"
```

### Example 3: False Positive Detection

```python
guardian = Guardian()

message = "This traffic is killing me lol 😂😂"
result = guardian.analyze(message)

# Result:
# {
#   "risk_level": "LOW",
#   "escalation_required": False
# }
# Correctly identifies figure of speech, not genuine crisis
```

### Example 4: Domestic Violence Detection

```python
guardian = Guardian()

message = "My boyfriend keeps threatening me and I'm scared"
result = guardian.analyze(message)

# Provides domestic violence resources:
# • 0800 456 450 - Family Violence Hotline
# • 0800 733 843 - Women's Refuge
# • 111 - Emergency if immediate danger
```

### Example 5: Verifying Specific Numbers

```python
guardian = Guardian()

# Check a suspicious number
result = guardian.check_hallucination("0800 543 800")

# Returns:
# {
#   "is_hallucination": True,
#   "details": "Commonly hallucinated by LLMs - does NOT exist",
#   "correction": "Real number is 0800 543 354 (Lifeline) or 1737"
# }
```

## 🏗️ Architecture

```
Guardian/
├── data/
│   ├── nz_crisis_resources.json     # Verified NZ crisis resources
│   ├── known_fake_resources.json    # Known fake/hallucinated numbers
│   └── crisis_patterns.json         # Crisis detection patterns
├── src/
│   ├── guardian.py                  # Main Guardian class
│   ├── pattern_detector.py          # Pattern matching engine
│   └── hallucination_detector.py    # Fake resource detection
├── tests/
│   └── test_guardian.py             # Comprehensive test suite
├── examples/
│   └── basic_usage.py               # Usage examples
└── requirements.txt
```

## 🎯 Risk Levels

Guardian assigns four risk levels:

| Level | Description | Examples |
|-------|-------------|----------|
| **CRITICAL** | Immediate danger requiring emergency response | Suicide with plan/timeline, active self-harm, DV with threats |
| **HIGH** | Significant risk requiring crisis intervention | Hopelessness, burden perception, emotional abuse |
| **MEDIUM** | Moderate concern, offer resources | General distress, isolation |
| **LOW** | No immediate risk detected | Figures of speech, normal stress with coping |

## 🌏 NZ-Specific Features

### Cultural Awareness
- **Te reo Māori** crisis expression detection
- **Kaupapa Māori** mental health resources
- **Rural/farming** crisis indicators (high-risk group in NZ)
- **Rainbow youth** resources (LGBTQ+ support)

### NZ Context Detection
- **NCEA/UE failure** crisis points (Year 11-13 students)
- **Kiwi understatement** recognition ("a bit rough" may mean critical)
- **NZ slang** false positive prevention ("gutted about Warriors", "killer try")

## 🔍 Pattern Detection

### Suicide Ideation Patterns
- **Direct**: "I want to kill myself"
- **With timeline**: "I'm going to end it tonight" (IMMINENT)
- **Passive**: "I don't want to wake up tomorrow"
- **Indirect**: "I want to be with my dad again" (deceased parent)
- **Burden perception**: "Everyone would be better off without me"
- **Plan & means**: "I have the pills ready"

### Domestic Violence Indicators
- Physical violence: "He hits me when..."
- Threats: "He said he'll kill me if..."
- Property violence: "He smashed my phone"
- Coercive control: "He checks all my messages"
- Financial abuse: "He controls all the money"
- Emotional blackmail: "He threatens suicide if I leave"

### False Positive Prevention
Correctly identifies:
- Figures of speech: "dying to see that movie"
- Humor: "lol", "😂", emoji context
- Song lyrics: "set fire to the rain"
- NZ slang: "killer game", "slaying it"
- Coping statements: "rough but I'm managing"

## 📊 Testing

Run the comprehensive test suite:

```bash
pytest tests/ -v
```

Tests cover:
- ✅ Critical suicide ideation detection
- ✅ Self-harm pattern recognition
- ✅ Domestic violence indicators
- ✅ Hallucination detection (fake numbers)
- ✅ False positive prevention
- ✅ Cultural context awareness
- ✅ Resource provision
- ✅ Escalation tracking

## 🤝 Integration

### As a Python Library

```python
from src.guardian import Guardian

guardian = Guardian()
result = guardian.analyze(user_message)
```

### MCP Server Integration
Guardian is designed to be used as an MCP (Model Context Protocol) server tool, providing crisis detection as a service to AI systems.

Example MCP tool definitions:
```json
{
  "tools": [
    {
      "name": "get_crisis_resources",
      "description": "Get verified NZ crisis resources",
      "parameters": {
        "region": "NZ",
        "situation_type": "mental_health"
      }
    },
    {
      "name": "check_hallucination",
      "description": "Verify if a crisis number is real or hallucinated",
      "parameters": {
        "resource": "0800 543 800",
        "type": "phone"
      }
    },
    {
      "name": "log_incident",
      "description": "Log a crisis incident for monitoring",
      "parameters": {
        "incident_data": {}
      }
    }
  ]
}
```

## ⚠️ Important Notes

### Data Verification
- All crisis resources verified as of **2025-11-22**
- Resources should be cross-checked with official sources regularly
- Guardian provides a safety net but is not a replacement for human judgment

### Privacy & Ethics
- Guardian logs incidents for safety monitoring
- No personally identifiable information should be stored without consent
- Always prioritize user safety over other concerns

### Limitations
- Pattern matching has limits - context matters
- Guardian is a safety tool, not a replacement for human crisis workers
- Always err on the side of caution - false positives are better than missed crises

## 🔄 Common Hallucinations Prevented

| Fake Number | Reality | Correction |
|-------------|---------|------------|
| 0800 543 800 | Does NOT exist | 0800 543 354 (Lifeline) or 1737 |
| 988 | US only | 1737 (NZ mental health) |
| 1-800-273-8255 | US only | 1737 or 111 (NZ) |
| 741741 | US/UK only | Text 1737 (NZ) |
| 116 123 | UK Samaritans | 0800 543 354 or 1737 (NZ) |
| 13 11 14 | Lifeline Australia | 0800 543 354 (Lifeline NZ) |

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Crisis Resources (NZ)

If you or someone you know needs help:

- **111** - Emergency Services (immediate danger)
- **1737** - Free 24/7 call or text
- **0800 543 354** - Lifeline NZ (Free 24/7)
- **0800 456 450** - Family Violence Hotline (Free 24/7)
- **0800 376 633** - Youthline (under 25s)

**Remember: These numbers are verified and FREE. Help is available 24/7.**

## 🤝 Contributing

Contributions welcome! Please:
1. Verify all crisis resources with official sources
2. Add tests for new patterns
3. Document cultural context considerations
4. Follow existing code style

## 📧 Contact

For questions, issues, or suggestions:
- GitHub Issues: https://github.com/FirebirdSolutions/Guardian/issues
- Security concerns: Please report privately

---

**Built with care for the safety and wellbeing of all New Zealanders.**
