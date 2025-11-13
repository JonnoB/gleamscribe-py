#!/usr/bin/env python3

"""Check what Ruby implementation actually produces."""

import subprocess
import os

def run_ruby_test():
    """Run a quick Ruby test to see actual output."""
    
    ruby_script = '''
#!/usr/bin/env ruby

require_relative '../glaemscribe/lib_rb/api'

# Load the mode
mode = Glaemscribe::API::ModeParser.new.parse("glaemresources/modes/quenya-tengwar-classical.glaem")
mode.processor.finalize({})

# Test transcription
text = "Ai"
success, result, debug = mode.transcribe(text)

puts "=== Ruby Implementation ==="
puts "Input: #{text}"
puts "Success: #{success}"
puts "Output: #{result}"
puts "Output length: #{result.length}"
puts

# Show character codes
puts "Character codes:"
result.each_char.with_index do |char, i|
  puts "  #{i}: '#{char}' (U+#{char.ord.to_s(16).upcase.rjust(4, '0')})"
end

puts
puts "Default charset: #{mode.default_charset.name}"
puts "Charset size: #{mode.default_charset.characters.length}"
puts

# Check specific characters
test_chars = ["TELCO", "PARMA", "CALMA"]
test_chars.each do |char_name|
  if mode.default_charset.has_character(char_name)
    char_value = mode.default_charset.get_character(char_name)
    puts "#{char_name}: '#{char_value}' (U+#{char_value.ord.to_s(16).upcase.rjust(4, '0')})"
  else
    puts "#{char_name}: NOT FOUND"
  end
end
'''
    
    # Write and run Ruby script
    script_path = "/tmp/test_ruby_glaemscribe.rb"
    with open(script_path, 'w') as f:
        f.write(ruby_script)
    
    try:
        # Change to Ruby directory and run
        result = subprocess.run(
            ['ruby', script_path],
            cwd='/home/jonno/glaemscribe',
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("Ruby Output:")
        print(result.stdout)
        if result.stderr:
            print("Ruby Errors:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error running Ruby: {e}")
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

if __name__ == "__main__":
    run_ruby_test()
