import os
import json
from typing import Set, List, Optional
from dataclasses import dataclass, field


@dataclass
class DirectoryContents:
    directory: str
    files: List[str] = field(default_factory=list)

    def add_file(self, filename: str) -> None:
        self.files.append(filename)

    def __len__(self) -> int:
        return len(self.files)

    def to_dict(self) -> dict:
        return {
            "directory": self.directory,
            "files": sorted(self.files)
        }


def collect_directory_contents(
        root_dir: str,
        file_extension: str,
        exclude_dirs: Optional[Set[str]] = None
) -> List[DirectoryContents]:
    exclude_dirs = exclude_dirs or set()
    contents: List[DirectoryContents] = []
    root_dir = os.path.abspath(root_dir)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude_dirs and not d.startswith('.')
        ]

        rel_path = os.path.relpath(dirpath, root_dir)
        if rel_path == '.':
            rel_path = ''
        rel_path = rel_path.replace(os.path.sep, '/')

        if os.path.basename(dirpath) in exclude_dirs:
            continue

        directory_contents = DirectoryContents(rel_path)
        for filename in filenames:
            if filename.lower().endswith(file_extension.lower()):
                directory_contents.add_file(filename)

        if len(directory_contents) > 0:
            contents.append(directory_contents)

    return contents


def generate_directory_json(
        root_dir: str,
        file_extension: str,
        exclude_dirs: Optional[Set[str]] = None
) -> str:
    contents = collect_directory_contents(root_dir, file_extension, exclude_dirs)
    return json.dumps([c.to_dict() for c in contents], indent=2)


if __name__ == "__main__":
    basename: str = os.path.basename(__file__)
    file_extension_target = basename.split('.')[-2]
    json_data = generate_directory_json(
        root_dir=os.getcwd(),
        file_extension=file_extension_target,
        exclude_dirs={".git", "__pycache__", ".idea", "venv"}
    )

    json_file_name = basename.removesuffix('.py') + ".json"
    with open(json_file_name, 'w') as fs:
        fs.write(json_data)
