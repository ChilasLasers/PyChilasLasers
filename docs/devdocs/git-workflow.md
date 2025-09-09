# Git Workflow & Commit Conventions

This document outlines our Git workflow, branching strategy, and commit conventions for PyChilasLasers.

## 🌿 Branching Strategy

We use a **GitHub Flow** inspired approach with these main branches:

### Main Branches
- **`main`** - Production-ready code, always deployable
- **`develop`** - Integration branch for features (if needed for complex releases)

### Feature Branches
- **`feature/laser-sweep-mode`** - New features
- **`fix/temperature-calibration`** - Bug fixes  
- **`docs/api-reference`** - Documentation updates
- **`refactor/communication-layer`** - Code refactoring

### Branch Naming Convention
```
<type>/<short-description>

Examples:
feature/heater-control-api
fix/wavelength-validation
docs/examples-update
refactor/error-handling
test/sweep-mode-coverage
```

## 📝 Conventional Commits

We follow **Conventional Commits** specification for consistent, parsable commit messages.

### Commit Message Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type       | Description                                      | Example                              |
| ---------- | ------------------------------------------------ | ------------------------------------ |
| `feat`     | New feature                                      | `feat: implement sweep mode bounds`  |
| `fix`      | Bug fix                                          | `fix: correct heater enumeration`    |
| `docs`     | Documentation changes                            | `docs: add sweep mode examples`      |
| `style`    | Code style (formatting, no logic changes)       | `style: fix imports in laser.py`     |
| `refactor` | Code refactoring (no feat/fix)                  | `refactor: simplify TEC controller`  |
| `test`     | Adding/updating tests                            | `test: add sweep mode unit tests`    |
| `chore`    | Maintenance (build, deps, etc.)                 | `chore: update uv dependencies`      |
| `perf`     | Performance improvements                         | `perf: optimize wavelength lookup`   |
| `ci`       | CI/CD changes                                    | `ci: add automated testing workflow` |
| `build`    | Build system or dependencies                     | `build: configure uv for packaging`  |

### Scopes (Optional)

Use scopes to indicate which part of the codebase is affected:

```
feat(laser): add power control methods
fix(sweep): handle boundary conditions  
docs(examples): update basic usage guide
test(components): add TEC controller tests
refactor(comm): improve error handling
```

### Examples of Good Commits

#### ✅ Simple Feature
```
feat: implement sweep mode set_bounds()

Add method to configure wavelength sweep boundaries with validation.
Includes bounds checking and error handling for invalid ranges.
```

#### ✅ Bug Fix
```
fix: correct heater channel enumeration

Heater channels were incorrectly mapped causing wrong channel control.
Updated channel mapping to match hardware specification.

Fixes #123
```

#### ✅ Documentation
```
docs: add example for steady mode usage

- Add comprehensive steady mode example
- Include error handling patterns
- Update README with new example links
```

#### ✅ Breaking Change
```
feat!: redesign laser initialization API

BREAKING CHANGE: Laser constructor now requires explicit port specification.
Old: Laser() 
New: Laser(port="COM1")

This change improves connection reliability and explicit hardware targeting.
```

#### ✅ Multi-component Change
```
feat(laser): add comprehensive wavelength control

- Implement set_wavelength() with validation
- Add get_wavelength() for current reading  
- Include wavelength bounds checking
- Update laser status to include wavelength info

Closes #45, #67
```


## 📋 PR Guidelines

### PR Title Format
Use conventional commit format for PR titles:
```
feat(laser): add wavelength sweep functionality
fix(tec): resolve temperature reading inconsistency  
docs: update installation instructions
```


## ✅ Commit Quality Checklist

Before committing, ensure:

- [ ] **Clear type**: Use appropriate conventional commit type
- [ ] **Descriptive subject**: Explain what changed in ~50 chars
- [ ] **Present tense**: "Add feature" not "Added feature"  
- [ ] **Imperative mood**: "Fix bug" not "Fixes bug"
- [ ] **Body (if needed)**: Explain why, not what
- [ ] **Reference issues**: Include relevant issue numbers
- [ ] **Breaking changes**: Mark with `!` and explain

## 🚫 Common Mistakes to Avoid

### ❌ Bad Commit Messages
```bash
# Too vague
git commit -m "fix stuff"
git commit -m "update code"

# Wrong tense/mood
git commit -m "fixed the laser bug"
git commit -m "adding new feature"

# Missing context
git commit -m "refactor"
git commit -m "tests"
```

### ✅ Good Commit Messages
```bash
# Clear and specific
git commit -m "fix(laser): prevent power spike on startup"
git commit -m "feat(sweep): add continuous sweep mode"

# Proper tense/mood  
git commit -m "refactor(tec): simplify temperature control logic"
git commit -m "test(modes): add boundary condition tests"

# With context
git commit -m "docs(examples): add basic laser control tutorial

Include step-by-step guide for new users to get started
with basic laser operations like power and wavelength control."
```

Following these conventions ensures a clean, readable Git history that makes it easy to understand changes, generate changelogs, and track down issues!
