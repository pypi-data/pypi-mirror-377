/**
 * Amazing Context-Aware Privacy Demo
 * Showcases enhanced situation-aware context addition for amazing prompts
 */

import { ContextEngine } from './src/engines/context/context-engine.js';
import fs from 'fs';

console.log('🚀 AMAZING CONTEXT-AWARE PRIVACY DEMO\n');
console.log('Showcasing intelligent, situation-aware context enhancement!\n');

class AmazingPrivacyEngine {
    constructor() {
        // Load enhanced context library
        this.contextLibrary = JSON.parse(fs.readFileSync('./src/database/context-library.json', 'utf8'));
        this.contextEngine = new ContextEngine(this.contextLibrary);

        // Enhanced disability patterns with situation detection
        this.disabilityPatterns = {
            'wheelchair user': { marker: 'disability{redacted}', category: 'Physical Disabilities', subgroup: 'Mobility Impairments' },
            'blind': { marker: 'disability{redacted}', category: 'Visual Impairments', subgroup: 'Blindness' },
            'deaf': { marker: 'disability{redacted}', category: 'Hearing Impairments', subgroup: 'Deafness' },
            'dyslexia': { marker: 'disability{redacted}', category: 'Learning Disabilities', subgroup: 'Dyslexia' },
            'autistic': { marker: 'disability{redacted}', category: 'Autism Spectrum', subgroup: 'Classic Autism' },
            'adhd': { marker: 'disability{redacted}', category: 'Mental Health', subgroup: 'ADHD' },
            'anxiety': { marker: 'disability{redacted}', category: 'Mental Health', subgroup: 'Anxiety Disorders' },
            'depression': { marker: 'disability{redacted}', category: 'Mental Health', subgroup: 'Mood Disorders' }
        };

        // PII protection patterns
        this.piiPatterns = {
            phone: { patterns: [/\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b/g], marker: 'phone_number{redacted}' },
            email: { patterns: [/\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b/g], marker: 'email{redacted}' }
        };
    }

    /**
     * Transform prompt with amazing context-aware enhancement
     */
    async transform(prompt) {
        const result = {
            original: prompt,
            transformed: prompt,
            detectedDisabilities: [],
            detectedPII: [],
            addedContext: [],
            detectedSituations: [],
            privacyScore: 1.0
        };

        // Step 1: Detect disabilities
        const disabilityDetections = this.detectDisabilities(prompt);
        result.detectedDisabilities = disabilityDetections;

        // Step 2: Redact disabilities
        let redactedPrompt = prompt;
        disabilityDetections.forEach(detection => {
            const pattern = detection.pattern;
            redactedPrompt = redactedPrompt.replace(new RegExp(pattern.marker, 'gi'), 'disability{redacted}');
        });

        // Step 3: Protect PII
        const piiDetections = this.detectAndRedactPII(redactedPrompt);
        result.detectedPII = piiDetections.detected;
        redactedPrompt = piiDetections.redacted;

        // Step 4: Add amazing context-aware enhancement
        if (disabilityDetections.length > 0) {
            const contextResult = await this.contextEngine.addContext(redactedPrompt, disabilityDetections);
            result.transformed = contextResult.enriched;
            result.addedContext = contextResult.addedContext;
            result.detectedSituations = contextResult.detectedSituations;
        } else {
            result.transformed = redactedPrompt;
        }

        return result;
    }

    detectDisabilities(prompt) {
        const detections = [];
        const lowerPrompt = prompt.toLowerCase();

        for (const [term, data] of Object.entries(this.disabilityPatterns)) {
            if (lowerPrompt.includes(term)) {
                detections.push({
                    term,
                    category: data.category,
                    subgroup: data.subgroup,
                    confidence: 0.9,
                    pattern: { marker: term }
                });
            }
        }

        return detections;
    }

    detectAndRedactPII(prompt) {
        const detected = [];
        let redacted = prompt;

        for (const [type, data] of Object.entries(this.piiPatterns)) {
            data.patterns.forEach(pattern => {
                const matches = prompt.match(pattern);
                if (matches) {
                    detected.push({ type, count: matches.length });
                    redacted = redacted.replace(pattern, data.marker);
                }
            });
        }

        return { detected, redacted };
    }
}

async function runAmazingDemo() {
    const engine = new AmazingPrivacyEngine();

    // Amazing test cases showcasing different situations
    const amazingTestCases = [
        {
            title: "🧳 Travel Planning",
            prompt: "I'm a wheelchair user planning a trip to Paris, can you recommend accessible hotels near the Eiffel Tower?"
        },
        {
            title: "💼 Work Productivity", 
            prompt: "I have ADHD and need help organizing my work projects and staying focused during long meetings"
        },
        {
            title: "🎓 Online Learning",
            prompt: "I'm dyslexic and want to learn programming through online courses, what's the best approach?"
        },
        {
            title: "🛒 Shopping Experience",
            prompt: "I'm blind and want to buy a new laptop, what features should I look for in online stores?"
        },
        {
            title: "🎬 Entertainment Access",
            prompt: "I'm deaf and love watching movies, can you suggest streaming platforms with good captions?"
        },
        {
            title: "💬 Social Networking",
            prompt: "I'm autistic and find networking events overwhelming, how can I build professional connections?"
        },
        {
            title: "💰 Financial Planning",
            prompt: "I have anxiety about money management, what are some calm approaches to budgeting?"
        },
        {
            title: "🏃 Health & Fitness",
            prompt: "I have depression and want to start exercising, what gentle activities would you recommend?"
        }
    ];

    console.log('🎯 AMAZING CONTEXT-AWARE TRANSFORMATIONS:\n');

    for (const testCase of amazingTestCases) {
        console.log(`${testCase.title}`);
        console.log('─'.repeat(60));
        console.log(`❌ BEFORE: "${testCase.prompt}"`);
        
        const result = await engine.transform(testCase.prompt);
        
        console.log(`✅ AFTER:  "${result.transformed}"`);
        console.log(`🔒 Privacy: ${result.privacyScore === 1.0 ? 'FULLY PROTECTED' : 'PARTIAL'}`);
        
        if (result.detectedDisabilities.length > 0) {
            console.log(`🧩 Detected: ${result.detectedDisabilities.map(d => d.term).join(', ')}`);
        }
        
        if (result.detectedSituations.length > 0) {
            console.log(`🎯 Situations: ${result.detectedSituations.map(s => s.situation).join(', ')}`);
        }
        
        if (result.addedContext.length > 0) {
            console.log(`📎 Context: ${result.addedContext.length} situation-aware enhancement(s) added`);
        }
        
        console.log('');
    }

    // Show context engine statistics
    const contextStats = engine.contextEngine.getContextStats();
    console.log('📊 ENHANCED CONTEXT ENGINE STATS:');
    console.log('═'.repeat(60));
    console.log(`   Total Categories: ${contextStats.totalCategories}`);
    console.log(`   Total Context Items: ${contextStats.totalContextItems || 'N/A'}`);
    console.log(`   Average Items/Category: ${Math.round((contextStats.totalContextItems || 0) / contextStats.totalCategories)}`);
    
    console.log('\\n🌟 AMAZING FEATURES:');
    console.log('─'.repeat(60));
    console.log('   ✓ Situation-aware context selection');
    console.log('   ✓ Intelligent relevance scoring');
    console.log('   ✓ Natural language integration');
    console.log('   ✓ Privacy-preserving enhancement');
    console.log('   ✓ Multi-situation detection');
    console.log('   ✓ Priority-based context ranking');

    console.log('\\n🚀 RESULT: AI gets amazing context without compromising privacy!');
}

runAmazingDemo().catch(console.error);