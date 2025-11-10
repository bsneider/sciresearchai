#!/usr/bin/env python3
"""
Verify Bach + Local PubMed Data Integration
Tests that the streamlined Bach system can properly use the downloaded PubMed data.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def test_data_exists():
    """Verify that PubMed data files exist and are accessible."""
    print("🔍 Testing PubMed data files...")

    data_paths = [
        "temp_aiscientist/data/pubmed_data_2000.csv",
        "temp_aiscientist/data/pubmed_data.csv"
    ]

    for path in data_paths:
        if Path(path).exists():
            size_mb = Path(path).stat().st_size / (1024 * 1024)
            print(f"✅ Found: {path} ({size_mb:.1f}MB)")
        else:
            print(f"❌ Missing: {path}")
            return False

    return True

def test_dependencies():
    """Test that all required dependencies are installed."""
    print("\n🔍 Testing dependencies...")

    try:
        import pandas as pd
        print("✅ pandas installed")
    except ImportError:
        print("❌ pandas not installed")
        return False

    return True

async def test_local_loader():
    """Test local PubMed data loader directly."""
    print("\n🔍 Testing local PubMed data loader...")

    try:
        # Set environment variable
        os.environ["LOCAL_PUBMED_DATA_PATH"] = "temp_aiscientist/data/pubmed_data_2000.csv"

        # Import and test
        sys.path.append('.claude/commands/bach/utils/apis')
        from local_pubmed_data import LocalPubMedDataLoader

        loader = LocalPubMedDataLoader()
        if loader.initialize():
            stats = loader.get_statistics()
            print(f"✅ Loader initialized with {stats['total_articles']} articles")

            # Test search
            results = loader.search("cardiac", limit=3)
            print(f"✅ Search found {len(results)} results")
            return True
        else:
            print("❌ Failed to initialize loader")
            return False

    except Exception as e:
        print(f"❌ Local loader test failed: {e}")
        return False

async def test_streamlined_executor():
    """Test streamlined research executor with local data."""
    print("\n🔍 Testing streamlined research executor...")

    try:
        os.environ["LOCAL_PUBMED_DATA_PATH"] = "temp_aiscientist/data/pubmed_data_2000.csv"

        sys.path.append('.claude/commands/bach/utils')
        from streamlined_research_executor import StreamlinedResearchExecutor

        executor = StreamlinedResearchExecutor("cardiac rehabilitation")
        papers = await executor.search_papers(max_results=3)

        local_papers = [p for p in papers if p.get('source') == 'local_pubmed']

        if len(local_papers) > 0:
            print(f"✅ Executor found {len(local_papers)} local papers")
            print(f"📄 First local paper: {local_papers[0]['title'][:60]}...")
            return True
        else:
            print("❌ No local papers found by executor")
            return False

    except Exception as e:
        print(f"❌ Executor test failed: {e}")
        return False

def test_complete_bach():
    """Test complete streamlined Bach system."""
    print("\n🔍 Testing complete streamlined Bach system...")

    try:
        cmd = [
            "python", ".claude/commands/bach/streamlined_bach.py",
            "cardiac prevention"
        ]

        env = os.environ.copy()
        env["LOCAL_PUBMED_DATA_PATH"] = "temp_aiscientist/data/pubmed_data_2000.csv"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )

        if result.returncode == 0:
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "papers from local PubMed data" in line:
                    print(f"✅ {line.strip()}")
                    return True

            print("✅ Bach completed successfully")
            return True
        else:
            print(f"❌ Bach failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Complete Bach test failed: {e}")
        return False

async def main():
    """Run all verification tests."""
    print("🚀 Bach + Local PubMed Data Integration Verification")
    print("=" * 60)

    tests = [
        ("Data Files", test_data_exists),
        ("Dependencies", test_dependencies),
        ("Local Loader", test_local_loader),
        ("Streamlined Executor", test_streamlined_executor),
        ("Complete Bach", test_complete_bach),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall Result: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! Bach is ready to use with local PubMed data.")
        print("\n💡 Usage:")
        print("   export LOCAL_PUBMED_DATA_PATH=\"temp_aiscientist/data/pubmed_data_2000.csv\"")
        print("   python .claude/commands/bach/streamlined_bach.py \"your research topic\"")
    else:
        print("⚠️  Some tests failed. Check the details above.")

    return passed == len(results)

if __name__ == "__main__":
    asyncio.run(main())