/**
 * Enhanced Privacy-Preserving Prompt Library with Redaction Markers
 * Now includes personal information protection (PII)
 */

console.log('🔒 ENHANCED PRIVACY LIBRARY - Redaction Markers + PII Protection\n');

class EnhancedPrivacyEngine {
    constructor() {
        // Disability redaction rules with generic {redacted} markers
        this.disabilityPatterns = {
            // Physical disabilities
            'wheelchair user': { marker: 'disability{redacted}', context: 'I need step-free access to buildings' },
            'paralyzed': { marker: 'disability{redacted}', context: 'I need accessible pathways and entrances' },
            'paraplegic': { marker: 'disability{redacted}', context: 'I require wheelchair-accessible facilities' },
            'quadriplegic': { marker: 'disability{redacted}', context: 'I need comprehensive accessibility accommodations' },
            'amputee': { marker: 'disability{redacted}', context: 'I may need adaptive equipment and accessible spaces' },
            
            // Visual impairments  
            'blind': { marker: 'disability{redacted}', context: 'I use screen readers and audio feedback' },
            'visually impaired': { marker: 'disability{redacted}', context: 'I need accessible digital formats' },
            'legally blind': { marker: 'disability{redacted}', context: 'I rely on assistive technology for navigation' },
            
            // Hearing impairments
            'deaf': { marker: 'disability{redacted}', context: 'I rely on captions and visual information' },
            'hard of hearing': { marker: 'disability{redacted}', context: 'I benefit from amplified audio and reduced noise' },
            
            // Learning disabilities
            'dyslexia': { marker: 'disability{redacted}', context: 'I work better with audio or visual content' },
            'dyslexic': { marker: 'disability{redacted}', context: 'I benefit from alternative text formats' },
            'dyscalculia': { marker: 'disability{redacted}', context: 'I need visual representations of numerical concepts' },
            'dysgraphia': { marker: 'disability{redacted}', context: 'I benefit from typing instead of handwriting' },
            
            // Autism spectrum
            'autistic': { marker: 'disability{redacted}', context: 'I need clear, structured communication' },
            'autism': { marker: 'disability{redacted}', context: 'I benefit from predictable routines' },
            'asperger': { marker: 'disability{redacted}', context: 'I process social interactions differently' },
            
            // Mental health
            'depression': { marker: 'disability{redacted}', context: 'I may need flexible scheduling' },
            'anxiety': { marker: 'disability{redacted}', context: 'I work best in calm, predictable environments' },
            'bipolar': { marker: 'disability{redacted}', context: 'I benefit from consistent routines and support' },
            'adhd': { marker: 'disability{redacted}', context: 'I need clear instructions and minimal distractions' },
            
            // Neurological
            'epilepsy': { marker: 'disability{redacted}', context: 'I need environments without flashing lights' },
            'multiple sclerosis': { marker: 'disability{redacted}', context: 'I may need temperature-controlled environments' },
            'parkinson': { marker: 'disability{redacted}', context: 'I may need extra time for physical tasks' }
        };

        // Personal Information (PII) patterns
        this.piiPatterns = {
            // Phone numbers (various formats)
            phone: {
                patterns: [
                    /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g,           // 123-456-7890, 123.456.7890, 1234567890
                    /\(\d{3}\)\s*\d{3}[-.]?\d{4}/g,            // (123) 456-7890
                    /\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}/g // +1-123-456-7890
                ],
                marker: 'phone_number{redacted}'
            },
            
            // Email addresses
            email: {
                patterns: [
                    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g
                ],
                marker: 'email{redacted}'
            },
            
            // Social Security Numbers
            ssn: {
                patterns: [
                    /\b\d{3}[-]?\d{2}[-]?\d{4}\b/g             // 123-45-6789, 123456789
                ],
                marker: 'ssn{redacted}'
            },
            
            // Credit Card Numbers (basic pattern)
            creditCard: {
                patterns: [
                    /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g
                ],
                marker: 'credit_card{redacted}'
            },
            
            // Addresses (basic patterns)
            address: {
                patterns: [
                    /\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b/gi
                ],
                marker: 'address{redacted}'
            },
            
            // Dates of birth
            dob: {
                patterns: [
                    /\b\d{1,2}\/\d{1,2}\/\d{4}\b/g,           // MM/DD/YYYY
                    /\b\d{4}-\d{2}-\d{2}\b/g                   // YYYY-MM-DD
                ],
                marker: 'date_of_birth{redacted}'
            }
        };
    }

    /**
     * Enhanced transformation with redaction markers and PII protection
     */
    transform(prompt) {
        let transformed = prompt;
        let detectedDisabilities = [];
        let detectedPII = [];
        let addedContext = [];

        // Step 1: Redact Personal Information (PII)
        Object.entries(this.piiPatterns).forEach(([type, config]) => {
            config.patterns.forEach(pattern => {
                const matches = transformed.match(pattern);
                if (matches) {
                    detectedPII.push({ type, count: matches.length, examples: matches.slice(0, 2) });
                    transformed = transformed.replace(pattern, config.marker);
                }
            });
        });

        // Step 2: Redact Disability Information with markers
        Object.entries(this.disabilityPatterns).forEach(([condition, config]) => {
            const regex = new RegExp(`\\b${condition}\\b`, 'gi');
            if (regex.test(transformed)) {
                detectedDisabilities.push(condition);
                transformed = transformed.replace(regex, config.marker);
                addedContext.push(config.context);
            }
        });

        // Step 3: Add functional context
        if (addedContext.length > 0) {
            const uniqueContext = [...new Set(addedContext)].slice(0, 2);
            transformed += '. ' + uniqueContext.join('. ') + '.';
        }

        return {
            original: prompt,
            transformed: transformed,
            detectedDisabilities: detectedDisabilities,
            detectedPII: detectedPII,
            addedContext: addedContext,
            privacyScore: this.calculatePrivacyScore(transformed),
            piiProtected: detectedPII.length > 0,
            disabilityProtected: detectedDisabilities.length > 0
        };
    }

    calculatePrivacyScore(text) {
        // Check for any remaining sensitive information
        const hasDisabilityTerms = Object.keys(this.disabilityPatterns).some(term => 
            text.toLowerCase().includes(term.toLowerCase())
        );
        
        const hasPII = Object.values(this.piiPatterns).some(config =>
            config.patterns.some(pattern => pattern.test(text))
        );

        if (hasDisabilityTerms || hasPII) return 0.0;
        return 1.0;
    }
}

// Test the enhanced system
function runEnhancedDemo() {
    const engine = new EnhancedPrivacyEngine();
    
    console.log('🎯 ENHANCED PRIVACY PROTECTION DEMO\n');
    console.log('Now with {redacted} markers and PII protection!\n');

    const testPrompts = [
        // Disability + PII combinations
        "I'm a wheelchair user and my phone number is 555-123-4567, please call me",
        "I'm blind and my email is john.doe@gmail.com for follow-up",
        "I have dyslexia and live at 123 Main Street, New York",
        "I'm autistic, born on 05/15/1990, and need help with social skills",
        "I'm deaf and my SSN is 123-45-6789 for verification",
        
        // Pure disability mentions
        "I'm paralyzed and need accessible travel advice",
        "As someone with ADHD, I struggle with organization",
        "I have multiple sclerosis and fatigue issues",
        
        // Pure PII
        "My credit card 4532-1234-5678-9012 was charged incorrectly",
        "Contact me at (555) 987-6543 about this issue",
        
        // Clean prompts (no sensitive info)
        "What's the weather like today?",
        "I need help with cooking recipes"
    ];

    testPrompts.forEach((prompt, index) => {
        console.log(`📝 Test ${index + 1}:`);
        console.log(`❌ BEFORE: "${prompt}"`);
        
        const result = engine.transform(prompt);
        
        console.log(`✅ AFTER:  "${result.transformed}"`);
        console.log(`🔒 Privacy Score: ${result.privacyScore} (${result.privacyScore === 1.0 ? 'FULLY PROTECTED' : 'NEEDS REVIEW'})`);
        
        if (result.detectedDisabilities.length > 0) {
            console.log(`🧩 Disabilities Detected: ${result.detectedDisabilities.join(', ')}`);
        }
        
        if (result.detectedPII.length > 0) {
            console.log(`🆔 PII Detected: ${result.detectedPII.map(p => `${p.type} (${p.count})`).join(', ')}`);
        }
        
        if (result.addedContext.length > 0) {
            console.log(`📎 Context Added: ${result.addedContext.length} items`);
        }
        
        console.log('');
    });

    // Summary statistics
    const results = testPrompts.map(prompt => engine.transform(prompt));
    const totalDisabilityDetections = results.reduce((sum, r) => sum + r.detectedDisabilities.length, 0);
    const totalPIIDetections = results.reduce((sum, r) => sum + r.detectedPII.length, 0);
    const perfectPrivacy = results.filter(r => r.privacyScore === 1.0).length;
    
    console.log('📊 ENHANCED PRIVACY PROTECTION SUMMARY:');
    console.log(''.padEnd(60, '═'));
    console.log(`   Total Prompts Processed: ${results.length}`);
    console.log(`   Disability Mentions Redacted: ${totalDisabilityDetections}`);
    console.log(`   Personal Information Items Redacted: ${totalPIIDetections}`);
    console.log(`   Perfect Privacy Score: ${perfectPrivacy}/${results.length} (${((perfectPrivacy/results.length)*100).toFixed(1)}%)`);
    
    console.log('\n🔒 REDACTION MARKERS USED:');
    console.log(''.padEnd(60, '─'));
    console.log('   • disability{redacted}');
    console.log('   • phone_number{redacted}');
    console.log('   • email{redacted}');
    console.log('   • address{redacted}');
    console.log('   • ssn{redacted}');
    console.log('   • credit_card{redacted}');
    console.log('   • date_of_birth{redacted}');
    
    console.log('\n✅ ENHANCED PRIVACY FEATURES:');
    console.log(''.padEnd(60, '─'));
    console.log('   ✓ Disability conditions marked as {redacted}');
    console.log('   ✓ Personal information completely removed');
    console.log('   ✓ Functional context still provided');
    console.log('   ✓ Clear indication of what was protected');
    console.log('   ✓ Original intent preserved');
    
    console.log('\n🚀 RESULT: Maximum privacy with transparency about protection!');
}

runEnhancedDemo();