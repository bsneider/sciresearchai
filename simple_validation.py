#!/usr/bin/env python3
"""
Simple Milestone 1 Validation Script
"""

import os
import re

def check_method_exists(file_path, class_name, method_name):
    """Check if a method exists in a class"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Find class definition
        class_pattern = rf'class {class_name}[^:]*:'
        class_match = re.search(class_pattern, content)

        if not class_match:
            return False

        # Extract class content (simplified)
        class_start = class_match.end()
        remaining_content = content[class_start:]

        # Look for method in class
        method_pattern = rf'def {method_name}\s*\('
        return bool(re.search(method_pattern, remaining_content))

    except Exception:
        return False

def validate_methods():
    """Validate key methods exist"""
    print("🔍 Validating Key Methods...")

    validations = [
        ('agents/paper_search/search_agent.py', 'SearchAgent', 'search_all_databases'),
        ('agents/paper_search/search_agent.py', 'SearchAgent', 'search_semantic_scholar'),
        ('agents/paper_search/search_agent.py', 'SearchAgent', 'search_arxiv'),
        ('agents/paper_search/search_agent.py', 'SearchAgent', 'search_pubmed'),
        ('agents/paper_search/search_agent.py', 'SearchAgent', 'vector_search'),
        ('agents/paper_search/search_agent.py', 'SearchAgent', 'score_relevance'),
        ('agents/paper_search/api_integrations.py', 'APIIntegrationManager', 'search'),
        ('agents/paper_search/api_integrations.py', 'APIIntegrationManager', 'search_all'),
        ('agents/paper_search/vector_search.py', 'VectorSearchEngine', 'semantic_search'),
        ('agents/paper_search/vector_search.py', 'VectorSearchEngine', 'hybrid_search'),
        ('agents/paper_search/vector_search.py', 'VectorSearchEngine', 'add_documents'),
        ('agents/paper_search/search_workflow.py', 'SearchWorkflowOrchestrator', 'execute_search_workflow'),
        ('agents/paper_search/search_workflow.py', 'SearchWorkflowOrchestrator', 'execute_enhanced_search_workflow'),
        ('agents/paper_search/search_workflow.py', 'SearchWorkflowOrchestrator', 'coordinate_parallel_search'),
    ]

    passed = 0
    total = len(validations)

    for file_path, class_name, method_name in validations:
        if os.path.exists(file_path):
            if check_method_exists(file_path, class_name, method_name):
                print(f"  ✅ {class_name}.{method_name}() found")
                passed += 1
            else:
                print(f"  ❌ {class_name}.{method_name}() not found")
        else:
            print(f"  ❌ {file_path} missing")

    print(f"\nMethods: {passed}/{total} validated")
    return passed == total

def validate_test_count():
    """Check test method count more accurately"""
    print("🔍 Counting Test Methods...")

    test_files = [
        'tests/unit/test_search_agent.py',
        'tests/unit/test_api_integrations.py',
        'tests/unit/test_vector_search.py',
        'tests/unit/test_search_workflow.py'
    ]

    total_methods = 0

    for test_file in test_files:
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()

            # Count test methods
            test_methods = len(re.findall(r'def test_[^(]*\(', content))
            total_methods += test_methods
            print(f"  📊 {os.path.basename(test_file)}: {test_methods} test methods")

    print(f"  📊 Total test methods: {total_methods}")

    if total_methods >= 50:
        print("  ✅ Sufficient test coverage")
        return True
    else:
        print("  ❌ Insufficient test coverage (need >= 50)")
        return False

def main():
    """Run simple validation"""
    print("🚀 Simple Milestone 1 Validation")
    print("=" * 50)

    # Check file structure
    print("🔍 Checking File Structure...")
    required_files = [
        'agents/paper_search/__init__.py',
        'agents/paper_search/search_agent.py',
        'agents/paper_search/api_integrations.py',
        'agents/paper_search/vector_search.py',
        'agents/paper_search/search_workflow.py',
        'agents/paper_search/README.md'
    ]

    structure_ok = all(os.path.exists(f) for f in required_files)
    print(f"  {'✅' if structure_ok else '❌'} All required files present")

    # Check methods
    methods_ok = validate_methods()

    # Check test count
    tests_ok = validate_test_count()

    # Final result
    print("\n" + "=" * 50)
    if structure_ok and methods_ok and tests_ok:
        print("🎉 MILESTONE 1 VALIDATION SUCCESSFUL!")
        return True
    else:
        print("❌ MILESTONE 1 VALIDATION FAILED")
        print(f"Structure: {'✅' if structure_ok else '❌'}")
        print(f"Methods: {'✅' if methods_ok else '❌'}")
        print(f"Tests: {'✅' if tests_ok else '❌'}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)