/**
 * Main Detection Engine
 * Scans user prompts for disability-related terms and patterns
 */

export class DetectionEngine {
    constructor(patternsDatabase) {
        this.patterns = patternsDatabase;
        this.confidence = 0.85; // Detection confidence threshold
    }

    /**
     * Analyze prompt for disability mentions
     * @param {string} prompt - User's original prompt
     * @returns {Object} Detection results
     */
    async analyzePrompt(prompt) {
        const detections = [];
        const cleanPrompt = prompt.toLowerCase().trim();

        // Scan through all category patterns
        for (const [category, categoryData] of Object.entries(this.patterns)) {
            for (const [subgroup, patterns] of Object.entries(categoryData.subgroups)) {
                const matches = this.findMatches(cleanPrompt, patterns);
                
                if (matches.length > 0) {
                    detections.push({
                        category,
                        subgroup,
                        matches,
                        confidence: this.calculateConfidence(matches, patterns),
                        position: this.findPositions(prompt, matches)
                    });
                }
            }
        }

        return {
            hasDetections: detections.length > 0,
            detections,
            originalPrompt: prompt,
            analyzedAt: new Date().toISOString()
        };
    }

    /**
     * Find pattern matches in text
     */
    findMatches(text, patterns) {
        const matches = [];
        
        patterns.forEach(pattern => {
            const regex = new RegExp(pattern.pattern, 'gi');
            const match = text.match(regex);
            
            if (match) {
                matches.push({
                    pattern: pattern.pattern,
                    type: pattern.type,
                    matched: match,
                    severity: pattern.severity || 'medium'
                });
            }
        });

        return matches;
    }

    /**
     * Calculate confidence score for detections
     */
    calculateConfidence(matches, allPatterns) {
        if (matches.length === 0) return 0;
        
        const totalWeight = matches.reduce((sum, match) => {
            const weight = match.severity === 'high' ? 1.0 : 
                          match.severity === 'medium' ? 0.7 : 0.4;
            return sum + weight;
        }, 0);

        return Math.min(totalWeight / allPatterns.length, 1.0);
    }

    /**
     * Find positions of matches in original text
     */
    findPositions(originalText, matches) {
        return matches.map(match => {
            const positions = [];
            match.matched.forEach(m => {
                const index = originalText.toLowerCase().indexOf(m);
                if (index !== -1) {
                    positions.push({ start: index, end: index + m.length });
                }
            });
            return { match: match.pattern, positions };
        });
    }
}

export default DetectionEngine;