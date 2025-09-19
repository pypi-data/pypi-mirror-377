/**
 * Visual Impairments - Blindness
 * Covers total blindness, legal blindness, and severe visual impairment
 */

export const blindness = {
    category: "Visual Impairments", 
    subgroup: "Blindness",
    
    detectionPatterns: [
        { pattern: "\\b(blind|blindness)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(can't see|cannot see|unable to see)\\b", type: "functional_limitation", severity: "high" },
        { pattern: "\\b(visually impaired|vision impaired)\\b", type: "functional_description", severity: "medium" },
        { pattern: "\\b(screen reader|jaws|nvda|voiceover)\\b", type: "assistive_technology", severity: "high" },
        { pattern: "\\b(braille|tactile)\\b", type: "assistive_technology", severity: "high" },
        { pattern: "\\b(white cane|guide dog|seeing eye dog)\\b", type: "assistive_device", severity: "high" },
        { pattern: "\\b(legally blind|total blindness)\\b", type: "medical_condition", severity: "high" },
        { pattern: "\\b(vision loss|sight loss)\\b", type: "medical_condition", severity: "medium" },
        { pattern: "\\b(audio description|alt text)\\b", type: "accessibility_feature", severity: "medium" }
    ],

    redactionRules: [
        {
            id: "blind_001",
            pattern: "\\b(I am|I'm)\\s+blind\\b",
            replacement: "I use non-visual methods",
            flags: "gi"
        },
        {
            id: "blind_002",
            pattern: "\\b(I am|I'm)\\s+visually impaired\\b", 
            replacement: "I process information through audio and touch",
            flags: "gi"
        },
        {
            id: "blind_003",
            pattern: "\\bbecause (I am|I'm) blind\\b",
            replacement: "since I rely on screen readers",
            flags: "gi"
        },
        {
            id: "blind_004",
            pattern: "\\bmy blindness\\b",
            replacement: "my need for accessible formats", 
            flags: "gi"
        },
        {
            id: "blind_005",
            pattern: "\\bas a blind person\\b",
            replacement: "as someone who uses assistive technology",
            flags: "gi"
        },
        {
            id: "blind_006",
            pattern: "\\b(I can't see|I cannot see)\\b",
            replacement: "I access information through audio",
            flags: "gi"
        }
    ],

    functionalContext: [
        "I use screen readers to access digital content",
        "Audio descriptions and text alternatives for images are essential", 
        "Clear heading structures and proper labels help me navigate",
        "Keyboard navigation is my primary input method",
        "High contrast text and large fonts benefit my remaining vision",
        "Tactile feedback and audio cues improve my interaction experience",
        "Descriptive language helps me understand visual content"
    ],

    accommodations: {
        digital: [
            "screen reader compatibility",
            "keyboard-only navigation",
            "alt text for all images",
            "proper heading structure",
            "descriptive link text", 
            "audio descriptions for video",
            "accessible form labels",
            "focus indicators",
            "consistent navigation"
        ],
        physical: [
            "tactile markers and signage",
            "audio announcements",
            "consistent layout and organization",
            "obstacle-free pathways",
            "good lighting for residual vision",
            "high contrast visual elements"
        ],
        communication: [
            "verbal descriptions of visual content",
            "audio formats for documents",
            "clear speaking pace",
            "detailed directions and instructions",
            "confirmation of visual information"
        ],
        technological: [
            "screen reading software",
            "voice control systems", 
            "braille displays",
            "audio books and materials",
            "text-to-speech applications",
            "magnification software"
        ]
    },

    scenarios: [
        "Reading and writing documents",
        "Navigating websites and apps",
        "Using computer software",
        "Accessing printed materials", 
        "Following visual presentations",
        "Understanding charts and graphs",
        "Shopping online or in stores",
        "Using public transportation"
    ],

    sensitivity: "high"
};

export default blindness;