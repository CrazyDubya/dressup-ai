# Fashion Outfit Generator Rules and Guidelines

## Core Principles

### 1. Style Integrity
- Maintain consistency within chosen style categories
- Respect cultural and historical accuracy
- Ensure outfit components are compatible
- Follow seasonal and weather-appropriate guidelines
- Consider context-specific requirements

### 2. Image Generation
- Each outfit can have multiple images
- Images must be stored in outfit-specific directories
- Image metadata must be tracked in outfit_images.csv
- Follow naming convention: image_[timestamp]_[index].jpg
- Include all necessary prompt information

### 3. Data Management
- All outfits must be recorded in outfit_catalog.csv
- All images must be tracked in outfit_images.csv
- Maintain proper directory structure
- Follow consistent naming conventions
- Implement proper error handling

## Style Guidelines

### 1. Real-World Outfits
- Must be practical and wearable
- Consider body type and fit
- Account for weather and season
- Respect cultural norms
- Include budget considerations

### 2. Character Outfits
- Must align with character background
- Consider world-building context
- Maintain period accuracy
- Reflect character personality
- Support story elements

### 3. Style Categories
- Professional must be workplace-appropriate
- Casual must maintain style while being comfortable
- Formal must meet event requirements
- Fantasy must align with world rules
- Historical must be period-accurate

## Technical Requirements

### 1. Code Structure
- Follow PEP 8 style guide
- Implement proper error handling
- Include comprehensive logging
- Maintain clean code architecture
- Document all functions and classes

### 2. File Management
- Use consistent file naming
- Implement proper directory structure
- Handle file operations safely
- Include error recovery
- Maintain data integrity

### 3. API Usage
- Handle API rate limits
- Implement proper error handling
- Cache responses when appropriate
- Use API keys securely
- Follow API best practices

## User Interface Guidelines

### 1. TUI Design
- Clear menu structure
- Informative feedback
- Error messages
- Progress indicators
- Consistent navigation

### 2. User Input
- Validate all inputs
- Provide clear prompts
- Handle errors gracefully
- Allow for corrections
- Support cancellation

### 3. Output Format
- Clear outfit descriptions
- Organized image display
- Proper error messages
- Status updates
- Progress indicators

## Documentation Requirements

### 1. Code Documentation
- Function docstrings
- Class documentation
- Module descriptions
- Usage examples
- Type hints

### 2. User Documentation
- Installation guide
- Usage instructions
- Configuration details
- Troubleshooting guide
- API documentation

### 3. System Documentation
- Architecture overview
- Component interaction
- Data flow diagrams
- Error handling
- Recovery procedures

## Security Guidelines

### 1. API Keys
- Never commit API keys
- Use environment variables
- Implement key rotation
- Monitor usage
- Handle expiration

### 2. Data Protection
- Sanitize user input
- Protect sensitive data
- Implement access control
- Handle errors securely
- Log security events

### 3. Error Handling
- Never expose system details
- Log errors securely
- Implement graceful fallback
- Provide user-friendly messages
- Monitor security events

## Performance Guidelines

### 1. Response Time
- Quick menu navigation
- Efficient image generation
- Responsive user interface
- Optimized file operations
- Proper caching

### 2. Resource Usage
- Efficient memory usage
- Proper file handling
- Optimized API calls
- Resource cleanup
- Performance monitoring

### 3. Scalability
- Handle multiple users
- Support batch operations
- Implement proper caching
- Handle large datasets
- Support future growth 