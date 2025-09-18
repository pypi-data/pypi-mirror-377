#!/usr/bin/env python3
"""
ATX Mainframe BRE Analyzer - FastMCP Server
Provides structured navigation of Business Rules Engine (BRE) hierarchy
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("atx-mainframe-bre-analyzer")

class BRENavigator:
    """Business Rules Engine Navigator"""
    
    def __init__(self):
        self.app_level_bre = os.getenv("ATX_MF_APPLICATION_LEVEL_BRE")
        component_level_bre = os.getenv("ATX_MF_COMPONENT_LEVEL_BRE")
        
        if not self.app_level_bre or not component_level_bre:
            raise ValueError("BRE environment variables not set")
        
        # Auto-detect component level structure
        self.component_level_bre = self._detect_component_level_path(component_level_bre)
    
    def _detect_component_level_path(self, base_path: str) -> str:
        """Auto-detect the correct component level path structure"""
        base = Path(base_path)
        
        # Check if cbl/jcl directories exist directly
        if (base / "cbl").exists() and (base / "jcl").exists():
            return str(base)
        
        # Search for any subdirectory containing both cbl and jcl folders
        for item in base.iterdir():
            if item.is_dir():
                if (item / "cbl").exists() and (item / "jcl").exists():
                    return str(item)
        
        # Return original path if no valid structure found
        return str(base)
    
    def get_business_functions(self) -> List[Dict[str, Any]]:
        """Get all business functions from Application Level BRE"""
        functions = []
        
        if not Path(self.app_level_bre).exists():
            return functions
            
        for item in Path(self.app_level_bre).iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                function_info = {
                    "name": item.name,
                    "path": str(item),
                    "has_main_spec": (item / f"{item.name}.json").exists(),
                    "entry_points": self._get_entry_points(item)
                }
                functions.append(function_info)
        
        return sorted(functions, key=lambda x: x["name"])
    
    def _get_entry_points(self, function_dir: Path) -> List[Dict[str, Any]]:
        """Get entry points for a business function"""
        entry_points = []
        
        for item in function_dir.iterdir():
            if item.is_dir() and item.name.startswith("entrypoint-"):
                program_name = item.name.replace("entrypoint-", "")
                entry_point_info = {
                    "name": program_name,
                    "directory": item.name,
                    "path": str(item),
                    "has_spec": (item / f"entrypoint-{program_name}.json").exists(),
                    "component_dependencies": self._get_component_dependencies(program_name)
                }
                entry_points.append(entry_point_info)
        
        return sorted(entry_points, key=lambda x: x["name"])
    
    def _get_component_dependencies(self, program_name: str) -> Dict[str, List[str]]:
        """Get component level dependencies for a program"""
        dependencies = {"cobol": [], "jcl": []}
        
        # Check COBOL components
        cbl_dir = Path(self.component_level_bre) / "cbl"
        if cbl_dir.exists():
            for cbl_file in cbl_dir.glob("*.json"):
                if program_name.upper() in cbl_file.stem.upper():
                    dependencies["cobol"].append(cbl_file.name)
        
        # Check JCL components  
        jcl_dir = Path(self.component_level_bre) / "jcl"
        if jcl_dir.exists():
            for jcl_file in jcl_dir.glob("*.json"):
                if program_name.upper() in jcl_file.stem.upper():
                    dependencies["jcl"].append(jcl_file.name)
        
        return dependencies
    
    def get_all_component_files(self) -> Dict[str, List[str]]:
        """Get all component level files"""
        components = {}
        base_path = Path(self.component_level_bre)
        
        # Dynamically discover all component types
        if base_path.exists():
            for item in base_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    component_type = item.name
                    components[component_type] = sorted([f.name for f in item.glob("*.json")])
        
        return components
    
    def search_components_by_pattern(self, pattern: str) -> Dict[str, List[str]]:
        """Search component files by pattern"""
        results = {}
        pattern_upper = pattern.upper()
        base_path = Path(self.component_level_bre)
        
        # Dynamically discover all component types
        if base_path.exists():
            for item in base_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    component_type = item.name
                    results[component_type] = []
                    
                    # Search files in this component type directory
                    for file in item.glob("*.json"):
                        if pattern_upper in file.stem.upper():
                            results[component_type].append(file.name)
        
        return results
    
    def read_component_bre_file(self, component_name: str, component_type: str) -> Dict[str, Any]:
        """Read and parse a component BRE JSON file"""
        if component_type not in ["cbl", "jcl"]:
            return {"error": "Component type must be 'cbl' or 'jcl'"}
        
        file_path = Path(self.component_level_bre) / component_type / f"{component_name}-{component_type}.json"
        
        if not file_path.exists():
            return {"error": f"Component file not found: {file_path}"}
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return {
                "component_name": component_name,
                "component_type": component_type,
                "file_path": str(file_path),
                "data": data,
                "file_size": file_path.stat().st_size
            }
        except Exception as e:
            return {"error": f"Failed to read {file_path}: {str(e)}"}
    
    def count_rules_in_bre_file(self, file_path: Path) -> Dict[str, Any]:
        """Count and categorize rules in a BRE JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            rule_analysis = {
                "total_rules": 0,
                "rule_categories": {},
                "rule_structures": [],
                "business_rules": 0,
                "ui_navigation_rules": 0,
                "validation_rules": 0,
                "processing_rules": 0
            }
            
            # Check different possible rule structures
            rule_locations = [
                ("rules", "rules"),
                ("business_rules", "business_rules"),
                ("analysis.rules", "analysis"),
                ("component_analysis.rules", "component_analysis"),
                ("rule_analysis", "rule_analysis"),
                ("cobol_rules", "cobol_rules"),
                ("jcl_rules", "jcl_rules")
            ]
            
            for location_path, location_name in rule_locations:
                rules = self._get_nested_value(data, location_path)
                if rules and isinstance(rules, list):
                    rule_count = len(rules)
                    rule_analysis["total_rules"] += rule_count
                    rule_analysis["rule_structures"].append({
                        "location": location_name,
                        "count": rule_count,
                        "path": location_path
                    })
                    
                    # Categorize rules if possible
                    categorized = self._categorize_rules(rules)
                    rule_analysis["business_rules"] += categorized.get("business", 0)
                    rule_analysis["ui_navigation_rules"] += categorized.get("ui_navigation", 0)
                    rule_analysis["validation_rules"] += categorized.get("validation", 0)
                    rule_analysis["processing_rules"] += categorized.get("processing", 0)
            
            return rule_analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze {file_path}: {str(e)}"}
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _categorize_rules(self, rules: List[Dict]) -> Dict[str, int]:
        """Categorize rules based on content analysis"""
        categories = {"business": 0, "ui_navigation": 0, "validation": 0, "processing": 0}
        
        for rule in rules:
            if not isinstance(rule, dict):
                continue
                
            rule_text = str(rule).lower()
            
            # UI/Navigation indicators
            if any(keyword in rule_text for keyword in ["pf key", "screen", "cursor", "map", "display", "menu"]):
                categories["ui_navigation"] += 1
            # Validation indicators
            elif any(keyword in rule_text for keyword in ["validate", "check", "format", "length", "required"]):
                categories["validation"] += 1
            # Processing indicators
            elif any(keyword in rule_text for keyword in ["calculate", "process", "update", "insert", "delete"]):
                categories["processing"] += 1
            # Default to business logic
            else:
                categories["business"] += 1
        
        return categories
    
    def get_business_function_rule_count(self, function_name: str) -> Dict[str, Any]:
        """Get detailed rule count analysis for a business function"""
        function_details = self.get_business_functions()
        function = next((f for f in function_details if f["name"] == function_name), None)
        
        if not function:
            return {"error": f"Business function '{function_name}' not found"}
        
        rule_summary = {
            "function_name": function_name,
            "total_rules": 0,
            "components": [],
            "rule_breakdown": {
                "business_rules": 0,
                "ui_navigation_rules": 0,
                "validation_rules": 0,
                "processing_rules": 0
            }
        }
        
        # Analyze each component in the business function
        for entry_point in function["entry_points"]:
            component_name = entry_point["name"]
            
            # Check COBOL components
            for cobol_file in entry_point["component_dependencies"]["cobol"]:
                file_path = Path(self.component_level_bre) / "cbl" / cobol_file
                if file_path.exists():
                    analysis = self.count_rules_in_bre_file(file_path)
                    if "error" not in analysis:
                        component_info = {
                            "component_name": component_name,
                            "file_type": "cobol",
                            "file_name": cobol_file,
                            "file_path": str(file_path),
                            "rule_count": analysis["total_rules"],
                            "rule_breakdown": {
                                "business_rules": analysis["business_rules"],
                                "ui_navigation_rules": analysis["ui_navigation_rules"],
                                "validation_rules": analysis["validation_rules"],
                                "processing_rules": analysis["processing_rules"]
                            },
                            "rule_structures": analysis["rule_structures"]
                        }
                        rule_summary["components"].append(component_info)
                        rule_summary["total_rules"] += analysis["total_rules"]
                        for rule_type in rule_summary["rule_breakdown"]:
                            rule_summary["rule_breakdown"][rule_type] += analysis[rule_type]
            
            # Check JCL components
            for jcl_file in entry_point["component_dependencies"]["jcl"]:
                file_path = Path(self.component_level_bre) / "jcl" / jcl_file
                if file_path.exists():
                    analysis = self.count_rules_in_bre_file(file_path)
                    if "error" not in analysis:
                        component_info = {
                            "component_name": component_name,
                            "file_type": "jcl",
                            "file_name": jcl_file,
                            "file_path": str(file_path),
                            "rule_count": analysis["total_rules"],
                            "rule_breakdown": {
                                "business_rules": analysis["business_rules"],
                                "ui_navigation_rules": analysis["ui_navigation_rules"],
                                "validation_rules": analysis["validation_rules"],
                                "processing_rules": analysis["processing_rules"]
                            },
                            "rule_structures": analysis["rule_structures"]
                        }
                        rule_summary["components"].append(component_info)
                        rule_summary["total_rules"] += analysis["total_rules"]
                        for rule_type in rule_summary["rule_breakdown"]:
                            rule_summary["rule_breakdown"][rule_type] += analysis[rule_type]
        
        return rule_summary

# Initialize navigator
navigator = BRENavigator()

@mcp.tool()
def list_business_functions() -> Dict[str, Any]:
    """List all business functions from Application Level BRE with their entry points and component dependencies"""
    functions = navigator.get_business_functions()
    
    return {
        "business_functions": functions,
        "total_functions": len(functions),
        "summary": {
            "functions_with_specs": len([f for f in functions if f["has_main_spec"]]),
            "total_entry_points": sum(len(f["entry_points"]) for f in functions),
            "functions_with_entry_points": len([f for f in functions if f["entry_points"]])
        }
    }

@mcp.tool()
def get_business_function_details(function_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific business function including all entry points and their component dependencies"""
    functions = navigator.get_business_functions()
    function_details = next((f for f in functions if f["name"] == function_name), None)
    
    if not function_details:
        available = [f["name"] for f in functions]
        return {
            "error": f"Business function '{function_name}' not found",
            "available_functions": available
        }
    
    return function_details

@mcp.tool()
def list_component_types() -> Dict[str, Any]:
    """List all available component types in the BRE directory
    
    Use this FIRST to discover available component types before using component-related tools.
    Shows type names, file counts, and sample filenames to guide proper usage.
    """
    component_types = []
    base_path = Path(navigator.component_level_bre)
    
    if base_path.exists():
        for item in base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Count files in each directory
                file_count = len(list(item.glob("*.json")))
                if file_count > 0:
                    component_types.append({
                        "type": item.name,
                        "file_count": file_count,
                        "sample_files": [f.name for f in list(item.glob("*.json"))[:3]]
                    })
    
    return {
        "component_types": component_types,
        "total_types": len(component_types),
        "base_path": str(base_path)
    }

@mcp.tool()
def list_all_components() -> Dict[str, Any]:
    """List all component level files (COBOL and JCL) available in the BRE"""
    components = navigator.get_all_component_files()
    
    # Calculate summary dynamically
    total_components = sum(len(files) for files in components.values())
    summary = {f"total_{comp_type}_files": len(files) for comp_type, files in components.items()}
    summary["total_components"] = total_components
    
    return {
        "components": components,
        "summary": summary
    }

@mcp.tool()
def search_components(pattern: str) -> Dict[str, Any]:
    """Search for component files by pattern/program name"""
    results = navigator.search_components_by_pattern(pattern)
    
    # Calculate summary dynamically
    total_matches = sum(len(files) for files in results.values())
    summary = {f"{comp_type}_matches": len(files) for comp_type, files in results.items()}
    summary["total_matches"] = total_matches
    
    return {
        "search_pattern": pattern,
        "results": results,
        "summary": summary
    }

@mcp.tool()
def get_bre_overview() -> Dict[str, Any]:
    """Get complete BRE hierarchy overview with statistics"""
    functions = navigator.get_business_functions()
    components = navigator.get_all_component_files()
    
    return {
        "bre_directories": {
            "application_level": navigator.app_level_bre,
            "component_level": navigator.component_level_bre
        },
        "business_functions": {
            "total": len(functions),
            "with_specifications": len([f for f in functions if f["has_main_spec"]]),
            "with_entry_points": len([f for f in functions if f["entry_points"]]),
            "total_entry_points": sum(len(f["entry_points"]) for f in functions)
        },
        "component_files": {
            "cobol": len(components["cobol"]),
            "jcl": len(components["jcl"]),
            "total": len(components["cobol"]) + len(components["jcl"])
        },
        "function_list": [f["name"] for f in functions]
    }

@mcp.tool()
def read_component_bre_content(component_name: str, component_type: str) -> Dict[str, Any]:
    """Read the complete content of a component BRE JSON file
    
    IMPORTANT: Use list_component_types() FIRST to see available component types.
    
    Args:
        component_name: Component name (e.g., 'COTRN02C')
        component_type: Exact type from list_component_types() (e.g., 'cbl', 'jcl')
    
    Workflow: list_component_types() → search_components() → read_component_bre_content()
    """
    return navigator.read_component_bre_file(component_name, component_type)

@mcp.tool()
def get_component_rule_analysis(component_name: str, component_type: str) -> Dict[str, Any]:
    """Get detailed rule analysis for a specific component
    
    IMPORTANT: Use list_component_types() FIRST to see available component types.
    
    Args:
        component_name: Component name (e.g., 'COTRN02C')  
        component_type: Exact type from list_component_types() (e.g., 'cbl', 'jcl')
    
    Provides rule counts and categorization for the component.
    """
    if component_type not in ["cbl", "jcl"]:
        return {"error": "Component type must be 'cbl' or 'jcl'"}
    
    file_path = Path(navigator.component_level_bre) / component_type / f"{component_name}-{component_type}.json"
    
    if not file_path.exists():
        return {"error": f"Component file not found: {file_path}"}
    
    analysis = navigator.count_rules_in_bre_file(file_path)
    analysis["component_name"] = component_name
    analysis["component_type"] = component_type
    analysis["file_path"] = str(file_path)
    
    return analysis

@mcp.tool()
def get_business_function_rules(function_name: str) -> Dict[str, Any]:
    """Get comprehensive rule count and analysis for a business function"""
    return navigator.get_business_function_rule_count(function_name)

@mcp.tool()
def get_all_business_function_rule_counts() -> Dict[str, Any]:
    """Get rule counts for all business functions"""
    functions = navigator.get_business_functions()
    
    summary = {
        "total_functions": len(functions),
        "function_rule_counts": [],
        "grand_total_rules": 0,
        "rule_breakdown_summary": {
            "business_rules": 0,
            "ui_navigation_rules": 0,
            "validation_rules": 0,
            "processing_rules": 0
        }
    }
    
    for function in functions:
        function_analysis = navigator.get_business_function_rule_count(function["name"])
        if "error" not in function_analysis:
            function_summary = {
                "function_name": function["name"],
                "total_rules": function_analysis["total_rules"],
                "component_count": len(function_analysis["components"]),
                "rule_breakdown": function_analysis["rule_breakdown"]
            }
            summary["function_rule_counts"].append(function_summary)
            summary["grand_total_rules"] += function_analysis["total_rules"]
            
            # Add to grand totals
            for rule_type, count in function_analysis["rule_breakdown"].items():
                summary["rule_breakdown_summary"][rule_type] += count
    
    # Sort by rule count descending
    summary["function_rule_counts"].sort(key=lambda x: x["total_rules"], reverse=True)
    
    return summary

def main():
    """Main entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()
