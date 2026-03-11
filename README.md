# SLEEB Lab Experiments

Repository for experimental workflows combining cameras, microcontrollers, and Bonsai.
Microcontrollers are controlled via [Belay](https://github.com/BrianPugh/belay), which lets you write MicroPython device code directly in Python classes and call it from your computer.

## Repository structure

```
BelayExperiments/
├── pyproject.toml               # Python dependencies (managed with uv)
├── experiments/
│   ├── start.py                 # Entry point called by Bonsai — instantiates the device
│   ├── devices/
│   │   ├── __init__.py          # Exports all device classes
│   │   ├── PicoBonn.py          # Pico with BME688 + BH1745 sensors, NeoPixels, fan
│   │   └── PicoBonnAction.py    # Pico with NeoPixels and fan only (no I2C sensors)
│   └── bonsai-workflows/        # Bonsai .bonsai workflow files
```

## Setup

Requirements: [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Clone the repository, then from the repo root:
uv sync
```

This creates a `.venv` folder in the repo root with all dependencies installed.

## Bonsai integration

Bonsai workflows use the `Bonsai.Scripting.Python` package to talk to the microcontroller.
The workflow calls `start.py` to instantiate the device, then calls its methods via `Eval` nodes.

### Critical setup step

Every Bonsai workflow that uses Python must have its `CreateRuntime` node configured to point to the virtual environment in this repository.

1. Open the workflow in Bonsai
2. Click the **CreateRuntime** node
3. Set **PythonHome** to the `.venv` folder in the repo root, e.g.:
   ```
   C:\path\to\BelayExperiments\.venv
   ```
   This path is **user- and machine-specific** — each person must set it to match where they cloned the repo.

### How it works

| Bonsai node | What it does |
|---|---|
| `CreateRuntime` | Starts a Python interpreter from the `.venv` |
| `CreateModule` → `start.py` | Runs `start.py`, which connects to the Pico and exposes it as `pico` |
| `Eval` → `pico.some_method()` | Calls a device task on the Pico |

`start.py` adds its own directory to `sys.path` so that `from devices.PicoBonn import PicoBonn` works regardless of Bonsai's working directory.

## Adding a new device

1. Create a new file in `experiments/devices/`, e.g. `MyDevice.py`
2. Subclass `belay.Device` and define `@Device.setup` and `@Device.task` methods
3. Add the class to `experiments/devices/__init__.py`:
   ```python
   from .MyDevice import MyDevice
   __all__ = [..., "MyDevice"]
   ```
4. In `experiments/start.py`, import and instantiate your device with its USB specifier:
   ```python
   from devices.MyDevice import MyDevice
   device = MyDevice(spec)
   ```
5. Use `device.method_name()` in Bonsai `Eval` nodes

### Finding your device's USB specifier

```python
import belay
print(belay.list_devices())
```

This prints all connected USB devices with their VID, PID, serial number, and location.
Copy those values into the `belay.UsbSpecifier(...)` call in `start.py`.
