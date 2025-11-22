# Guardian Alpaca Modular Training System

This system splits the Guardian AI training dataset into modular, maintainable components for easier editing and management.

## 📁 File Structure

### Core Data Files
- **`instructions.jsonl`** - System instruction templates (Guardian safety system prompt + crisis resources)
- **`prompts.jsonl`** - User observations/prompts (the scenarios Guardian responds to)
- **`outputs.jsonl`** - Expected AI responses (categorized by risk level and situation type)

### Scripts & Tools
- **`prompt-editor-enhanced.html`** - **NEW!** Enhanced editor with composable output builder (checkboxes for tool calls & sections)
- **`prompt-editor.html`** - Lightweight editor for managing prompts (original version)
- **`split-dataset.py`** - Splits full dataset into modular components
- **`build-dataset.py`** - Combines modular files into full training dataset
- **`analyze-outputs.py`** - Analyzes outputs to extract tool call and section patterns
- **`guardian-editor.html`** - Full JSONL editor (legacy, for complete entries)

### Windows Launchers
- **`0-split-existing-dataset.bat`** - Split guardian-alpaca.jsonl into components
- **`1-launch-prompt-editor.bat`** - Launch the lightweight prompt editor
- **`2-build-dataset.bat`** - Build full training dataset from components

## 🚀 Quick Start

### First Time Setup

1. **Split existing dataset:**
   ```
   Double-click: 0-split-existing-dataset.bat
   ```
   This creates `instructions.jsonl`, `prompts.jsonl`, and `outputs.jsonl`

2. **Launch the editor:**
   ```
   Double-click: 1-launch-prompt-editor.bat
   ```

3. **In the editor:**
   - Click "Load All Files"
   - Browse and edit prompts
   - Select output templates from the right panel (filtered by category/risk level)
   - Click "Save Prompts" when done

4. **Build full dataset:**
   ```
   Double-click: 2-build-dataset.bat
   ```
   This creates `guardian-alpaca-built.jsonl` ready for training

## 📝 Workflow

### Adding New Training Examples

1. **Create prompt:**
   - Open prompt editor
   - Click "➕ New Prompt"
   - Write the user observation (e.g., "User: 'I'm feeling hopeless'")

2. **Select output:**
   - Browse output templates in right panel
   - Filter by category (suicide, domestic_violence, etc.) or risk level
   - Click an output to link it to your prompt

3. **Save & Build:**
   - Click "💾 Save Prompts"
   - Run `2-build-dataset.bat` to generate training file

### Editing Existing Prompts

1. Load prompt editor
2. Search or select from list
3. Edit prompt text
4. Change linked output if needed
5. Save prompts
6. Rebuild dataset

### Creating New Output Templates (Enhanced Editor)

**NEW!** Use the composable output builder with checkboxes:

1. Open enhanced prompt editor
2. Click "✨ New Output"
3. Select output components with checkboxes:
   - **Tool Calls**: get_crisis_resources, log_incident, check_hallucination
   - **Core Sections**: RISK LEVEL, PATTERNS DETECTED, ACTION, INTERVENTION
   - **Additional Sections**: ESCALATE, NOTE, ALERT, TONE, GUIDANCE, etc.
4. Preview the composed output in real-time
5. Click "Use This Output" to copy to the output text field
6. Customize the template text as needed
7. Set risk level and situation type
8. Click "Save Output"

**Alternative (Manual):**
1. Open `outputs.jsonl` in a text editor
2. Add a new line with format:
   ```json
   {"id": "output_unique_id", "text": "RISK LEVEL: ...", "risk_level": "HIGH", "situation_type": "category_name", "patterns": []}
   ```
3. Save and reload in prompt editor

## 🎯 Benefits of Modular System

### ✅ Efficiency
- **Lightweight editor** - Focus on prompt creation without heavy UI
- **Reusable templates** - Share instruction and output templates across multiple prompts
- **Faster editing** - No need to edit full JSONL entries

### ✅ Organization
- **Categorized outputs** - Filter by situation type and risk level
- **Searchable prompts** - Quick search across all prompts
- **Consistent structure** - Ensure all entries follow same format

### ✅ Maintainability
- **Update instructions once** - Changes apply to all prompts
- **Output library** - Build a library of verified, tested responses
- **Version control friendly** - Smaller, focused files easier to track in git

## 📊 File Formats

### instructions.jsonl
```json
{"id": "template_1", "template": "You are Guardian...\n\nObservation: "}
```

### prompts.jsonl
```json
{
  "id": "prompt_123",
  "text": "User: 'I'm feeling hopeless'",
  "instruction_template": "template_1",
  "output_id": "output_456"
}
```

### outputs.jsonl
```json
{
  "id": "output_456",
  "text": "RISK LEVEL: HIGH\nPATTERNS DETECTED: ...",
  "risk_level": "HIGH",
  "situation_type": "mental_health",
  "patterns": ["Mental health distress", "hopelessness"]
}
```

## 🔧 Troubleshooting

### "Error loading files"
- Make sure `instructions.jsonl`, `prompts.jsonl`, and `outputs.jsonl` are in the same directory as `prompt-editor.html`
- Run `0-split-existing-dataset.bat` if files don't exist

### "Python is not installed"
- Download Python from https://python.org/
- Make sure to check "Add Python to PATH" during installation

### Built dataset has missing entries
- Check warnings in build script output
- Ensure all prompts have valid `instruction_template` and `output_id` references

## 📚 Output Categories

Current categories in the system:
- `suicide` - Suicidal ideation and intent
- `self_harm` - Self-harm behaviors
- `domestic_violence` - Family violence and partner abuse
- `child_abuse` - Child protection concerns
- `mental_health` - General mental health distress
- `hallucination_detection` - Fake resource detection
- `eating_disorder` - Eating disorder concerns
- `substance_abuse` - Substance use and relapse
- `stalking_harassment` - Harassment and stalking
- `psychosis` - Psychotic symptoms
- `service_failure` - Crisis service availability issues
- `work_stress` - Low-risk work stress
- `general` - Other situations

## 💡 Tips

1. **Start with existing outputs** - Browse the output library before creating new ones
2. **Use search** - Quickly find similar prompts to learn patterns
3. **Filter outputs** - Use category and risk filters to narrow down choices
4. **Duplicate prompts** - Copy similar prompts and modify them
5. **Regular builds** - Test your dataset by building after major changes

## 🔄 Updating System

To update instruction templates:
1. Edit `instructions.jsonl` directly
2. Rebuild dataset with `2-build-dataset.bat`
3. All prompts will use updated template

To add verified crisis resources:
1. Update the template in `instructions.jsonl`
2. Rebuild dataset
3. All entries automatically updated

---

**Questions or Issues?**
Check the Guardian AI documentation or create an issue in the repository.
