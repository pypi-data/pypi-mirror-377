#!/usr/bin/env python3
"""
MD to JS Converter Script
Converts formatted markdown files to JavaScript snippet registry format
"""

import os
import re
import json
from pathlib import Path


def escape_js_string(text):
    """
    Escape special characters for JavaScript string.
    
    Args:
        text (str): The text to escape
    
    Returns:
        str: Escaped text safe for JavaScript strings
    """
    # Process in specific order to avoid double-escaping
    return (text
            .replace('\\', '\\\\')  # Escape backslashes first
            .replace('"', '\\"')   # Escape double quotes
            .replace('\n', '\\n')  # Escape newlines
            .replace('\r', '\\r')  # Escape carriage returns
            .replace('\t', '\\t'))  # Escape tabs


def extract_snippets_from_md(md_content, filename):
    """
    Extract snippets from markdown content.
    
    Args:
        md_content (str): The markdown file content
        filename (str): The source filename (without .md extension)
    
    Returns:
        list: List of snippet dictionaries
    """
    snippets = []
    
    # Split content by sections starting with ##
    sections = re.split(r'^## ', md_content, flags=re.MULTILINE)
    
    for section in sections[1:]:  # Skip the first empty split
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Extract title (first line)
        title_line = lines[0].strip()
        
        # Initialize snippet data
        snippet = {
            "title": title_line,
            "id": "",
            "description": "",
            "content": "",
            "type": filename,
            "author": ""
        }
        
        # Parse the rest of the section
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            
            # Extract ID
            if line.startswith('**ID**:'):
                id_match = re.search(r'`([^`]+)`', line)
                if id_match:
                    snippet["id"] = id_match.group(1)
            
            # Extract Description
            elif line.startswith('**Description**:'):
                snippet["description"] = line.replace('**Description**:', '').strip()
            
            # Extract Prompt content
            elif line.startswith('**Prompt:**'):
                # Look for the code block
                i += 1
                if i < len(lines) and lines[i].strip() == '```':
                    # Start of code block
                    i += 1
                    content_lines = []
                    
                    # Collect all lines until end of code block
                    while i < len(lines):
                        if lines[i].strip() == '```':
                            break
                        content_lines.append(lines[i])
                        i += 1
                    
                    # Join content and escape for JSON
                    content = '\n'.join(content_lines)
                    # Escape special characters for JavaScript string
                    content = escape_js_string(content)
                    snippet["content"] = content
            
            i += 1
        
        # Only add snippet if it has required fields
        if snippet["id"] and snippet["title"] and snippet["description"]:
            snippets.append(snippet)
    
    return snippets


def convert_md_files_to_js():
    """
    Convert all MD files in current directory to JS format.
    """
    current_dir = Path(__file__).parent
    md_files = list(current_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found in the current directory.")
        return
    
    all_snippets = []
    
    # Process each MD file
    for md_file in md_files:
        print(f"Processing: {md_file.name}")
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract filename without extension
            filename = md_file.stem
            
            # Extract snippets
            snippets = extract_snippets_from_md(content, filename)
            all_snippets.extend(snippets)
            
            print(f"  Extracted {len(snippets)} snippets")
            
        except Exception as e:
            print(f"Error processing {md_file.name}: {e}")
    
    # Generate JavaScript content
    js_content = generate_js_content(all_snippets)
    
    # Write to output file
    output_file = current_dir / 'generated_snippets.js'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\nGenerated {len(all_snippets)} total snippets")
    print(f"Output written to: {output_file}")


def generate_js_content(snippets):
    """
    Generate the JavaScript content with proper formatting.
    
    Args:
        snippets (list): List of snippet dictionaries
    
    Returns:
        str: Generated JavaScript content
    """
    # Header
    js_lines = [
        "// Auto-generated from markdown files",
        "// DO NOT EDIT DIRECTLY - Edit the .md files and run the converter script",
        "",
        "// Register snippets with the global registry",
        "if (typeof window.registerPromptSnippets === 'function') {",
        "  window.registerPromptSnippets({",
        '    "snippets": ['
    ]
    
    # Add snippets
    for i, snippet in enumerate(snippets):
        comma = "," if i < len(snippets) - 1 else ""
        
        js_lines.extend([
            "    {",
            f'      "title": "{escape_js_string(snippet["title"])}",',
            f'      "id": "{escape_js_string(snippet["id"])}",',
            f'      "description": "{escape_js_string(snippet["description"])}",',
            f'      "content": "{snippet["content"]}",',
            f'      "type": "{escape_js_string(snippet["type"])}",',
            f'      "author": "{escape_js_string(snippet["author"])}"',
            f"    }}{comma}"
        ])
    
    # Footer
    js_lines.extend([
        "  ]",
        "  });",
        "} else {",
        "  // Fallback for backwards compatibility",
        "  window.__PROMPT_SNIPPETS = {",
        '    "snippets": [',
        "      // ... all the snippets would be here in fallback mode",
        "    ]",
        "  };",
        "}"
    ])
    
    return '\n'.join(js_lines)


def main():
    """Main function to run the converter."""
    print("MD to JS Converter")
    print("==================")
    print("Converting markdown files to JavaScript snippet format...")
    print()
    
    try:
        convert_md_files_to_js()
        print("\nConversion completed successfully!")
        
    except Exception as e:
        print(f"\nError during conversion: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
