/**
 * Redaction Engine
 * Replaces disability mentions with privacy-preserving functional language
 */

export class RedactionEngine {
    constructor(redactionRules) {
        this.rules = redactionRules;
        this.preserveContext = true;
    }

    /**
     * Apply redaction rules to transform prompt
     * @param {string} prompt - Original prompt
     * @param {Array} detections - Detected disability mentions
     * @returns {Object} Redacted prompt with metadata
     */
    async redactPrompt(prompt, detections) {
        let redactedPrompt = prompt;
        const appliedRules = [];
        const redactionLog = [];

        // Apply category-specific redaction rules
        for (const detection of detections) {
            const categoryRules = this.rules[detection.category];
            
            if (categoryRules && categoryRules[detection.subgroup]) {
                const subgroupRules = categoryRules[detection.subgroup];
                
                for (const rule of subgroupRules) {
                    const result = this.applyRule(redactedPrompt, rule, detection);
                    
                    if (result.applied) {
                        redactedPrompt = result.text;
                        appliedRules.push(rule.id);
                        redactionLog.push({
                            rule: rule.id,
                            original: result.original,
                            replacement: result.replacement,
                            position: result.position
                        });
                    }
                }
            }
        }

        return {
            original: prompt,
            redacted: redactedPrompt,
            appliedRules,
            redactionLog,
            privacyScore: this.calculatePrivacyScore(redactionLog),
            processedAt: new Date().toISOString()
        };
    }

    /**
     * Apply a single redaction rule
     */
    applyRule(text, rule, detection) {
        const regex = new RegExp(rule.pattern, rule.flags || 'gi');
        const matches = text.match(regex);
        
        if (matches) {
            const replacement = this.generateReplacement(rule, detection);
            const originalMatch = matches[0];
            const newText = text.replace(regex, replacement);
            
            return {
                applied: true,
                text: newText,
                original: originalMatch,
                replacement: replacement,
                position: text.indexOf(originalMatch)
            };
        }

        return { applied: false, text };
    }

    /**
     * Generate appropriate replacement text
     */
    generateReplacement(rule, detection) {
        let replacement = rule.replacement;

        // Handle dynamic replacements based on context
        if (rule.contextual) {
            const contextMap = {
                'mobility': 'I use mobility assistance',
                'visual': 'I use alternative visual methods',
                'hearing': 'I use alternative communication methods',
                'cognitive': 'I process information differently'
            };

            const contextKey = this.getContextKey(detection.category);
            replacement = contextMap[contextKey] || replacement;
        }

        return replacement;
    }

    /**
     * Get context key for replacement generation
     */
    getContextKey(category) {
        const keyMap = {
            'Physical Disabilities': 'mobility',
            'Visual Impairments': 'visual',
            'Hearing Impairments': 'hearing',
            'Intellectual Disabilities': 'cognitive',
            'Learning Disabilities': 'cognitive'
        };

        return keyMap[category] || 'general';
    }

    /**
     * Calculate privacy protection score
     */
    calculatePrivacyScore(redactionLog) {
        if (redactionLog.length === 0) return 1.0;

        const totalRedactions = redactionLog.length;
        const highRiskTermsRedacted = redactionLog.filter(
            log => log.rule.includes('medical') || log.rule.includes('diagnostic')
        ).length;

        return Math.min((totalRedactions + highRiskTermsRedacted) / (totalRedactions * 2), 1.0);
    }
}

export default RedactionEngine;