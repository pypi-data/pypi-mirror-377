/**
 * Visual Impairments - Low Vision
 * Covers partial sight, low vision, and visual field defects
 */

export const lowVision = {
    category: "Visual Impairments",
    subgroup: "Low Vision", 
    
    detectionPatterns: [
        { pattern: "\\b(low vision|partial sight)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(magnifier|magnification)\\b", type: "assistive_technology", severity: "high" },
        { pattern: "\\b(large print|big text)\\b", type: "accessibility_need", severity: "medium" },
        { pattern: "\\b(blurry vision|poor vision)\\b", type: "symptom", severity: "medium" },
        { pattern: "\\b(peripheral vision|tunnel vision)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(visual field|field of vision)\\b", type: "medical_condition", severity: "medium" },
        { pattern: "\\b(macular degeneration|amd)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(glaucoma|cataracts)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(diabetic retinopathy)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(high contrast|contrast sensitivity)\\b", type: "accessibility_need", severity: "medium" }
    ],

    redactionRules: [
        {
            id: "lowvision_001",
            pattern: "\\b(I have|I've got)\\s+(low vision|macular degeneration|glaucoma)\\b",
            replacement: "I have limited visual clarity",
            flags: "gi"
        },
        {
            id: "lowvision_002",
            pattern: "\\bmy (low vision|poor vision|blurry vision)\\b", 
            replacement: "my visual limitations",
            flags: "gi"
        },
        {
            id: "lowvision_003",
            pattern: "\\bbecause of my (glaucoma|cataracts|macular degeneration)\\b",
            replacement: "due to my visual needs",
            flags: "gi"
        },
        {
            id: "lowvision_004",
            pattern: "\\b(I am|I'm)\\s+partially sighted\\b",
            replacement: "I have variable visual ability",
            flags: "gi"
        }
    ],

    functionalContext: [
        "I benefit from large text sizes and high contrast displays",
        "Good lighting conditions are essential for my visual tasks",
        "Magnification tools help me see fine details clearly", 
        "Simple, uncluttered layouts work best for me",
        "I may need extra time to process visual information",
        "Color coding alone isn't sufficient - I need text labels too",
        "Consistent placement of interface elements helps me navigate"
    ],

    accommodations: {
        digital: [
            "zoom and magnification features",
            "high contrast color schemes",
            "large font options", 
            "adjustable text size",
            "clear visual hierarchy",
            "good color contrast ratios",
            "customizable display settings",
            "reduced visual clutter"
        ],
        physical: [
            "adequate task lighting",
            "glare reduction",
            "large print materials",
            "high contrast signage",
            "clear visual markers",
            "organized layouts"
        ],
        environmental: [
            "controlled lighting conditions",
            "minimal glare and reflections",
            "consistent illumination",
            "clear visual pathways"
        ]
    },

    sensitivity: "high"
};

export default lowVision;