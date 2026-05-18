"""
Project Code Extractor Script
Scans through all project files and creates a single markdown file with all code.
"""

import os
import sys
from pathlib import Path
import mimetypes
import datetime


class ProjectCodeExtractor:
    def __init__(self, root_dir=None, output_file="payment_code.md"):
        """
        Initialize the code extractor.

        Args:
            root_dir: Starting directory (defaults to current directory)
            output_file: Name of the output markdown file
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.output_file = Path(output_file)

        # Common directories to exclude
        self.exclude_dirs = {
            "venv",
            "env",
            ".venv",
            ".env",
            "test",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".git",
            ".svn",
            ".hg",
            "node_modules",
            "dist",
            "build",
            ".idea",
            ".vscode",
            ".vs",
            "coverage",
            ".coverage",
            "logs",
            "log",
            "tmp",
            "temp",
            ".tox",
            ".hypothesis",
            "htmlcov",
            ".pytest",
            "tests",
            "test",
            "migrations",
            "staticfiles",
            "static",
            "mediafiles",
        }

        # Common files to exclude
        self.exclude_files = {
            self.output_file.name,  # Don't include the output file itself
            ".gitignore",
            ".env",
            ".env.local",
            "package-lock.json",
            "yarn.lock",
            "requirements.txt",
            "Pipfile.lock",
            "poetry.lock",
            "pyproject.toml",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "*.so",
            "*.dll",
            "*.dylib",
            "*.class",
            "*.jar",
            "*.war",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "*.md",
            "*.yml",
            "*yaml",
            "schema.yml",
        }

        # File extensions to include (empty list means include all)
        # You can customize this if you want only specific file types
        self.include_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".html",
            ".htm",
            ".css",
            ".scss",
            ".less",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".sql",
            ".sh",
            ".bash",
            ".bat",
            ".yml",
            ".yaml",
            ".json",
            ".xml",
            ".md",
            ".txt",
            ".csv",
            ".vue",
            ".svelte",
        }

    def should_exclude(self, path):
        """Check if a path should be excluded."""
        # Check if any excluded directory is in the path
        for part in path.parts:
            if part in self.exclude_dirs:
                return True

        # Check if file is in exclude list
        if path.name in self.exclude_files:
            return True

        # Check file extensions
        if path.is_file():
            # Check if it's a binary file
            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type and not mime_type.startswith("text/"):
                return True

            # If we have specific extensions to include, check them
            if self.include_extensions:
                if path.suffix not in self.include_extensions:
                    return True

        return False

    def get_file_content(self, file_path):
        """Read file content with proper encoding handling."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ["latin-1", "iso-8859-1", "cp1252"]:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue

            # If all fails, return empty string
            print(f"Warning: Could not read {file_path} (binary file?)")
            return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def scan_project(self):
        """Scan the project and collect all files."""
        print(f"Scanning project from: {self.root_dir}")
        print(f"Excluding directories: {', '.join(sorted(self.exclude_dirs))}")

        files = []
        total_size = 0

        for file_path in self.root_dir.rglob("*"):
            # Skip if should be excluded
            if self.should_exclude(file_path):
                continue

            if file_path.is_file():
                try:
                    # Get file size
                    size = file_path.stat().st_size

                    # Skip very large files (optional - you can adjust this)
                    if size > 10 * 1024 * 1024:  # 10MB
                        print(
                            f"Skipping large file: {file_path} ({size/1024/1024:.1f} MB)"
                        )
                        continue

                    # Get relative path
                    rel_path = file_path.relative_to(self.root_dir)

                    files.append(
                        {"path": rel_path, "full_path": file_path, "size": size}
                    )

                    total_size += size
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        print(f"\nFound {len(files)} files (total: {total_size/1024/1024:.2f} MB)")
        return files

    def create_markdown(self, files):
        """Create markdown file with all code."""
        print(f"\nCreating markdown file: {self.output_file}")

        with open(self.output_file, "w", encoding="utf-8") as md_file:
            # Write header
            md_file.write(f"# Project Code Documentation\n\n")
            md_file.write(f"**Project Root:** `{self.root_dir}`\n\n")
            md_file.write(f"**Total Files:** {len(files)}\n\n")
            md_file.write("---\n\n")

            # Group files by directory for better organization
            files_by_dir = {}
            for file_info in files:
                dir_path = str(file_info["path"].parent)
                if dir_path == ".":
                    dir_path = "root"

                if dir_path not in files_by_dir:
                    files_by_dir[dir_path] = []
                files_by_dir[dir_path].append(file_info)

            # Write files by directory
            for dir_path in sorted(files_by_dir.keys()):
                md_file.write(f"## Directory: `{dir_path}`\n\n")

                for file_info in sorted(
                    files_by_dir[dir_path], key=lambda x: x["path"]
                ):
                    file_path = file_info["path"]
                    full_path = file_info["full_path"]

                    # Get file extension for code block language
                    extension = file_path.suffix.lower()
                    lang_map = {
                        ".py": "python",
                        ".js": "javascript",
                        ".ts": "typescript",
                        ".jsx": "jsx",
                        ".tsx": "tsx",
                        ".html": "html",
                        ".htm": "html",
                        ".css": "css",
                        ".scss": "scss",
                        ".less": "less",
                        ".java": "java",
                        ".cpp": "cpp",
                        ".c": "c",
                        ".h": "c",
                        ".go": "go",
                        ".rs": "rust",
                        ".rb": "ruby",
                        ".php": "php",
                        ".sql": "sql",
                        ".sh": "bash",
                        ".bash": "bash",
                        ".yml": "yaml",
                        ".yaml": "yaml",
                        ".json": "json",
                        ".xml": "xml",
                        ".md": "markdown",
                        ".txt": "text",
                        ".vue": "vue",
                        ".svelte": "html",
                    }

                    language = lang_map.get(extension, "text")

                    # Write file header
                    md_file.write(f"### File: `{file_path}`\n\n")
                    md_file.write(f"**Size:** {file_info['size']} bytes  \n")

                    # Get and write file content
                    content = self.get_file_content(full_path)

                    if content.strip():
                        md_file.write(f"```{language}\n")
                        md_file.write(content)

                        # Ensure the file ends with newline
                        if not content.endswith("\n"):
                            md_file.write("\n")

                        md_file.write("```\n\n")
                    else:
                        md_file.write("*File is empty*\n\n")

                    md_file.write("---\n\n")

            # Add summary
            md_file.write("## Summary\n\n")
            md_file.write(f"- **Project scanned from:** `{self.root_dir}`\n")
            md_file.write(f"- **Total files extracted:** {len(files)}\n")
            md_file.write(f"- **Output file:** `{self.output_file}`\n")
            md_file.write(
                f"- **Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

        print(f"✓ Markdown file created successfully: {self.output_file}")
        print(f"✓ Total size: {self.output_file.stat().st_size/1024/1024:.2f} MB")

    def run(self):
        """Run the full extraction process."""
        try:
            files = self.scan_project()

            if not files:
                print("No files found to process!")
                return

            self.create_markdown(files)

        except KeyboardInterrupt:
            print("\n\nProcess interrupted by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nError: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


def main():
    """Main function with command line argument support."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract all code from a project into a single markdown file."
    )
    parser.add_argument(
        "--root",
        "-r",
        default=".",
        help="Root directory to start scanning (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="project_code.md",
        help="Output markdown file name (default: project_code.md)",
    )
    parser.add_argument(
        "--exclude", nargs="+", default=[], help="Additional directories to exclude"
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include all file types (not just text files)",
    )

    args = parser.parse_args()

    # Create extractor
    extractor = ProjectCodeExtractor(root_dir=args.root, output_file=args.output)

    # Add additional exclusions
    if args.exclude:
        extractor.exclude_dirs.update(args.exclude)

    # If include-all is specified, clear the extensions filter
    if args.include_all:
        extractor.include_extensions = set()

    # Run the extraction
    extractor.run()


if __name__ == "__main__":
    # Add datetime import for the template string
    import datetime

    main()
