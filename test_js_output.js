#!/usr/bin/env node

const fs = require('fs');
const vm = require('vm');

// Load the glaemscribe library
function include(path) { 
    const code = fs.readFileSync(path, 'utf-8'); 
    vm.runInThisContext(code, path); 
}

// Try to load the built JS file
const buildPath = '/home/jonno/glaemscribe/build/web/glaemscribe/js/glaemscribe.js';
if (fs.existsSync(buildPath)) {
    include(buildPath);
    
    // Load charset
    const charsetPath = '/home/jonno/glaemscribe/build/web/glaemscribe/js/charsets/tengwar_ds_sindarin.cst.js';
    if (fs.existsSync(charsetPath)) {
        include(charsetPath);
    }
    
    // Load mode
    const modePath = '/home/jonno/glaemscribe/build/web/glaemscribe/js/modes/quenya-tengwar-classical.glaem.js';
    if (fs.existsSync(modePath)) {
        include(modePath);
    }
    
    // Test transcription
    const text = 'Ai ! laurië lantar lassi súrinen ,';
    const result = Glaemscribe.transcribe(text, 'quenya-tengwar-classical', 'tengwar_ds', {});
    
    console.log('Input:', text);
    console.log('Output:', result);
    console.log('Output length:', result.length);
    console.log('Output hex:', Array.from(result).map(c => '0x' + c.charCodeAt(0).toString(16)).join(', '));
} else {
    console.log('Build path not found:', buildPath);
    console.log('Checking for source files...');
    
    const srcPath = '/home/jonno/glaemscribe/lib_js/api.js';
    if (fs.existsSync(srcPath)) {
        console.log('Source files found. Need to build first.');
    }
}
