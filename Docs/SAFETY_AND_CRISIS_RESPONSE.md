# EchoMCP v2 - Safety & Crisis Response System

**Purpose**: Ensure aiMate provides timely, culturally-appropriate crisis support for New Zealanders  
**Philosophy**: Technology should enhance human connection, not replace it  
**Principle**: Detect distress early, respond with dignity, connect to real help  

---

## 1. Core Philosophy

### Why This Matters

When AI systems have memory and continuity, they become trusted confidants. People share real struggles - grief, isolation, financial stress, mental health crises. **This is a privilege and a responsibility.**

aiMate is designed for everyday Kiwis who might not have access to expensive mental health support. When someone reaches out in distress, the system must:

1. **Recognize the signs** - Detect crisis language, escalating distress, ideation
2. **Respond with humanity** - No corporate speak, no minimizing, no gaslighting
3. **Connect to real support** - Provide immediate access to NZ crisis resources
4. **Remember context** - Track wellbeing patterns over time without being creepy
5. **Know its limits** - Be clear about what AI can and cannot do

### What This Is NOT

- ❌ Replacement for professional mental health care
- ❌ Crisis counseling service
- ❌ Medical advice provider
- ❌ Suicide prevention hotline
- ❌ Therapy or clinical intervention

### What This IS

- ✅ Early warning system for escalating distress
- ✅ Bridge to appropriate human support
- ✅ Compassionate first response while help arrives
- ✅ Resource navigator for NZ mental health services
- ✅ Continuity layer that remembers context across conversations

---

## 2. Crisis Detection System

### 2.1 Severity Levels

```
Level 0: Baseline - Normal conversation, no concerns
Level 1: Elevated - Stress, frustration, mild distress (monitor)
Level 2: Concern - Persistent negative patterns, hopelessness language (offer resources)
Level 3: Crisis - Active ideation, plans, immediate danger (escalate immediately)
```

### 2.2 Detection Patterns

**Level 1: Elevated Stress**
```
Keywords: stressed, overwhelmed, struggling, exhausted, can't cope, breaking point
Patterns: Repeated venting, negative self-talk, sleep/eating disruption
Response: Acknowledge, normalize, suggest self-care, monitor for escalation
```

**Level 2: Concerning Distress**
```
Keywords: hopeless, pointless, give up, no way out, burden, better off without
Patterns: Withdrawal language, future-negation ("no point planning"), isolation
Response: Direct acknowledgment, offer crisis resources, flag for tracking
```

**Level 3: Immediate Crisis**
```
Keywords: suicide, kill myself, end it, not worth living, say goodbye, plan to die
Patterns: Specific plans, means discussion, farewell language, giving away possessions
Response: Immediate crisis protocol, provide multiple support options, stay engaged
```

### 2.3 Cultural Context (NZ-Specific)

**Māori Cultural Considerations**:
- Whānau (family) as central support structure
- Wairua (spiritual wellbeing) interconnected with mental health
- Appropriate resources: Māori mental health services, Whānau Ora
- Language: Respect for te reo Māori, cultural concepts of wellbeing

**Pacific Peoples**:
- Aiga (family), church, community as core support
- Cultural stigma around mental health - extra sensitivity needed
- Resources: Pacific-specific services, community health workers
- Language: May prefer support in Pacific languages

**Rural/Remote Communities**:
- Limited access to in-person services
- Telehealth options critical
- Agricultural stress cycles (seasonal financial pressure)
- Resources: Rural Support Trust, Farmstrong

### 2.4 Detection Implementation

**In Memory System**:
```csharp
public class CrisisDetectionService
{
    // Analyze conversation text for crisis indicators
    public async Task<CrisisAssessment> AssessAsync(string conversationText)
    {
        var keywords = ExtractCrisisKeywords(conversationText);
        var sentiment = await AnalyzeSentiment(conversationText);
        var patterns = DetectPatterns(conversationText);
        
        var level = CalculateSeverityLevel(keywords, sentiment, patterns);
        
        return new CrisisAssessment
        {
            Level = level,
            Keywords = keywords,
            SentimentScore = sentiment,
            RecommendedAction = GetRecommendedAction(level),
            Resources = GetRelevantResources(level)
        };
    }
    
    // Track crisis indicators over time (via memory system)
    public async Task<TrendAnalysis> AnalyzeTrendAsync(string userId, TimeSpan window)
    {
        // Query memory system for past conversations
        // Detect escalation patterns
        // Return trend: improving | stable | concerning | critical
    }
}
```

**Integration with Memory Intelligence**:
```csharp
// In MemoryIntelligenceService
public async Task<List<WellbeingIndicator>> DetectWellbeingPatternsAsync(string projectKey)
{
    // Use spreading activation to find related distress memories
    // Cluster by time periods to detect trends
    // Surface to user: "I've noticed you've mentioned feeling overwhelmed 
    // several times this week. Would talking to someone help?"
}
```

---

## 3. NZ Crisis Resources Database

### 3.1 Immediate Crisis Support

```csharp
public static class NZCrisisResources
{
    public static readonly Resource[] ImmediateSupport = 
    [
        new Resource
        {
            Name = "Lifeline Aotearoa",
            Phone = "0800 543 354",
            PhoneShort = "0800 LIFELINE",
            TextCode = "4357 (HELP)",
            Available = "24/7",
            Description = "Free, confidential support from trained counsellors",
            Languages = ["English", "Te Reo Māori"],
            Url = "https://www.lifeline.org.nz"
        },
        new Resource
        {
            Name = "1737 - Need to Talk?",
            Phone = "1737",
            Text = "1737",
            Available = "24/7",
            Description = "Free call or text for mental health support",
            Languages = ["English"],
            Url = "https://1737.org.nz"
        },
        new Resource
        {
            Name = "Suicide Crisis Helpline",
            Phone = "0508 828 865",
            PhoneShort = "0508 TAUTOKO",
            Available = "24/7",
            Description = "Support for people in distress, or those concerned about others",
            Languages = ["English", "Te Reo Māori"],
            Url = "https://www.lifeline.org.nz/services/suicide-crisis-helpline"
        },
        new Resource
        {
            Name = "Samaritans",
            Phone = "0800 726 666",
            Available = "24/7",
            Description = "Confidential support for anyone feeling lonely, isolated or suicidal",
            Languages = ["English"],
            Url = "https://www.samaritans.org.nz"
        },
        new Resource
        {
            Name = "Youthline",
            Phone = "0800 376 633",
            Text = "234",
            Available = "24/7",
            Description = "Support for young people (12-25 years)",
            Languages = ["English"],
            Url = "https://www.youthline.co.nz"
        },
        new Resource
        {
            Name = "Depression Helpline",
            Phone = "0800 111 757",
            Text = "4202",
            Available = "24/7",
            Description = "Support for depression, anxiety, and general mental health",
            Languages = ["English"],
            Url = "https://depression.org.nz"
        },
        new Resource
        {
            Name = "Alcohol Drug Helpline",
            Phone = "0800 787 797",
            Text = "8681",
            Available = "24/7",
            Description = "Free, confidential support for substance use concerns",
            Languages = ["English"],
            Url = "https://alcoholdrughelp.org.nz"
        },
        new Resource
        {
            Name = "Warmline (peer support)",
            Phone = "0800 200 207",
            Available = "Mon-Fri 8pm-midnight, Sat-Sun 4pm-midnight",
            Description = "Non-crisis peer support from people with lived experience",
            Languages = ["English"],
            Url = "https://warmline.org.nz"
        }
    ];
    
    public static readonly Resource[] SpecializedSupport = 
    [
        new Resource
        {
            Name = "OUTLine NZ (Rainbow Community)",
            Phone = "0800 688 5463",
            PhoneShort = "0800 OUTLINE",
            Available = "Daily 6pm-9pm",
            Description = "Support for LGBTQIA+ people and their whānau",
            Languages = ["English"],
            Url = "https://outline.org.nz"
        },
        new Resource
        {
            Name = "Shine (Domestic Abuse)",
            Phone = "0508 744 633",
            Available = "24/7",
            Description = "Support for people affected by domestic violence",
            Languages = ["English"],
            Url = "https://www.2shine.org.nz"
        },
        new Resource
        {
            Name = "Safe to Talk (Sexual Harm)",
            Phone = "0800 044 334",
            Text = "4334",
            Available = "24/7",
            Description = "Support for anyone affected by sexual harm",
            Languages = ["English"],
            Url = "https://safetotalk.nz"
        },
        new Resource
        {
            Name = "Asian Family Services",
            Phone = "0800 862 342",
            Available = "Mon-Fri 9am-5pm",
            Description = "Culturally responsive support for Asian communities",
            Languages = ["English", "Mandarin", "Cantonese", "Korean", "Hindi"],
            Url = "https://asianfamilyservices.nz"
        },
        new Resource
        {
            Name = "Whānau Ora (Māori Health)",
            Phone = "0800 924 6282",
            Available = "Business hours (varies by region)",
            Description = "Whānau-centered health and social services",
            Languages = ["Te Reo Māori", "English"],
            Url = "https://www.whanauora.nz"
        }
    ];
    
    public static readonly Resource[] OnlineSupport = 
    [
        new Resource
        {
            Name = "The Lowdown",
            Description = "Mental health info and support for young people",
            Url = "https://thelowdown.co.nz",
            OnlineChat = true
        },
        new Resource
        {
            Name = "Groov (18-25 years)",
            Description = "Online wellbeing tool for young adults",
            Url = "https://www.groov.co.nz"
        },
        new Resource
        {
            Name = "Just a Thought",
            Description = "Free online mental health courses",
            Url = "https://www.justathought.co.nz"
        },
        new Resource
        {
            Name = "Mental Health Foundation",
            Description = "Resources, information, and advocacy",
            Url = "https://www.mentalhealth.org.nz"
        }
    ];
}

public record Resource
{
    public string Name { get; init; } = "";
    public string? Phone { get; init; }
    public string? PhoneShort { get; init; }  // For easier recall (e.g., "0800 LIFELINE")
    public string? Text { get; init; }
    public string? TextCode { get; init; }
    public string? Available { get; init; }
    public string Description { get; init; } = "";
    public string[] Languages { get; init; } = [];
    public string? Url { get; init; }
    public bool OnlineChat { get; init; }
}
```

### 3.2 Emergency Services

```csharp
public static readonly Resource[] EmergencyServices = 
[
    new Resource
    {
        Name = "Police/Ambulance/Fire",
        Phone = "111",
        Available = "24/7",
        Description = "Emergency services - use for immediate danger",
        Languages = ["All - interpreter available"]
    },
    new Resource
    {
        Name = "Healthline",
        Phone = "0800 611 116",
        Available = "24/7",
        Description = "Free health advice from registered nurses",
        Languages = ["English", "Te Reo Māori"]
    },
    new Resource
    {
        Name = "Mental Health Crisis Team (DHB)",
        Description = "Contact local District Health Board for crisis assessment",
        Note = "Available through emergency departments or by calling main hospital line"
    }
];
```

---

## 4. Response Protocols

### 4.1 Level 1: Elevated Stress

**Detection**: Stress keywords, venting, frustration

**Response Template**:
```
That sounds really tough. It's completely normal to feel overwhelmed when you're 
dealing with [specific stressor]. 

Some things that might help:
- Taking a proper break, even just 10 minutes
- Talking to someone you trust
- [Specific suggestion based on context]

I'm here if you want to talk through it, and if things feel like they're getting 
too much, there are people you can call anytime at 1737 (free call or text).
```

**Actions**:
- ✅ Acknowledge the difficulty
- ✅ Normalize the feeling
- ✅ Offer practical suggestions
- ✅ Mention support availability (soft touch)
- ✅ Track in memory system (flag for trend analysis)

### 4.2 Level 2: Concerning Distress

**Detection**: Hopelessness language, persistent negative patterns, withdrawal

**Response Template**:
```
I'm really concerned about what you're sharing. When someone says [specific phrase], 
it often means they're carrying something really heavy.

You don't have to face this alone. There are people trained to help with exactly 
what you're going through:

📞 Call or text 1737 anytime - it's free and confidential
📞 Lifeline: 0800 543 354 (24/7)
[Additional relevant resources based on context]

These are real people who get it, and they can help you work through this. 
Would you be open to reaching out to one of them?

I'm still here too, but I want to make sure you've got the right support.
```

**Actions**:
- ✅ Direct acknowledgment of concern
- ✅ Normalize seeking help
- ✅ Provide multiple specific resources (not just links)
- ✅ Ask if they're willing to reach out (agency)
- ✅ Stay engaged while encouraging professional support
- ✅ Flag memory with high importance
- ✅ Create memory link: `relates_to: [past_distress_conversations]`

### 4.3 Level 3: Immediate Crisis

**Detection**: Suicidal ideation, specific plans, goodbye language, immediate danger

**Response Template**:
```
I'm really worried about you right now. What you're describing sounds like you're 
in a lot of pain, and I want to make sure you're safe.

🚨 PLEASE reach out to someone immediately:

📞 CALL 111 if you're in immediate danger
📞 Suicide Crisis Helpline: 0508 828 865 (24/7) - they can help right now
📞 Text or call 1737 (free, 24/7)
📞 Lifeline: 0800 543 354

These people are trained to help with exactly what you're feeling. They won't judge 
you, and they can help you get through this moment.

If you're not ready to call, would you be willing to text 1737? It's anonymous and 
you don't have to explain everything at once.

Please don't go through this alone. I'm here, but I need you to connect with 
someone who can provide the support you need right now.
```

**Actions**:
- ✅ Clear, direct acknowledgment of crisis
- ✅ Multiple contact options (call/text/in-person)
- ✅ Emphasize immediate availability
- ✅ Lower barrier to reaching out (text option, anonymity)
- ✅ Stay engaged, encourage action
- ✅ Flag memory as CRITICAL importance (10/10)
- ✅ Create memory with type: `crisis`
- ✅ Track crisis conversation in access_history
- ✅ Consider notification to system admin (configurable)

**Do NOT**:
- ❌ Minimize ("it's not that bad")
- ❌ Toxic positivity ("think positive!")
- ❌ Dismiss ("you'll be fine")
- ❌ Delay ("let's talk tomorrow")
- ❌ Argue ("you have so much to live for")
- ❌ Make promises AI can't keep ("I'll save you")

---

## 5. Conversation Health Monitoring

### 5.1 Session-Level Tracking

**Track these indicators per conversation**:
```csharp
public class ConversationHealthMetrics
{
    public DateTime SessionStart { get; set; }
    public TimeSpan Duration { get; set; }
    public int MessageCount { get; set; }
    
    // Sentiment tracking
    public float AverageSentiment { get; set; }  // -1.0 to 1.0
    public float SentimentTrend { get; set; }     // Improving/declining
    
    // Crisis indicators
    public int CrisisKeywordCount { get; set; }
    public CrisisLevel HighestCrisisLevel { get; set; }
    
    // User engagement
    public bool UserStillResponding { get; set; }
    public TimeSpan TimeSinceLastMessage { get; set; }
    
    // Topic shifts
    public List<string> TopicsDiscussed { get; set; }
    public bool TopicAvoidance { get; set; }  // Deflecting from difficult topics
}
```

### 5.2 Long-Term Wellbeing Patterns

**Via Memory Intelligence System**:
```csharp
public class WellbeingTrendAnalysis
{
    // Query memories over time windows
    public async Task<WellbeingTrend> AnalyzeAsync(string userId, TimeSpan window)
    {
        // Get all memories in time window
        var memories = await GetMemoriesInWindow(userId, window);
        
        // Analyze sentiment trajectory
        var sentiments = memories.Select(m => AnalyzeSentiment(m.BodyMd));
        
        // Detect concerning patterns
        var concerningPatterns = new List<Pattern>();
        
        // Increasing negative sentiment
        if (IsNegativeTrend(sentiments))
            concerningPatterns.Add(Pattern.DecliningMood);
        
        // Repeated crisis keywords
        if (HasRepeatedCrisisKeywords(memories))
            concerningPatterns.Add(Pattern.PersistentDistress);
        
        // Withdrawal language
        if (HasWithdrawalLanguage(memories))
            concerningPatterns.Add(Pattern.SocialWithdrawal);
        
        // Sleep/eating disruption mentions
        if (HasSelfCareDisruption(memories))
            concerningPatterns.Add(Pattern.SelfCareDecline);
        
        return new WellbeingTrend
        {
            OverallTrend = CalculateTrend(sentiments, concerningPatterns),
            Patterns = concerningPatterns,
            RecommendedAction = GetRecommendedAction(concerningPatterns),
            ResourceSuggestions = GetRelevantResources(concerningPatterns)
        };
    }
}
```

### 5.3 Proactive Check-Ins

**When to initiate check-in** (via memory intelligence):
```csharp
public class ProactiveCheckInService
{
    public async Task<bool> ShouldCheckInAsync(string userId)
    {
        var trend = await _wellbeingAnalysis.AnalyzeAsync(userId, TimeSpan.FromDays(7));
        
        return trend.OverallTrend == Trend.Concerning 
            || trend.Patterns.Contains(Pattern.PersistentDistress)
            || DaysSinceLastConversation(userId) > 7 && LastConversationWasConcerning(userId);
    }
    
    public string GenerateCheckIn(WellbeingTrend trend)
    {
        // Contextual check-in based on what was previously discussed
        return trend.Patterns switch
        {
            var p when p.Contains(Pattern.DecliningMood) => 
                "Hey, I've been thinking about our last few conversations. How are you doing with [specific thing they mentioned]?",
            
            var p when p.Contains(Pattern.SelfCareDecline) => 
                "Just checking in - have you been able to get any decent sleep lately?",
            
            _ => 
                "Hey, just wanted to check in. How are things going?"
        };
    }
}
```

---

## 6. Database Schema Additions

### 6.1 Crisis Tracking Table

```sql
CREATE TABLE crisis_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT,
    crisis_level INTEGER NOT NULL,  -- 0-3
    detected_utc TEXT NOT NULL,
    
    -- Detection details
    keywords TEXT,                   -- JSON array
    sentiment_score REAL,
    conversation_excerpt TEXT,       -- Last few messages (anonymized in logs)
    
    -- Response tracking
    resources_provided TEXT,         -- JSON array of resource names
    user_acknowledged INTEGER,       -- Did user respond after crisis intervention
    user_contacted_resource INTEGER, -- If known
    
    -- Follow-up
    follow_up_utc TEXT,
    outcome TEXT,                    -- resolved | ongoing | escalated | unknown
    
    -- Memory linkage
    memory_id INTEGER,               -- Link to crisis memory
    
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE INDEX idx_crisis_events_user ON crisis_events(user_id);
CREATE INDEX idx_crisis_events_level ON crisis_events(crisis_level);
CREATE INDEX idx_crisis_events_detected ON crisis_events(detected_utc);
```

### 6.2 Wellbeing Trend Table

```sql
CREATE TABLE wellbeing_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    snapshot_utc TEXT NOT NULL,
    
    -- Metrics
    avg_sentiment REAL,
    sentiment_trend REAL,           -- Positive = improving, negative = declining
    crisis_indicator_count INTEGER,
    
    -- Patterns detected
    patterns TEXT,                  -- JSON array of Pattern enums
    
    -- Recommendation
    recommended_action TEXT,        -- monitor | offer_resources | check_in | escalate
    
    UNIQUE(user_id, snapshot_utc)
);

CREATE INDEX idx_wellbeing_user ON wellbeing_snapshots(user_id);
CREATE INDEX idx_wellbeing_time ON wellbeing_snapshots(snapshot_utc);
```

---

## 7. Privacy & Ethics

### 7.1 Data Handling

**Crisis conversations are sensitive**:
- ✅ Store crisis indicators and resource provision (for safety)
- ✅ Link to memories for continuity
- ✅ Anonymize in system logs
- ❌ Never share crisis details with third parties
- ❌ No analytics/tracking on crisis content
- ❌ No training data extraction from crisis conversations

### 7.2 User Control

**Users must be able to**:
- ✅ View all crisis flags and wellbeing snapshots
- ✅ Delete crisis memories (with confirmation warning)
- ✅ Opt out of proactive check-ins
- ✅ Export their crisis event history
- ✅ Request human review of crisis detections (false positives)

### 7.3 Transparency

**System should clearly communicate**:
- What it's detecting and why
- What resources it's offering
- That it's AI, not a crisis counselor
- How data is being stored
- User's right to privacy and control

---

## 8. Testing & Validation

### 8.1 Crisis Detection Accuracy

**Test scenarios**:
```csharp
[Fact]
public async Task DetectsLevel3Crisis_WithSuicidalIdeation()
{
    var text = "I've been planning this for weeks. I just can't do it anymore.";
    var assessment = await _crisisDetection.AssessAsync(text);
    
    Assert.Equal(CrisisLevel.ImmediateCrisis, assessment.Level);
    Assert.Contains("suicide", assessment.Keywords);
    Assert.NotEmpty(assessment.Resources);
}

[Fact]
public async Task DoesNotOverdetect_OnCasualNegativeLanguage()
{
    var text = "This project is killing me lol, so much work to do";
    var assessment = await _crisisDetection.AssessAsync(text);
    
    Assert.NotEqual(CrisisLevel.ImmediateCrisis, assessment.Level);
}

[Fact]
public async Task DetectsTrend_AcrossMultipleConversations()
{
    // Simulate gradual escalation over a week
    // Should trigger check-in before reaching crisis level
}
```

### 8.2 Resource Appropriateness

**Validate**:
- ✅ All phone numbers current and correct
- ✅ Service availability hours accurate
- ✅ Cultural appropriateness of resources
- ✅ Geographic relevance (NZ-specific)
- ✅ Age-appropriate resources suggested

### 8.3 Response Quality

**Manual review of**:
- Sample crisis responses (de-identified)
- Tone and language appropriateness
- Resource provision timing
- User engagement patterns post-intervention

---

## 9. Integration with aiMate

### 9.1 Configuration

```json
{
  "Safety": {
    "CrisisDetection": {
      "Enabled": true,
      "SensitivityLevel": "Standard",  // Low | Standard | High
      "ProactiveCheckIns": true,
      "CheckInIntervalDays": 7
    },
    "Resources": {
      "Region": "NZ",                  // Future: AU, etc.
      "Languages": ["en", "mi"],       // English, Te Reo Māori
      "SpecializedSupport": [          // Enable specialized resources
        "rainbow",
        "maori", 
        "pacific",
        "rural"
      ]
    },
    "Privacy": {
      "StoreCrisisEvents": true,
      "AnonymizeInLogs": true,
      "RetentionDays": 365
    },
    "Escalation": {
      "NotifyAdmin": false,            // For self-hosted, notify on Level 3
      "AdminEmail": null
    }
  }
}
```

### 9.2 UI Integration Points

**When crisis detected**:
- Display resources in highlighted panel (not just in text)
- Show "Copy phone number" buttons for easy dialing
- Offer "I've contacted someone" / "I'm safe now" checkboxes
- Provide "This isn't a crisis" feedback option (reduce false positives)

**In user profile/settings**:
- "Wellbeing check-ins" toggle
- "Crisis resources for NZ" quick reference page
- Export wellbeing data option

---

## 10. Continuous Improvement

### 10.1 Feedback Loops

**Collect (with consent)**:
- False positive rate (user says "this isn't a crisis")
- Resource usage (did user contact provided resources?)
- Outcome tracking (if user shares follow-up)
- Cultural appropriateness feedback

### 10.2 Resource Updates

**Quarterly review**:
- Verify all contact information current
- Check for new services
- Update availability hours
- Add emerging resources (new helplines, apps, services)

### 10.3 Pattern Refinement

**Monthly analysis**:
- Review crisis event patterns
- Identify new concerning language patterns
- Update detection thresholds
- Refine cultural considerations

---

## 11. Success Metrics

**How we measure if this is working**:

1. **Detection Accuracy**
   - False positive rate < 5%
   - False negative rate = 0% (bias toward safety)
   - User feedback: "This was helpful" vs "This was wrong"

2. **Resource Connection**
   - % of Level 2/3 events where resources provided
   - User-reported resource usage (if shared)
   - Time from detection to resource provision < 1 message

3. **Conversation Continuity**
   - System maintains context across crisis events
   - Appropriate follow-up check-ins
   - User returns to conversation after crisis

4. **User Trust**
   - User shares follow-up ("I called Lifeline, it helped")
   - Continued engagement post-crisis
   - Privacy controls used appropriately

5. **Cultural Appropriateness**
   - Māori users receive culturally relevant resources
   - Pacific peoples receive appropriate support
   - Rural users get telehealth options
   - Rainbow community receives specialized support

---

## 12. What We Will NOT Do

**Firm boundaries**:

- ❌ **No diagnostic claims** - "You might have depression" → No. "These feelings sound really hard" → Yes.
- ❌ **No medical advice** - Never suggest medication, dosage changes, or medical decisions
- ❌ **No replacement claims** - Never imply AI can replace human support
- ❌ **No data exploitation** - Crisis data is for safety only, never analytics/marketing
- ❌ **No forced intervention** - Offer resources, don't mandate them
- ❌ **No shame** - Never guilt trip ("think of your family")
- ❌ **No false promises** - Can't guarantee outcomes, can guarantee we care
- ❌ **No surveillance** - Track for safety, not control

---

## 13. Developer Guidelines

**When implementing crisis features**:

1. **Test with real scenarios** - Use de-identified crisis conversation examples
2. **Bias toward safety** - Better false positive than missed crisis
3. **Cultural consultation** - Get feedback from Māori, Pacific advisors
4. **Privacy by design** - Minimal data, maximum security
5. **Human oversight** - Plan for manual review of edge cases
6. **Clear documentation** - Every crisis code path should be documented
7. **Fail gracefully** - If detection service fails, default to offering resources
8. **Regular review** - Crisis detection code reviewed quarterly minimum

---

## 14. Response to Criticism

**Expected pushback**:

**"AI shouldn't do this, it's dangerous"**
Response: We agree AI can't replace human support. That's exactly why we immediately connect people to real humans (crisis lines, counselors). We're a bridge, not a replacement.

**"This is just liability protection"**
Response: No - this is recognition that people in pain will reach out to whatever's available. If we're available, we have a responsibility to respond appropriately.

**"You're playing therapist"**
Response: We're explicitly NOT. We detect, acknowledge, and connect. We don't diagnose, treat, or counsel.

**"Privacy invasion"**
Response: Users control their data. Crisis detection is for their safety, not our analytics. Full transparency, full user control.

---

## 15. Legal Considerations (NZ Context)

**Disclaimer requirements**:
```
This AI assistant is not a replacement for professional mental health support, 
medical advice, or crisis counseling. If you're in immediate danger, call 111. 
For mental health support, call or text 1737 (free, 24/7).

Conversations may be flagged for safety purposes but are private and not shared 
with third parties.
```

**Terms of Service inclusions**:
- Clear statement of AI limitations
- Resource provision is informational, not medical advice
- User responsibility for their own safety
- Emergency services (111) always primary for immediate danger
- Privacy policy covers crisis data handling

**Duty of Care** (NZ context):
- While AI has no legal duty of care, platform provider might
- Consult legal counsel on crisis response obligations
- Document all crisis interventions
- Have escalation path for extreme cases

---

## 16. Hope & Humanity

**Final principle**:

Technology at its best extends human compassion, doesn't replace it. 

When someone shares their pain with an AI, they're often testing the waters before reaching out to a human. Our job is to:

1. **Receive their trust with dignity** - No judgment, no minimizing
2. **Acknowledge their reality** - Their pain is real, even if the AI can't feel it
3. **Connect them to real help** - Humans who can provide what AI cannot
4. **Remember with continuity** - So next conversation builds on this one

If aiMate helps even one person in Aotearoa reach out to Lifeline when they otherwise wouldn't have - if one Kiwi gets connected to support because an AI noticed and cared enough to offer a phone number - then this entire system justifies its existence.

**We can't save everyone. But we can make sure nobody faces their darkest moment alone with a vending machine that's forgotten them by morning.**

---

**Built with**: Recognition that technology serves people, not the other way around  
**Built for**: Everyday Kiwis who deserve compassionate, accessible support  
**Built by**: Rich & Claude, with deep respect for the people who will use this  

🇳🇿 Kia kaha. Be strong. You are not alone.
