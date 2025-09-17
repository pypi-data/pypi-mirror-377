#!/usr/bin/env python3
"""Poetry build script for Cython extensions."""

import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path
from distutils.core import setup, Distribution
from distutils.extension import Extension as DistutilsExtension

try:
    import numpy as np
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
except ImportError as e:
    print(f"Build dependency missing: {e}", file=sys.stderr)
    print("Please ensure Cython and numpy are installed", file=sys.stderr)
    sys.exit(1)


def build_extension():
    """Build the Cython extension and place it in the package directory."""
    print("Building Cython extensions...")
    
    # Check for CI environment variables
    is_ci = os.environ.get("CIBUILDWHEEL", False) or os.environ.get("CI", False)
    
    # Determine platform-specific compilation flags
    if platform.system() == "Windows":
        extra_compile_args = ["/O2"]
        extra_link_args = []
    else:
        extra_compile_args = ["-O3", "-ffast-math"]
        extra_link_args = []
        
        # Add additional flags for CI builds
        if is_ci:
            extra_compile_args.extend(["-Wno-unreachable-code"])

    # Define the extension
    extensions = [
        DistutilsExtension(
            "brisket",
            ["src/brisket/brisket.pyx"],
            include_dirs=[np.get_include()],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )
    ]

    # Cythonize the extensions
    ext_modules = cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
        },
        annotate=False,  # Set to True for debugging
    )

    # Create a temporary directory for building
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Set up distribution
            dist = Distribution({
                'name': 'brisket',
                'ext_modules': ext_modules,
                'cmdclass': {'build_ext': build_ext},
            })
            
            # Build extensions
            build_cmd = build_ext(dist)
            build_cmd.build_lib = temp_dir
            build_cmd.build_temp = os.path.join(temp_dir, 'temp')
            build_cmd.finalize_options()
            build_cmd.run()
            
            # Find the built extension file
            package_dir = Path("src/brisket")
            
            # Look for the compiled extension in the temp directory
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(('.so', '.pyd')) and 'brisket' in file:
                        src_path = os.path.join(root, file)
                        
                        # Determine the destination filename
                        if platform.system() == "Windows":
                            dst_filename = "brisket.pyd"
                        else:
                            dst_filename = "brisket.so"
                        
                        dst_path = package_dir / dst_filename
                        
                        # Ensure destination directory exists
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy the extension
                        shutil.copy2(src_path, dst_path)
                        print(f"Copied {src_path} -> {dst_path}")
                        
                        print("Cython extension build completed successfully")
                        return
            
            print("Warning: No compiled extension found", file=sys.stderr)
            
        except Exception as e:
            if is_ci and os.environ.get("CIBUILDWHEEL"):
                # Allow failures in CI if specified
                print(f"Build failed: {e}", file=sys.stderr)
                print("Continuing despite build failure in CI environment", file=sys.stderr)
            else:
                print(f"Build failed: {e}", file=sys.stderr)
                raise


if __name__ == "__main__":
    build_extension()