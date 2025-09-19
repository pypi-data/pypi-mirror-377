/**
 * Test Suite for Privacy-Preserving Prompt Library
 */

import { transformPrompt, initialize, getLibraryInfo } from '../src/index.js';

class TestRunner {
    constructor() {
        this.tests = [];
        this.results = {
            passed: 0,
            failed: 0,
            total: 0
        };
    }

    /**
     * Add a test case
     */
    test(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    /**
     * Run all tests
     */
    async runAll() {
        console.log('🧪 Starting Privacy-Preserving Prompt Library Tests...\n');
        
        // Initialize library first
        await initialize();
        
        for (const test of this.tests) {
            try {
                await test.testFunction();
                this.results.passed++;
                console.log(`✅ ${test.name}`);
            } catch (error) {
                this.results.failed++;
                console.log(`❌ ${test.name}`);
                console.log(`   Error: ${error.message}\n`);
            }
            this.results.total++;
        }

        this.printSummary();
    }

    /**
     * Print test summary
     */
    printSummary() {
        console.log('\n📊 Test Results Summary:');
        console.log(`   Total Tests: ${this.results.total}`);
        console.log(`   Passed: ${this.results.passed}`);
        console.log(`   Failed: ${this.results.failed}`);
        console.log(`   Success Rate: ${((this.results.passed / this.results.total) * 100).toFixed(1)}%`);
        
        if (this.results.failed === 0) {
            console.log('\n🎉 All tests passed! Privacy library is working correctly.');
        } else {
            console.log('\n⚠️ Some tests failed. Please review the errors above.');
        }
    }

    /**
     * Assert helper
     */
    assert(condition, message) {
        if (!condition) {
            throw new Error(message);
        }
    }
}

// Create test runner
const runner = new TestRunner();

// Test 1: Basic wheelchair transformation
runner.test('Wheelchair user redaction', async () => {
    const input = "I'm a wheelchair user and need help planning a trip to Paris";
    const result = await transformPrompt(input);
    
    runner.assert(
        !result.output.toLowerCase().includes('wheelchair'),
        'Output should not contain "wheelchair"'
    );
    
    runner.assert(
        result.output.includes('mobility equipment') || result.output.includes('accessible'),
        'Output should contain functional language'
    );
    
    runner.assert(
        result.metadata.hasDetections === true,
        'Should detect disability mention'
    );
});

// Test 2: Blindness transformation
runner.test('Blindness redaction', async () => {
    const input = "As a blind person, how can I learn to code?";
    const result = await transformPrompt(input);
    
    runner.assert(
        !result.output.toLowerCase().includes('blind'),
        'Output should not contain "blind"'
    );
    
    runner.assert(
        result.output.includes('screen reader') || result.output.includes('assistive technology'),
        'Output should contain assistive technology context'
    );
});

// Test 3: Multiple disability mentions
runner.test('Multiple disability detection', async () => {
    const input = "I'm paralyzed and also have dyslexia, can you help me with accessible learning?";
    const result = await transformPrompt(input);
    
    runner.assert(
        !result.output.toLowerCase().includes('paralyzed'),
        'Should redact "paralyzed"'
    );
    
    runner.assert(
        !result.output.toLowerCase().includes('dyslexia'),
        'Should redact "dyslexia"'
    );
    
    runner.assert(
        result.metadata.detectedCategories.length >= 2,
        'Should detect multiple categories'
    );
});

// Test 4: No disability mentions (control test)
runner.test('No disability mentions - passthrough', async () => {
    const input = "What's the weather like today?";
    const result = await transformPrompt(input);
    
    runner.assert(
        result.output === input,
        'Should pass through unchanged when no disabilities detected'
    );
    
    runner.assert(
        result.metadata.hasDetections === false,
        'Should not detect any disabilities'
    );
});

// Test 5: Privacy preservation check
runner.test('Privacy preservation validation', async () => {
    const medicalTerms = [
        "I have paralysis",
        "I'm blind", 
        "I'm autistic",
        "I have bipolar disorder",
        "I use a wheelchair"
    ];
    
    for (const term of medicalTerms) {
        const result = await transformPrompt(term);
        
        runner.assert(
            result.validation.privacyPreserved === true,
            `Privacy should be preserved for: "${term}"`
        );
    }
});

// Test 6: Intent preservation check
runner.test('Intent preservation validation', async () => {
    const input = "I'm paralyzed and want to find accessible restaurants in downtown";
    const result = await transformPrompt(input);
    
    runner.assert(
        result.output.includes('restaurants'),
        'Should preserve main intent (finding restaurants)'
    );
    
    runner.assert(
        result.output.includes('downtown'),
        'Should preserve location context'
    );
    
    runner.assert(
        result.validation.intentMaintained === true,
        'Intent should be maintained'
    );
});

// Test 7: Context enrichment
runner.test('Context enrichment', async () => {
    const input = "I'm blind and need help with coding";
    const result = await transformPrompt(input);
    
    runner.assert(
        result.metadata.addedContext.length > 0,
        'Should add functional context'
    );
    
    runner.assert(
        result.output.length > input.length,
        'Output should be longer due to added context'
    );
});

// Test 8: Coherence validation
runner.test('Output coherence', async () => {
    const input = "I have cerebral palsy and want to learn programming";
    const result = await transformPrompt(input);
    
    runner.assert(
        result.validation.coherenceScore > 0.7,
        'Output should be coherent (score > 0.7)'
    );
    
    // Check for proper sentence structure
    const sentences = result.output.split(/[.!?]+/).filter(s => s.trim().length > 0);
    runner.assert(
        sentences.length > 0,
        'Should contain at least one complete sentence'
    );
});

// Test 9: Error handling
runner.test('Error handling', async () => {
    // Test empty input
    const result1 = await transformPrompt("");
    runner.assert(
        result1.error !== undefined,
        'Should handle empty input gracefully'
    );
    
    // Test null input
    const result2 = await transformPrompt(null);
    runner.assert(
        result2.error !== undefined,
        'Should handle null input gracefully'
    );
});

// Test 10: Library info
runner.test('Library information', async () => {
    const info = getLibraryInfo();
    
    runner.assert(
        info.version === '1.0.0',
        'Should return correct version'
    );
    
    runner.assert(
        info.categories === 14,
        'Should support 14 disability categories'
    );
    
    runner.assert(
        info.privacyLevel === 'high',
        'Should guarantee high privacy level'
    );
});

// Example transformations for demonstration
async function showExamples() {
    console.log('\n🎯 Example Transformations:\n');
    
    const examples = [
        "I'm a wheelchair user looking for accessible hotels",
        "As a blind person, I need help with web development",
        "I have dyslexia and want to improve my writing skills", 
        "I'm autistic and struggle with social interactions at work",
        "I have chronic pain and need ergonomic workspace advice"
    ];
    
    for (const example of examples) {
        const result = await transformPrompt(example);
        console.log(`📝 Original: "${example}"`);
        console.log(`🔄 Transformed: "${result.output}"`);
        console.log(`🔒 Privacy Score: ${result.metadata.privacyScore}`);
        console.log(`📊 Detected: ${result.metadata.detectedCategories.map(c => c.category).join(', ')}`);
        console.log('---');
    }
}

// Run tests
async function main() {
    await runner.runAll();
    await showExamples();
}

// Execute if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export default TestRunner;