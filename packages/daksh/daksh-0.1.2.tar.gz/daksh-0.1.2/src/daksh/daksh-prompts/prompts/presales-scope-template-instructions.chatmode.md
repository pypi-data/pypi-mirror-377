---
description: 
globs: 
alwaysApply: false
---
# Presales Scope Sheet Template Instructions

## Overview
This document provides instructions for creating a presales scope sheet using the standardized CSV format. The template follows a phased delivery approach with clear categorization of features and functionalities.

## Template Structure

### Column Headers
The scope sheet should contain the following columns:
- **Product Aspect**: Main category/component identification
- **Phase 1**: Initial delivery phase features
- **Phase 2**: Second phase deliverables  
- **Phase 3**: Third phase enhancements
- **Phase 4**: Final phase advanced features
- **Business Case**: Business justification or additional notes

### Template Format
```csv
Product Aspect,Phase 1,Phase 2,Phase 3,Phase 4,Business Case
```

## Instructions for Filling the Template

### 1. Product Aspect Column
- **Purpose**: Identifies the main product component or module
- **Format**: Use hierarchical naming convention
- **Examples**:
  - `Framework` (main category header)
  - `Framework Frontend` (subcategory)
  - `Framework Backend` (subcategory)
  - `ModuleName` (main category)
  - `ModuleName Frontend` (subcategory)
  - `ModuleName Backend` (subcategory)

### 2. Phase Columns (Phase 1-4)
- **Purpose**: Define deliverables for each development phase
- **Guidelines**:
  - Start with foundational features in Phase 1
  - Progress to more advanced features in later phases
  - Leave cells empty if no deliverables for that phase
  - Use descriptive feature names
  - Include technical components and user-facing features

### 3. Business Case Column
- **Purpose**: Provide business justification or additional context
- **Usage**: Optional - use when specific business reasoning is needed

## Content Guidelines

### Feature Naming Conventions
- Use clear, descriptive names for features
- Include both technical and functional aspects
- Examples:
  - `UI Approach Style Establishment`
  - `Access Control Management`
  - `Dashboard - Pending tasks, approvals`

### Categorization Best Practices

#### Framework Components
- Include foundational elements first
- Separate frontend and backend concerns
- Examples:
  - Authentication modules
  - UI component libraries
  - Microservice setups
  - Security frameworks

#### Module-Specific Features
- Group related functionalities together
- Maintain consistency between frontend and backend features
- Consider user workflows and business processes

### Phase Distribution Strategy

#### Phase 1 (Foundation)
- Core system setup
- Basic authentication
- Essential UI components
- Fundamental data management

#### Phase 2 (Core Features)
- User management
- Dashboard functionality
- Core business logic
- Integration frameworks

#### Phase 3 (Advanced Features)
- Advanced reporting
- Complex integrations
- Enhanced user experience
- Specialized functionalities

#### Phase 4 (Premium Features)
- Advanced analytics
- AI/ML capabilities
- Complex integrations
- Specialized enterprise features

## Template Creation Process

### Step 1: Identify Main Categories
1. List all major product components/modules
2. Create main category headers (e.g., `Framework`, `ModuleName`)

### Step 2: Define Subcategories
1. For each main category, create Frontend/Backend subdivisions
2. Add category separator rows (empty rows) between main categories

### Step 3: Map Features to Phases
1. List all features for each subcategory
2. Distribute features across phases based on:
   - Technical dependencies
   - Business priorities
   - Development complexity
   - User impact

### Step 4: Add Business Context
1. Include business justification where relevant
2. Note any special considerations or requirements

## Example Template Structure

```csv
Product Aspect,Phase 1,Phase 2,Phase 3,Phase 4,Business Case
Framework,,,,,
Framework Frontend,Basic UI Setup,Advanced Components,Notifications,Accessibility,
Framework Backend,Auth Module,User Management,Audit System,Advanced Security,
,,,,,
ModuleName,,,,,
ModuleName Frontend,Core UI,Dashboard,Reports,Analytics,
ModuleName Backend,Data Management,Business Logic,Integrations,AI Features,
```

## Quality Checklist

### Before Finalizing
- [ ] All major product components are included
- [ ] Features are logically distributed across phases
- [ ] Frontend and backend features are balanced
- [ ] Dependencies between phases are considered
- [ ] Business priorities are reflected in phase ordering
- [ ] Feature names are clear and descriptive
- [ ] Template follows consistent formatting

### Review Points
- Are foundational features in early phases?
- Do later phases build upon earlier deliverables?
- Is the scope realistic for each phase?
- Are all stakeholder requirements represented?
- Is the technical feasibility considered?

## Usage Notes

1. **Flexibility**: Template can be adapted for different project types
2. **Scalability**: Add more phases if needed for larger projects
3. **Customization**: Modify categories based on specific product requirements
4. **Version Control**: Maintain versions as scope evolves during presales process
5. **Stakeholder Review**: Share with technical and business stakeholders for validation

## Best Practices

- Keep feature descriptions concise but descriptive
- Maintain consistency in naming conventions
- Use empty rows to separate major product sections
- Consider technical dependencies when phasing features
- Align phases with business milestone expectations
- Regular review and updates during presales discussions
- Include both functional and non-functional requirements

This template provides a standardized approach to creating comprehensive presales scope documentation that can be easily understood by both technical and business stakeholders.
