#!/usr/bin/env python3
"""
Test verification script to check test structure and imports.
"""

import ast
import sys
from pathlib import Path


def analyze_test_file(file_path):
    """Analyze a test file for structure and coverage."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Count test functions
        test_functions = []
        test_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_functions.append(node.name)
            elif isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                test_classes.append(node.name)
                # Count methods in test class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        test_functions.append(f"{node.name}.{item.name}")
        
        return {
            'file': file_path.name,
            'test_classes': test_classes,
            'test_functions': len(test_functions),
            'functions': test_functions
        }
    
    except Exception as e:
        return {'file': file_path.name, 'error': str(e)}


def main():
    """Main analysis function."""
    project_dir = Path(__file__).parent
    test_files = list(project_dir.glob('test_*.py'))
    
    print("🔍 Test Structure Analysis")
    print("=" * 50)
    
    total_tests = 0
    
    for test_file in sorted(test_files):
        result = analyze_test_file(test_file)
        
        if 'error' in result:
            print(f"❌ {result['file']}: {result['error']}")
            continue
        
        print(f"\n📋 {result['file']}")
        print(f"   Classes: {len(result['test_classes'])}")
        print(f"   Test Functions: {result['test_functions']}")
        
        for class_name in result['test_classes']:
            print(f"   - {class_name}")
        
        total_tests += result['test_functions']
    
    print(f"\n📊 Summary:")
    print(f"   Total test files: {len(test_files)}")
    print(f"   Total test functions: {total_tests}")
    
    # Check for main.py
    main_file = project_dir / 'main.py'
    if main_file.exists():
        print(f"✅ main.py exists")
        
        # Basic analysis of main.py
        try:
            with open(main_file, 'r') as f:
                content = f.read()
            
            functions = []
            classes = []
            
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            print(f"   Functions in main.py: {len(functions)}")
            print(f"   Classes in main.py: {len(classes)}")
            
        except Exception as e:
            print(f"❌ Error analyzing main.py: {e}")
    else:
        print(f"❌ main.py not found")
    
    # Check test coverage areas
    coverage_areas = [
        'validation',
        'authentication', 
        'import',
        'export',
        'debug',
        'error',
        'cli'
    ]
    
    print(f"\n🎯 Coverage Areas Analysis:")
    
    all_functions = []
    for test_file in test_files:
        result = analyze_test_file(test_file)
        if 'functions' in result:
            all_functions.extend(result['functions'])
    
    for area in coverage_areas:
        matching = [f for f in all_functions if area.lower() in f.lower()]
        print(f"   {area.title()}: {len(matching)} tests")
    
    print(f"\n✅ Test structure analysis complete!")
    
    if total_tests >= 50:
        print(f"🎉 Excellent test coverage with {total_tests} tests!")
    elif total_tests >= 30:
        print(f"👍 Good test coverage with {total_tests} tests!")
    else:
        print(f"⚠️  Consider adding more tests (current: {total_tests})")


if __name__ == "__main__":
    main()