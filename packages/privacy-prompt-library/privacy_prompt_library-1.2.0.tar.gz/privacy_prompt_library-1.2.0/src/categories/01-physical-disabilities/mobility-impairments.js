/**
 * Physical Disabilities - Mobility Impairments
 * Covers paralysis, amputation, cerebral palsy, spinal cord injuries
 */

export const mobilityImpairments = {
    category: "Physical Disabilities",
    subgroup: "Mobility Impairments",
    
    // Detection patterns for identifying mentions
    detectionPatterns: [
        { pattern: "\\b(wheelchair|wheelchairs?)\\b", type: "assistive_device", severity: "high" },
        { pattern: "\\b(paralyz(ed|is)|paralys(ed|is))\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(paraplegic|quadriplegic)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(spinal cord injury|sci)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(can't walk|cannot walk|unable to walk)\\b", type: "functional_limitation", severity: "medium" },
        { pattern: "\\b(mobility impaired|mobility impairment)\\b", type: "functional_description", severity: "medium" },
        { pattern: "\\b(cerebral palsy|cp)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(amputee|amputation)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(walking aid|walking aids|mobility aid)\\b", type: "assistive_device", severity: "medium" },
        { pattern: "\\b(crutches|walker|walking frame)\\b", type: "assistive_device", severity: "medium" }
    ],

    // Redaction rules - replace medical terms with functional language
    redactionRules: [
        {
            id: "mobility_001",
            pattern: "\\b(I am|I'm)\\s+(a\\s+)?wheelchair user\\b",
            replacement: "I use mobility equipment",
            flags: "gi",
            contextual: true
        },
        {
            id: "mobility_002", 
            pattern: "\\b(I am|I'm)\\s+(paralyz(ed|is)|paralys(ed|is))\\b",
            replacement: "I have limited mobility",
            flags: "gi",
            contextual: true
        },
        {
            id: "mobility_003",
            pattern: "\\b(I am|I'm)\\s+(paraplegic|quadriplegic)\\b", 
            replacement: "I have mobility considerations",
            flags: "gi",
            contextual: true
        },
        {
            id: "mobility_004",
            pattern: "\\bmy wheelchair\\b",
            replacement: "my mobility device",
            flags: "gi"
        },
        {
            id: "mobility_005",
            pattern: "\\bbecause of my paralysis\\b",
            replacement: "due to my mobility needs",
            flags: "gi"
        },
        {
            id: "mobility_006",
            pattern: "\\bas a wheelchair user\\b",
            replacement: "as someone who requires accessible spaces", 
            flags: "gi"
        },
        {
            id: "mobility_007",
            pattern: "\\b(I have|I've got)\\s+paralysis\\b",
            replacement: "I experience mobility challenges",
            flags: "gi"
        }
    ],

    // Functional context to add for better AI responses
    functionalContext: [
        "I need step-free access to buildings and entrances",
        "Elevator access is essential for multi-story buildings", 
        "Wide doorways (minimum 32 inches) and clear pathways work best for me",
        "Accessible parking close to entrances is helpful",
        "Level surfaces without steps, curbs, or significant slopes are important",
        "Accessible restrooms with proper clearance space are necessary",
        "Tables and counters at accessible heights improve my experience"
    ],

    // Alternative phrasing options
    alternativePhrasings: {
        personFirst: "person who uses a wheelchair",
        identityFirst: "wheelchair user", 
        neutral: "requires wheelchair accessibility",
        functional: "uses mobility assistance"
    },

    // Common scenarios for this subgroup
    scenarios: [
        "Attending meetings in office buildings",
        "Shopping at retail stores and malls", 
        "Using public transportation",
        "Dining at restaurants",
        "Accessing healthcare facilities",
        "Attending educational institutions",
        "Visiting entertainment venues"
    ],

    // Specific accommodations needed
    accommodations: {
        physical: [
            "ramps and level entrances",
            "elevator access", 
            "accessible parking spaces",
            "wide doorways and hallways",
            "accessible restrooms",
            "lowered counters and service areas",
            "clear floor space and turning areas"
        ],
        digital: [
            "voice commands for devices",
            "accessible website navigation", 
            "mobile device compatibility",
            "alternative input methods"
        ],
        communication: [
            "written instructions when verbal isn't sufficient",
            "visual aids and diagrams",
            "patient communication allowing extra time"
        ],
        environmental: [
            "climate-controlled environments",
            "adequate lighting",
            "minimal background noise for concentration",
            "comfortable seating options"
        ]
    },

    // Privacy sensitivity level
    sensitivity: "high"
};

export default mobilityImpairments;