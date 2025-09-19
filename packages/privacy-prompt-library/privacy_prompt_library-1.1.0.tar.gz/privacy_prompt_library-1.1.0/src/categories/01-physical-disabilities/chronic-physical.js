/**
 * Physical Disabilities - Chronic Physical Conditions  
 * Covers arthritis, muscular dystrophy, multiple sclerosis, chronic pain
 */

export const chronicPhysical = {
    category: "Physical Disabilities",
    subgroup: "Chronic Physical Conditions",
    
    detectionPatterns: [
        { pattern: "\\b(arthritis|arthritic)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(muscular dystrophy|md)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(multiple sclerosis|ms)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(chronic pain|persistent pain)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(fibromyalgia|fibro)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(lupus|sle)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(chronic fatigue|cfs)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(joint pain|muscle weakness)\\b", type: "symptom", severity: "medium" },
        { pattern: "\\b(mobility issues|movement difficulties)\\b", type: "functional_limitation", severity: "medium" },
        { pattern: "\\b(fatigue|exhaustion|low energy)\\b", type: "symptom", severity: "low" }
    ],

    redactionRules: [
        {
            id: "chronic_001",
            pattern: "\\b(I have|I've got)\\s+(arthritis|muscular dystrophy|multiple sclerosis)\\b",
            replacement: "I have a chronic physical condition",
            flags: "gi"
        },
        {
            id: "chronic_002", 
            pattern: "\\bmy (arthritis|fibromyalgia|lupus|ms)\\b",
            replacement: "my chronic condition",
            flags: "gi"
        },
        {
            id: "chronic_003",
            pattern: "\\bbecause of my (chronic pain|arthritis|fibromyalgia)\\b",
            replacement: "due to my physical limitations",
            flags: "gi"
        },
        {
            id: "chronic_004",
            pattern: "\\b(I am|I'm)\\s+chronically ill\\b",
            replacement: "I manage ongoing physical challenges",
            flags: "gi"
        },
        {
            id: "chronic_005",
            pattern: "\\bmy chronic pain\\b",
            replacement: "my physical discomfort",
            flags: "gi"
        }
    ],

    functionalContext: [
        "I may need frequent breaks during long activities",
        "Flexible scheduling helps accommodate unpredictable symptoms", 
        "Climate-controlled environments reduce discomfort",
        "Ergonomic seating and workspace setups are beneficial",
        "I may have varying energy levels throughout the day",
        "Stress reduction techniques help manage symptoms",
        "Access to quiet spaces for rest periods is helpful"
    ],

    accommodations: {
        physical: [
            "ergonomic furniture and equipment",
            "adjustable workstations", 
            "temperature control",
            "comfortable seating options",
            "accessible rest areas",
            "minimal physical demands",
            "flexible physical positioning"
        ],
        temporal: [
            "flexible scheduling",
            "frequent breaks",
            "variable work hours",
            "deadline extensions when needed",
            "pace adjustment options"
        ],
        environmental: [
            "stress-free environments",
            "noise reduction",
            "good lighting conditions",
            "air quality considerations"
        ]
    },

    sensitivity: "high"
};

export default chronicPhysical;