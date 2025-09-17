# CLI Reference

The `bear-gui-tools` command provides several utilities for working with your project.

## Available Commands

### `version`
Display the current version of Bear GUI Tools.

```bash
bear-gui-tools version
```

### `debug_info`
Show detailed environment and system information.

```bash
bear-gui-tools debug_info
```

Options:
- `--no-color, -n`: Disable colored output

### `bump`
Bump the project version and create a git tag.

```bash
bear-gui-tools bump <version_type>
```

Arguments:
- `version_type`: One of `patch`, `minor`, or `major`

Examples:
```bash
# Bump patch version (1.0.0 -> 1.0.1)
bear-gui-tools bump patch

# Bump minor version (1.0.1 -> 1.1.0)  
bear-gui-tools bump minor

# Bump major version (1.1.0 -> 2.0.0)
bear-gui-tools bump major
```



## Global Options

- `--version, -V`: Show version information and exit
- `--help`: Show help message and exit

