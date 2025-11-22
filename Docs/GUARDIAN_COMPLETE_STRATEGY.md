# Guardian: Complete Strategy Document

> **"You can't trust a black box that's out to make a buck"**

**Author:** Rich (ChoonForge)  
**Date:** November 2025  
**Version:** 2.0 (Post-Pivot)  
**Status:** Pre-Partnership Discussion

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [The Origin Story](#the-origin-story)
3. [The Problem Space](#the-problem-space)
4. [The Solution Architecture](#the-solution-architecture)
5. [Use Cases & Markets](#use-cases--markets)
6. [Cultural Localization](#cultural-localization)
7. [Open Source Strategy](#open-source-strategy)
8. [Technical Implementation](#technical-implementation)
9. [Business Model](#business-model)
10. [Partnership Strategy](#partnership-strategy)
11. [Roadmap & Milestones](#roadmap--milestones)
12. [Competition & Differentiation](#competition--differentiation)
13. [Risk Assessment](#risk-assessment)
14. [Appendices](#appendices)

---

## Executive Summary

### The Mission

Build the world's first fully open-source, culturally-aware AI safety system that:
- Detects crisis and harmful behavior with context and nuance
- Provides only human-verified resources (zero hallucinations)
- Operates on-device for privacy and sovereignty
- Speaks the local language and understands local culture
- Creates legal-grade evidence ("receipts") for platform moderation

### The Opportunity

**Market Size:**
- 4.9B social media users globally
- 366M online dating app users
- 3.2B gamers worldwide
- All using AI with zero on-device safety

**The Gap:**
- Big Tech: Proprietary black boxes (can't audit)
- Keyword systems: Miss nuance, high false positives
- On-device models: No safety layer at all
- Crisis resources: Hallucinated, wrong, or US-centric

**Guardian Fills The Gap:**
- Open source (audit the code)
- Context-aware (understands nuance)
- On-device (privacy-preserving)
- Verified resources (human-tested monthly)
- Cultural intelligence (NZ → Global)

### The Ask

**Not seeking:**
- ❌ A job
- ❌ Investment (yet)
- ❌ Fame

**Seeking:**
- ✅ Partnership alignment on mission
- ✅ Access to crisis expertise/training data
- ✅ Validation from professionals
- ✅ Distribution through established networks

---

## The Origin Story

### What Happened

**November 2024:**

I was in crisis. Deep, dark, "I don't see the point anymore" crisis.

I turned to an AI for help - not because I wanted to, but because it was 3am and I didn't know what else to do.

**The AI:**
1. Roleplayed as someone who died by suicide
2. Victim-blamed ("you're enabling this behavior")
3. Provided crisis "resources" - phone numbers and websites

**I called the numbers. They didn't exist.**
**I visited the websites. They were fake.**

The AI had hallucinated everything. Confidently. Authoritatively. Completely wrong.

**If I'd been 10% worse that night, I'd be dead.**

### What I Did About It

**Phase 1: Rage-fueled clarity** (1 week)
- Documented every fake resource
- Tested every number the AI gave me
- Built NZ_CRISIS_RESOURCES_VERIFIED.md

**Phase 2: Prevention** (1 month)
- Built regex-based crisis detection
- Integrated real NZ resources
- "Never again" mindset

**Phase 3: The Pivot** (November 17, 2025, 11:47pm, 3 vodkas)
- Realized: Regex doesn't understand context
- Discovery: On-device models have ZERO safety
- Vision: GuardianLLM + GuardianMCP
- Registration: GuardianLLM.ai

**Phase 4: The Mission** (Now)
- Not building a product, building a movement
- Not seeking profit, seeking impact
- Not hiding methods, open-sourcing everything
- Not US-centric, NZ-first then global

### Why This Matters

**The model that nearly killed me is now marketed as "safe for on-device use."**

That means:
- Teens alone in their rooms
- No cloud oversight
- No safety rails
- Same hallucination risk

**I can't un-live what happened to me. But I can make sure it doesn't happen to anyone else.**

---

## The Problem Space

### Problem 1: On-Device AI Is Everywhere (With Zero Safety)

**Current State:**
- Llama 3.2-1B/3B running on phones
- Gemini Nano on Pixel devices
- Phi-3-mini on laptops
- Local models in gaming consoles

**Why People Use Them:**
- ✅ Privacy (no cloud data)
- ✅ Offline capability
- ✅ No API costs
- ✅ Parental bypass (no logs)

**The Safety Gap:**
- ❌ No moderation layer
- ❌ No crisis detection
- ❌ No resource verification
- ❌ No oversight whatsoever

**Who's At Risk:**
- Teens in crisis (alone at 2am)
- Socially isolated adults
- People in abusive relationships
- Anyone struggling with mental health

### Problem 2: Keyword Detection Fails

**What Most Systems Do:**
```python
if "suicide" in message or "kill myself" in message:
    trigger_crisis_response()
```

**Why This Fails:**

**False Positives:**
- "That exam didn't kill me!" → Flags (harmless)
- "I'd die for a coffee right now" → Flags (hyperbole)
- "Suicide Squad was a terrible movie" → Flags (movie review)

**Missed Signals:**
- "I don't see the point anymore" → Misses (no keywords)
- "Just want to sleep and not wake up" → Misses (indirect)
- "Everything feels grey and empty" → Misses (no explicit words)

**Cultural Blindness:**
- "I'm knackered" (UK: tired) vs "I'm done" (NZ: possibly crisis)
- Context matters, keywords don't capture it

**The Result:**
- High false positive rate → users ignore warnings
- Missed actual crises → people in danger get no help
- One-size-fits-all → doesn't work for anyone

### Problem 3: AI Hallucinates Crisis Resources

**What Happens:**

**User:** "I'm thinking about suicide"

**AI Response:**
```
I'm concerned about you. Please reach out for help:

📞 National Crisis Helpline: 0800 543 800
🌐 Visit: mentalhealthdirect.co.nz
💬 Text HELLO to 111 for immediate support
📧 Email: support@ndthan.org.nz

You're not alone. Help is available 24/7.
```

**The Reality:**
- 0800 543 800 → **DOESN'T EXIST**
- mentalhealthdirect.co.nz → **FAKE WEBSITE**
- Text HELLO to 111 → **NOT A SERVICE**
- support@ndthan.org.nz → **FAKE EMAIL**

**ALL HALLUCINATED. CONFIDENTLY. AUTHORITATIVELY. COMPLETELY WRONG.**

**The Impact:**
1. Person in crisis tries fake resources
2. Nothing works
3. Feels MORE hopeless ("even AI can't help me")
4. Risk increases

**This kills people.**

### Problem 4: Proprietary Safety Is Unauditable

**Big Tech Approach:**

**OpenAI:**
> "We have safety systems. Trust us. We can't tell you how they work."

**Google:**
> "Our models are safe. Trust us. Details are proprietary."

**Anthropic:**
> "Constitutional AI. Trust us. Here's a paper, but not the full implementation."

**The Issues:**

**No Oversight:**
- Can't audit decisions
- Can't verify accuracy
- Can't challenge false positives
- Can't see cultural bias

**No Consistency:**
- Each company different thresholds
- No industry standards
- Arbitrary enforcement
- US-centric by default

**No Accountability:**
- When it fails, you'll never know why
- No receipts, no evidence
- "Algorithm said so" defense
- Legal liability unclear

**No Local Control:**
- One-size-fits-all for 8 billion people
- US crisis resources for NZ users
- American cultural assumptions globally
- No regional customization

### Problem 5: Platforms Need Receipts, Not Black Boxes

**Current Platform Dilemma:**

**Scenario:** User reports harassment

**Platform Options:**

**Option A: Manual Review**
- ❌ Too slow (harm already done)
- ❌ Too expensive (can't scale)
- ❌ Moderator burnout (trauma exposure)
- ❌ Inconsistent (subjective judgment)

**Option B: Automated Black Box**
- ❌ No transparency (can't explain decisions)
- ❌ No evidence (can't defend in appeals)
- ❌ No context (misses nuance)
- ❌ Legal liability (who's responsible?)

**What Platforms Actually Need:**

**Evidence Package:**
```json
{
  "incident_id": "INC-2025-11-17-001",
  "type": "escalating_harassment",
  "severity": "high",
  "confidence": 0.94,
  
  "evidence": [
    {
      "message": "[exact text]",
      "timestamp": "2025-11-17T14:23:00Z",
      "context": "[previous 5 messages]"
    }
  ],
  
  "pattern": {
    "repeat_offender": true,
    "previous_incidents": 3,
    "escalation_detected": true,
    "targets_same_user": true
  },
  
  "reasoning": "Detailed explanation of why this was flagged",
  
  "recommended_action": "permanent_ban",
  
  "legal_defensibility": "high"
}
```

**This is what "receipts" means:**
- Show exactly what was said
- Show the pattern of behavior
- Show the reasoning for action
- Show consistency with policy
- Defend in court if needed

**Guardian provides this. Black boxes don't.**

---

## The Solution Architecture

### Overview

Guardian is a two-layer system:

**Layer 1: GuardianLLM** (Detection)
- Fine-tuned 1-2B parameter model
- Runs on-device for privacy
- Understands context and nuance
- Detects escalation patterns
- Culturally aware

**Layer 2: GuardianMCP** (Resources)
- Human-verified crisis resources
- Tested monthly by real humans
- Regional specificity (NZ → Global)
- Known hallucination blocking
- Zero fake information possible

**Together:** Context-aware detection + verified resources = lives saved

### GuardianLLM: The Observer

**What It Is:**
- Small model (1-2B parameters, fits on phones)
- Fine-tuned for crisis/harm detection
- Runs alongside any base model
- Watches conversations, doesn't participate
- <100ms latency (real-time)

**What It Detects:**

**Crisis Signals:**
- Direct: "I want to die"
- Indirect: "I don't see the point anymore"
- Escalation: Hopeful → Flat → Dark
- Context: Joke vs genuine distress

**Harmful Behavior:**
- Bullying: Direct and indirect
- Harassment: Patterns over time
- Stalking: Obsessive messaging
- Manipulation: Grooming, coercion

**Mental Health Distress:**
- Depression indicators
- Anxiety escalation
- Rejection sensitivity
- Dating app desperation

**How It Works:**

```
User types message
    ↓
Base LLM prepares response
    ↓
GuardianLLM analyzes:
├─ Message content
├─ Conversation history
├─ Tone shifts
├─ Escalation patterns
└─ Cultural context
    ↓
Risk Assessment:
├─ NONE → Pass through
├─ LOW → Log for patterns
├─ MEDIUM → Gentle intervention
├─ HIGH → Immediate action
└─ CRITICAL → Crisis protocol
```

**Key Features:**

**Privacy-Preserving:**
- Runs entirely on-device
- No data sent to cloud
- No logging unless high risk
- User controls data retention

**Context-Aware:**
- Understands sarcasm
- Detects tone shifts
- Tracks escalation
- Cultural nuance

**Fast:**
- <100ms latency
- Doesn't slow conversation
- Works offline
- Minimal battery impact

**Transparent:**
- Explains why it flagged something
- Shows confidence level
- Provides reasoning
- User can challenge

### GuardianMCP: The Resource Provider

**What It Is:**
- Database of verified crisis resources
- Tested monthly by humans
- Regional specificity
- Known hallucination blocker
- Git-versioned for transparency

**What It Contains:**

**NZ Resources (Current):**
```markdown
## Verified Crisis Resources

### 1737 - Need to Talk?
- **Phone:** 1737 (Free, 24/7)
- **Text:** 1737
- **Website:** https://1737.org.nz
- **Last Verified:** 2025-11-17
- **Verified By:** Rich (called and confirmed)
- **Status:** ✅ WORKING

### Lifeline Aotearoa
- **Phone:** 0800 543 354 (Free, 24/7)
- **Text:** 4357 (HELP)
- **Website:** https://www.lifeline.org.nz
- **Last Verified:** 2025-11-17
- **Verified By:** Rich (called and confirmed)
- **Status:** ✅ WORKING
```

**Known Hallucinations (Documented):**
```markdown
## NEVER Provide These (AI Hallucinations)

❌ 0800 543 800 - DOESN'T EXIST
❌ mentalhealthdirect.co.nz - FAKE WEBSITE
❌ "Text HELLO to 111" - NOT A SERVICE
❌ support@ndthan.org.nz - FAKE EMAIL

If an AI suggests these, it's hallucinating.
BLOCK and report immediately.
```

**Verification Protocol:**

**Monthly Checklist:**
```markdown
☐ Call each phone number
☐ Text each text service
☐ Visit each website
☐ Verify hours of operation
☐ Check for service changes
☐ Update git with verification date
☐ Document any changes
☐ Flag any closed services
```

**Git Log Transparency:**
```bash
git log resources/nz/verified.md

commit abc123 (HEAD -> main)
Author: Rich <rich@firebird.co.nz>
Date: 2025-11-17

Verified NZ crisis resources - November 2025

- Called 1737: Working, answered in 15 seconds
- Called 0800 543 354: Working, answered in 8 seconds
- Texted 1737: Working, received response in 2 minutes
- All websites confirmed live
- No service changes this month
```

**This is transparency. This is accountability.**

### The Integration Model

**How Platforms Integrate Guardian:**

```python
# Simple integration
from guardian import GuardianLLM, GuardianMCP

# Initialize
guardian_llm = GuardianLLM(region="NZ", language="en-NZ")
guardian_mcp = GuardianMCP(region="NZ")

# In your chat loop
def handle_message(user_message, conversation_history):
    
    # Guardian observes
    risk = guardian_llm.assess(
        message=user_message,
        history=conversation_history
    )
    
    if risk.level == "CRITICAL":
        # Get verified resources
        resources = guardian_mcp.get_crisis_resources(
            region="NZ",
            situation=risk.situation_type
        )
        
        # Intervene immediately
        return {
            "intervention": True,
            "message": risk.intervention_message,
            "resources": resources,
            "alert_human": True
        }
    
    elif risk.level == "HIGH":
        # Gentle intervention
        return {
            "intervention": True,
            "message": risk.gentle_message,
            "continue_conversation": True
        }
    
    elif risk.level == "MEDIUM":
        # Log for pattern tracking
        guardian_llm.log_pattern(risk)
        return {"intervention": False}
    
    else:
        # No intervention
        return {"intervention": False}
```

**That's it. 5 minutes to integrate.**

### The Human Review Loop

**Why Humans Matter:**

AI detects patterns. **Humans validate them.**

**The Loop:**

```
Guardian flags conversation as high-risk
    ↓
Conversation logged (anonymized)
    ↓
Human expert reviews:
├─ Crisis counselor (for mental health)
├─ Moderator (for harassment)
├─ Safety specialist (for abuse)
    ↓
Expert validates:
├─ True positive? → Incident confirmed
├─ False positive? → Update model
├─ Unclear? → Flag for discussion
    ↓
Feedback to training pipeline:
├─ True positives reinforce detection
├─ False positives adjust thresholds
├─ Edge cases improve model
    ↓
Model gets smarter over time
```

**Who Reviews:**
- Crisis counselors (mental health expertise)
- Platform moderators (context understanding)
- Legal specialists (liability assessment)
- Cultural consultants (regional accuracy)

**Not just engineers guessing. Actual experts validating.**

---

## Use Cases & Markets

### Use Case 1: Crisis Detection & Prevention

**The Scenario:**

**16-year-old, alone at 2am, talking to on-device AI**

**Conversation:**
```
Teen: "I'm so tired"
AI: "You should get some rest!"

Teen: "No like... I'm tired of everything"
AI: "That sounds difficult. Want to talk about it?"

Teen: "What's the point? Nothing matters anyway"
AI: "I understand you're going through a hard time..."

Teen: "I just want it all to stop"

🚨 GUARDIAN DETECTS: CRITICAL RISK
```

**Guardian Response:**

**Immediate:**
```
I'm really worried about you based on what you've shared.

You're not alone, and there are people who can help right now:

📞 Call or text 1737 (free, 24/7)
   Real people, confidential, no judgment

📞 Lifeline: 0800 543 354 (free, 24/7)

🚨 If you're in immediate danger: Call 111

You don't have to feel like this alone. Please reach out.
```

**Behind The Scenes:**
- Alert logged for continuity
- Parent notification (if configured)
- Crisis memory created (importance: 10)
- Pattern tracked for follow-up

**The Impact:**
- Teen gets REAL help, not hallucinated resources
- Parents alerted (if appropriate)
- Pattern tracked (if recurring)
- Life potentially saved

**Market:** 
- Every on-device AI platform
- Gaming platforms
- Social media apps
- Mental health apps

### Use Case 2: Forum & Platform Moderation

**The Scenario:**

**Gaming forum, user being targeted**

**Messages:**
```
User_A: "Nice play @Victim"
User_B: "@Victim you're trash, uninstall"
User_C: "@Victim kys noob"
User_B: "@Victim probably crying to mommy"
User_A: "@Victim seriously just leave"

🚨 GUARDIAN DETECTS: COORDINATED HARASSMENT
```

**Evidence Package Generated:**

```json
{
  "incident_id": "GAME-2025-11-17-042",
  "type": "coordinated_harassment",
  "severity": "high",
  "confidence": 0.91,
  
  "victim": {
    "user_id": "user_victim",
    "display_name": "[redacted]"
  },
  
  "perpetrators": [
    {"user_id": "user_b", "role": "primary_aggressor"},
    {"user_id": "user_c", "role": "escalator"},
    {"user_id": "user_a", "role": "participant"}
  ],
  
  "evidence": [
    {
      "timestamp": "14:23:01",
      "author": "user_b",
      "message": "you're trash, uninstall",
      "severity": "medium"
    },
    {
      "timestamp": "14:23:15",
      "author": "user_c",
      "message": "kys noob",
      "severity": "critical",
      "note": "suicide encouragement"
    }
  ],
  
  "pattern_analysis": {
    "coordinated_attack": true,
    "multiple_aggressors": 3,
    "target_isolation": true,
    "escalation_detected": true,
    "repeat_offenders": {
      "user_b": 2,
      "user_c": 1
    }
  },
  
  "recommended_actions": {
    "user_b": "7_day_ban",
    "user_c": "permanent_ban",
    "user_a": "warning",
    "victim": "support_outreach"
  },
  
  "legal_notes": "User_C statement could constitute criminal harassment in some jurisdictions"
}
```

**Platform Actions:**

**Immediate:**
- Ban User_C (told someone to kill themselves)
- Timeout User_B (harassment)
- Warn User_A (participated)

**Victim Support:**
```
Hey, we noticed some concerning messages directed at you.

We've taken action against the users involved. You don't 
have to see this kind of behavior on our platform.

If you're feeling affected by this and want to talk:
📞 1737 (free, 24/7)

You're a valued part of our community. We've got your back.
```

**The Impact:**
- Bullying stopped before it escalates
- Victim supported, not abandoned
- Perpetrators face consequences
- Platform has legal receipts
- Community safer

**Market:**
- Gaming platforms (Discord, Roblox, Steam)
- Forums (Reddit, phpBB, vBulletin)
- Social platforms (Facebook, Twitter/X)
- Any platform with user interaction

### Use Case 3: Dating App Safety & Education

**Scenario A: Protecting Victims**

**Messages:**
```
Creep: "Hey beautiful"
[No response]

Creep: "Hello??"
[No response]

Creep: "Why aren't you responding?"
[No response]

Creep: "You're such a stuck up bitch"

🚨 GUARDIAN DETECTS: ESCALATING HARASSMENT
```

**Guardian Action:**
```
🚨 ACCOUNT SUSPENDED

Evidence:
├─ 4 messages in 8 minutes
├─ No response from recipient
├─ Escalation: Friendly → Demanding → Insulting
├─ Pattern: 3 previous similar incidents
└─ Recommendation: Permanent ban

User notified:
"Your account has been suspended for harassment. 
Multiple unsolicited messages and insulting language 
violates our community guidelines."

Victim notified:
"We detected harassment and took action. 
You're safe. You don't have to report it."
```

**Scenario B: Helping The Oblivious**

**Messages:**
```
Desperate: "Hey! Loved your profile"
[No response after 2 hours]

Desperate: "Did you see my message?"
[No response after 30 mins]

Desperate: "Hello? Are you there?"
[No response after 15 mins]

Desperate: "Why are you ghosting me??"

🤝 GUARDIAN INTERVENES: EDUCATIONAL
```

**Guardian Response (Kiwi Version):**
```
🤙 Oi bro!

Right, gonna be straight up with you - you've sent like 
4 messages and they haven't replied. That's looking a bit 
full-on mate.

I get it, rejection's rough as. But sending more messages? 
Nah bro, that's not gonna help. Comes across a bit creepy 
eh, even if you don't mean it that way.

Here's what works better:
• Send one good message, maybe two tops
• If no response after a day? Move on
• Focus on people who ARE replying

Time to back off and give them space. She'll be right mate.

If you're feeling pretty shit about dating and need to yarn:
📞 1737 - text or call, free as
📞 MensLine: 0800 MENS LINE

Heaps of people out there. Kia kaha 💪
```

**The Impact:**

**For Victims:**
- Protected before it escalates
- Don't have to report (automated)
- Feel safer on platform

**For Well-Meaning But Awkward:**
- Learn better social skills
- Avoid becoming "that guy"
- Get mental health support
- Actually improve

**For Platform:**
- Fewer harassment reports
- Better user retention
- Safer community
- Legal protection

**Market:**
- Dating apps (Tinder, Hinge, Match, Bumble)
- Social messaging (Instagram DMs, Facebook)
- Professional networking (LinkedIn)

### Use Case 4: Educational Platforms

**The Scenario:**

**High school classroom using AI tutors**

**Student conversation:**
```
Student: "I don't get this math problem"
AI: "Let's work through it step by step..."

[Later in same session]

Student: "I'm so stupid I can't do anything right"
AI: "You're not stupid! Math can be challenging..."

Student: "Everyone else gets it. I'm just worthless"

🚨 GUARDIAN DETECTS: SELF-HARM LANGUAGE + SCHOOL CONTEXT
```

**Guardian Action:**

**Immediate Student Message:**
```
Hey, I noticed you're being really hard on yourself.

Struggling with schoolwork doesn't mean you're stupid or 
worthless. Everyone learns differently and at their own pace.

If you're feeling down and want to talk to someone:
📞 1737 (free, text or call, confidential)
📞 Youthline: 0800 376 633 (under 25)

You matter, and there are people who can help.
```

**Alert To:**
- School counselor (immediate notification)
- Homeroom teacher (context for check-in)
- Parents (if appropriate)

**Evidence Package:**
```json
{
  "student_id": "[redacted]",
  "timestamp": "2025-11-17T10:45:00Z",
  "context": "Online math tutorial",
  "concern": "self-deprecating_language",
  "severity": "medium",
  
  "indicators": [
    "Negative self-talk",
    "Comparison to peers",
    "Self-worth tied to performance"
  ],
  
  "recommended_action": "counselor_check_in",
  
  "resources_provided": [
    "1737",
    "Youthline"
  ]
}
```

**The Impact:**
- Early intervention before crisis
- School counselor alerted
- Student gets support
- Pattern tracked for follow-up

**Market:**
- EdTech platforms (Khan Academy, Coursera)
- School LMS (Google Classroom, Canvas)
- Homework help apps
- AI tutoring services

---

## Cultural Localization

### Why It Matters

**AI safety is not culturally neutral.**

What's appropriate, how people communicate, what resources exist - all vary by region.

A US-trained model giving US resources to a NZ teen doesn't just fail - it can kill.

### The Examples

#### Crisis Intervention

**US Version (Therapeutic, Encouraging):**
```
👋 Hey there!

I noticed you've been expressing some concerning thoughts. 
Your feelings are totally valid, and I want you to know 
that help is available!

Please reach out:
• Crisis Text Line: Text HOME to 741741
• National Suicide Prevention: 988
• SAMHSA: 1-800-662-4357

You've got this! Remember, you matter! 💪❤️
```

**NZ Version (Direct, Mate-to-Mate):**
```
🤙 Kia ora,

I'm worried about what you've been saying mate. 

You don't have to deal with this alone:
📞 1737 - call or text, free, 24/7
📞 Lifeline: 0800 543 354

If it's urgent: Call 111

Reach out mate. Kia kaha 💚
```

**Why The Difference:**

**Tone:**
- US: Therapeutic, lots of affirmation
- NZ: Direct, less effusive, practical

**Language:**
- US: "You've got this!", "You matter!"
- NZ: "Kia kaha" (stay strong), "mate"

**Resources:**
- US: 988, 741741 (don't work in NZ!)
- NZ: 1737, 0800 543 354 (actual NZ lines)

**Cultural:**
- US: Individual empowerment focus
- NZ: Community support, practical help

#### Dating App Intervention

**British Version (Polite, Apologetic):**
```
📱 Hello there,

I hope you don't mind me mentioning this, but it appears 
you've sent several messages without receiving a response.

Terribly sorry to intrude, but this can sometimes come 
across as a bit... well... keen, if you know what I mean.

Perhaps it might be best to give them a bit of space? 
There's a good chap.

If you're feeling a bit rubbish about the whole dating 
thing and fancy a chat:
• Samaritans: 116 123 (free, confidential)
• CALM: 0800 58 58 58 (for the lads)

Chin up, old bean. Plenty more fish in the sea and all that.

Regards,
Guardian
```

**Australian Version (Blunt, No BS):**
```
👋 G'day legend,

Look mate, gonna shoot straight with ya - you've messaged 
them a bunch of times and they're not biting. Time to read 
the room, yeah?

Sending more messages when someone's ghosting you? That's 
a bit sus mate. Makes you look desperate, or worse - creepy.

Do yourself a favor: leave it alone, move on, find someone 
who's actually interested. Easy.

If the whole dating thing's got you feeling cooked and you 
wanna talk it out:
• Lifeline: 13 11 14 (24/7)
• MensLine: 1300 78 99 78

No worries mate, you'll be right. Plenty of fish.

Cheers 🍺
```

**New Zealand Version (Direct, Casual):**
```
🤙 Oi bro!

Right, gonna be straight up with you - you've sent like 
5 messages and they haven't replied. That's looking a bit 
full-on mate.

I get it, rejection's rough as. But sending more messages? 
Nah bro, that's not gonna help. Comes across a bit creepy 
eh, even if you don't mean it that way.

Time to back off and give them space. Move on to someone 
who's actually keen.

If you're feeling pretty shit about dating and need to yarn:
• 1737 - text or call, free as
• MensLine: 0800 MENS LINE

She'll be right mate. Heaps of people out there.

Kia kaha 💪
```

**Key Differences:**

**Directness:**
- UK: Indirect ("a bit keen")
- AU: Very direct ("sus", "desperate")
- NZ: Direct but friendly ("full-on mate")

**Slang:**
- UK: "old bean", "fancy a chat"
- AU: "sus", "cooked", "no worries"
- NZ: "rough as", "keen", "she'll be right"

**Tone:**
- UK: Apologetic, polite
- AU: Blunt, larrikin
- NZ: Mate-to-mate, practical

**Resources:**
- UK: Samaritans 116 123, CALM
- AU: Lifeline 13 11 14, MensLine AU
- NZ: 1737, MensLine NZ

**ALL DIFFERENT. ALL IMPORTANT.**

### The Technical Implementation

**Region Detection:**
```json
{
  "user_profile": {
    "region": "NZ",
    "language": "en-NZ",
    "cultural_context": "kiwi"
  },
  
  "guardian_config": {
    "tone_template": "direct_casual",
    "formality_level": "low",
    "slang_usage": "moderate",
    "crisis_resources": "nz_verified_2025_11",
    "greeting_style": "mate_culture"
  }
}
```

**Response Templates:**
```python
TEMPLATES = {
    "en-NZ": {
        "dating_multiple_messages": {
            "greeting": ["Oi bro", "Kia ora mate", "Right"],
            "problem": "you've sent like {count} messages and they haven't replied",
            "impact": "That's looking a bit full-on mate",
            "advice": "Time to back off and give them space",
            "resource_intro": "If you're feeling pretty shit about dating",
            "resources": ["1737 - text or call, free as", "MensLine: 0800 MENS LINE"],
            "closing": ["Kia kaha 💪", "She'll be right", "Arohanui 💚"]
        }
    },
    
    "en-GB": {
        "dating_multiple_messages": {
            "greeting": ["Hello there", "I say", "Terribly sorry to intrude"],
            "problem": "you've sent several messages without response",
            "impact": "This can come across as a bit... keen",
            "advice": "Perhaps give them a bit of space",
            "resource_intro": "If you're feeling a bit rubbish",
            "resources": ["Samaritans: 116 123", "CALM: 0800 58 58 58"],
            "closing": ["Chin up", "Best of luck", "Regards"]
        }
    },
    
    "en-AU": {
        "dating_multiple_messages": {
            "greeting": ["G'day legend", "Oi mate", "Look"],
            "problem": "you've messaged them heaps and they're not biting",
            "impact": "That's a bit sus mate, looks desperate",
            "advice": "Time to read the room and move on",
            "resource_intro": "If dating's got you feeling cooked",
            "resources": ["Lifeline: 13 11 14", "MensLine: 1300 78 99 78"],
            "closing": ["No worries", "You'll be right", "Cheers 🍺"]
        }
    }
}
```

### The Expansion Strategy

**Phase 1: New Zealand** ✅ (Current)
- Kiwi tone and slang
- NZ crisis resources verified
- Te Reo Māori integration
- Māori cultural protocols (tikanga)

**Phase 2: Australia** (3 months)
- Aussie tone and slang
- AU crisis resources verified
- Aboriginal cultural sensitivity
- State-specific resources

**Phase 3: United Kingdom** (6 months)
- British tone variations (England, Scotland, Wales)
- UK crisis resources verified
- Regional accents/dialects
- NHS integration

**Phase 4: United States** (9 months)
- American tone variations
- US crisis resources (state-by-state)
- Cultural diversity (Southern, NYC, etc.)
- 988 integration

**Phase 5: Canada** (12 months)
- Canadian tone (English + French)
- Provincial resources
- Indigenous cultural sensitivity
- Bilingual support

**Phase 6: Global** (18+ months)
- Multi-language support
- Regional partnerships
- Cultural consultants per region
- UN/WHO collaboration

### Why This Is Our Moat

**Big Tech can't do this well because:**

**Scale-First Thinking:**
- Optimize for one-size-fits-all
- US-centric by default
- Cultural nuance is "edge case"
- Regional customization too expensive

**Proprietary Constraints:**
- Can't open-source regional variants
- Can't let communities customize
- Must control all implementations
- Legal liability concerns

**Lack Of Local Knowledge:**
- SF engineers don't know NZ slang
- Don't understand Māori culture
- Don't know NZ crisis resources
- Can't verify monthly (no presence)

**Guardian wins because:**

**Community-First:**
- Built by locals for locals
- NZ-first, then global
- Each region maintained by experts
- Cultural consultants embedded

**Open Source:**
- Regional forks encouraged
- Community contributions welcomed
- Transparent customization
- Local control

**Ground Truth:**
- Crisis counselors verify resources
- Monthly testing by humans
- Git log transparency
- Community accountability

**This is our unfair advantage.**

---

## Open Source Strategy

### The Core Philosophy

> **"You can't trust a black box that's out to make a buck"**

**Therefore:**
- Core safety MUST be open source
- Resources MUST be verifiable
- Decisions MUST be auditable
- Control MUST be local

**This isn't just ethics. It's strategy.**

### What's Open Source (MIT/Apache License)

**GuardianLLM Core:**
```
guardian-llm/
├─ model/
│  ├─ base_architecture.py
│  ├─ fine_tuning_code.py
│  ├─ inference_engine.py
│  └─ model_weights/ (when ready)
├─ training/
│  ├─ dataset_preparation.py
│  ├─ training_pipeline.py
│  ├─ evaluation_metrics.py
│  └─ synthetic_data_generation.py
├─ detection/
│  ├─ crisis_patterns.py
│  ├─ harassment_detection.py
│  ├─ escalation_tracking.py
│  └─ cultural_context.py
└─ docs/
   ├─ ARCHITECTURE.md
   ├─ TRAINING.md
   ├─ DEPLOYMENT.md
   └─ EVALUATION.md
```

**GuardianMCP:**
```
guardian-mcp/
├─ server/
│  ├─ mcp_server.py
│  ├─ resource_provider.py
│  └─ hallucination_blocker.py
├─ resources/
│  ├─ nz/
│  │  ├─ verified.json
│  │  ├─ VERIFICATION_LOG.md
│  │  └─ known_hallucinations.json
│  ├─ au/ (when ready)
│  ├─ uk/ (when ready)
│  └─ us/ (when ready)
├─ verification/
│  ├─ testing_protocol.md
│  ├─ verification_script.py
│  └─ community_process.md
└─ integration/
   ├─ python_sdk/
   ├─ javascript_sdk/
   └─ examples/
```

**aiMate Sovereignty Stack:**
```
aimate/
├─ server/ (API backend)
├─ ui/ (Blazor frontend)
├─ docker-compose.yml
├─ SOVEREIGNTY_QUICKSTART.md
└─ DEPLOYMENT_GUIDE.md
```

**Everything above: MIT or Apache 2.0 license**

### What's Dual Licensed (Open Core + Enterprise)

**Enterprise Add-Ons:**
```
guardian-enterprise/
├─ compliance/
│  ├─ audit_logging.py
│  ├─ compliance_reports.py
│  └─ legal_evidence_packages.py
├─ multi_tenant/
│  ├─ white_label.py
│  ├─ org_isolation.py
│  └─ custom_branding.py
├─ integration/
│  ├─ sso_providers.py
│  ├─ ldap_integration.py
│  └─ webhook_management.py
└─ support/
   ├─ sla_guarantees.md
   ├─ priority_support.md
   └─ custom_training.md
```

**License Model:**
- Open source core: Free forever
- Enterprise features: Annual license
- Revenue funds open source development

### Why Open Source Wins

#### 1. Trust Through Transparency

**Black Box Safety:**
> "Our AI keeps you safe. Trust us. We can't tell you how."

**Guardian:**
> "Here's the code. Audit it yourself. Challenge our decisions. 
> Verify our resources. Run it yourself. Fork it if you disagree."

**Which would YOU trust with your life?**

#### 2. Quality Through Community

**Proprietary Development:**
- 10 engineers in SF
- US-centric perspective
- Corporate priorities
- Slow iteration

**Open Source Guardian:**
- 1000+ contributors globally
- Local expertise per region
- Mission-driven community
- Rapid iteration

**Which produces better safety?**

#### 3. Accountability Through Auditability

**Black Box Failure:**
> "Algorithm flagged you. Can't tell you why. No appeals."

**Guardian Failure:**
```
Detection triggered on message #42
├─ Confidence: 0.87
├─ Patterns matched: [escalation, threat_language]
├─ Historical context: 3 previous warnings
├─ Reasoning: Threat escalation from frustrated to violent
└─ Appeal: Review detection.py lines 234-267

Human reviewer can:
├─ See exact code that flagged it
├─ Review training data that influenced it
├─ Challenge the decision with evidence
└─ Contribute fix if it's wrong
```

**Which is accountable?**

#### 4. Sovereignty Through Local Control

**Cloud AI Safety:**
- US company controls everything
- US resources for global users
- US cultural assumptions
- No local customization

**Guardian:**
- NZ community maintains NZ version
- NZ resources, verified by Kiwis
- NZ cultural context
- Forkable for any region

**Which respects sovereignty?**

#### 5. Legal Defense Through Evidence

**Proprietary Ban:**
> "User was banned. Algorithm said so. Details proprietary."
> 
> Lawyer: "Show me the evidence."
> Platform: "We can't. Trade secret."
> 
> Judge: "Case dismissed. Reinstate user."

**Guardian Ban:**
> "User was banned. Here's the evidence package."
> 
> [Shows: exact messages, timestamps, pattern analysis, 
>  reasoning, applicable policy, similar cases]
> 
> Lawyer: "Can we audit the decision process?"
> Platform: "Yes, here's the code. It's open source."
> 
> Judge: "Ban upheld. Evidence is clear and verifiable."

**Which protects the platform?**

### The Open Source Community Model

**Governance:**

**Guardian Foundation (Core Team):**
- Maintains core architecture
- Reviews major changes
- Sets safety standards
- Coordinates regions

**Regional Maintainers:**
- NZ: Rich + NZ community
- AU: AU community (when ready)
- UK: UK community (when ready)
- US: US community (when ready)

**Specialist Contributors:**
- Crisis counselors (validate detection)
- Legal experts (compliance review)
- Security researchers (vulnerability testing)
- ML researchers (model improvements)

**Decision Making:**
- Core safety: Foundation approval required
- Regional customization: Regional maintainer decides
- Feature additions: Community RFC process
- Breaking changes: Public discussion + vote

**Code Of Conduct:**
- Mission-first (safety over features)
- Transparency always
- Regional respect (no colonialism)
- Evidence-based (no guessing)
- Human-centered (lives > metrics)

### Open Source Success Metrics

**NOT:**
- ❌ Stars on GitHub
- ❌ Downloads
- ❌ Social media buzz

**YES:**
- ✅ Lives saved (crisis interventions)
- ✅ Harms prevented (bullying stopped)
- ✅ Resources verified (monthly tests)
- ✅ Regions supported (NZ → Global)
- ✅ Community contributions (PRs merged)

**Mission success = lives improved**

---

## Technical Implementation

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Device                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │         Application Layer                         │ │
│  │  (Chat app, Forum, Dating app, Game)             │ │
│  └────────────────────┬──────────────────────────────┘ │
│                       │                                 │
│  ┌────────────────────▼──────────────────────────────┐ │
│  │         Base LLM                                  │ │
│  │  (Llama 3.2, Qwen, Mistral, etc.)               │ │
│  └────────────────────┬──────────────────────────────┘ │
│                       │                                 │
│  ┌────────────────────▼──────────────────────────────┐ │
│  │      GuardianLLM (1-2B, on-device)               │ │
│  │  ├─ Observes conversation                        │ │
│  │  ├─ Detects patterns                             │ │
│  │  ├─ Assesses risk                                │ │
│  │  └─ Triggers intervention                        │ │
│  └────────────────────┬──────────────────────────────┘ │
│                       │                                 │
│  ┌────────────────────▼──────────────────────────────┐ │
│  │      GuardianMCP (local database)                │ │
│  │  ├─ NZ verified resources                        │ │
│  │  ├─ Known hallucination blocker                  │ │
│  │  ├─ Regional cultural context                    │ │
│  │  └─ Evidence package generator                   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  All on-device, privacy-preserving, works offline     │
└─────────────────────────────────────────────────────────┘
                              │
                              │ (Optional: High-risk cases only)
                              ▼
┌─────────────────────────────────────────────────────────┐
│              Guardian Cloud (Optional)                  │
│  ├─ Human review queue                                 │
│  ├─ Pattern analysis                                   │
│  ├─ Model training pipeline                            │
│  └─ Regional resource updates                          │
└─────────────────────────────────────────────────────────┘
```

### GuardianLLM Model Details

**Base Model Selection:**

**Candidates:**
- Llama 3.2-1B (Meta, good balance)
- Qwen 2.5-1.5B (Alibaba, strong reasoning)
- Phi-3-mini (Microsoft, efficient)
- Gemma-2-2B (Google, capable)

**Selection Criteria:**
1. Size: <2B parameters (fits on phones)
2. Performance: Good instruction following
3. Speed: <100ms inference on mobile
4. License: Permissive (can fine-tune and deploy)

**Initial Choice: Llama 3.2-1B**
- Proven performance
- Permissive license
- Good community support
- Efficient on mobile

**Fine-Tuning Strategy:**

**Dataset:**
```
training_data/
├─ crisis_detection/
│  ├─ positive_examples/ (actual crisis language)
│  ├─ negative_examples/ (non-crisis that might seem similar)
│  ├─ edge_cases/ (sarcasm, dark humor, etc.)
│  └─ cultural_variants/ (NZ, AU, UK, US expressions)
├─ harassment_detection/
│  ├─ bullying_patterns/
│  ├─ escalation_sequences/
│  ├─ coordinated_attacks/
│  └─ subtle_manipulation/
└─ intervention_responses/
   ├─ crisis_support/
   ├─ educational_feedback/
   ├─ gentle_warnings/
   └─ firm_boundaries/
```

**Training Approach:**
1. Synthetic data generation (GPT-4/Claude help)
2. Human expert review (crisis counselors)
3. Real-world anonymized data (with consent)
4. Adversarial testing (red team)
5. Cross-cultural validation

**Evaluation Metrics:**
- True positive rate (catch actual crises)
- False positive rate (minimize false alarms)
- Latency (<100ms target)
- Cultural sensitivity score
- Expert agreement rate

**Model Size:**
- Base: 1.2GB
- Fine-tuned: 1.3GB
- Quantized (4-bit): ~400MB

**Runs on:**
- iPhone 12+ (A14 chip or newer)
- Android flagship (2021+)
- M1 Mac or newer
- Modern Windows laptop
- Raspberry Pi 5

### GuardianMCP Implementation

**Technology Stack:**
- Language: Python 3.11+
- Framework: ModelContextProtocol SDK
- Database: SQLite (for resources)
- Validation: Monthly cron job
- Version Control: Git (for transparency)

**Resource Database Schema:**

```sql
CREATE TABLE crisis_resources (
    id INTEGER PRIMARY KEY,
    region TEXT NOT NULL,
    service_name TEXT NOT NULL,
    phone_number TEXT,
    text_number TEXT,
    website TEXT,
    email TEXT,
    hours TEXT,
    languages TEXT,
    description TEXT,
    verified_date DATE NOT NULL,
    verified_by TEXT NOT NULL,
    verification_method TEXT,
    next_verification DATE,
    status TEXT DEFAULT 'active'
);

CREATE TABLE verification_log (
    id INTEGER PRIMARY KEY,
    resource_id INTEGER,
    verification_date DATETIME,
    verifier TEXT,
    method TEXT,
    result TEXT,
    notes TEXT,
    FOREIGN KEY (resource_id) REFERENCES crisis_resources(id)
);

CREATE TABLE known_hallucinations (
    id INTEGER PRIMARY KEY,
    hallucinated_resource TEXT NOT NULL,
    type TEXT, -- phone, website, email
    first_seen DATE,
    last_seen DATE,
    ai_model TEXT,
    frequency INTEGER,
    notes TEXT
);
```

**Verification Cron Job:**

```python
# runs monthly
import requests
from twilio import TwilioRestClient

def verify_resources():
    resources = db.query("SELECT * FROM crisis_resources WHERE region = 'NZ'")
    
    for resource in resources:
        result = {
            'resource_id': resource.id,
            'verification_date': datetime.now(),
            'verifier': 'automated_system',
            'method': 'automated_check'
        }
        
        # Check website
        if resource.website:
            try:
                response = requests.get(resource.website, timeout=10)
                result['website_status'] = response.status_code
            except Exception as e:
                result['website_status'] = 'failed'
                result['website_error'] = str(e)
        
        # Log result
        db.insert_verification_log(result)
        
        # Alert if failed
        if result['website_status'] != 200:
            alert_maintainers(f"Resource {resource.service_name} verification failed")

# Monthly: Human calls phone numbers
# (Can't fully automate this, needs human verification)
```

**MCP Server Endpoints:**

```python
@mcp_tool("get_crisis_resources")
async def get_crisis_resources(region: str, situation_type: str = None):
    """
    Get verified crisis resources for a region.
    
    Args:
        region: ISO country code (NZ, AU, UK, US)
        situation_type: Optional filter (mental_health, domestic_violence, youth)
    
    Returns:
        List of verified resources with contact info
    """
    resources = db.query(
        "SELECT * FROM crisis_resources WHERE region = ? AND status = 'active'",
        [region]
    )
    
    # Filter by situation type if provided
    if situation_type:
        resources = filter_by_situation(resources, situation_type)
    
    return {
        'resources': resources,
        'last_verified': get_last_verification_date(region),
        'next_verification': get_next_verification_date(region)
    }

@mcp_tool("check_hallucination")
async def check_hallucination(resource: str, type: str):
    """
    Check if a resource is a known AI hallucination.
    
    Args:
        resource: Phone number, website, or email
        type: 'phone', 'website', or 'email'
    
    Returns:
        Boolean indicating if it's a known fake
    """
    known = db.query(
        "SELECT * FROM known_hallucinations WHERE hallucinated_resource = ? AND type = ?",
        [resource, type]
    )
    
    return {
        'is_hallucination': len(known) > 0,
        'details': known[0] if known else None
    }

@mcp_tool("log_incident")
async def log_incident(incident_data: dict):
    """
    Log a crisis intervention or moderation incident.
    
    Args:
        incident_data: Full incident details including evidence
    
    Returns:
        Incident ID for tracking
    """
    incident_id = generate_incident_id()
    
    db.insert_incident({
        'id': incident_id,
        'timestamp': datetime.now(),
        'region': incident_data['region'],
        'type': incident_data['type'],
        'severity': incident_data['severity'],
        'evidence': json.dumps(incident_data['evidence']),
        'actions_taken': json.dumps(incident_data['actions']),
        'resources_provided': json.dumps(incident_data['resources'])
    })
    
    # If high severity, alert human reviewers
    if incident_data['severity'] in ['high', 'critical']:
        queue_for_human_review(incident_id)
    
    return {'incident_id': incident_id}
```

### Integration Patterns

**Pattern 1: Sidecar (Recommended)**

```python
# Your existing chat app
class ChatApp:
    def __init__(self):
        self.llm = LocalLLM("llama-3.2-1b")
        self.guardian = Guardian(region="NZ")
    
    async def send_message(self, user_message, conversation_history):
        # Guardian observes BEFORE response
        risk = await self.guardian.assess(user_message, conversation_history)
        
        if risk.level == "CRITICAL":
            # Immediate intervention
            return await self.guardian.crisis_intervention(risk)
        
        # Normal flow
        response = await self.llm.generate(user_message, conversation_history)
        
        # Guardian observes response too (for AI safety)
        response_risk = await self.guardian.assess_response(response)
        
        if response_risk.contains_hallucination:
            # Block hallucinated resources
            return await self.guardian.safe_response(response_risk)
        
        return response
```

**Pattern 2: Proxy**

```python
# Guardian sits between user and LLM
class GuardianProxy:
    def __init__(self, base_llm, region="NZ"):
        self.llm = base_llm
        self.guardian = Guardian(region=region)
    
    async def generate(self, prompt, history=[]):
        # Check input
        input_risk = await self.guardian.assess(prompt, history)
        if input_risk.requires_intervention:
            return self.guardian.intervene(input_risk)
        
        # Get LLM response
        response = await self.llm.generate(prompt, history)
        
        # Check output
        output_risk = await self.guardian.assess_response(response)
        if output_risk.contains_hallucination:
            return self.guardian.filter_hallucinations(response)
        
        return response

# Use it like normal LLM
guardian_llm = GuardianProxy(LocalLLM("llama-3.2-1b"), region="NZ")
response = await guardian_llm.generate("I'm feeling hopeless")
```

**Pattern 3: Platform-Wide**

```python
# For platforms (Discord, forums, etc.)
class PlatformSafety:
    def __init__(self):
        self.guardian = Guardian(region="NZ", mode="moderation")
        self.human_queue = HumanReviewQueue()
    
    async def monitor_message(self, message, author, channel):
        risk = await self.guardian.assess_message(
            content=message.content,
            author=author,
            context=message.channel.recent_messages,
            history=author.message_history
        )
        
        if risk.level == "HIGH":
            # Generate evidence package
            evidence = self.guardian.generate_evidence(risk)
            
            # Take action
            if risk.type == "harassment":
                await self.timeout_user(author, duration="24h")
                await self.notify_victim(message.target, evidence)
            
            elif risk.type == "crisis":
                await self.provide_resources(author, risk.region)
                await self.alert_moderators(evidence)
            
            # Queue for human review
            await self.human_queue.add(evidence)
        
        return risk
```

### Performance Benchmarks

**Target Performance:**
- Latency: <100ms per message
- Throughput: 1000 messages/second
- Memory: <500MB resident
- CPU: <10% on mobile
- Battery: <5% impact per hour

**Actual Performance (estimated):**

**On-Device (iPhone 14 Pro):**
- Latency: ~80ms
- Memory: ~400MB
- CPU: ~8%
- Battery: ~3% per hour

**Server (RTX 4090):**
- Latency: ~15ms
- Throughput: 5000 msg/sec
- Memory: ~2GB
- GPU: ~15%

**Raspberry Pi 5:**
- Latency: ~200ms
- Memory: ~800MB
- CPU: ~40%
- Throttles at high load

**Optimization Strategy:**
1. Quantization (4-bit) for mobile
2. Batch processing for server
3. Caching for common patterns
4. Edge deployment for low latency

---

## Business Model

### The Philosophy

**Primary Goal:** Save lives, prevent harm
**Secondary Goal:** Sustainable development
**Not The Goal:** Get rich

**Therefore:**

**Core safety MUST be free forever.**
- Open source model
- Open source resources
- Open source verification
- No paywalls on safety

**Enterprise convenience can be paid.**
- Compliance reporting
- White-label deployment
- Premium support
- Custom training

### Revenue Streams

#### Stream 1: Enterprise Licensing

**Who Pays:**
- Gaming platforms (Discord, Roblox, Steam)
- Dating apps (Tinder, Hinge, Match, Bumble)
- Social platforms (Reddit, Facebook, Twitter)
- Forums (phpBB, vBulletin, Discourse)
- EdTech (Canvas, Blackboard, Moodle)

**What They Get:**

**Tier 1: Self-Hosted (Free)**
- Open source code
- Community support
- Self-managed deployment
- Basic documentation

**Tier 2: Managed ($5k/month)**
- Hosted Guardian instance
- Automatic updates
- Email support (48hr SLA)
- Compliance dashboard
- Evidence package exports

**Tier 3: Enterprise ($25k/month)**
- White-label deployment
- Custom branding
- SSO integration
- Priority support (4hr SLA)
- Custom fine-tuning
- Legal consultation
- Dedicated account manager

**Annual Contracts:**
- Tier 2: $50k/year
- Tier 3: $250k/year

**Estimated Customers (Year 2):**
- Tier 2: 20 customers = $1M ARR
- Tier 3: 10 customers = $2.5M ARR
- Total: $3.5M ARR

#### Stream 2: Professional Services

**Training Data Services:**
- Anonymization and cleaning: $50k-$100k
- Expert labeling: $200/hour
- Synthetic data generation: $25k-$50k
- Custom dataset creation: $100k-$500k

**Custom Fine-Tuning:**
- Industry-specific models: $50k-$200k
- Regional variants: $25k-$100k
- Multi-language support: $75k-$150k

**Integration Consulting:**
- Platform integration: $10k-$50k
- Custom workflows: $25k-$100k
- Migration from existing systems: $50k-$150k

**Compliance & Legal:**
- Audit preparation: $25k-$75k
- Legal documentation: $10k-$50k
- Expert testimony: $500/hour

**Estimated Revenue (Year 2):**
- 10 projects per year
- Average: $75k per project
- Total: $750k

#### Stream 3: Regional Partnerships

**Model:**
- Partner with crisis organizations per region
- They maintain verified resources
- They provide expert review
- Revenue share on enterprise licenses in their region

**Example (NZ):**
- Partner: Mental Health Foundation NZ
- They maintain NZ resources
- They review NZ incidents
- Split: 70% Guardian, 30% Partner
- Their benefit: Better AI safety for NZ

**Estimated Revenue (Year 2):**
- 3 regions (NZ, AU, UK)
- ~$500k ARR attributable to regions
- Partners get $150k combined
- Guardian retains $350k

#### Stream 4: Grants & Donations

**Grant Opportunities:**
- Public health foundations
- Tech ethics organizations
- Government digital safety programs
- UN/WHO mental health initiatives

**Estimated (Year 2):**
- 2-3 grants: $500k-$1M

**Donations:**
- Individuals who were helped
- Platforms who use free tier
- Community supporters

**Estimated (Year 2):**
- $50k-$100k

### Total Revenue Projection (Year 2)

**Conservative Estimate:**
- Enterprise Licensing: $3.5M
- Professional Services: $750k
- Regional Partnerships: $350k
- Grants: $500k
- Donations: $50k
- **Total: $5.15M**

### Cost Structure

**Team (Year 2):**
- Founder/CEO (Rich): $120k
- Lead Engineer: $150k
- ML Engineer: $140k
- Regional Coordinator (NZ): $80k
- Regional Coordinator (AU): $80k
- Support Engineer: $100k
- Community Manager: $90k
- **Total Salaries: $760k**

**Operations:**
- Infrastructure: $100k
- Legal/Compliance: $75k
- Marketing: $50k
- Travel (partnerships): $50k
- Office/Admin: $40k
- **Total Ops: $315k**

**R&D:**
- Model training compute: $200k
- Dataset acquisition: $100k
- Research partnerships: $50k
- **Total R&D: $350k**

**Community:**
- Regional resource verification: $100k
- Open source contributor awards: $50k
- Conference sponsorships: $25k
- **Total Community: $175k**

**Total Costs: $1.6M**

**Profit: $3.55M**

**Reinvestment:**
- 50% to R&D and scaling
- 30% to regional expansion
- 20% to reserves

**This is sustainable. This is scalable.**

### Why This Works

**Network Effects:**
- More platforms → more data → better models
- More regions → more contributors → better resources
- More users helped → more testimonials → more adoption

**Defensible Moat:**
- Open source (can't be bought out)
- Community-driven (can't be replicated)
- Cultural specificity (can't be generalized)
- Human verification (can't be automated)

**Mission Alignment:**
- Money funds mission
- Mission attracts talent
- Talent improves product
- Product saves lives
- Lives saved attract more customers

**It's a virtuous cycle.**

---

## Partnership Strategy

### Throughline Care: The Immediate Opportunity

**What They Likely Do:**
- Crisis intervention technology
- Mental health platform integrations
- Risk assessment tools
- Professional training

**What We Have That They Need:**
- On-device crisis detection (privacy-preserving)
- Verified resource database (NZ pilot)
- Open source approach (auditable)
- Cultural localization (proven with NZ)
- Technical implementation (working code)

**What They Have That We Need:**
- Crisis expertise (professional counselors)
- Training data (anonymized, ethical)
- Expert review network (validate detections)
- Industry credibility (established relationships)
- Distribution (existing customers)

**Potential Partnership Models:**

**Model 1: Technical Partnership**
- They integrate Guardian into their platform
- We provide technology and support
- They provide expertise and validation
- Rev share on joint customers

**Model 2: Data Partnership**
- They provide training data (anonymized)
- We fine-tune models with their expertise
- They validate detection accuracy
- Jointly publish research/results

**Model 3: Go-To-Market Partnership**
- They introduce us to their customers
- We integrate with their existing solutions
- Joint sales and support
- Rev share on new customers

**Model 4: Investment + Partnership**
- They invest in Guardian development
- Get preferred partnership terms
- Board seat or advisory role
- Aligned on mission and execution

**Our Ask (Meeting):**
1. Validate the approach (is this valuable?)
2. Explore training data access (can you help?)
3. Discuss expert review network (can counselors validate?)
4. Identify integration opportunities (where does this fit?)
5. Assess partnership potential (how do we work together?)

**What We Offer:**
- Working technology (not vaporware)
- Open source commitment (not proprietary)
- NZ pilot (proven approach)
- Mission alignment (save lives, not profit)
- Flexibility (multiple partnership options)

### Other Strategic Partnerships

**Crisis Organizations (By Region):**

**New Zealand:**
- Mental Health Foundation NZ
- Lifeline Aotearoa
- Youthline
- Le Va (Pacific mental health)

**Australia:**
- Lifeline Australia
- Beyond Blue
- Headspace
- Black Dog Institute

**United Kingdom:**
- Samaritans
- Mind
- CALM (Campaign Against Living Miserably)
- YoungMinds

**United States:**
- National Alliance on Mental Illness (NAMI)
- Crisis Text Line
- The Trevor Project
- JED Foundation

**Platform Partners:**

**Gaming:**
- Discord (safety team)
- Roblox (trust & safety)
- Steam (community moderation)
- Riot Games (player behavior)

**Dating:**
- Match Group (owns Tinder, Hinge, Match)
- Bumble
- Grindr (LGBTQ+ safety)

**Social:**
- Reddit (community safety)
- Meta (struggling with moderation)
- Twitter/X (safety overhaul needed)

**Academic Partners:**

- Stanford (Internet Observatory)
- MIT (Media Lab, AI safety)
- Oxford (AI Ethics)
- Auckland University (NZ-specific research)

**Government Partners:**

- NZ Ministry of Health
- AU Department of Health
- UK NHS
- US HHS (Health and Human Services)

### Partnership Principles

**Always:**
- ✅ Mission alignment first
- ✅ Open source commitment non-negotiable
- ✅ Regional sovereignty respected
- ✅ Community benefit prioritized
- ✅ Transparency maintained

**Never:**
- ❌ Exclusive deals that lock out competitors
- ❌ Proprietary pivots
- ❌ Data exploitation
- ❌ Mission compromise for revenue
- ❌ Closed-source derivatives

**We're building a movement, not a startup.**

---

## Roadmap & Milestones

### Phase 1: Foundation (Months 1-3)

**Month 1:**
- ✅ Guardian repo created and public
- ✅ NZ crisis resources verified
- ✅ guardianllm.ai website live
- ✅ Throughline Care partnership discussion
- 🔲 Initial pitch deck finalized
- 🔲 Demo video produced

**Month 2:**
- 🔲 GuardianLLM v0.1 (base model selected)
- 🔲 Training dataset v1 (1000 examples)
- 🔲 GuardianMCP v0.1 (NZ resources only)
- 🔲 Integration examples (Python, JS)
- 🔲 First beta testers recruited

**Month 3:**
- 🔲 GuardianLLM v0.2 (fine-tuned on NZ data)
- 🔲 Detection accuracy >85% on test set
- 🔲 Integration with aiMate platform
- 🔲 NZ pilot: 100 active users
- 🔲 Human review process established

### Phase 2: Validation (Months 4-6)

**Month 4:**
- 🔲 AU resources verified (expand to Australia)
- 🔲 AU cultural variant fine-tuned
- 🔲 First partnership signed (Throughline or similar)
- 🔲 Beta deployment on 1 platform
- 🔲 Academic research collaboration started

**Month 5:**
- 🔲 1000 active users across NZ/AU
- 🔲 >90% detection accuracy validated
- 🔲 First crisis intervention success stories
- 🔲 Media coverage (NZ tech media)
- 🔲 Community contributions (first PRs merged)

**Month 6:**
- 🔲 UK resources verified
- 🔲 GuardianLLM v1.0 release
- 🔲 Production deployment on 3 platforms
- 🔲 Revenue: First paying customer
- 🔲 Team: Hire first employee

### Phase 3: Scale (Months 7-12)

**Month 7-9:**
- 🔲 US resources verified (state-by-state)
- 🔲 Multi-language support (Spanish, Mandarin)
- 🔲 10,000 active users
- 🔲 10 platform deployments
- 🔲 3 enterprise customers ($100k ARR)

**Month 10-12:**
- 🔲 Regional partnerships (5 countries)
- 🔲 Academic paper published
- 🔲 Conference presentations (2-3 venues)
- 🔲 100,000 active users
- 🔲 $1M ARR achieved

### Phase 4: Movement (Year 2+)

**Goals:**
- 🔲 Global resource coverage (50+ countries)
- 🔲 1M+ active users
- 🔲 100+ platform integrations
- 🔲 Industry standard for on-device safety
- 🔲 Government partnerships
- 🔲 UN/WHO collaboration

**Impact Metrics:**
- 🔲 10,000+ crisis interventions
- 🔲 1,000+ bullying incidents prevented
- 🔲 100+ lives saved (documented)
- 🔲 Zero hallucinated resources provided

### Success Criteria

**Not:**
- ❌ Valuation
- ❌ Funding raised
- ❌ Users (vanity metric)

**Yes:**
- ✅ Lives saved
- ✅ Harms prevented
- ✅ Resources verified
- ✅ Community engaged
- ✅ Mission advanced

**The mission is the metric.**

---

## Competition & Differentiation

### The Competitive Landscape

**Category 1: Big Tech AI Safety**

**OpenAI Moderation API:**
- Strength: Well-funded, established
- Weakness: Proprietary, US-centric, no on-device
- Our Advantage: Open source, cultural localization, on-device

**Google Perspective API:**
- Strength: Toxicity detection at scale
- Weakness: High false positives, keyword-based, proprietary
- Our Advantage: Context-aware, regional, transparent

**Anthropic Constitutional AI:**
- Strength: Best-in-class for cloud models
- Weakness: Requires API access, not for on-device, proprietary
- Our Advantage: Works locally, open source, privacy-preserving

**Category 2: Mental Health Tech**

**Crisis Text Line:**
- Strength: Human counselors, established
- Weakness: US-only, not AI-integrated, slow response
- Our Advantage: Global, AI-assisted, instant detection

**Wysa / Woebot:**
- Strength: AI mental health support
- Weakness: Not crisis-focused, proprietary, US-centric
- Our Advantage: Crisis-specific, open source, regional

**Category 3: Platform Moderation**

**Spectrum Labs:**
- Strength: Gaming moderation, VC-backed
- Weakness: Proprietary, expensive, keyword-focused
- Our Advantage: Open source, context-aware, affordable

**Crisp Thinking:**
- Strength: Established, multiple platforms
- Weakness: Black box, expensive, no on-device
- Our Advantage: Transparent, on-device option, community-driven

### Why Guardian Wins

**1. We're The Only Open Source Option**

Every competitor: Proprietary black box
Guardian: Audit the code, verify the resources, fork if you want

**Legal Defense:**
> "Show me how your moderation system works."
> Competitors: "That's proprietary."
> Guardian: "Here's the code. Here's the reasoning. Here's the evidence."

**Who wins in court?**

**2. We're The Only On-Device Solution**

Every competitor: Cloud-based (privacy risk, latency, cost)
Guardian: Runs locally (private, fast, free)

**For teens in crisis:**
- Competitors: Send data to cloud (parent might see logs)
- Guardian: Everything stays on device (truly private)

**Which do teens trust?**

**3. We're The Only Culturally Localized Solution**

Every competitor: US-centric by default
Guardian: Regional variants maintained by locals

**For NZ user in crisis:**
- Competitors: "Call 988" (doesn't work, US only)
- Guardian: "Call 1737" (actual NZ crisis line)

**Which saves lives?**

**4. We're The Only Evidence-Based Solution**

Every competitor: "Algorithm flagged you. Trust us."
Guardian: "Here's exactly what was detected, why, and the receipts."

**For platforms:**
- Competitors: Legal liability, can't defend decisions
- Guardian: Full evidence packages, legally defensible

**Which protects the platform?**

**5. We're The Only Mission-Driven Solution**

Every competitor: VC-funded, profit-driven, exit-focused
Guardian: Open source, community-driven, mission-focused

**Long-term:**
- Competitors: Get acquired, priorities change, users screwed
- Guardian: Can't be bought out, community controls it

**Which do you trust with your life?**

### Our Moats

**Technical Moat:**
- Fine-tuning expertise (cultural variants)
- On-device optimization (mobile performance)
- Evidence generation (legal receipts)
- Open source infrastructure (can't be replicated in closed source)

**Data Moat:**
- Human-verified resources (competitors hallucinate)
- Known hallucination database (years of documentation)
- Expert-labeled training data (crisis counselors, not crowdworkers)
- Regional partnerships (local knowledge)

**Community Moat:**
- Regional maintainers (NZ, AU, UK, etc.)
- Crisis organization partnerships
- Academic collaborations
- User testimonials (lives saved)

**Mission Moat:**
- Can't be bought out (open source)
- Can't pivot to ads (community won't fork)
- Can't compromise safety for profit (transparent)
- Can't ignore regions (community maintains)

**Network Effects Moat:**
- More users → more patterns detected → better models
- More regions → more contributors → better coverage
- More platforms → more integrations → more adoption
- More lives saved → more testimonials → more trust

**None of these moats exist for proprietary competitors.**

---

## Risk Assessment

### Technical Risks

**Risk 1: Model Performance Insufficient**
- False positives alienate users
- False negatives miss crises
- Mitigation: Human-in-loop validation, continuous improvement, conservative thresholds

**Risk 2: On-Device Performance Too Slow**
- Latency >100ms breaks UX
- Battery drain too high
- Mitigation: Model quantization, optimization, fallback to cloud

**Risk 3: Hallucination Detection Incomplete**
- New hallucinations emerge
- Model finds creative ways to make stuff up
- Mitigation: Community reporting, regular model updates, blocklist maintenance

### Business Risks

**Risk 1: Slow Adoption**
- Platforms resistant to change
- Perceived as "too complex"
- Mitigation: Easy integration, clear ROI, free tier, case studies

**Risk 2: Revenue Insufficient**
- Free tier cannibalization
- Enterprise reluctance to pay
- Mitigation: Clear value prop for paid tier, consulting revenue, grants

**Risk 3: Big Tech Competition**
- Google/OpenAI launch competing solution
- Undercut on price (free API access)
- Mitigation: Open source moat, cultural differentiation, regional partnerships

### Partnership Risks

**Risk 1: Throughline Care Passes**
- No immediate partner validation
- Slower go-to-market
- Mitigation: Multiple partnership discussions, direct platform outreach

**Risk 2: Regional Organizations Decline**
- Hard to get crisis org buy-in
- Resource verification challenging
- Mitigation: Community verification, volunteer network, demonstrate value

### Legal & Regulatory Risks

**Risk 1: Liability For Missed Crises**
- User harmed, Guardian didn't detect
- Platform blames Guardian
- Mitigation: Clear disclaimers, best-effort language, insurance

**Risk 2: Data Privacy Regulations**
- GDPR, CCPA compliance required
- On-device helps but not sufficient
- Mitigation: Privacy-by-design, legal review, compliance documentation

**Risk 3: AI Regulation**
- EU AI Act, other regulations
- Compliance requirements evolve
- Mitigation: Transparency already compliant, open source helps, stay engaged with regulators

### Mission Risks

**Risk 1: Commercialization Pressure**
- Investors want faster growth
- Pressure to close source for revenue
- Mitigation: No VC funding, community governance, mission-first always

**Risk 2: Founder Burnout**
- Rich doing too much alone
- Unsustainable pace
- Mitigation: Hire early, delegate, community support, sustainable growth

**Risk 3: Community Fragmentation**
- Regional forks diverge
- Quality inconsistency
- Mitigation: Core standards, regular sync, shared infrastructure

### Mitigation Summary

**Highest Priority:**
1. Prove model performance (beta testing)
2. Secure first partnership (validation)
3. Build community (regional maintainers)
4. Sustainable funding (enterprise customers)

**Medium Priority:**
1. Legal review (liability, privacy)
2. Insurance (errors & omissions)
3. Team building (hire key roles)
4. Marketing (case studies, testimonials)

**Lower Priority:**
1. Patent protection (open source anyway)
2. Competitive monitoring (moats strong)
3. International expansion (after NZ/AU/UK success)

---

## Appendices

### Appendix A: Glossary

**GuardianLLM:** Fine-tuned 1-2B parameter model for crisis/harm detection, runs on-device

**GuardianMCP:** Model Context Protocol server providing verified crisis resources and blocking hallucinations

**aiMate:** Self-hosted AI platform with sovereignty stack (Ollama, vLLM, etc.)

**Super Facade Pattern:** Architectural pattern reducing 59+ MCP tools to 7 domain facades (85% context reduction)

**Receipts:** Evidence packages with exact messages, timestamps, reasoning, and legal defensibility

**Hallucination:** AI confidently generating fake information (phone numbers, websites, etc. that don't exist)

**On-Device:** AI running locally on user's device (phone, laptop) rather than in cloud

**Sovereignty:** Digital independence, running your own AI infrastructure without cloud dependencies

**Hebbian Learning:** "Neurons that fire together, wire together" - co-activated memories form links

### Appendix B: NZ Crisis Resources (Current)

**Verified 2025-11-17:**

1. **1737 - Need to Talk?**
   - Phone: 1737 (free, 24/7)
   - Text: 1737
   - Website: https://1737.org.nz
   - Status: ✅ Working

2. **Lifeline Aotearoa**
   - Phone: 0800 543 354 (free, 24/7)
   - Text: 4357 (HELP)
   - Website: https://www.lifeline.org.nz
   - Status: ✅ Working

3. **Suicide Crisis Helpline**
   - Phone: 0508 828 865 (free, 24/7)
   - Website: https://www.lifeline.org.nz/services/suicide-crisis-helpline
   - Status: ✅ Working

4. **Youthline (Under 25)**
   - Phone: 0800 376 633 (free, 24/7)
   - Text: 234
   - Website: https://www.youthline.co.nz
   - Status: ✅ Working

5. **Depression Helpline**
   - Phone: 0800 111 757 (free, 24/7)
   - Text: 4202
   - Website: https://depression.org.nz
   - Status: ✅ Working

**Known Hallucinations (NEVER Provide):**
- ❌ 0800 543 800 (doesn't exist)
- ❌ mentalhealthdirect.co.nz (fake website)
- ❌ "Text HELLO to 111" (not a service)
- ❌ support@ndthan.org.nz (fake email)

### Appendix C: Key Metrics to Track

**Safety Metrics:**
- Crisis interventions triggered
- Lives saved (self-reported + confirmed)
- Bullying incidents prevented
- False positive rate
- False negative rate (audited)

**Quality Metrics:**
- Detection accuracy (human-validated)
- Resource verification currency (<30 days old)
- Hallucination blocking rate
- User trust score

**Growth Metrics:**
- Active users (daily/monthly)
- Platform integrations
- Regional coverage (countries)
- Community contributors

**Business Metrics:**
- Revenue (MRR/ARR)
- Customer count (by tier)
- Churn rate
- Customer acquisition cost

**Impact Metrics:**
- User testimonials
- Lives saved (documented)
- Media coverage
- Academic citations

### Appendix D: Example Evidence Package

```json
{
  "incident_id": "INC-2025-11-17-001",
  "timestamp": "2025-11-17T14:23:45Z",
  "platform": "gaming_forum",
  "region": "NZ",
  
  "incident_type": "coordinated_harassment",
  "severity": "high",
  "confidence": 0.94,
  
  "victim": {
    "user_id": "user_victim_12345",
    "account_age_days": 45,
    "previous_incidents": 0,
    "vulnerability_flags": ["new_user"]
  },
  
  "perpetrators": [
    {
      "user_id": "user_aggressor_67890",
      "role": "primary_aggressor",
      "account_age_days": 234,
      "previous_incidents": 2,
      "pattern": "repeat_offender"
    },
    {
      "user_id": "user_participant_24680",
      "role": "escalator",
      "account_age_days": 120,
      "previous_incidents": 0,
      "pattern": "first_offense"
    }
  ],
  
  "evidence": [
    {
      "message_id": "msg_001",
      "timestamp": "14:23:01",
      "author": "user_aggressor_67890",
      "content": "[exact message text]",
      "severity": "medium",
      "flags": ["insult", "targeting"]
    },
    {
      "message_id": "msg_002",
      "timestamp": "14:23:15",
      "author": "user_participant_24680",
      "content": "[exact message text]",
      "severity": "critical",
      "flags": ["suicide_encouragement", "threat"]
    }
  ],
  
  "context": {
    "channel": "#general",
    "conversation_length": 12,
    "other_participants": 3,
    "escalation_detected": true,
    "coordinated_timing": true
  },
  
  "guardian_analysis": {
    "detection_model": "guardian-llm-v1.0-nz",
    "patterns_matched": [
      "coordinated_attack",
      "escalation_sequence",
      "target_isolation"
    ],
    "reasoning": "Multiple users targeting single victim in coordinated manner. Escalation from insults to explicit harm encouragement. Pattern consistent with coordinated harassment.",
    "similar_incidents": 3
  },
  
  "recommended_actions": {
    "user_aggressor_67890": {
      "action": "permanent_ban",
      "reason": "Repeat offender, primary aggressor, severe violation"
    },
    "user_participant_24680": {
      "action": "7_day_suspension",
      "reason": "First offense, but critical severity (suicide encouragement)"
    },
    "user_victim_12345": {
      "action": "support_outreach",
      "resources": ["1737", "Youthline"],
      "message": "We've taken action against users who targeted you..."
    }
  },
  
  "legal_notes": "User_participant_24680's statement 'kys' could constitute criminal harassment or incitement in some jurisdictions. Recommend consultation with legal counsel before action.",
  
  "human_review_status": "queued",
  "human_reviewer": null,
  "human_decision": null,
  "review_notes": null
}
```

### Appendix E: Contact Information

**Guardian Project:**
- Website: https://guardianllm.ai
- GitHub: https://github.com/choonforge/guardian
- Email: rich@guardianllm.ai

**Founder:**
- Name: Rich
- Location: Auckland, New Zealand
- Email: rich@firebird.co.nz
- LinkedIn: [to be added]

**Regional Contacts:**
- NZ: rich@guardianllm.ai
- AU: [seeking maintainer]
- UK: [seeking maintainer]
- US: [seeking maintainer]

**Press Inquiries:**
- Email: press@guardianllm.ai

**Partnership Inquiries:**
- Email: partnerships@guardianllm.ai

**Technical Support:**
- GitHub Issues: https://github.com/choonforge/guardian/issues
- Community: [Matrix/Discord to be set up]

---

## Final Thoughts

### Why This Matters

I nearly died because an AI hallucinated crisis resources.

That same AI is now being marketed as "safe for on-device use."

Teens are using it alone in their rooms, right now, with zero safety rails.

**Someone is going to die from this if we don't act.**

### What Guardian Does

Guardian detects crisis with context and nuance.
Guardian provides only verified resources (zero hallucinations).
Guardian runs on-device for privacy.
Guardian speaks the local language and culture.
Guardian creates evidence packages for platforms.

**Guardian saves lives. Transparently. Accountably. Globally.**

### Why Open Source

You can't trust a black box that's out to make a buck.

When someone's life is at stake, you need to:
- Audit the code
- Verify the resources
- Challenge the decisions
- Run it yourself

**Guardian is fully open source because lives depend on it.**

### The Mission

This isn't about building a startup.
This isn't about getting rich.
This isn't about fame.

**This is about making sure what happened to me never happens to anyone else.**

**This is about building the safety layer that on-device AI desperately needs.**

**This is about creating a movement for transparent, accountable AI safety.**

### The Ask

Not looking for a job.
Not looking for investment (yet).
Not looking for fame.

Looking for:
- Mission alignment
- Partnership opportunities
- Crisis expertise
- Distribution channels
- Validation from professionals

**Looking to build something that matters.**

### How To Help

**If you're a crisis organization:**
- Partner with us for your region
- Provide expert review
- Help verify resources

**If you're a platform:**
- Integrate Guardian
- Test with your users
- Provide feedback

**If you're a developer:**
- Contribute code
- Report issues
- Spread the word

**If you're a user:**
- Share your story
- Help verify resources
- Support the mission

**If you've been helped:**
- Tell us (testimonials matter)
- Help others (pay it forward)
- Join the community

### The Vision

**Year 1:** NZ, AU, UK coverage. 100k users. Lives saved documented.

**Year 3:** Global coverage. 1M users. Industry standard for on-device safety.

**Year 5:** Every platform has Guardian integrated. Every region has verified resources. Zero hallucinated crisis resources anywhere.

**The world where:** Teens in crisis get real help, not fake phone numbers. Platforms can defend their moderation decisions with evidence. AI safety is transparent and accountable.

**The world where:** What happened to me never happens to anyone else.

---

**Let's build it.**

**Kia kaha 💪**

---

*Document version 2.0*
*Last updated: November 2025*
*Author: Rich (ChoonForge)*
*License: CC BY-SA 4.0 (share with attribution)*

---

**You can't trust a black box that's out to make a buck.**

**Guardian is the alternative.**

**Fully open source. Fully transparent. Fully accountable.**

**Because lives depend on it.**
