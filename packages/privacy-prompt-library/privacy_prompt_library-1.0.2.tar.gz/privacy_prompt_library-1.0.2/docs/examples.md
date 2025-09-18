# Usage Examples

## Basic Usage

```javascript
import { transformPrompt } from './src/index.js';

// Simple transformation
const result = await transformPrompt("I'm paralyzed and need travel advice");
console.log(result.output);
// "I have limited mobility and need travel advice. I need step-free access to buildings and entrances."
```

## Advanced Usage

```javascript
import { transformBatch, getLibraryInfo } from './src/index.js';

// Batch processing
const prompts = [
    "I'm blind and learning to code",
    "As a wheelchair user, I need accessible venues",
    "I have dyslexia and want writing help"
];

const results = await transformBatch(prompts);
results.forEach(result => {
    console.log(`${result.input} → ${result.output}`);
});

// Library information
const info = getLibraryInfo();
console.log(`Privacy Level: ${info.privacyLevel}`);
```

## Example Transformations

| **Original Prompt** | **Transformed Prompt** |
|---------------------|------------------------|
| "I'm a wheelchair user looking for restaurants" | "I use mobility equipment looking for restaurants. I need step-free access to buildings and entrances." |
| "As a blind person, how do I code?" | "As someone who uses assistive technology, how do I code? I use screen readers to access digital content." |
| "I have dyslexia and need help writing" | "I process text information differently and need help writing. I work better with audio or visual content rather than text-heavy materials." |

## Privacy Guarantees

✅ **No medical terms disclosed**  
✅ **No diagnostic language**  
✅ **Functional needs preserved**  
✅ **Original intent maintained**  

## Error Handling

```javascript
const result = await transformPrompt("invalid input");
if (result.error) {
    console.log(`Error: ${result.error.message}`);
    // Fallback to original prompt
    console.log(`Fallback: ${result.output}`);
}
```