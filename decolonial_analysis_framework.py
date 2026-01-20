"""
DECOLONIAL DISCOURSE ANALYSIS FRAMEWORK
For Aging Narratives Study
"""

# ============================================================================
# CODING FRAMEWORK FOR MANUAL NARRATIVE ANALYSIS
# ============================================================================

CODING_CATEGORIES = {
    
    '1. NARRATIVE TYPE': {
        'description': 'Primary narrative framing of aging',
        'codes': {
            'LIMITING': 'Crisis, burden, problem, threat, decline, loss, dependency',
            'NEUTRAL': 'Demographic shift, statistical reporting, factual description',
            'EMPOWERING': 'Opportunity, wisdom, experience, active engagement, contribution'
        },
        'examples': {
            'LIMITING': '"aging tsunami threatens healthcare system"',
            'NEUTRAL': '"population over 65 increased by 15%"',
            'EMPOWERING': '"older adults lead community volunteer programs"'
        }
    },
    
    '2. AGEISM INDICATORS': {
        'description': 'Forms of ageist discourse present',
        'codes': {
            'BENEVOLENT': 'Patronizing, infantilizing, cute, sweet, "young at heart"',
            'HOSTILE': 'Burden, drain, decline, obsolete, resistant to change',
            'AMBIVALENT': 'Mixed messages, contradictory framing',
            'NONE_DETECTED': 'No clear ageist language or framing'
        }
    },
    
    '3. VOICE & REPRESENTATION': {
        'description': 'Whose voices are centered in the narrative?',
        'codes': {
            'OLDER_ADULTS_CENTERED': 'Quotes, perspectives, agency from older people',
            'EXPERT_DOMINATED': 'Primarily researchers, policymakers, doctors speaking about aging',
            'FAMILY_CAREGIVER_FOCUSED': 'Adult children, caregivers as primary voices',
            'INSTITUTIONAL_VOICE': 'Government, corporations, healthcare systems',
            'NO_DIRECT_VOICES': 'Statistics and third-person description only'
        },
        'decolonial_note': 'Whose knowledge is considered legitimate? Who has authority to speak?'
    },
    
    '4. RACIALIZED/COLONIZED AGING': {
        'description': 'How are race, ethnicity, colonization addressed?',
        'codes': {
            'RACE_INVISIBLE': 'Implicitly white/Western framing with no mention of race',
            'TOKENIZED': 'Brief mention of "diverse elders" without depth',
            'DISPARITIES_NOTED': 'Acknowledges racial health/economic disparities',
            'STRUCTURAL_ANALYSIS': 'Connects aging inequality to colonialism, racism, capitalism',
            'INDIGENOUS_ERASURE': 'Western aging models applied universally, erasing Indigenous knowledge'
        },
        'critical_questions': [
            'Are Indigenous/racialized elders visible or erased?',
            'Is Western aging used as universal standard?',
            'Are structural causes of disparities addressed?'
        ]
    },
    
    '5. ECONOMIC FRAMING': {
        'description': 'How is economic relationship to aging constructed?',
        'codes': {
            'BURDEN_FRAME': 'Cost, drain, unsustainable, crisis for economy/taxpayers',
            'PRODUCTIVE_AGING': 'Work longer, volunteer, contribute, stay engaged',
            'RIGHTS_BASED': 'Entitlement, social contract, collective responsibility',
            'NEOLIBERAL': 'Individual responsibility, private solutions, market-based'
        },
        'decolonial_note': 'Who benefits from positioning elders as burdens vs. assets?'
    },
    
    '6. CULTURAL KNOWLEDGE SYSTEMS': {
        'description': 'What knowledge systems are privileged or erased?',
        'codes': {
            'BIOMEDICAL_ONLY': 'Medical/scientific expertise exclusively',
            'ELDER_WISDOM_PRESENT': 'Recognition of accumulated knowledge, experience',
            'INDIGENOUS_KNOWLEDGE': 'Traditional practices, intergenerational teaching',
            'DIVERSE_EPISTEMOLOGIES': 'Multiple ways of knowing about aging valued'
        }
    },
    
    '7. AGENCY & POWER': {
        'description': 'How is older adult agency constructed?',
        'codes': {
            'PASSIVE_RECIPIENT': 'Object of care, policy, intervention',
            'CONSUMER_AGENT': 'Choice, independence through market participation',
            'POLITICAL_AGENT': 'Advocacy, activism, collective organizing',
            'KNOWLEDGE_HOLDER': 'Teacher, mentor, community resource'
        }
    },
    
    '8. TEMPORAL ORIENTATION': {
        'description': 'How is time and aging progression framed?',
        'codes': {
            'DECLINE_NARRATIVE': 'Inevitable deterioration, loss, past-oriented',
            'DEVELOPMENTAL': 'New stage with opportunities, future-oriented',
            'LIMINAL': 'Between, uncertain, waiting',
            'CYCLICAL': 'Part of life cycle, continuity, regeneration'
        }
    }
}

# ============================================================================
# DECOLONIAL ANALYSIS QUESTIONS
# ============================================================================

DECOLONIAL_FRAMEWORK = {
    
    'POWER_RELATIONS': [
        'Who has authority to define "successful aging"?',
        'Whose aging experiences are centered vs. marginalized?',
        'What colonial structures shape aging inequality?',
        'How does Western biomedicine colonize understandings of aging?'
    ],
    
    'KNOWLEDGE_HIERARCHIES': [
        'What knowledge systems are valued vs. dismissed?',
        'How is elder wisdom positioned relative to expert knowledge?',
        'Are Indigenous aging practices visible or erased?',
        'Who is considered a credible source of knowledge about aging?'
    ],
    
    'ECONOMIC_EXPLOITATION': [
        'Who profits from framing elders as burdens vs. assets?',
        'How does neoliberalism shape aging discourse?',
        'What labor (care work) is made invisible?',
        'How are pensions/social supports framed (entitlement vs. burden)?'
    ],
    
    'INTERSECTIONALITY': [
        'How do race, class, gender, disability intersect with ageism?',
        'Are Indigenous, Black, racialized elders visible?',
        'How are immigration, citizenship status implicated?',
        'What about LGBTQ2S+ aging experiences?'
    ],
    
    'RESISTANCE_POSSIBILITIES': [
        'Are alternative aging narratives presented?',
        'What counter-narratives exist?',
        'How might decolonial aging look different?',
        'What solidarities are possible?'
    ]
}

# ============================================================================
# CODING INSTRUCTIONS
# ============================================================================

CODING_PROCESS = """
FOR EACH ARTICLE IN YOUR SAMPLE:

1. READ THE FULL ARTICLE
   - Note immediate emotional/interpretive response
   - Identify dominant framing

2. CODE EACH CATEGORY (1-8)
   - Select primary code
   - Note secondary codes if applicable
   - Add quotes/evidence in notes field

3. APPLY DECOLONIAL LENS
   - Use questions in DECOLONIAL_FRAMEWORK
   - Identify colonial/racist structures
   - Note whose voices are present/absent
   - Consider who benefits from this framing

4. DOCUMENT IN SPREADSHEET
   - Use aging_narratives_coding_sample.csv
   - Add codes to designated columns
   - Include rich qualitative notes
   - Flag particularly significant examples

5. TRACK PATTERNS
   - Are certain outlets more ageist?
   - Do limiting narratives correlate with certain topics?
   - Are racialized elders more likely to be absent?
   - How does voice representation vary by narrative type?

INTER-CODER RELIABILITY:
If working with others:
- Code 20% of sample independently
- Calculate Cohen's kappa
- Discuss disagreements
- Refine coding framework
- Re-code if necessary
"""

# ============================================================================
# ANALYSIS OUTPUTS
# ============================================================================

EXPECTED_FINDINGS = """
After coding your sample, you should be able to answer:

QUANTITATIVE:
- What % of articles use limiting vs. empowering frames?
- How often are older adults' voices centered?
- What % of articles acknowledge race/colonization?
- Distribution across ageism types
- Correlation between narrative type and voice representation

QUALITATIVE:
- Dominant tropes and metaphors used
- Patterns in whose voices are valued
- How structural inequalities are (in)visible
- Alternative narratives present
- Gaps and silences in coverage

DECOLONIAL INSIGHTS:
- How colonial knowledge systems shape aging discourse
- Whose aging is normalized vs. pathologized
- How neoliberalism influences framing
- Resistance and counter-narratives
- Implications for social justice

RECOMMENDATIONS:
- For journalists covering aging
- For researchers studying aging
- For policymakers
- For older adults and advocates
- For decolonizing gerontology
"""

# ============================================================================
# SAMPLE CODED ENTRY (EXAMPLE)
# ============================================================================

EXAMPLE_CODED_ARTICLE = {
    'title': '"Silver Tsunami" Warning: Healthcare Crisis Looms',
    'url': 'example.com/article',
    'category': 'limiting',
    'phrase': 'aging tsunami',
    
    'CODES': {
        'narrative_type': 'LIMITING',
        'ageism_type': 'HOSTILE',
        'voice_representation': 'EXPERT_DOMINATED',
        'racialized_aging': 'RACE_INVISIBLE',
        'economic_framing': 'BURDEN_FRAME',
        'knowledge_systems': 'BIOMEDICAL_ONLY',
        'agency': 'PASSIVE_RECIPIENT',
        'temporal_orientation': 'DECLINE_NARRATIVE'
    },
    
    'ANALYSIS': {
        'decolonial_notes': """
        - "Tsunami" metaphor dehumanizes older adults as natural disaster
        - Only doctors and economists quoted; no older adult voices
        - Implicitly white/middle-class aging assumed as norm
        - Indigenous elder knowledge completely absent
        - Neoliberal framing: individual burden not social responsibility
        - Who benefits from crisis narrative? Private healthcare industry
        """,
        
        'key_quotes': [
            '"aging population threatens to overwhelm system"',
            '"unprecedented burden on younger generations"',
            '"we can\'t afford this many old people"'
        ],
        
        'colonial_structures_identified': [
            'Ageism intersects with capitalism',
            'Western biomedical model universalized',
            'Productivity-based worth (ableism)',
            'Generational warfare narrative'
        ]
    }
}

# ============================================================================
# VISUALIZATION IDEAS
# ============================================================================

RECOMMENDED_VISUALIZATIONS = """
1. NARRATIVE DISTRIBUTION PIE CHART
   - % limiting, neutral, empowering

2. VOICE REPRESENTATION BAR CHART
   - Frequency of each voice type by narrative category

3. TEMPORAL TREND LINE GRAPH
   - Three narrative types over time (2023)
   - Identify spikes, correlate with events

4. AGEISM TYPE STACKED BAR
   - Benevolent, hostile, ambivalent by outlet/topic

5. INTERSECTIONALITY MATRIX
   - Narrative type × race visibility
   - Narrative type × voice representation

6. WORD CLOUD
   - Metaphors used in limiting narratives
   - Language in empowering narratives

7. NETWORK DIAGRAM
   - Connections between narrative elements
   - Co-occurrence of codes
"""

print("Decolonial Discourse Analysis Framework loaded.")
print("Use this guide alongside aging_narratives_coding_sample.csv")
print("for manual coding of your article sample.")
