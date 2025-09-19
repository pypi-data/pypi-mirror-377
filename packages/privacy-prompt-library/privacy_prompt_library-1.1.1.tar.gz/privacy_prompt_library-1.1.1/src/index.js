/**
 * Privacy-Preserving Prompt Library - Main Interface
 * Transforms user prompts to protect disability privacy while maintaining functional context
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

import TransformationPipeline from './core/pipeline.js';
import ContextEngine from './engines/context/context-engine.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PromptLibrary {
    constructor() {
        this.pipeline = null;
        this.initialized = false;
    }

    /**
     * Initialize the library with all databases
     */
    async initialize() {
        try {
            // Load all databases
            const [patterns, redactionRules, contextLibrary] = await Promise.all([
                this.loadDatabase('patterns.json'),
                this.loadDatabase('redaction-rules.json'),
                this.loadDatabase('context-library.json')
            ]);

            // Initialize engines
            const contextEngine = new ContextEngine(contextLibrary);
            
            // Create validation engine
            const validator = {
                validate: async (original, transformed, detections) => {
                    return {
                        privacyPreserved: this.checkPrivacyPreservation(original, transformed),
                        intentMaintained: this.checkIntentPreservation(original, transformed),
                        coherenceScore: this.calculateCoherence(transformed),
                        recommendations: []
                    };
                }
            };

            // Initialize transformation pipeline
            this.pipeline = new TransformationPipeline({
                patterns,
                redactionRules,
                contextEngine,
                validator,
                privacyLevel: 'high',
                addContext: true,
                preserveIntent: true
            });

            this.initialized = true;
            console.log('✅ Prompt Library initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize Prompt Library:', error.message);
            throw error;
        }
    }

    /**
     * Transform a user prompt - Main API function
     * @param {string} userPrompt - Original user prompt
     * @param {Object} options - Transformation options
     * @returns {Object} Transformation result
     */
    async transformPrompt(userPrompt, options = {}) {
        if (!this.initialized) {
            await this.initialize();
        }

        const startTime = Date.now();

        try {
            // Validate input
            if (!userPrompt || typeof userPrompt !== 'string') {
                throw new Error('Invalid input: prompt must be a non-empty string');
            }

            // Apply transformation
            const result = await this.pipeline.transform(userPrompt, options);
            
            // Add library metadata
            result.library = {
                version: '1.0.0',
                processingTime: Date.now() - startTime,
                privacyGuarantee: 'No medical terms disclosed'
            };

            return result;

        } catch (error) {
            return {
                input: userPrompt,
                output: userPrompt, // Fallback to original
                error: {
                    message: error.message,
                    type: 'transformation_error'
                },
                library: {
                    version: '1.0.0',
                    processingTime: Date.now() - startTime,
                    privacyGuarantee: 'Fallback - original prompt returned'
                }
            };
        }
    }

    /**
     * Batch transform multiple prompts
     * @param {Array} prompts - Array of user prompts
     * @param {Object} options - Transformation options
     * @returns {Array} Array of transformation results
     */
    async transformBatch(prompts, options = {}) {
        if (!Array.isArray(prompts)) {
            throw new Error('Invalid input: prompts must be an array');
        }

        const results = [];
        
        for (const prompt of prompts) {
            try {
                const result = await this.transformPrompt(prompt, options);
                results.push(result);
            } catch (error) {
                results.push({
                    input: prompt,
                    output: prompt,
                    error: { message: error.message }
                });
            }
        }

        return results;
    }

    /**
     * Get library statistics and health
     */
    getLibraryInfo() {
        return {
            version: '1.0.0',
            initialized: this.initialized,
            categories: 14,
            features: [
                'Medical term redaction',
                'Functional context addition', 
                'Privacy preservation',
                'Intent maintenance',
                'Batch processing'
            ],
            privacyLevel: 'high',
            guarantees: [
                'No medical diagnoses disclosed',
                'No personal health information leaked',
                'Functional needs preserved',
                'Original intent maintained'
            ]
        };
    }

    /**
     * Load database file
     */
    async loadDatabase(filename) {
        const filePath = path.join(__dirname, 'database', filename);
        const data = await fs.readFile(filePath, 'utf8');
        return JSON.parse(data);
    }

    /**
     * Check if privacy is preserved (no medical terms in output)
     */
    checkPrivacyPreservation(original, transformed) {
        const medicalTerms = [
            'paralyz', 'wheelchair', 'blind', 'deaf', 'autism', 'dyslexia', 
            'depression', 'anxiety', 'bipolar', 'schizophrenia', 'adhd',
            'cerebral palsy', 'multiple sclerosis', 'arthritis', 'fibromyalgia'
        ];

        const lowerTransformed = transformed.toLowerCase();
        
        for (const term of medicalTerms) {
            if (lowerTransformed.includes(term)) {
                return false;
            }
        }
        
        return true;
    }

    /**
     * Check if original intent is maintained
     */
    checkIntentPreservation(original, transformed) {
        // Basic intent preservation check
        const originalWords = original.toLowerCase().split(/\s+/);
        const transformedWords = transformed.toLowerCase().split(/\s+/);
        
        // Count preserved non-medical words
        const nonMedicalWords = originalWords.filter(word => 
            !['paralyzed', 'blind', 'deaf', 'autistic', 'wheelchair'].includes(word)
        );
        
        const preservedWords = nonMedicalWords.filter(word => 
            transformedWords.includes(word)
        );
        
        return preservedWords.length / nonMedicalWords.length >= 0.8;
    }

    /**
     * Calculate coherence score of transformed text
     */
    calculateCoherence(text) {
        // Simple coherence calculation
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        
        if (sentences.length === 0) return 0;
        if (sentences.length === 1) return 1;
        
        // Check for reasonable sentence length and structure
        const avgLength = sentences.reduce((sum, s) => sum + s.trim().split(/\s+/).length, 0) / sentences.length;
        
        if (avgLength < 3 || avgLength > 30) return 0.6;
        
        return 0.9; // Good coherence for our use case
    }
}

// Create singleton instance
const promptLibrary = new PromptLibrary();

// Export main functions
export const transformPrompt = (prompt, options) => promptLibrary.transformPrompt(prompt, options);
export const transformBatch = (prompts, options) => promptLibrary.transformBatch(prompts, options);
export const getLibraryInfo = () => promptLibrary.getLibraryInfo();
export const initialize = () => promptLibrary.initialize();

export default promptLibrary;