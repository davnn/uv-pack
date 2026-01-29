from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "PackLayout"
]

@dataclass(frozen=True, slots=True)
class PackLayout:
    output_directory: Path
    gitignore_file: Path
    requirements_txt: Path
    requirements_export_txt: Path
    requirements_local_txt: Path
    _wheels_dir: Path
    _vendor_dir: Path
    _python_dir: Path

    @property
    def wheels_dir(self) -> Path:
        self._wheels_dir.mkdir(exist_ok=True)
        return self._wheels_dir

    @property
    def vendor_dir(self) -> Path:
        self._vendor_dir.mkdir(exist_ok=True)
        return self._vendor_dir

    @property
    def python_dir(self) -> Path:
        self._python_dir.mkdir(exist_ok=True)
        return self._python_dir

    @classmethod
    def create(cls, output_directory: Path) -> "PackLayout":
        output_directory.mkdir(parents=True, exist_ok=True)
        wheels_dir = output_directory / "wheels"
        vendor_dir = output_directory / "vendor"
        python_dir = output_directory / "python"

        gitignore_file = output_directory / ".gitignore"
        gitignore_file.write_text("*", encoding="utf-8")

        return cls(
            output_directory,
            gitignore_file=gitignore_file,
            requirements_txt=output_directory / "requirements.txt",
            requirements_export_txt=wheels_dir / "requirements.txt",
            requirements_local_txt=vendor_dir / "requirements.txt",
            _wheels_dir=wheels_dir,
            _vendor_dir=vendor_dir,
            _python_dir=python_dir,
        )
