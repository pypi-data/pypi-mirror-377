# Tuya Outlet CLI

A simple Python CLI to control a Tuya-compatible 3-way smart power strip **over your local network** without using the Tuya cloud (except once during setup). Basically just a simple wrapper around the awesome [tinytuya](https://github.com/jasonacox/tinytuya) project.

## Features
- Turn each plug **on/off** individually
- Show status including plug states and energy data (voltage, current, power)
- Simple setup command for device configuration
- Robust configuration management with timeout and retry options

## Installation

### Option 1: Install from PyPI (System-wide)

```bash
pipx install tuya-strip
```

### Option 2: Install from Source (System-wide)

```bash
git clone https://github.com/wanjawischmeier/tuya-strip.git
cd tuya-strip
pipx install .
```

### Option 3: Install from Source (Local development)

1. Install [Poetry](https://python-poetry.org/docs/#installation)

2. Clone this repo:
```bash
git clone https://github.com/wanjawischmeier/tuya-strip.git
cd tuya-strip
```

3. Install dependencies:
```bash
poetry install
```
> [!NOTE]
> To enable `sudo tuya-strip` commands, create a system symlink:
> ```bash
> sudo ln -sf ~/.local/bin/tuya-strip /usr/local/bin/tuya-strip
> ```

## Setup

Configure your device credentials:
```bash
tuya-strip setup
```

For system-wide configuration (requires sudo):
```bash
sudo tuya-strip setup --system-wide
```

The setup command will prompt you to enter your device details (you can get these by running the [tinytuya setup wizard](https://github.com/jasonacox/tinytuya?tab=readme-ov-file#setup-wizard---getting-local-keys)):
- Device ID
  - Can be found in the respective `devices` entry in the generated `snapshot.json` -> `id` field
  - Or initially in the [cloud console](platform.tuya.com), under `<Your-Project> -> Devices -> All Devices -> Device ID`
- Device IP
  - Can be found in the same entry -> `ip` field
  - Or in the `devices.json` under the same field
- Local Key
  - Can be found in the same entry -> `key` field
  - Or in the `devices.json` under the same field
- Protocol Version (default: 3.3)
  - Can be found in the `devices.json`, at the very bottom of the respective device -> `version` field

Configuration is saved to your home directory (`~/.tuya-strip`) by default. Use `--system-wide` to store configuration in `/etc/tuya-strip/config` for all users.

> [!NOTE]  
> If you installed for local development, prefix all commands with `poetry run` (e.g., `poetry run tuya-strip setup`)

## Usage

```bash
tuya-strip status                    # Show current state and energy data
tuya-strip on 1                      # Turn on plug 1
tuya-strip off 3                     # Turn off plug 3
tuya-strip --timeout 5 status        # Use custom timeout
tuya-strip --retries 5 on 2          # Use custom retry count
```

## Example Output
```yaml
Loading config from: C:\Users\username\.tuya-strip
Switches: {'1': True, '2': False, '3': True}
Energy: {'voltage_V': 229, 'current_mA': 120, 'power_W': 24}
```
