# %%
# Test notebook

# %%

# %%
import subprocess


subprocess.call(["pip", "install", "process"])
# %%
# Test notebook - run process on LT
import shutil
import tempfile
from pathlib import Path

from process.core.repository import get_process_root
from process.main import SingleRun

# Define input file name relative to project dir, then copy to temp dir
data_dir = get_process_root() / "../examples/data/"
input_file = data_dir / "large_tokamak_IN.DAT"

# Copy the file to avoid polluting the project directory with example files
temp_dir = tempfile.TemporaryDirectory()
input_path = Path(temp_dir.name) / "large_tokamak_IN.DAT"
shutil.copy(input_file, input_path)

# Run process on an input file in a temporary directory
single_run = SingleRun(input_path.as_posix())
single_run.run()
