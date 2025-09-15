# RaterHub Automator Project Rules

## Project Overview
The RaterHub Automator is a Private and personal Python-based tool designed to streamline the evaluation of AI-generated responses on the RaterHub platform. It automates the process of capturing screenshots of the RaterHub webpage, sending them to an AI model (currently configured for Gemini) for analysis through vertexai api, parsing the AI's response, and filling in ratings, checkboxes, and comments on the RaterHub task page aligning with the parsed ratings outputted by the AI. The tool is only to be used personally by Zade, the developer/overseer of the Raterhub Automator. Development should never consider other users using the tool, as it will only ever be used by Zade.

## Architecture & Design Principles

### **Modular Structure**
- **Core Automation**: `raterhub_automator.py` - Main automation logic, screenshot capture, AI analysis, form filling
- **GUI Interface**: `automator_gui.py` - PySimpleGUI-based user interface for process management
- **Utilities**: `extract_raterhub_elements.py` - DOM element extraction and debugging tools
- **Configuration**: `config.json` - Runtime settings and behavior control
- **Chrome Integration**: `launch-chrome.bat` - Chrome debugging setup

### **Error Handling Philosophy**
- **Fail-Safe Design**: Always prefer releasing tasks over incorrect submissions
- **Comprehensive Logging**: Extensive print statements for debugging and user feedback
- **Graceful Degradation**: Multiple fallback strategies for UI interactions
- **Exception Chaining**: Catch specific exceptions first, then general ones
- **User Feedback**: Clear error messages explaining what went wrong and potential fixes

## Code Style & Conventions

### **Naming Standards**
- **Functions/Variables**: `snake_case` (e.g., `process_task`, `set_slider_value`, `screenshot_count`)
- **Constants/Maps**: `UPPER_CASE` (e.g., `RATING_MAP`, `GEMINI_PROMPT`, `SXS_VALUE_MAP`)
- **Classes**: `PascalCase` (if needed, though current codebase is function-based)
- **Files**: `snake_case.py` or descriptive names (`extract_raterhub_elements.py`)

### **Function Design**
- **Single Responsibility**: Each function should have one clear purpose
- **Descriptive Names**: Function names should clearly indicate their purpose
- **Comprehensive Docstrings**: Include purpose, parameters, return values, and exceptions
- **Return Patterns**: Use consistent return patterns (success/failure booleans, tuples for multiple values)

### **Variable Naming**
- **Descriptive**: `screenshot_paths` not `paths`, `raterhub_handle` not `handle`
- **Context-Aware**: Include context in names (`a_rating`, `b_rating`, `sxs_position`)
- **Avoid Abbreviations**: Use full words unless they're domain-specific (e.g., `sxs` for side-by-side)

## Selenium & Browser Automation

### **Element Location Strategy**
- **Prefer Stable Selectors**: Use IDs when available, then specific class combinations
- **XPath for Complex Queries**: Use XPath for complex element relationships
- **Fallback Mechanisms**: Always have backup selectors for critical elements
- **Wait Strategies**: Use WebDriverWait with explicit conditions, avoid implicit waits

### **Chrome Debug Integration**
- **Consistent Port**: Always use port 9222 for remote debugging
- **User Data Directory**: Use `C:\temp\chrome_debug` for persistent sessions
- **Launch Arguments**: Include security and stability flags (`--remote-allow-origins=*`, `--disable-extensions`)

### **Screenshot & Interaction Patterns**
- **Scroll Management**: Always scroll to elements before interaction
- **Multiple Screenshots**: Take multiple screenshots to capture full page content
- **Action Chains**: Use ActionChains for complex interactions (sliders, drag-drop)
- **JavaScript Execution**: Use JavaScript for reliable clicks when Selenium clicks fail

## AI Integration & Response Processing

### **Prompt Engineering**
- **Structured Prompts**: Use clear, structured prompts with examples
- **Output Format**: Enforce specific output formats for reliable parsing
- **Error Handling**: Include fallback instructions for edge cases
- **Context Preservation**: Maintain context about the evaluation task

### **Response Parsing**
- **Regex-Based**: Use robust regex patterns for response extraction
- **Validation**: Validate all extracted data before use
- **Fallback Values**: Provide sensible defaults for missing data
- **Error Recovery**: Handle parsing failures gracefully with Error Messages

## Configuration & Environment

### **Config File Management**
- **JSON Structure**: Use clean, readable JSON with descriptive keys
- **Default Values**: Provide sensible defaults for all configuration options
- **Validation**: Validate configuration values on startup
- **Runtime Override**: Support command-line overrides for key settings

### **Environment Setup**
- **Windows-Specific**: Acknowledge Windows-specific dependencies and paths
- **Chrome Path**: Use standard Chrome installation path with fallback options
- **Credentials**: Use environment variables for sensitive data (Google Cloud credentials)
- **Dependencies**: Clearly document all required packages and versions

## UI & User Experience

### **GUI Design (PySimpleGUI)**
- **Simple Layout**: Keep interface clean and functional
- **Clear Actions**: Button names should clearly indicate their function
- **Status Feedback**: Provide real-time feedback through output windows
- **Error Display**: Show errors in user-friendly format

### **Process Management**
- **Chrome Lifecycle**: Manage Chrome process creation and cleanup
- **Port Management**: Check port availability before launching
- **Process Cleanup**: Always clean up processes on exit
- **User Guidance**: Provide clear instructions for manual steps

## Testing & Debugging

### **Element Extraction**
- **DOM Analysis**: Use detailed DOM extraction for debugging element issues
- **Multiple Strategies**: Test different element location strategies
- **Attribute Inspection**: Examine all relevant element attributes
- **Dynamic Content**: Account for dynamically loaded content

### **Automation Testing**
- **Dry Run Mode**: Support testing without actual submissions
- **Step-by-Step**: Allow pausing between automation steps
- **Screenshot Verification**: Save screenshots for manual verification
- **Logging Levels**: Support different levels of logging detail

## Security & Safety

### **Task Safety**
- **Release Over Risk**: Always notify user when uncertain
- **Validation Checks**: Validate all form inputs before submission
- **User Confirmation**: Require user confirmation for critical actions
- **Audit Trail**: Log all actions for review and debugging

### **Credential Management**
- **Environment Variables**: Use environment variables for API keys
- **Secure Storage**: Use secure credential storage when possible
- **Access Control**: Limit access to sensitive operations

## Performance & Optimization

### **Resource Management**
- **Memory Cleanup**: Clean up screenshots and temporary files
- **Process Efficiency**: Minimize unnecessary waits and operations
- **Batch Operations**: Group related operations when possible
- **Resource Monitoring**: Monitor system resources during automation

### **Timing & Delays**
- **Configurable Delays**: Make delays configurable through config
- **Random Variation**: Add random variation to avoid detection
- **Adaptive Timing**: Adjust timing based on system performance
- **Minimum Waits**: Ensure minimum waits for stability

## Future Development Guidelines

### **Extensibility**
- **Plugin Architecture**: Design for easy addition of new AI models
- **Configuration Expansion**: Support new configuration options easily
- **API Integration**: Design for multiple AI service integrations

### **Maintainability**
- **Code Documentation**: Maintain comprehensive documentation
- **Version Control**: Use clear commit messages and branching
- **Dependency Management**: Keep dependencies up to date
- **Backward Compatibility**: Maintain compatibility when possible

## Common Patterns to Follow

### **Error Handling Template**
```python
try:
    # Main operation
    result = perform_operation()
    print(f"Success: {operation_description}")
    return True
except SpecificException as e:
    print(f"Specific error in {operation_name}: {e}")
    return False
except Exception as e:
    print(f"Unexpected error in {operation_name}: {e}")
    return False
```

### **Element Interaction Template**
```python
def interact_with_element(driver, wait, locator, description):
    try:
        element = wait.until(EC.presence_of_element_located(locator))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        # Perform interaction
        print(f"Successfully interacted with {description}")
        return True
    except Exception as e:
        print(f"Error interacting with {description}: {e}")
        return False
```

### **Configuration Loading Template**
```python
# Load config with validation
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    # Validate required keys
    required_keys = ['ai', 'auto_submit', 'loop_tasks']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
except Exception as e:
    print(f"Config error: {e}")
    # Use defaults or exit
```

## File-Specific Guidelines

### **raterhub_automator.py**
- Main automation logic
- Comprehensive error handling with task release fallbacks
- Structured AI prompt and response parsing
- Robust element interaction with multiple strategies

### **automator_gui.py**
- Simple, functional GUI design
- Process management and cleanup
- User guidance and feedback
- Chrome lifecycle management

### **extract_raterhub_elements.py**
- Detailed DOM analysis for debugging
- Comprehensive element attribute extraction
- Support for automation development and troubleshooting

### **config.json**
- Clean, readable configuration structure
- Sensible defaults for all options
- Support for runtime behavior modification

Remember: This is a private/personal Windows-specific automation tool for a specialized platform. Prioritize reliability, safety, and user feedback over performance optimization. Always err on the side of caution when dealing with task submissions.