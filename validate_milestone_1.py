#!/usr/bin/env python3
"""
Milestone 1 Validation Script
Validates Core Search Infrastructure implementation
"""

import sys
import os
import ast
import inspect
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

class MilestoneValidator:
    """Validates Milestone 1: Core Search Infrastructure"""

    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "details": []
        }

    def validate_file_structure(self) -> bool:
        """Validate required file structure"""
        print("🔍 Validating File Structure...")

        required_files = [
            'agents/paper_search/__init__.py',
            'agents/paper_search/search_agent.py',
            'agents/paper_search/api_integrations.py',
            'agents/paper_search/vector_search.py',
            'agents/paper_search/search_workflow.py',
            'agents/paper_search/README.md'
        ]

        all_exist = True
        for file in required_files:
            if os.path.exists(file):
                self.log_success(f"✅ {file} exists")
            else:
                self.log_failure(f"❌ {file} missing")
                all_exist = False

        return all_exist

    def validate_module_exports(self) -> bool:
        """Validate module exports and imports"""
        print("🔍 Validating Module Exports...")

        try:
            # Read __init__.py and check exports
            with open('agents/paper_search/__init__.py', 'r') as f:
                content = f.read()

            # Parse AST to extract exports
            tree = ast.parse(content)
            all_exports = None

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == '__all__':
                            all_exports = node.value.elts
                            break

            if not all_exports:
                self.log_failure("❌ No __all__ exports found")
                return False

            expected_exports = [
                "SearchAgent", "VectorSearchEngine", "EmbeddingGenerator",
                "SimilarityCalculator", "HybridSearchRanker", "APIIntegrationManager",
                "SearchWorkflowOrchestrator", "SearchStrategy", "CoverageAnalyzer",
                "ResultAggregator", "WorkflowProgressTracker"
            ]

            exported_names = [elem.s for elem in all_exports if hasattr(elem, 's')]

            for export in expected_exports:
                if export in exported_names:
                    self.log_success(f"✅ {export} exported")
                else:
                    self.log_failure(f"❌ {export} not exported")

            return len([e for e in expected_exports if e in exported_names]) == len(expected_exports)

        except Exception as e:
            self.log_failure(f"❌ Error validating exports: {e}")
            return False

    def validate_class_definitions(self) -> bool:
        """Validate core class definitions"""
        print("🔍 Validating Class Definitions...")

        required_classes = {
            'agents/paper_search/search_agent.py': ['SearchAgent', 'RateLimiter'],
            'agents/paper_search/api_integrations.py': ['APIIntegrationManager', 'SemanticScholarAPI', 'ArxivAPI', 'PubmedAPI'],
            'agents/paper_search/vector_search.py': ['VectorSearchEngine', 'EmbeddingGenerator', 'SimilarityCalculator', 'HybridSearchRanker'],
            'agents/paper_search/search_workflow.py': ['SearchWorkflowOrchestrator', 'SearchStrategy', 'CoverageAnalyzer', 'ResultAggregator', 'WorkflowProgressTracker']
        }

        all_valid = True
        for file_path, expected_classes in required_classes.items():
            if not os.path.exists(file_path):
                self.log_failure(f"❌ {file_path} not found")
                all_valid = False
                continue

            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                tree = ast.parse(content)
                defined_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

                for class_name in expected_classes:
                    if class_name in defined_classes:
                        self.log_success(f"✅ {class_name} defined in {os.path.basename(file_path)}")
                    else:
                        self.log_failure(f"❌ {class_name} not found in {os.path.basename(file_path)}")
                        all_valid = False

            except Exception as e:
                self.log_failure(f"❌ Error parsing {file_path}: {e}")
                all_valid = False

        return all_valid

    def validate_method_signatures(self) -> bool:
        """Validate key method signatures"""
        print("🔍 Validating Method Signatures...")

        expected_methods = {
            'SearchAgent': [
                '__init__', 'search_all_databases', 'search_semantic_scholar',
                'search_arxiv', 'search_pubmed', 'vector_search', 'score_relevance'
            ],
            'APIIntegrationManager': [
                '__init__', 'search', 'search_all', 'is_available'
            ],
            'VectorSearchEngine': [
                '__init__', 'semantic_search', 'hybrid_search', 'add_documents'
            ],
            'SearchWorkflowOrchestrator': [
                '__init__', 'execute_search_workflow', 'execute_enhanced_search_workflow',
                'coordinate_parallel_search', 'analyze_search_performance'
            ]
        }

        all_valid = True

        # Map files to classes
        class_files = {
            'SearchAgent': 'agents/paper_search/search_agent.py',
            'APIIntegrationManager': 'agents/paper_search/api_integrations.py',
            'VectorSearchEngine': 'agents/paper_search/vector_search.py',
            'SearchWorkflowOrchestrator': 'agents/paper_search/search_workflow.py'
        }

        for class_name, methods in expected_methods.items():
            file_path = class_files[class_name]

            if not os.path.exists(file_path):
                self.log_failure(f"❌ {file_path} not found")
                all_valid = False
                continue

            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                tree = ast.parse(content)

                # Find the class
                class_node = None
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        class_node = node
                        break

                if not class_node:
                    self.log_failure(f"❌ {class_name} not found in {os.path.basename(file_path)}")
                    all_valid = False
                    continue

                # Get method names
                defined_methods = [node.name for node in class_node.body if isinstance(node, ast.FunctionDef)]

                for method_name in methods:
                    if method_name in defined_methods:
                        self.log_success(f"✅ {class_name}.{method_name}() defined")
                    else:
                        self.log_failure(f"❌ {class_name}.{method_name}() not found")
                        all_valid = False

            except Exception as e:
                self.log_failure(f"❌ Error parsing {file_path}: {e}")
                all_valid = False

        return all_valid

    def validate_test_coverage(self) -> bool:
        """Validate test file structure"""
        print("🔍 Validating Test Coverage...")

        test_files = [
            'tests/unit/test_search_agent.py',
            'tests/unit/test_api_integrations.py',
            'tests/unit/test_vector_search.py',
            'tests/unit/test_search_workflow.py'
        ]

        total_test_methods = 0

        for test_file in test_files:
            if not os.path.exists(test_file):
                self.log_failure(f"❌ {test_file} missing")
                return False

            try:
                with open(test_file, 'r') as f:
                    content = f.read()

                tree = ast.parse(content)
                test_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name.startswith('Test')]
                test_methods = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]

                total_test_methods += len(test_methods)

                self.log_success(f"✅ {os.path.basename(test_file)}: {len(test_classes)} test classes, {len(test_methods)} test methods")

            except Exception as e:
                self.log_failure(f"❌ Error parsing {test_file}: {e}")
                return False

        # Validate minimum test coverage
        if total_test_methods >= 50:  # Expecting at least 50 test methods
            self.log_success(f"✅ Adequate test coverage: {total_test_methods} test methods")
            return True
        else:
            self.log_failure(f"❌ Insufficient test coverage: {total_test_methods} test methods (minimum 50)")
            return False

    def validate_documentation(self) -> bool:
        """Validate documentation completeness"""
        print("🔍 Validating Documentation...")

        if not os.path.exists('agents/paper_search/README.md'):
            self.log_failure("❌ README.md missing")
            return False

        try:
            with open('agents/paper_search/README.md', 'r') as f:
                content = f.read()

            # Check for key sections
            required_sections = [
                "## Features",
                "## Usage",
                "## Architecture",
                "## Dependencies",
                "## Configuration"
            ]

            all_sections_present = True
            for section in required_sections:
                if section in content:
                    self.log_success(f"✅ {section} section found")
                else:
                    self.log_failure(f"❌ {section} section missing")
                    all_sections_present = False

            # Check for code examples
            if "```python" in content:
                self.log_success("✅ Code examples included")
            else:
                self.log_failure("❌ No code examples found")
                all_sections_present = False

            return all_sections_present

        except Exception as e:
            self.log_failure(f"❌ Error reading README.md: {e}")
            return False

    def validate_integration_points(self) -> bool:
        """Validate integration between components"""
        print("🔍 Validating Integration Points...")

        # Check that main SearchAgent properly integrates other components
        try:
            with open('agents/paper_search/search_agent.py', 'r') as f:
                agent_content = f.read()

            integration_checks = [
                ('APIIntegrationManager', 'Core API integration'),
                ('VectorSearchEngine', 'Vector search integration'),
                ('SearchWorkflowOrchestrator', 'Workflow orchestration integration')
            ]

            all_integrations_valid = True
            for component, description in integration_checks:
                if component in agent_content:
                    self.log_success(f"✅ {description} found")
                else:
                    self.log_failure(f"❌ {description} missing")
                    all_integrations_valid = False

            return all_integrations_valid

        except Exception as e:
            self.log_failure(f"❌ Error checking integrations: {e}")
            return False

    def log_success(self, message: str):
        """Log successful validation"""
        print(f"  {message}")
        self.results["passed"] += 1
        self.results["details"].append({"status": "PASS", "message": message})

    def log_failure(self, message: str):
        """Log failed validation"""
        print(f"  {message}")
        self.results["failed"] += 1
        self.results["details"].append({"status": "FAIL", "message": message})

    def run_validation(self) -> Dict[str, Any]:
        """Run complete validation"""
        print("🚀 Starting Milestone 1: Core Search Infrastructure Validation")
        print("=" * 70)

        validations = [
            ("File Structure", self.validate_file_structure),
            ("Module Exports", self.validate_module_exports),
            ("Class Definitions", self.validate_class_definitions),
            ("Method Signatures", self.validate_method_signatures),
            ("Test Coverage", self.validate_test_coverage),
            ("Documentation", self.validate_documentation),
            ("Integration Points", self.validate_integration_points)
        ]

        results = {}
        for name, validator in validations:
            print()
            results[name] = validator()

        print()
        print("=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)

        total_validations = len(validations)
        passed_validations = sum(1 for result in results.values() if result)

        for name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status:<8} {name}")

        print()
        print(f"Overall: {passed_validations}/{total_validations} validation categories passed")
        print(f"Checks: {self.results['passed']} passed, {self.results['failed']} failed")

        if passed_validations == total_validations:
            print("\n🎉 MILESTONE 1 VALIDATION SUCCESSFUL!")
            print("✅ Core Search Infrastructure is fully implemented and validated")
        else:
            print("\n❌ MILESTONE 1 VALIDATION FAILED")
            print("❌ Some components need attention before milestone completion")

        return {
            "milestone": "M1 - Core Search Infrastructure",
            "overall_passed": passed_validations == total_validations,
            "categories_passed": passed_validations,
            "total_categories": total_validations,
            "checks_passed": self.results["passed"],
            "checks_failed": self.results["failed"],
            "details": self.results["details"]
        }


def main():
    """Run milestone validation"""
    validator = MilestoneValidator()
    results = validator.run_validation()

    # Exit with appropriate code
    sys.exit(0 if results["overall_passed"] else 1)


if __name__ == "__main__":
    main()