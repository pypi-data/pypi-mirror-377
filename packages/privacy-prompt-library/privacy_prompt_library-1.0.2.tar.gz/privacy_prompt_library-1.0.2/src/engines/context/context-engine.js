/**
 * Enhanced Context Enrichment Engine
 * Adds intelligent, situation-aware functional context without revealing medical conditions
 */

export class ContextEngine {
    constructor(contextDatabase) {
        this.contextDb = contextDatabase;
        this.maxContextItems = 2; // Limit to avoid overwhelming output
        this.situationKeywords = {
            travel: ['travel', 'trip', 'vacation', 'hotel', 'flight', 'destination', 'visit'],
            work: ['work', 'job', 'office', 'meeting', 'project', 'career', 'professional', 'workplace'],
            education: ['learn', 'study', 'school', 'course', 'class', 'education', 'university', 'training'],
            technology: ['app', 'software', 'website', 'digital', 'computer', 'tech', 'online', 'platform'],
            social: ['social', 'friends', 'party', 'event', 'gathering', 'networking', 'community'],
            health: ['health', 'medical', 'doctor', 'therapy', 'treatment', 'wellness', 'exercise'],
            shopping: ['buy', 'purchase', 'shop', 'store', 'market', 'product', 'price'],
            entertainment: ['movie', 'music', 'game', 'show', 'entertainment', 'fun', 'activity'],
            finance: ['money', 'budget', 'financial', 'bank', 'investment', 'cost', 'payment'],
            communication: ['call', 'email', 'message', 'communicate', 'contact', 'phone', 'text']
        };
    }

    /**
     * Add intelligent, situation-aware context based on detections and prompt content
     * @param {string} prompt - Redacted prompt
     * @param {Array} detections - Detected disability categories
     * @returns {Object} Enriched prompt with contextually relevant information
     */
    async addContext(prompt, detections) {
        const contextItems = [];
        const usedCategories = new Set();
        
        // Analyze prompt for situational context
        const detectedSituations = this.analyzeSituation(prompt);

        // Select most relevant context for each detection
        for (const detection of detections) {
            const categoryKey = `${detection.category}-${detection.subgroup}`;
            
            if (!usedCategories.has(categoryKey)) {
                const context = this.selectSituationAwareContext(detection, detectedSituations, prompt);
                if (context.length > 0) {
                    contextItems.push(...context);
                    usedCategories.add(categoryKey);
                }
            }
        }

        // Limit and prioritize context items
        const selectedContext = this.prioritizeContext(contextItems, detections, detectedSituations);
        
        // Integrate context into prompt
        const enrichedPrompt = this.integrateContext(prompt, selectedContext);

        return {
            original: prompt,
            enriched: enrichedPrompt,
            addedContext: selectedContext,
            contextSources: Array.from(usedCategories),
            detectedSituations: detectedSituations,
            enrichedAt: new Date().toISOString()
        };
    }

    /**
     * Analyze prompt to detect situational context
     */
    analyzeSituation(prompt) {
        const lowerPrompt = prompt.toLowerCase();
        const detectedSituations = [];
        
        for (const [situation, keywords] of Object.entries(this.situationKeywords)) {
            const matchCount = keywords.filter(keyword => lowerPrompt.includes(keyword)).length;
            if (matchCount > 0) {
                detectedSituations.push({
                    situation,
                    relevance: matchCount,
                    keywords: keywords.filter(keyword => lowerPrompt.includes(keyword))
                });
            }
        }
        
        return detectedSituations.sort((a, b) => b.relevance - a.relevance);
    }

    /**
     * Select context items that match both the disability and the situation
     */
    selectSituationAwareContext(detection, detectedSituations, prompt) {
        const categoryData = this.contextDb[detection.category];
        if (!categoryData) return [];

        const subgroupData = categoryData[detection.subgroup];
        if (!subgroupData || !Array.isArray(subgroupData)) return [];

        // Filter context by situation relevance
        let relevantContext = subgroupData;
        
        if (detectedSituations.length > 0) {
            const topSituations = detectedSituations.slice(0, 2).map(s => s.situation);
            
            relevantContext = subgroupData.filter(item => {
                if (!item.situations) return true; // Include items without situation filters
                return item.situations.some(sit => topSituations.includes(sit));
            });
            
            // If no situation-specific context found, fall back to general items
            if (relevantContext.length === 0) {
                relevantContext = subgroupData.filter(item => !item.situations);
            }
        }

        // Prioritize by priority level and situation relevance
        return relevantContext
            .sort((a, b) => {
                const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
                return priorityOrder[b.priority] - priorityOrder[a.priority];
            })
            .slice(0, 2); // Max 2 items per detection
    }

    /**
     * Select appropriate context for a specific detection
     */
    selectContextForDetection(detection) {
        const categoryContext = this.contextDb[detection.category];
        
        if (!categoryContext || !categoryContext[detection.subgroup]) {
            return [];
        }

        const subgroupContext = categoryContext[detection.subgroup];
        
        // Select context based on confidence and relevance
        return subgroupContext.filter(item => {
            return item.priority === 'high' || 
                   (item.priority === 'medium' && detection.confidence > 0.8);
        }).slice(0, 2); // Limit per subgroup
    }

    /**
     * Prioritize context items to avoid overwhelming output
     */
    prioritizeContext(contextItems, detections) {
        // Remove duplicates
        const uniqueItems = [...new Set(contextItems.map(item => item.text))];
        
        // Sort by priority and relevance
        const prioritized = uniqueItems.map(text => {
            const item = contextItems.find(c => c.text === text);
            return {
                text,
                priority: item.priority,
                relevance: this.calculateRelevance(text, detections)
            };
        }).sort((a, b) => {
            // Sort by priority first, then relevance
            const priorityWeight = { high: 3, medium: 2, low: 1 };
            const aPriority = priorityWeight[a.priority] || 1;
            const bPriority = priorityWeight[b.priority] || 1;
            
            if (aPriority !== bPriority) {
                return bPriority - aPriority;
            }
            
            return b.relevance - a.relevance;
        });

        // Return top items
        return prioritized.slice(0, this.maxContextItems).map(item => item.text);
    }

    /**
     * Calculate relevance score for context item
     */
    calculateRelevance(contextText, detections) {
        let relevanceScore = 0;
        
        detections.forEach(detection => {
            // Higher relevance for higher confidence detections
            relevanceScore += detection.confidence;
            
            // Bonus for multiple related detections
            if (detection.matches && detection.matches.length > 1) {
                relevanceScore += 0.2;
            }
        });

        return relevanceScore;
    }

    /**
     * Integrate context into the prompt naturally
     */
    integrateContext(prompt, contextItems) {
        if (contextItems.length === 0) {
            return prompt;
        }

        // Add context as additional sentences
        const contextString = contextItems.join('. ');
        
        // Determine best placement
        if (prompt.endsWith('.') || prompt.endsWith('!') || prompt.endsWith('?')) {
            return `${prompt} ${contextString}.`;
        } else {
            return `${prompt}. ${contextString}.`;
        }
    }

    /**
     * Get context statistics
     */
    getContextStats() {
        return {
            totalCategories: Object.keys(this.contextDb).length,
            totalContextItems: this.getTotalContextItems(),
            averageItemsPerCategory: this.getAverageItemsPerCategory()
        };
    }

    getTotalContextItems() {
        let total = 0;
        for (const category of Object.values(this.contextDb)) {
            for (const subgroup of Object.values(category)) {
                total += subgroup.length;
            }
        }
        return total;
    }

    getAverageItemsPerCategory() {
        const totalItems = this.getTotalContextItems();
        const totalCategories = Object.keys(this.contextDb).length;
        return totalCategories > 0 ? totalItems / totalCategories : 0;
    }
}

export default ContextEngine;