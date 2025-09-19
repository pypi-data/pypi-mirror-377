/**
 * Transformation Pipeline
 * Orchestrates the complete prompt transformation process
 */

import DetectionEngine from './detector.js';
import RedactionEngine from './redactor.js';

export class TransformationPipeline {
    constructor(config) {
        this.detectionEngine = new DetectionEngine(config.patterns);
        this.redactionEngine = new RedactionEngine(config.redactionRules);
        this.contextEngine = config.contextEngine;
        this.validator = config.validator;
        
        // Pipeline configuration
        this.config = {
            privacyLevel: config.privacyLevel || 'high',
            addContext: config.addContext !== false,
            preserveIntent: config.preserveIntent !== false,
            maxProcessingTime: config.maxProcessingTime || 5000
        };
    }

    /**
     * Main transformation function
     * @param {string} userPrompt - Original user prompt
     * @param {Object} options - Transformation options
     * @returns {Object} Complete transformation result
     */
    async transform(userPrompt, options = {}) {
        const startTime = Date.now();
        
        try {
            // Step 1: Input validation
            this.validateInput(userPrompt);

            // Step 2: Detection phase
            const detectionResult = await this.detectionEngine.analyzePrompt(userPrompt);

            // Step 3: Redaction phase (if detections found)
            let redactionResult = { 
                redacted: userPrompt, 
                appliedRules: [], 
                privacyScore: 1.0 
            };
            
            if (detectionResult.hasDetections) {
                redactionResult = await this.redactionEngine.redactPrompt(
                    userPrompt, 
                    detectionResult.detections
                );
            }

            // Step 4: Context enrichment
            let enrichedPrompt = redactionResult.redacted;
            let addedContext = [];
            
            if (this.config.addContext && detectionResult.hasDetections) {
                const contextResult = await this.contextEngine.addContext(
                    enrichedPrompt,
                    detectionResult.detections
                );
                enrichedPrompt = contextResult.enriched;
                addedContext = contextResult.addedContext;
            }

            // Step 5: Final validation
            const validationResult = await this.validator.validate(
                userPrompt,
                enrichedPrompt,
                detectionResult.detections
            );

            // Step 6: Compile final result
            const processingTime = Date.now() - startTime;
            
            return this.compileResult({
                original: userPrompt,
                transformed: enrichedPrompt,
                detectionResult,
                redactionResult,
                addedContext,
                validationResult,
                processingTime,
                options
            });

        } catch (error) {
            return this.handleError(error, userPrompt, startTime);
        }
    }

    /**
     * Validate input prompt
     */
    validateInput(prompt) {
        if (!prompt || typeof prompt !== 'string') {
            throw new Error('Invalid input: prompt must be a non-empty string');
        }
        
        if (prompt.length > 10000) {
            throw new Error('Input too long: maximum 10,000 characters allowed');
        }
        
        if (prompt.trim().length === 0) {
            throw new Error('Invalid input: prompt cannot be empty');
        }
    }

    /**
     * Compile final transformation result
     */
    compileResult(data) {
        return {
            // Core outputs
            input: data.original,
            output: data.transformed,
            
            // Processing metadata
            metadata: {
                hasDetections: data.detectionResult.hasDetections,
                detectedCategories: data.detectionResult.detections.map(d => ({
                    category: d.category,
                    subgroup: d.subgroup,
                    confidence: d.confidence
                })),
                appliedRules: data.redactionResult.appliedRules,
                addedContext: data.addedContext,
                privacyScore: data.redactionResult.privacyScore,
                coherenceScore: data.validationResult.coherenceScore,
                processingTime: data.processingTime,
                transformedAt: new Date().toISOString()
            },
            
            // Quality assurance
            validation: {
                privacyPreserved: data.validationResult.privacyPreserved,
                intentMaintained: data.validationResult.intentMaintained,
                coherenceScore: data.validationResult.coherenceScore,
                recommendedChanges: data.validationResult.recommendations
            },
            
            // Configuration used
            config: {
                privacyLevel: this.config.privacyLevel,
                contextAdded: this.config.addContext,
                intentPreserved: this.config.preserveIntent
            }
        };
    }

    /**
     * Handle processing errors
     */
    handleError(error, originalPrompt, startTime) {
        const processingTime = Date.now() - startTime;
        
        return {
            input: originalPrompt,
            output: originalPrompt, // Fallback to original
            error: {
                message: error.message,
                type: error.constructor.name,
                processingTime
            },
            metadata: {
                hasDetections: false,
                detectedCategories: [],
                appliedRules: [],
                addedContext: [],
                privacyScore: 0.0,
                coherenceScore: 0.0,
                transformedAt: new Date().toISOString()
            }
        };
    }

    /**
     * Get pipeline statistics
     */
    getStatistics() {
        return {
            totalProcessed: this.stats?.totalProcessed || 0,
            averageProcessingTime: this.stats?.averageProcessingTime || 0,
            privacySuccessRate: this.stats?.privacySuccessRate || 0,
            mostCommonCategories: this.stats?.mostCommonCategories || []
        };
    }
}

export default TransformationPipeline;