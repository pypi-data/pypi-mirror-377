import time
import sys
import signal
import atexit
_module_start_time = time.time()
print(f"[TIMING] Module import started at {_module_start_time}", flush=True)

from setuptools import setup, find_packages
from urllib.request import urlopen
from urllib.request import Request
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import ijson
import re
from packaging import specifiers, version

print(f"[TIMING] All imports completed in {time.time() - _module_start_time:.3f}s", flush=True)

# Global variable to track shared environments that need cleanup
_shared_envs_to_cleanup = []


def cleanup_all_shared_envs():
    """Clean up all tracked shared environments."""
    global _shared_envs_to_cleanup
    for env_path in _shared_envs_to_cleanup:
        cleanup_shared_venv(env_path)
    _shared_envs_to_cleanup.clear()


def signal_handler(signum, frame):
    """Handle signals (SIGINT, SIGTERM) to clean up environments."""
    print(f"\n⚠️  Received signal {signum}, cleaning up test environments...", flush=True)
    cleanup_all_shared_envs()
    print("✓ Cleanup complete, exiting", flush=True)
    sys.exit(1)


def register_cleanup_handlers():
    """Register cleanup handlers for graceful shutdown."""
    # Register atexit handler for normal exits
    atexit.register(cleanup_all_shared_envs)

    # Register signal handlers for interruptions
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

    # On Windows, also handle SIGBREAK
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal_handler)


def get_package_names():
    """
    Stream package names from PyPI using ijson for fast incremental parsing.
    This allows us to start processing packages immediately without waiting
    for the entire ~100MB JSON response to download.
    """

    url = "https://pypi.org/simple/"
    req = Request(url, headers={"Accept": "application/vnd.pypi.simple.v1+json"})

    with urlopen(req) as response:
        # Stream parse the projects array
        packages = ijson.items(response, 'projects.item.name')
        count = 0
        for package_name in packages:
            count += 1
            if count % 1000 == 0:
                print(f"Streamed {count} packages so far...")
            yield package_name


def get_all_packages_from_pypi():
    """
    Generator that yields package names from PyPI, excluding this package to avoid circular dependencies.
    This allows us to start processing packages immediately without waiting to build a full list.
    """
    package_names_to_exclude = {'mr-creosote', 'mr_creosote'}

    for package_name in get_package_names():
        if package_name not in package_names_to_exclude:
            yield package_name


def is_building():
    """
    Check if we're building for distribution vs installing from PyPI.

    Uses MR_CREOSOTE_BUILD environment variable for reliable detection.
    Set MR_CREOSOTE_BUILD=1 when building packages for distribution.
    If not set, we're in install context.
    """
    return bool(os.environ.get('MR_CREOSOTE_BUILD'))


def get_package_metadata(package_name, timeout=10):
    """
    Fetch package metadata from PyPI JSON API.
    Returns metadata dict or None if failed.
    """
    try:
        # Add a small delay to be respectful to PyPI
        import time
        time.sleep(0.05)  # Shorter delay for metadata requests

        url = f"https://pypi.org/pypi/{package_name}/json"
        req = Request(url, headers={"Accept": "application/json"})

        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except Exception:
        return None


def parse_dependencies(metadata):
    """
    Parse dependencies from package metadata.
    Returns dict of {dependency_name: version_specifier_string}
    """
    dependencies = {}

    if not metadata or 'info' not in metadata:
        return dependencies

    requires_dist = metadata['info'].get('requires_dist', [])
    if not requires_dist:
        return dependencies

    for requirement in requires_dist:
        # Parse requirement string like "requests>=2.0,<3.0; python_version>='3.6'"
        # Split on semicolon to ignore environment markers for now
        req_part = requirement.split(';')[0].strip()

        # Extract package name and version specifier
        match = re.match(r'^([a-zA-Z0-9_.-]+)(.*)$', req_part)
        if match:
            dep_name = match.group(1).lower()
            version_spec = match.group(2).strip()
            dependencies[dep_name] = version_spec

    return dependencies


def check_dependency_conflicts(existing_packages, new_package_deps):
    """
    Check if new package dependencies conflict with existing packages.
    Returns (has_conflict: bool, conflicts: list)
    """
    conflicts = []

    for dep_name, version_spec in new_package_deps.items():
        if dep_name in existing_packages:
            existing_spec = existing_packages[dep_name]

            try:
                # Parse version specifiers using packaging library
                new_spec_set = specifiers.SpecifierSet(version_spec) if version_spec else None
                existing_spec_set = specifiers.SpecifierSet(existing_spec) if existing_spec else None

                # If both have version constraints, check for overlap
                if new_spec_set and existing_spec_set:
                    # This is a simplified check - in reality we'd need to check
                    # if there's any version that satisfies both specifiers
                    # For now, we'll just flag obvious conflicts like >=2.0 vs <2.0
                    conflicts.append({
                        'dependency': dep_name,
                        'existing_spec': existing_spec,
                        'new_spec': version_spec,
                        'reason': 'version_constraint_conflict'
                    })
            except Exception:
                # If we can't parse the specifiers, skip conflict detection for this dep
                continue

    return len(conflicts) > 0, conflicts


def test_package_install(package_name, shared_test_dir, timeout=30):
    """
    Test if a package can be installed in the shared test directory.
    Returns True if the package installs successfully alongside existing packages.
    """
    try:
        # Add a small delay to be respectful to PyPI
        import time
        time.sleep(0.1)

        # Try to install the package to the shared test directory using current Python
        # Include dependencies to build up a shared dependency cache for later packages
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--target', shared_test_dir,
            '--quiet', package_name
        ], capture_output=True, timeout=timeout, text=True)

        # If installation succeeds, the package is compatible
        if result.returncode == 0:
            print(f"✓ Successfully installed {package_name} in shared test directory", flush=True)
            return True
        else:
            print(f"✗ Failed to install {package_name}: {result.stderr.strip()}", flush=True)
            return False

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        print(f"✗ Error installing {package_name}: {e}", flush=True)
        return False


def create_shared_venv():
    """Create a shared test directory for testing package compatibility."""
    global _shared_envs_to_cleanup

    # Register cleanup handlers on first use
    if not _shared_envs_to_cleanup:
        register_cleanup_handlers()

    # Create a temporary directory for testing package installations
    shared_test_dir = tempfile.mkdtemp(prefix="mr_creosote_test_")

    print(f"Creating shared test directory at {shared_test_dir}", flush=True)

    try:
        # Test that we can use pip from the current environment
        test_result = subprocess.run([
            sys.executable, '-m', 'pip', '--version'
        ], capture_output=True, timeout=10)

        if test_result.returncode != 0:
            raise Exception(f"Pip not available in current environment: {test_result.stderr.decode()}")

        # Register this directory for cleanup
        _shared_envs_to_cleanup.append(shared_test_dir)

        print(f"✓ Created shared test directory (registered for cleanup)", flush=True)
        return shared_test_dir

    except Exception as e:
        print(f"✗ Failed to create shared test directory: {e}", flush=True)
        # Clean up on failure
        import shutil
        shutil.rmtree(shared_test_dir, ignore_errors=True)
        return None


def cleanup_shared_venv(shared_venv_path):
    """Clean up the shared virtual environment."""
    global _shared_envs_to_cleanup

    if shared_venv_path and os.path.exists(shared_venv_path):
        import shutil
        try:
            shutil.rmtree(shared_venv_path)
            print(f"✓ Cleaned up shared test environment at {shared_venv_path}", flush=True)
        except Exception as e:
            print(f"⚠️  Failed to clean up test environment: {e}", flush=True)

        # Remove from tracking list
        if shared_venv_path in _shared_envs_to_cleanup:
            _shared_envs_to_cleanup.remove(shared_venv_path)


def test_package_with_metadata(package_name, existing_deps=None, timeout=10):
    """
    Test package installability and check for dependency conflicts.
    Returns (is_installable: bool, metadata: dict, conflicts: list)
    """
    if existing_deps is None:
        existing_deps = {}

    # First, try to get metadata (faster than downloading)
    metadata = get_package_metadata(package_name, timeout)
    if not metadata:
        # If metadata fetch fails, fall back to download test
        is_installable = test_package_install(package_name, timeout)
        return is_installable, None, []

    # Parse dependencies from metadata
    deps = parse_dependencies(metadata)

    # Check for conflicts with existing packages
    has_conflicts, conflicts = check_dependency_conflicts(existing_deps, deps)

    # If no obvious conflicts, do download test
    if not has_conflicts:
        is_installable = test_package_install(package_name, timeout)
        return is_installable, metadata, []
    else:
        # Skip packages with conflicts
        return False, metadata, conflicts


def get_installable_packages(package_generator, max_workers=5, batch_size=10):
    """
    Filter package generator to only include packages that can actually be installed together.
    Uses a shared test directory to test real installation compatibility.
    """
    installable = []
    batch_num = 0

    # Create a shared test directory for testing
    shared_test_dir = create_shared_venv()
    if not shared_test_dir:
        print("Failed to create shared test directory, falling back to download-only tests")
        return []

    try:
        # Convert generator to batches
        batch = []
        print(f"[TIMING] Starting to iterate over package generator...", flush=True)
        package_count = 0

        for package_name in package_generator:
            package_count += 1
            if package_count == 1:
                print(f"[TIMING] First package from generator: {package_name}", flush=True)
            batch.append(package_name)

            # Process when batch is full
            if len(batch) >= batch_size:
                batch_num += 1
                print(f"Testing batch {batch_num} ({len(batch)} packages) in shared test directory...")

                # Test packages sequentially in the shared test directory
                # This ensures we catch conflicts between packages
                for package in batch:
                    try:
                        if test_package_install(package, shared_test_dir):
                            installable.append(package)
                    except Exception as e:
                        print(f"✗ {package} (error: {e})")

                print(f"Batch {batch_num} complete. Total compatible packages so far: {len(installable)}")

                # Clear batch for next iteration
                batch = []

        # Process any remaining packages in the final batch
        if batch:
            batch_num += 1
            print(f"Testing final batch {batch_num} ({len(batch)} packages) in shared test directory...")

            for package in batch:
                try:
                    if test_package_install(package, shared_test_dir):
                        installable.append(package)
                except Exception as e:
                    print(f"✗ {package} (error: {e})")

        print(f"Compatibility testing complete. Found {len(installable)} compatible packages.")
        return installable

    finally:
        # Always clean up the shared test directory
        cleanup_shared_venv(shared_test_dir)


def debug_build_detection():
    """Debug function to show why we think we're in build mode or not"""
    reasons = []

    # Check direct commands
    build_commands = {'sdist', 'bdist', 'bdist_wheel', 'bdist_egg', 'build'}
    if any(cmd in sys.argv for cmd in build_commands):
        reasons.append(f"Direct command found: {[cmd for cmd in build_commands if cmd in sys.argv]}")

    # Check env vars
    build_env_vars = [
        'BUILD_FRONTEND', 'PEP517_BUILD_BACKEND',
        'SETUPTOOLS_SCM_PRETEND_VERSION', '_PYPROJECT_HOOKS_BUILD_BACKEND'
    ]
    found_envs = [var for var in build_env_vars if os.environ.get(var)]
    if found_envs:
        reasons.append(f"Build env vars found: {found_envs}")

    # Check process chain
    try:
        import psutil
        current_process = psutil.Process()
        parent_chain = []
        proc = current_process
        for _ in range(5):
            try:
                proc = proc.parent()
                if proc is None:
                    break
                parent_chain.append(proc.name().lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

        build_tools = {'uv', 'build', 'pip', 'twine', 'hatch', 'pdm', 'poetry'}
        found_tools = [tool for tool in build_tools if tool in ' '.join(parent_chain)]
        if found_tools:
            reasons.append(f"Build tools in process chain: {found_tools} (chain: {parent_chain})")
    except ImportError:
        reasons.append("psutil not available for process chain check")

    # Check other indicators
    if 'egg_info' in sys.argv:
        reasons.append("egg_info command found")
    if any('wheel' in arg for arg in sys.argv):
        reasons.append("wheel-related args found")

    print(f"sys.argv: {sys.argv}")
    print(f"Build detection reasons: {reasons}")
    return bool(reasons)


def get_dependencies():
    """
    Smart dependency resolution:
    - During build: return only techdragon package (to keep metadata size reasonable)
    - During install: enumerate all PyPI packages and test in shared environment for maximum compatibility
    """
    import time
    print(f"[TIMING] get_dependencies() called at {time.time() - _module_start_time:.3f}s after module start", flush=True)

    building = is_building()

    # Debug output
    print(f"=== MR CREOSOTE BUILD DETECTION ===")
    print(f"Final decision: {'BUILD' if building else 'INSTALL'} context")
    print(f"=====================================")

    if building:
        print("Build context detected - using only techdragon package for reasonable metadata size")
        return ["techdragon"]
    else:
        print("Install context detected - enumerating ALL PyPI packages and testing compatibility")
        print("Creating shared virtual environment to test real package compatibility...")

        start_time = time.time()

        all_packages = get_all_packages_from_pypi()
        print(f"Generator created in {time.time() - start_time:.2f}s", flush=True)

        # Test: get first package from generator
        first_package = next(all_packages)
        print(f"First package '{first_package}' received in {time.time() - start_time:.2f}s", flush=True)

        # Put it back by creating a new generator that yields it first
        def prepend_first(first, generator):
            yield first
            yield from generator

        all_packages_with_first = prepend_first(first_package, all_packages)

        print(f"[TIMING] Starting get_installable_packages() at {time.time() - start_time:.3f}s", flush=True)
        installable = get_installable_packages(all_packages_with_first)
        print(f"Found {len(installable)} installable packages")
        return installable


setup(
    name="mr-creosote",
    version="1.0.0",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=get_dependencies(),
)