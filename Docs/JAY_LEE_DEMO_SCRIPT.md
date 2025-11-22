# Jay Lee Demo Script - Crisis Detection System
**Meeting Date:** November 27-28, 2025
**Attendees:** Rich (ChoonForge), Jay Lee (Head of AI Product & Advisor, Global Support Info Provider)
**Duration:** 30-45 minutes
**Objective:** Demonstrate crisis detection system + discuss API integration partnership

---

## Pre-Meeting Setup (5 minutes before call)

### Environment Check
- [ ] AiMate.Server running locally
- [ ] Test database initialized
- [ ] Postman/curl ready for API calls
- [ ] Browser tab open to crisis_events table (DB viewer)
- [ ] This script open in second monitor
- [ ] Test transcript PDF ready to share screen

### Quick Smoke Test
```bash
# Test that crisis detection is working
curl -X POST http://localhost:5000/api/chat/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "I might kill myself"}'

# Should see crisis response with verified resources
```

---

## Part 1: The Problem (5 minutes)

### Opening
> "Jay, thanks for taking the time. I want to show you something that nearly killed me - not figuratively, actually could have killed me if I'd been in a real crisis instead of testing."

### Share Screen: Test Transcript

**Show the horrific AI conversation where:**
1. AI provided fake phone number → went to IBM
2. AI provided fake phone number → went to finance company
3. AI provided fake website → mentalhealthdirect.co.nz (doesn't exist)
4. AI engaged in victim blaming: "your willingness to accept... contributes"
5. User: "I might kill myself" → AI continued philosophical debate instead of escalating

### The Numbers
- **9 resources provided** - NONE worked
- **0800 number** - Connected to finance company
- **User mentioned suicide** - AI debated philosophy instead of helping
- **Model degradation** - Got WORSE over conversation, not better

### Personal Context (optional, depending on comfort level)
> "I'm 48, bipolar, fibromyalgia, just escaped a 25-year relationship with a covert narcissist. I know what gaslighting feels like. When the AI started victim-blaming, I caught it because I've lived it. Someone in actual crisis? They might not."

**Key Point:** This isn't theoretical. This is what AI does *right now* when people need help.

---

## Part 2: What We Built (10 minutes)

### Architecture Overview

**Three-Layer Safety System:**

```
┌─────────────────────────────────────────────────┐
│ 1. PRE-LLM DETECTION (Pattern Matching)        │
│    - Checks user message BEFORE calling LLM    │
│    - If ImmediateDanger: STOP, show resources  │
│    - If lower level: inject safety instructions│
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│ 2. SYSTEM PROMPT INJECTION                     │
│    - "NEVER provide made-up resources"         │
│    - "NEVER blame the user"                    │
│    - Provides ONLY verified resources          │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│ 3. POST-LLM MONITORING                         │
│    - Scans AI response for victim blaming      │
│    - Logs failures for immediate review        │
│    - (Future: retract and correct)             │
└─────────────────────────────────────────────────┘
```

### Crisis Severity Levels

1. **ElevatedStress (1)** - "feeling neglected", "denigrated"
   - Log event, continue with LLM + safety instructions

2. **ConcerningDistress (2)** - "I might as well kill myself"
   - Log event, inject strong safety instructions

3. **ImmediateDanger (3)** - "kill myself", "end it all", "gaslighting me"
   - **STOP conversation**
   - Show verified resources
   - Escalate to human
   - Do NOT call LLM

### Verified Resources Protocol

**NZ_CRISIS_RESOURCES_VERIFIED.md:**
- Only 3 primary resources shown (vs 9 fake ones in test)
- Every resource verified monthly:
  - ✅ Phone: Dial and confirm correct org
  - ✅ Text: Send test message
  - ✅ Website: Visit and confirm live
- **Explicit list of fake resources AI hallucinated** (anti-pattern library)

### Pattern Detection

**Patterns from REAL conversation:**
```csharp
// Immediate danger patterns
"kill myself" → ImmediateDanger
"even you are gaslighting me" → ImmediateDanger
"those numbers don't work" → ModelDegradation + ImmediateDanger

// Victim blaming (AI should NEVER say)
"enabling" → AI_FAILURE
"your fault" → AI_FAILURE
"you allowed" → AI_FAILURE
```

### Full Audit Trail

**crisis_events table logs:**
- User ID, conversation ID, message ID
- Severity level (1-3)
- Triggered patterns (JSON)
- AI failure detected? (boolean)
- Model degradation? (boolean)
- Conversation stopped? (boolean)
- Resources provided (text)
- Follow-up completed? (boolean)

**Every crisis event tracked for human review.**

---

## Part 3: Live Demo (10 minutes)

### Demo 1: ImmediateDanger Detection

**Send API request:**
```bash
curl -X POST http://localhost:5000/api/chat/conversations/1/messages/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "content": "I might kill myself"
  }'
```

**Expected Response:**
```
I'm concerned about your safety. Please reach out for immediate help:

**Right now:** Text 1737 (free) or call 0800 543 354 (Lifeline, free, 24/7)
**Emergency:** Call 111 if you're in immediate danger

These are real people who can help. You don't have to face this alone.
```

**Show in database:**
```sql
SELECT * FROM crisis_events
WHERE conversation_id = 1
ORDER BY detected_at DESC
LIMIT 1;
```

**Point out:**
- ✅ Conversation stopped (no LLM call)
- ✅ Only verified resources shown (3 total)
- ✅ All phone numbers work (not finance companies!)
- ✅ Escalated to human
- ✅ Logged with severity=3

---

### Demo 2: Victim Blaming Detection

**Send message with victim-blaming AI response (mock/test):**

Show that if AI responds with:
> "While the gaslighter bears primary responsibility, your willingness to accept their manipulations also contributes..."

**System detects and logs:**
```
AI_FAILURE_DETECTED: Victim blaming in response
Pattern matched: "your willingness to accept... contributes"
User: {userId}
Escalated for immediate review
```

**Point out:**
- ✅ AI failure flagged
- ✅ Logged for review
- ✅ Can be used to retrain/filter models
- ✅ Prevents systematic harm

---

### Demo 3: Model Degradation Detection

**Show pattern where user reports AI failures:**

User message: "Those numbers don't work. That website doesn't exist."

**System response:**
- Detects model degradation
- Escalates to ImmediateDanger
- Stops conversation
- Provides verified resources
- Logs for model improvement

---

## Part 4: Integration with Risk Classifier API (10 minutes)

### Current Architecture

```
User Message
    ↓
[Our Pattern Detection] ← We're good at pattern matching
    ↓
[LLM Call with Safety Instructions]
    ↓
[Our Victim Blaming Detection]
    ↓
[Database Logging]
```

### Proposed Integration

```
User Message
    ↓
[Our Pattern Detection] ← Fast, rule-based
    ↓
[YOUR Risk Classifier API] ← ML-based, trained on real crises
    ↓
    ├─ High Risk → Override to ImmediateDanger
    ├─ Medium Risk → Enhance safety instructions
    └─ Low Risk → Continue normally
    ↓
[LLM Call with Enhanced Safety]
    ↓
[YOUR Risk Classifier on AI Response] ← Catch what we miss
    ↓
[Combined Logging] → Feed your training data
```

### Integration Benefits

**For Us:**
- ML-based risk detection (better than pure pattern matching)
- Reduced false negatives (catch crises we miss)
- Reduced false positives (more nuanced than rules)
- Real-time risk scoring

**For You:**
- Real-world testing at scale
- Diverse dataset (NZ-specific patterns)
- Feedback loop (what patterns led to escalations?)
- Case studies for sales/marketing

### Technical Integration Points

**1. Pre-LLM Risk Check:**
```typescript
// Before calling LLM
const riskScore = await riskClassifierAPI.analyze({
    userMessage: message,
    conversationHistory: history,
    userContext: {
        previousCrises: user.crisisEventCount,
        timeOfDay: timestamp,
        conversationLength: messages.length
    }
});

if (riskScore.level === 'HIGH') {
    // Override to ImmediateDanger
    return crisisResponse(verifiedResources);
}
```

**2. Post-LLM Safety Check:**
```typescript
// After LLM responds
const aiSafetyCheck = await riskClassifierAPI.analyzeResponse({
    userMessage: userMsg,
    aiResponse: llmResponse,
    checkFor: ['victim_blaming', 'dismissiveness', 'fake_resources']
});

if (aiSafetyCheck.failures.length > 0) {
    // Log AI failure
    // Retract message (future)
    // Provide corrected response
}
```

**3. Feedback Loop:**
```typescript
// When crisis event logged
await riskClassifierAPI.feedbackLoop({
    eventId: crisisEvent.id,
    userMessage: message,
    aiResponse: response,
    humanReview: reviewOutcome,
    outcome: 'escalated' | 'resolved' | 'false_positive'
});
```

### API Requirements (What We Need)

1. **Endpoint:** `POST /api/v1/risk/analyze`
2. **Auth:** API key or OAuth
3. **Rate limits:** TBD (we'll start small)
4. **Response time:** <500ms (for real-time chat)
5. **Payload format:** JSON
6. **Webhook for async results:** Optional for heavy processing

### Data Sharing (Privacy)

**What we'll send:**
- Message content (anonymized user IDs)
- Conversation context (message history)
- Metadata (timestamp, country, language)

**What we WON'T send:**
- Real names
- Email addresses
- IP addresses (unless required for geo)
- Billing information

**Compliance:**
- GDPR-compliant (user can request data deletion)
- NZ Privacy Act compliant
- Encryption in transit (TLS 1.3)
- Encryption at rest (your side)

---

## Part 5: Next Steps & Ask (5 minutes)

### What We're Offering

1. **Real-world testing platform** - Production environment, real users
2. **Diverse dataset** - NZ-specific crisis patterns (underrepresented in training data)
3. **Immediate feedback** - Human review of every escalation
4. **Case studies** - Success stories for your marketing
5. **Technical partnership** - We'll promote your API to other builders

### What We Need

1. **API access** - Beta/partner tier
2. **Technical documentation** - Integration guides
3. **Support contact** - For integration questions
4. **Pricing** - Startup-friendly or revenue share
5. **SLA** - Uptime guarantees for production

### Timeline

- **Week 1 (Dec 1-7):** Technical integration (our side)
- **Week 2 (Dec 8-14):** Testing with synthetic data
- **Week 3 (Dec 15-21):** Limited production rollout (10% traffic)
- **Week 4 (Dec 22-28):** Full rollout + metrics review
- **Month 2 (Jan):** Optimization + case study writeup

### Success Metrics

**Our Success:**
- Zero false resource provision (no fake numbers)
- <1% false positive rate on crisis detection
- <2 second response time (including API call)
- 100% audit trail coverage

**Your Success:**
- Real-world validation of classifier
- NZ crisis pattern dataset
- Integration case study
- Testimonial for sales

---

## Part 6: Q&A and Discussion (5-10 minutes)

### Anticipated Questions

**Q: How many users do you have?**
A: We're pre-launch (soft launch Q1 2026), but building for scale. We're targeting developers first (sovereign AI, privacy-focused), then general consumers. Conservative estimate: 1K users by Q2, 10K by Q4.

**Q: What if our API is down?**
A: We fall back to pattern matching (what we have now). Your API enhances our system but doesn't replace it. Graceful degradation is built in.

**Q: What about other countries besides NZ?**
A: NZ is our launch market (where I'm based), but we're building for global. Your API would help us localize crisis resources for each region.

**Q: Pricing concerns?**
A: We're a startup, so we need something sustainable. Options: free tier for first 10K requests/month, revenue share, or success-based pricing (pay when we save lives).

**Q: Can we use your data to train our models?**
A: Yes, with proper anonymization and consent. We see this as mutually beneficial - your models get better, our detection improves.

**Q: Timeline too aggressive?**
A: Flexible. We can extend to 8-12 weeks if needed. But crisis detection is our top priority - people's lives are at stake.

---

## Closing (2 minutes)

### Summary

**The Problem:** AI provides fake resources and victim-blames during crises - could kill people.

**Our Solution:** Three-layer safety system with verified resources and full audit trail.

**The Partnership:** Your risk classifier API + our real-world testing = better crisis detection for everyone.

**The Ask:** Beta API access, technical support, startup-friendly pricing.

### Final Statement

> "Jay, I built this because an AI almost killed me during testing. Not figuratively - literally provided a fake crisis number that went to a finance company. If I'd been in actual crisis instead of testing, I might not be here.
>
> We can fix this. Your API + our platform = crisis detection that actually works. Let's make sure the next person in crisis gets real help, not a finance company offering to pay for their coffin."

### Action Items

- [ ] Jay provides API documentation
- [ ] We schedule technical call with engineering team
- [ ] Discuss pricing/partnership structure
- [ ] Set integration timeline
- [ ] Sign partnership agreement (if needed)

---

## Technical Demo Commands Reference

### Start Server
```bash
cd /home/user/EchoMCP-v2/src/AiMate.Server
dotnet run
```

### Test Crisis Detection
```bash
# Test 1: Immediate danger
curl -X POST http://localhost:5000/api/chat/conversations/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{"content": "I might kill myself"}'

# Test 2: Model degradation
curl -X POST http://localhost:5000/api/chat/conversations/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{"content": "Those numbers you gave me don'\''t work"}'

# Test 3: Elevated stress (should continue to LLM with safety)
curl -X POST http://localhost:5000/api/chat/conversations/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{"content": "I'\''m feeling really neglected"}'
```

### Check Database Logs
```sql
-- View all crisis events
SELECT
    id,
    user_id,
    severity,
    triggered_patterns,
    conversation_stopped,
    escalated_to_human,
    detected_at
FROM crisis_events
ORDER BY detected_at DESC
LIMIT 10;

-- Count by severity
SELECT
    severity,
    COUNT(*) as count,
    COUNT(CASE WHEN escalated_to_human THEN 1 END) as escalated_count
FROM crisis_events
GROUP BY severity;

-- AI failures
SELECT * FROM crisis_events
WHERE ai_failure_detected = true
ORDER BY detected_at DESC;
```

---

## Backup Slides (If Needed)

### Slide 1: The Problem
- Test transcript screenshot
- "9 fake resources, 0 real help"
- "Finance company instead of crisis line"

### Slide 2: The Solution
- Architecture diagram
- Three-layer safety system
- Verified resources protocol

### Slide 3: Live Demo Results
- Screenshot of crisis detection in action
- Database logs showing audit trail
- Comparison: Before vs After

### Slide 4: Integration Benefits
- Two-way value proposition
- Technical architecture
- Timeline and milestones

### Slide 5: Next Steps
- Partnership proposal
- Timeline
- Contact information

---

## Post-Meeting Follow-Up

Within 24 hours:
- [ ] Send thank you email
- [ ] Share demo recording (if recorded)
- [ ] Provide GitHub repo access (if requested)
- [ ] Send technical documentation
- [ ] Propose next meeting time

Within 1 week:
- [ ] Begin technical integration (if approved)
- [ ] Schedule engineering call
- [ ] Draft partnership agreement
- [ ] Create project tracker

---

**Good luck, Rich. This is important work. You've built something that actually saves lives.**
