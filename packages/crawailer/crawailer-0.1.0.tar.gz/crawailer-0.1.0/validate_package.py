#!/usr/bin/env python3
"""
Package Validation Script

Validates that Crawailer is properly packaged for PyPI publication.
"""

import sys
import os
import zipfile
import tarfile
import json
from pathlib import Path

def validate_wheel(wheel_path):
    """Validate wheel distribution"""
    print(f"🔍 Validating wheel: {wheel_path}")
    
    with zipfile.ZipFile(wheel_path, 'r') as wheel:
        files = wheel.namelist()
        
        # Check for required files
        required_files = [
            'crawailer/__init__.py',
            'crawailer/api.py', 
            'crawailer/browser.py',
            'crawailer/content.py',
            'crawailer/cli.py'
        ]
        
        missing_files = []
        for req_file in required_files:
            if req_file not in files:
                missing_files.append(req_file)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        print(f"✅ All required Python files present")
        
        # Check metadata
        metadata_files = [f for f in files if f.endswith('METADATA')]
        if not metadata_files:
            print("❌ No METADATA file found")
            return False
        
        metadata_content = wheel.read(metadata_files[0]).decode('utf-8')
        
        # Check for key metadata
        required_metadata = [
            'Name: crawailer',
            'Version: 0.1.0',
            'Author-email: rpm',
            'License: MIT',
            'Requires-Python: >=3.11'
        ]
        
        for req_meta in required_metadata:
            if req_meta not in metadata_content:
                print(f"❌ Missing metadata: {req_meta}")
                return False
        
        print("✅ Wheel metadata is valid")
        
        # Check for entry points
        entry_point_files = [f for f in files if f.endswith('entry_points.txt')]
        if entry_point_files:
            entry_content = wheel.read(entry_point_files[0]).decode('utf-8')
            if 'crawailer = crawailer.cli:main' in entry_content:
                print("✅ CLI entry point configured")
            else:
                print("❌ CLI entry point not found")
                return False
        
        print(f"✅ Wheel contains {len(files)} files")
        return True

def validate_sdist(sdist_path):
    """Validate source distribution"""
    print(f"\n🔍 Validating sdist: {sdist_path}")
    
    with tarfile.open(sdist_path, 'r:gz') as tar:
        files = tar.getnames()
        
        # Check for required source files
        required_files = [
            'crawailer-0.1.0/src/crawailer/__init__.py',
            'crawailer-0.1.0/src/crawailer/api.py',
            'crawailer-0.1.0/pyproject.toml',
            'crawailer-0.1.0/README.md',
            'crawailer-0.1.0/LICENSE',
            'crawailer-0.1.0/CHANGELOG.md'
        ]
        
        missing_files = []
        for req_file in required_files:
            if req_file not in files:
                missing_files.append(req_file)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        print("✅ All required source files present")
        
        # Check documentation
        doc_files = [f for f in files if '/docs/' in f and f.endswith('.md')]
        print(f"✅ Documentation files: {len(doc_files)}")
        
        print(f"✅ Sdist contains {len(files)} files")
        return True

def validate_pyproject_toml():
    """Validate pyproject.toml configuration"""
    print(f"\n🔍 Validating pyproject.toml")
    
    pyproject_path = Path('pyproject.toml')
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False
    
    try:
        import tomllib
    except ImportError:
        # Python < 3.11 fallback
        try:
            import tomli as tomllib
        except ImportError:
            print("⚠️  Cannot validate TOML (no tomllib/tomli available)")
            return True
    
    try:
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
        
        # Check build system
        if 'build-system' not in config:
            print("❌ Missing build-system")
            return False
        
        if config['build-system']['build-backend'] != 'hatchling.build':
            print("❌ Incorrect build backend")
            return False
        
        print("✅ Build system configured correctly")
        
        # Check project metadata
        project = config.get('project', {})
        
        required_fields = ['name', 'description', 'requires-python', 'authors']
        for field in required_fields:
            if field not in project:
                print(f"❌ Missing project field: {field}")
                return False
        
        print("✅ Project metadata complete")
        
        # Check dependencies
        deps = project.get('dependencies', [])
        critical_deps = ['playwright', 'selectolax', 'markdownify']
        
        for dep in critical_deps:
            if not any(dep in d for d in deps):
                print(f"❌ Missing critical dependency: {dep}")
                return False
        
        print("✅ Dependencies configured correctly")
        
        # Check optional dependencies
        optional_deps = project.get('optional-dependencies', {})
        expected_groups = ['dev', 'ai', 'mcp', 'testing']
        
        for group in expected_groups:
            if group not in optional_deps:
                print(f"⚠️  Missing optional dependency group: {group}")
            else:
                print(f"✅ Optional dependency group '{group}': {len(optional_deps[group])} packages")
        
        # Check URLs
        urls = project.get('urls', {})
        required_urls = ['Homepage', 'Repository', 'Documentation']
        
        for url_type in required_urls:
            if url_type not in urls:
                print(f"❌ Missing URL: {url_type}")
                return False
        
        print("✅ Project URLs configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing pyproject.toml: {e}")
        return False

def validate_package_structure():
    """Validate source package structure"""
    print(f"\n🔍 Validating package structure")
    
    required_files = [
        'src/crawailer/__init__.py',
        'src/crawailer/api.py',
        'src/crawailer/browser.py',
        'src/crawailer/content.py',
        'src/crawailer/cli.py',
        'README.md',
        'LICENSE',
        'pyproject.toml',
        'CHANGELOG.md'
    ]
    
    missing_files = []
    for req_file in required_files:
        if not Path(req_file).exists():
            missing_files.append(req_file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files present")
    
    # Check documentation
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print("❌ Missing docs directory")
        return False
    
    doc_files = list(docs_dir.glob('*.md'))
    print(f"✅ Documentation files: {len(doc_files)}")
    
    expected_docs = ['README.md', 'JAVASCRIPT_API.md', 'API_REFERENCE.md', 'BENCHMARKS.md']
    for doc in expected_docs:
        doc_path = docs_dir / doc
        if doc_path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ Missing: {doc}")
    
    return True

def check_import_structure():
    """Check that imports work correctly"""
    print(f"\n🔍 Validating import structure")
    
    sys.path.insert(0, str(Path('src').absolute()))
    
    try:
        # Test basic import
        import crawailer
        print(f"✅ Basic import successful")
        print(f"  Version: {crawailer.__version__}")
        
        # Test submodule imports
        from crawailer import get, get_many, discover
        print("✅ High-level API functions importable")
        
        from crawailer import Browser, BrowserConfig, WebContent
        print("✅ Core classes importable") 
        
        # Check __all__ exports
        expected_exports = [
            'Browser', 'BrowserConfig', 'WebContent', 'ContentExtractor',
            'clean_text', 'extract_links', 'detect_content_type',
            'get', 'get_many', 'discover'
        ]
        
        missing_exports = []
        for export in expected_exports:
            if export not in crawailer.__all__:
                missing_exports.append(export)
        
        if missing_exports:
            print(f"❌ Missing from __all__: {missing_exports}")
            return False
        
        print("✅ All expected exports available")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all package validations"""
    print("🚀 Crawailer Package Validation")
    print("=" * 50)
    
    all_valid = True
    
    # Check package structure
    if not validate_package_structure():
        all_valid = False
    
    # Check pyproject.toml
    if not validate_pyproject_toml():
        all_valid = False
    
    # Check imports (may fail if dependencies not installed)
    try:
        if not check_import_structure():
            all_valid = False
    except Exception as e:
        print(f"⚠️  Import validation skipped (dependencies not installed): {e}")
    
    # Check distributions if they exist
    dist_dir = Path('dist')
    if dist_dir.exists():
        wheels = list(dist_dir.glob('*.whl'))
        sdists = list(dist_dir.glob('*.tar.gz'))
        
        for wheel in wheels:
            if not validate_wheel(wheel):
                all_valid = False
        
        for sdist in sdists:
            if not validate_sdist(sdist):
                all_valid = False
    else:
        print("\n⚠️  No dist/ directory found - run 'python -m build' first")
    
    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 Package validation successful!")
        print("✅ Ready for PyPI publication")
        return 0
    else:
        print("❌ Package validation failed")
        print("🔧 Please fix the issues above before publishing")
        return 1

if __name__ == "__main__":
    sys.exit(main())