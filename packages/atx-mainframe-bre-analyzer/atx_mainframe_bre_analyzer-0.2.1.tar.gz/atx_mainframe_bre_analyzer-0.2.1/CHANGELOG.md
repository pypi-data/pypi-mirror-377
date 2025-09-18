# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2024-09-17

### Added
- Auto-detection of component level directory structure
- Support for both direct `cbl/jcl` and nested directory layouts (e.g., `mainframe_code/cbl/jcl`)
- Automatic path resolution eliminates need for manual directory structure configuration

### Changed
- Enhanced BRENavigator initialization to automatically detect correct component paths
- Improved compatibility with different ATX BRE output directory structures

## [0.2.0] - 2024-09-02

### Added
- Complete rule analysis capabilities with 4 new tools:
  - `read_component_bre_content` - Read complete BRE JSON file content
  - `get_component_rule_analysis` - Detailed rule analysis for components  
  - `get_business_function_rules` - Rule analysis for business functions
  - `get_all_business_function_rule_counts` - Rule counts for all functions
- Advanced rule categorization (business, UI/navigation, validation, processing)
- Comprehensive rule counting and statistics across all components

### Changed
- Migrated from standard MCP to FastMCP for improved performance
- Enhanced business rules extraction analysis workflow

## [0.1.0] - 2024-09-01

### Added
- Initial release of ATX Mainframe BRE Analyzer
- Business function listing and analysis from ATX BRE output
- Component dependency mapping for COBOL and JCL
- Search functionality for mainframe components
- BRE hierarchy overview and statistics
- MCP server integration for ATX Business Rules Extraction analysis
- Support for mainframe modernization planning workflows
