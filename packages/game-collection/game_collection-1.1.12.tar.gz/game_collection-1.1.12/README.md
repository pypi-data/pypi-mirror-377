# Game Collection

A collection of classic arcade games including Snake, Tetris, Arkanoid, and Pac-Man, built with Python and Pygame.

## Features

- **Snake**: Classic snake game with growing mechanics
- **Tetris**: Block-stacking puzzle game with line clearing
- **Arkanoid**: Breakout-style game with paddle and ball physics
- **Pac-Man**: Maze navigation game with dots and ghosts

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd game-collection

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### From PyPI

```bash
# Standard installation
pip install game-collection

# If you have permission issues on Windows:
pip install game-collection --no-deps --user
```

### Windows Installation

If you encounter permission errors with pygame on Windows, use the automated installer:

```bash
# Run the installer
install_game.bat

# Or manual installation
pip install game-collection --no-deps --user
```

## Usage

### Command Line

After installation, you can run the game collection using:

```bash
# Using the entry point (if PATH is configured)
game-collection

# Using Python module (always works)
python -m game

# Using local file (for development)
python main.py
```

### Troubleshooting

If the `game-collection` command is not found:

1. **Windows**: Run `setup_path.bat` as administrator
2. **Alternative**: Always use `python -m game`
3. **See**: [Windows Installation Guide](WINDOWS_INSTALLATION_GUIDE.md) for detailed solutions

### Development

```bash
# Run the game
make run

# Run tests
make test-unit

# Run tests with coverage
make test-cov

# Check code quality
make quality

# Build executable
make build

# Setup pre-commit hooks
make pre-commit-install

# Run pre-commit on all files
make pre-commit-run

# Check readiness for PyPI publication
make publish-check

# Publish to TestPyPI (for testing)
make publish-test

# Publish to PyPI (requires API token)
make publish
```

### Debug Features

The game includes a debug overlay that can be toggled during gameplay:

- **F1**: Toggle debug overlay on/off
- **F2**: Reset FPS history
- **F3**: Toggle fullscreen mode

The debug overlay shows:
- Real-time FPS and FPS history
- Current game and state
- Mouse position
- Currently pressed keys
- Performance statistics

## Configuration

The game uses a configuration system that stores settings in platform-appropriate directories:

- **Windows**: `%APPDATA%/GameCollection/`
- **macOS**: `~/Library/Application Support/GameCollection/`
- **Linux**: `~/.local/share/GameCollection/`

### Configuration Files

- `config.json`: Game settings, controls, audio, and difficulty levels
- `scores.json`: High scores for all games

### Configuration Options

The configuration includes:

- **Display**: Resolution, fullscreen mode, FPS
- **Controls**: Key mappings for each game
- **Game Settings**: Speed, grid size, lives, etc.
- **Audio**: Volume levels and enable/disable
- **Difficulty**: Easy, Normal, Hard presets

## Development

### Project Structure

```
src/
├── game/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── main.py              # Main game loop
│   ├── config.py            # Configuration management
│   ├── config.json          # Default configuration
│   ├── games/               # Game implementations
│   │   ├── base.py          # Base game class
│   │   ├── logic.py         # Pure game logic functions
│   │   ├── snake.py         # Snake game
│   │   ├── tetris.py        # Tetris game
│   │   ├── arkanoid.py      # Arkanoid game
│   │   └── pacman.py        # Pac-Man game
│   └── ui/                  # User interface
│       ├── menu.py          # Main menu
│       └── scores.py        # Score management
tests/                       # Unit tests
docs/                        # Documentation
```

### Testing

The project includes comprehensive unit tests for all game logic:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_tetris_logic.py

# Run with coverage
python -m pytest tests/ --cov=src/game/games --cov-report=html
```

### Code Quality

The project uses modern Python tooling:

- **Ruff**: Fast linting and formatting
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Appdirs**: Platform-appropriate data directories

### Building Executables

```bash
# Build with PyInstaller
make build

# Or manually
pyinstaller --onefile --windowed --name GameCollection src/game/__main__.py
```

## Requirements

- Python 3.10+
- Pygame 2.5.0+
- Appdirs 1.4.4+ (for data directory management)

### Development Requirements

- Ruff 0.1.0+ (linting and formatting)
- MyPy 1.8.0+ (type checking)
- Pytest 7.4.0+ (testing)
- PyInstaller 5.13.0+ (executable building)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the quality checks: `make quality`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.
