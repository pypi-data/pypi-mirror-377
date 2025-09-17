import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from tqdm import tqdm

from runkmc.models import create_input_file
from runkmc.simulation import SimulationRegistry, SimulationResult

PACKAGE_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent
CPP_DIR = PROJECT_ROOT / "cpp"
BUILD_DIR = CPP_DIR / "build"
EXECUTABLE_PATH = BUILD_DIR / "RunKMC"


@dataclass
class SimulationConfig:

    model_name: str
    kmc_inputs: Dict[str, Any]
    report_polymers: bool = False
    report_sequences: bool = False


class RunKMC:

    def __init__(
        self, model_name: str, data_dir: Path | str, force_compile: bool = False
    ):
        self.model_name = model_name
        self.data_dir = Path(data_dir)
        self.registry = SimulationRegistry(self.model_name, self.data_dir)
        compile(force_compile)

    def run_simulation(
        self, config: SimulationConfig, sim_id: Optional[str] = None
    ) -> SimulationResult:

        if not EXECUTABLE_PATH.exists():
            compile()

        paths = self.registry.register_simulation(config.kmc_inputs, sim_id)

        create_input_file(config.model_name, config.kmc_inputs, paths.input_filepath)

        cmd = [
            str(EXECUTABLE_PATH.absolute()),
            str(paths.input_filepath.absolute()),
            str(paths.results_filepath.absolute()),
        ]

        if config.report_polymers:
            cmd.append(f"--report-polymers={paths.polymer_data_dir.absolute()}")
        if config.report_sequences:
            cmd.append(f"--report-sequences={paths.sequence_filepath.absolute()}")

        try:

            process = subprocess.Popen(
                cmd,
                cwd=PROJECT_ROOT,
                text=True,
            )
            print("Running KMC simulation...")
            print(f"Results: {str(paths.results_filepath.absolute())}")
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                error_msg = f"Simulation failed with return code {process.returncode}\n"
                if stderr:
                    error_msg += f"Error output:\n{stderr}"
                if stdout:
                    error_msg += f"Standard output:\n{stdout}"
                raise RuntimeError(error_msg)
            print(f"RunKMC executed successfully.")

        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            raise KeyboardInterrupt("Simulation interrupted by user.")

        return SimulationResult(
            model_name=config.model_name,
            params=config.kmc_inputs,
            paths=paths,
        )

    def run_or_retrieve(
        self, config: SimulationConfig, overwrite: bool = False
    ) -> SimulationResult:

        # Check if simulation already exists
        existing_sims = self.registry.find(config.kmc_inputs)

        if len(existing_sims) == 0:
            return self.run_simulation(config)

        paths = existing_sims[0]
        if overwrite:
            return self.run_simulation(config, paths.sim_id)

        print(f"Results: {str(paths.results_filepath.absolute())}")
        return SimulationResult(config.model_name, config.kmc_inputs, paths)


def compile(force: bool = False) -> None:

    precompiled_path = (
        PACKAGE_ROOT / "bin" / ("RunKMC.exe" if os.name == "nt" else "RunKMC")
    )
    if precompiled_path.exists() and not force:
        BUILD_DIR.mkdir(exist_ok=True)
        shutil.copy2(precompiled_path, EXECUTABLE_PATH)
        return

    _compile_from_source(force)


def _compile_from_source(force: bool = False) -> None:

    if not force and EXECUTABLE_PATH.exists():
        return

    # Ensure build directory exists
    BUILD_DIR.mkdir(exist_ok=True)

    # Add include path to find headers
    compile_cmd = (
        f"g++ "
        f"-I{CPP_DIR}/include "
        f"-I{CPP_DIR}/include/runkmc "
        f"-I{CPP_DIR}/include/runkmc/kmc "
        f"-I{CPP_DIR}/include/eigen-3.4.0 "
        f"{CPP_DIR}/src/RunKMC.cpp "
        f"-std=c++17 -O3 "
        f"-o {EXECUTABLE_PATH}"
    )

    try:
        subprocess.run(
            compile_cmd,
            shell=True,
            check=True,
            cwd=CPP_DIR,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Compilation failed: {e.stderr}")
    print("Compilation successful.")
