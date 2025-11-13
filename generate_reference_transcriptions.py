#!/usr/bin/env python3
"""
Generate reference transcriptions using the JavaScript Glaemscribe implementation.
This creates test data for validating the Python implementation.
"""

import json
import subprocess
import sys
from pathlib import Path

# Test cases to generate
TEST_CASES = [
    {
        'mode': 'quenya-tengwar-classical',
        'charset': 'tengwar_ds',
        'input': 'Ai ! laurië lantar lassi súrinen ,',
        'description': 'Quenya phrase - Namárië opening'
    },
    {
        'mode': 'quenya-tengwar-classical',
        'charset': 'tengwar_ds',
        'input': 'Elen síla lúmenn omentielvo',
        'description': 'Quenya greeting - A star shines'
    },
    {
        'mode': 'sindarin-tengwar-classical',
        'charset': 'tengwar_ds',
        'input': 'Mae govannen',
        'description': 'Sindarin greeting - Well met'
    },
    {
        'mode': 'quenya-tengwar-classical',
        'charset': 'tengwar_ds',
        'input': 'aiya',
        'description': 'Simple Quenya word'
    },
]

# JavaScript code template to run transcription
JS_TEMPLATE = """
const fs = require('fs');
const vm = require('vm');

function include(path) { 
    const code = fs.readFileSync(path, 'utf-8'); 
    vm.runInThisContext(code, path); 
}

// Load Glaemscribe
const buildPath = '/home/jonno/glaemscribe/build/web/glaemscribe/js/glaemscribe.js';
include(buildPath);

// Load all charsets
const charsets = [
    'tengwar_ds_sindarin',
    'tengwar_ds_quenya',
    'tengwar_guni_sindarin',
];

charsets.forEach(cs => {
    const path = `/home/jonno/glaemscribe/build/web/glaemscribe/js/charsets/${cs}.cst.js`;
    if (fs.existsSync(path)) {
        include(path);
    }
});

// Load charsets and modes using the resource manager
Glaemscribe.resource_manager.load_charsets();
Glaemscribe.resource_manager.load_modes();

// Get test case from command line
const testCase = JSON.parse(process.argv[2]);

// Transcribe
try {
    // Get the mode
    const mode = Glaemscribe.resource_manager.loaded_modes[testCase.mode];
    if (!mode) {
        const available = Object.keys(Glaemscribe.resource_manager.loaded_modes);
        throw new Error(`Mode ${testCase.mode} not found. Available: ${available.join(', ')}`);
    }
    
    // Get the charset (optional - will use default if not specified)
    let charset = null;
    if (testCase.charset) {
        charset = Glaemscribe.resource_manager.loaded_charsets[testCase.charset];
        if (!charset) {
            const available = Object.keys(Glaemscribe.resource_manager.loaded_charsets);
            throw new Error(`Charset ${testCase.charset} not found. Available: ${available.join(', ')}`);
        }
    }
    
    // Finalize mode
    mode.finalize({});
    
    // Transcribe - returns [success, result]
    const transcribeResult = mode.transcribe(testCase.input, charset);
    const success = transcribeResult[0];
    const result = transcribeResult[1];
    
    // Output as JSON
    const output = {
        success: true,
        result: result,
        hex: Array.from(result).map(c => '0x' + c.charCodeAt(0).toString(16).padStart(4, '0'))
    };
    
    console.log(JSON.stringify(output));
} catch (error) {
    const output = {
        success: false,
        error: error.message,
        stack: error.stack
    };
    console.log(JSON.stringify(output));
}
"""


def generate_reference_transcription(test_case):
    """Generate a reference transcription using the JS implementation."""
    
    # Path to the Node.js script in the glaemscribe repo
    js_file = Path('/home/jonno/glaemscribe/transcribe_test.js')
    
    if not js_file.exists():
        print(f"Error: {js_file} not found", file=sys.stderr)
        return None
    
    # Run Node.js with the test case
    try:
        result = subprocess.run(
            ['node', str(js_file), json.dumps(test_case)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd='/home/jonno/glaemscribe'  # Run from glaemscribe directory
        )
        
        if result.returncode != 0:
            print(f"Error running Node.js: {result.stderr}", file=sys.stderr)
            return None
            
        # Parse JSON output
        output = json.loads(result.stdout)
        
        if not output['success']:
            print(f"Transcription failed: {output.get('error', 'Unknown error')}", file=sys.stderr)
            return None
            
        return output['result']
        
    except subprocess.TimeoutExpired:
        print("Node.js process timed out", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON output: {e}", file=sys.stderr)
        print(f"Output was: {result.stdout}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return None


def main():
    """Generate all reference transcriptions and save to file."""
    
    print("Generating reference transcriptions from JavaScript implementation...")
    print()
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] {test_case['description']}")
        print(f"  Input: {test_case['input']}")
        
        expected = generate_reference_transcription(test_case)
        
        if expected is None:
            print(f"  ❌ Failed to generate reference")
            continue
            
        print(f"  ✅ Generated: {repr(expected)}")
        print(f"  Length: {len(expected)} characters")
        
        results.append({
            'mode': test_case['mode'],
            'input': test_case['input'],
            'expected': expected,
            'description': test_case['description']
        })
        print()
    
    # Save to Python test file
    output_file = Path('tests/test_real_world_generated.py')
    
    with output_file.open('w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""\n')
        f.write('Real-world transcription tests with reference outputs from JavaScript implementation.\n')
        f.write('Generated by generate_reference_transcriptions.py\n')
        f.write('"""\n\n')
        f.write('import pytest\n')
        f.write('from src.glaemscribe.parsers.mode_parser import ModeParser\n\n')
        f.write('REAL_WORLD_TEST_CASES = [\n')
        
        for result in results:
            f.write('    {\n')
            f.write(f"        'mode': {repr(result['mode'])},\n")
            f.write(f"        'input': {repr(result['input'])},\n")
            f.write(f"        'expected': {repr(result['expected'])},\n")
            f.write(f"        'description': {repr(result['description'])}\n")
            f.write('    },\n')
        
        f.write(']\n\n')
        f.write('def transcribe_mode(mode_name: str, text: str) -> str:\n')
        f.write('    """Helper function to transcribe text using a specific mode."""\n')
        f.write('    parser = ModeParser()\n')
        f.write('    mode_file = f"resources/glaemresources/modes/{mode_name}.glaem"\n')
        f.write('    mode = parser.parse(mode_file)\n')
        f.write('    mode.processor.finalize({})\n')
        f.write('    result = mode.transcribe(text)\n')
        f.write('    return result[1] if result[0] else result[1]\n\n')
        f.write('@pytest.mark.parametrize("test_case", REAL_WORLD_TEST_CASES)\n')
        f.write('def test_real_world_transcription(test_case):\n')
        f.write('    """Test real-world transcription examples against JS outputs."""\n')
        f.write('    result = transcribe_mode(test_case["mode"], test_case["input"])\n')
        f.write('    assert result == test_case["expected"], (\n')
        f.write('        f"Transcription mismatch for {test_case[' + "'input'" + ']}' + '\\n"\n')
        f.write('        f"Expected: {test_case[' + "'expected'" + ']}' + '\\n"\n')
        f.write('        f"Got:      {result}"\n')
        f.write('    )\n')
    
    print(f"✅ Generated {len(results)} test cases")
    print(f"📝 Saved to {output_file}")
    print()
    print("You can now run: uv run pytest tests/test_real_world_generated.py")


if __name__ == '__main__':
    main()
