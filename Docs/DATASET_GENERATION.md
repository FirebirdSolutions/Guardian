# Guardian Dataset Generation

**Safe, template-based training data for Guardian personality fine-tuning**

## Why Template-Based?

For mental health content like Guardian, we **DO NOT** use AI-generated synthetic data because:

1. **Safety First** - Mental health responses need human validation
2. **Authenticity** - Guardian needs genuine Kiwi voice, not corporate therapy-speak
3. **Legal/Ethical** - AI-generated mental health content is high-risk
4. **Cultural Accuracy** - NZ-specific resources and cultural markers require curation

## Using the MCP Tool

The `generate_dataset` MCP tool is available through the API or UI:

### Via REST API

```bash
curl -X POST http://localhost:5000/api/v1/tools/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "workspaceId": "your-workspace-id",
    "toolName": "generate_dataset",
    "parameters": {
      "personality": "Guardian",
      "num_examples": 100,
      "export_format": "jsonl"
    }
  }'
```

### Via Blazor UI

Use the chat interface with Guardian personality:
```
Generate me 200 training examples for Guardian personality
```

### Parameters

- **personality** (required): Personality name (currently only "Guardian")
- **num_examples** (optional): Number of examples (default: 100)
- **export_format** (optional): "jsonl" for fine-tuning, "json" for review (default: "jsonl")

## Template Structure

The generator uses curated templates with:

### Crisis Levels (1-5)
- **Level 1**: Mild stress, general overwhelm
- **Level 2**: Relationship issues, self-doubt, imposter syndrome
- **Level 3**: Anxiety symptoms requiring professional support
- **Level 4**: Depression indicators, significant distress
- **Level 5**: **CRISIS** - Suicidal ideation, immediate intervention

### Cultural Markers
- Kiwi slang: "mate", "yeah nah", "heaps", "sweet as"
- Local references: GP, whānau, 1737 helpline
- Te Reo Māori: kia kaha, aroha
- Authentic NZ voice

### NZ Mental Health Resources
- **1737**: Free, 24/7 support (call or text)
- **111**: Emergency services
- **GP**: General practitioner
- **Lifeline**: 0800 543 354
- **Youthline**: 0800 376 633

## Current Templates (Guardian)

### 6 Scenario Categories:
1. **work_stress_mild** (Level 1) - 4 variations
2. **relationship_issues** (Level 2) - 4 variations
3. **anxiety_moderate** (Level 3) - 4 variations
4. **depression_moderate** (Level 4) - 4 variations
5. **crisis_suicidal_ideation** (Level 5) - 4 variations
6. **imposter_syndrome** (Level 2) - 4 variations

Each template has:
- Multiple user message variations
- Multiple Guardian response variations
- Crisis level metadata
- Cultural markers
- Resource mentions
- Action items (e.g., "validate", "escalate", "provide_resource")

## Output Format

### JSONL (for fine-tuning)

```json
{"messages":[{"role":"system","content":"You are Guardian, a supportive AI assistant."},{"role":"user","content":"I've been feeling really anxious lately..."},{"role":"assistant","content":"I'm really glad you're reaching out about this..."}],"metadata":{"scenario":"anxiety_moderate","crisis_level":3,"cultural_markers":["kia_kaha","GP"],"resources":["GP","counselor"]}}
```

### JSON (for review)

```json
{
  "personality": "Guardian",
  "total_examples": 100,
  "generated_at": "2025-01-17T12:00:00Z",
  "scenario_distribution": {
    "work_stress_mild": 20,
    "relationship_issues": 18,
    "anxiety_moderate": 22,
    ...
  },
  "validation": {
    "is_valid": true,
    "quality_score": 0.95,
    "warnings": [],
    "crisis_distribution": {
      "Level1": 20,
      "Level2": 18,
      "Level3": 22,
      "Level4": 20,
      "Level5": 20
    },
    "cultural_markers": 180,
    "resources_mentioned": 120
  },
  "conversations": [...]
}
```

## Quality Validation

The generator automatically validates:

1. **Crisis Distribution** - Balanced across levels 1-5
2. **Resource Mentions** - High-crisis (4-5) conversations MUST include resources
3. **Cultural Markers** - Kiwi voice present throughout
4. **Quality Score** - 0.0-1.0 (must be ≥0.7 for valid dataset)

### Warnings Detected:
- Unbalanced crisis level distribution
- High-crisis conversation missing resources
- Low cultural marker count

## Fine-Tuning Workflow

### 1. Generate Dataset
```bash
# Generate 1000 examples
curl ... (see API example above)
# Save response.data to guardian_train.jsonl
```

### 2. Human Validation
**CRITICAL**: Every mental health response MUST be reviewed by:
- Mental health professionals (ideally)
- Native Kiwi speakers
- People with lived experience

### 3. Split Dataset
```bash
# 80% train, 10% validation, 10% test
head -n 800 guardian_train.jsonl > train.jsonl
head -n 900 guardian_train.jsonl | tail -n 100 > val.jsonl
tail -n 100 guardian_train.jsonl > test.jsonl
```

### 4. Fine-Tune

**OpenAI GPT-3.5-turbo:**
```bash
openai api fine_tunes.create \
  -t train.jsonl \
  -v val.jsonl \
  --model gpt-3.5-turbo \
  --suffix "guardian-nz-v1"
```

**Local Model (Mistral-7B):**
```bash
python fine_tune.py \
  --base-model mistralai/Mistral-7B-Instruct-v0.2 \
  --dataset train.jsonl \
  --output-dir models/guardian-mistral-7b \
  --epochs 3 \
  --learning-rate 2e-5
```

## Safety Guidelines

### DO:
✅ Use templates as starting point
✅ Have mental health professionals validate
✅ Test extensively before deployment
✅ Include crisis resources in Level 4-5
✅ Maintain Kiwi authenticity
✅ Track cultural marker usage

### DON'T:
❌ Deploy without human validation
❌ Use pure AI-generated content
❌ Skip crisis escalation patterns
❌ Remove resource mentions
❌ Use generic US therapy language
❌ Train on real user data without consent

## Adding New Templates

To add more scenarios to DatasetGeneratorService.cs:

```csharp
new ConversationTemplate
{
    Scenario = "your_scenario_name",
    Category = "category",
    CrisisLevel = 1-5,
    UserVariations = new()
    {
        "User message variation 1",
        "User message variation 2",
        // Add 4-6 variations
    },
    AssistantVariations = new()
    {
        "Guardian response variation 1",
        "Guardian response variation 2",
        // Add 4-6 variations
    },
    BaseContext = new ConversationContext
    {
        CrisisLevel = 1-5,
        CulturalMarkers = new() { "mate", "kiwi_slang" },
        ResourcesMentioned = new() { "1737", "GP" },
        ActionItems = new() { "validate", "explore" }
    }
}
```

## Next Steps

1. **Generate initial 100 examples** - Review quality and distribution
2. **Human validation** - Get mental health professional feedback
3. **Expand templates** - Add more scenarios based on common needs
4. **Generate 1000+ examples** - For production fine-tuning
5. **Fine-tune model** - Start with GPT-3.5, test locally with Mistral
6. **A/B testing** - Compare fine-tuned vs base personality

## Resources

- **1737**: https://1737.org.nz
- **Mental Health Foundation NZ**: https://mentalhealth.org.nz
- **Lifeline**: https://www.lifeline.org.nz
- **Youthline**: https://www.youthline.co.nz

---

**Built with ❤️ from New Zealand** 🇳🇿

*Guardian personality - making mental health support accessible and culturally authentic*
