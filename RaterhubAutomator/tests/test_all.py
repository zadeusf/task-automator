#!/usr/bin/env python3
"""
Comprehensive test script for RaterHub Automator
Tests all modules for syntax errors, import issues, and basic functionality
"""

import sys
import os
import traceback
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

def test_imports():
    """Test all module imports"""
    print("Testing module imports...")
    modules_to_test = [
        'utils.config_manager',
        'ai.ai_analyzer', 
        'core.browser_manager',
        'core.raterhub_page',
        'core.main',
        'gui.automator_gui'
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            print(f"  Importing {module_name}...", end=" ")
            __import__(module_name)
            print("✓ OK")
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed_imports.append((module_name, str(e)))
    
    return failed_imports

def test_config_manager():
    """Test config manager functionality"""
    print("\nTesting ConfigManager...")
    try:
        from utils.config_manager import ConfigManager, config
        
        # Test basic functionality
        print("  Testing config loading...", end=" ")
        test_config = ConfigManager()
        print("✓ OK")
        
        print("  Testing config.get()...", end=" ")
        value = config.get('ai', 'default')
        print(f"✓ OK (got: {value})")
        
        print("  Testing nested config access...", end=" ")
        vertex_config = config.get('vertex_ai', {})
        print(f"✓ OK (got: {type(vertex_config)})")
        
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        traceback.print_exc()
        return False

def test_ai_analyzer():
    """Test AI analyzer basic functionality"""
    print("\nTesting AIAnalyzer...")
    try:
        from ai.ai_analyzer import AIAnalyzer, parse_ai_response, GEMINI_PROMPT
        
        print("  Testing AIAnalyzer initialization...", end=" ")
        # Don't actually initialize (requires credentials)
        print("✓ OK (skipped - requires credentials)")
        
        print("  Testing GEMINI_PROMPT...", end=" ")
        if len(GEMINI_PROMPT.strip()) > 100:
            print("✓ OK")
        else:
            print("✗ FAILED: Prompt too short")
            return False
            
        print("  Testing parse_ai_response...", end=" ")
        test_response = """Response A Rating: 5
Response B Rating: 3
SxS: Better on left
Overall Explanation: Response A is more helpful"""
        
        parsed = parse_ai_response(test_response)
        expected_keys = ['action', 'a_rating', 'b_rating', 'sxs', 'explanation']
        if all(key in parsed for key in expected_keys):
            print("✓ OK")
        else:
            print(f"✗ FAILED: Missing keys. Got: {list(parsed.keys())}")
            return False
            
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        traceback.print_exc()
        return False

def test_browser_manager():
    """Test browser manager"""
    print("\nTesting BrowserManager...")
    try:
        from core.browser_manager import connect_to_chrome
        from gui.automator_gui import is_port_open
        
        print("  Testing is_port_open...", end=" ")
        # Test with a port that should be closed
        result = is_port_open(port=99999)
        if result == False:
            print("✓ OK")
        else:
            print(f"✗ FAILED: Expected False, got {result}")
            return False
            
        print("  Testing connect_to_chrome import...", end=" ")
        # Just test that the function exists, don't call it
        if callable(connect_to_chrome):
            print("✓ OK")
        else:
            print("✗ FAILED: Not callable")
            return False
            
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        traceback.print_exc()
        return False

def test_file_existence():
    """Test that all required files exist"""
    print("\nTesting file existence...")
    required_files = [
        'config.json',
        'main.py',
        'automator_gui.py',
        'ai_analyzer.py',
        'browser_manager.py',
        'config_manager.py',
        'raterhub_page.py',
        'requirements.txt',
        'launch-chrome.bat',
        'run_automator.bat',
        'get_config_value.py'
    ]
    
    missing_files = []
    
    for filename in required_files:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        print(f"  Checking {filename}...", end=" ")
        if os.path.exists(filepath):
            print("✓ OK")
        else:
            print("✗ MISSING")
            missing_files.append(filename)
    
    return missing_files

def test_config_json():
    """Test config.json validity"""
    print("\nTesting config.json...")
    try:
        import json
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        print("  Testing JSON validity...", end=" ")
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        print("✓ OK")
        
        print("  Testing required keys...", end=" ")
        required_keys = ['ai', 'vertex_ai', 'chrome_debug_port']
        missing_keys = [key for key in required_keys if key not in config_data]
        if not missing_keys:
            print("✓ OK")
        else:
            print(f"✗ FAILED: Missing keys: {missing_keys}")
            return False
            
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("RaterHub Automator - Comprehensive Test Suite")
    print("=" * 50)
    
    # Test file existence first
    missing_files = test_file_existence()
    if missing_files:
        print(f"\n❌ CRITICAL: Missing files: {missing_files}")
        return False
    
    # Test config.json
    if not test_config_json():
        print(f"\n❌ CRITICAL: config.json issues")
        return False
    
    # Test imports
    failed_imports = test_imports()
    if failed_imports:
        print(f"\n❌ CRITICAL: Import failures:")
        for module, error in failed_imports:
            print(f"  {module}: {error}")
        return False
    
    # Test individual modules
    tests = [
        test_config_manager,
        test_ai_analyzer,
        test_browser_manager
    ]
    
    failed_tests = []
    for test_func in tests:
        if not test_func():
            failed_tests.append(test_func.__name__)
    
    print("\n" + "=" * 50)
    if failed_tests:
        print(f"❌ TESTS FAILED: {len(failed_tests)} test(s) failed")
        for test_name in failed_tests:
            print(f"  - {test_name}")
        return False
    else:
        print("✅ ALL TESTS PASSED!")
        print("The RaterHub Automator appears to be working correctly.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)