# Golinks

A simple local HTTP redirect service that turns short URLs like `go/github` into full URLs.

## Installation

### Install manually

```bash
# Clone the repository
git clone https://github.com/yourusername/golinks.git
cd golinks

# Run the install script
./install

# Edit the config
vim ~/.config/golinks/config.json
```

## How it works

The `./install` script automates the entire setup:
1. Installs the Python package using uv
2. Adds `127.0.0.1 go` to your `/etc/hosts` file (with sudo permission)
3. Sets up port forwarding from port 80 to 8888 using pfctl (macOS) or iptables (Linux), so you can use `go/shortcut` instead of `go:8888/shortcut`
4. Sets up a LaunchAgent (macOS) or systemd service (Linux) to run the server at startup
5. Starts the golinks server immediately on port 8888

Once installed, golinks runs a lightweight HTTP server that reads shortcuts from a JSON config file at `~/.golinks/config.json` and redirects `http://go/shortcut` to the configured destination URL. The config file is hot-reloaded, so you can add new shortcuts without restarting the server.
