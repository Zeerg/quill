# Contributing to Quill

## Development Workflow

We follow a feature-branch workflow with pull requests to maintain code quality and track changes.

### Git Workflow

1. **Always work in feature branches**
   ```bash
   # Create and switch to a new feature branch
   git checkout -b feature/async-request-processing
   
   # Or for bug fixes
   git checkout -b fix/memory-leak-in-fuzzer
   ```

2. **Branch Naming Convention**
   - `feature/` - New features or enhancements
   - `fix/` - Bug fixes
   - `docs/` - Documentation updates
   - `refactor/` - Code refactoring
   - `test/` - Test additions or fixes
   - `perf/` - Performance improvements

3. **Development Process**
   ```bash
   # 1. Create feature branch
   git checkout -b feature/new-mutation-strategy
   
   # 2. Make changes
   # ... edit files ...
   
   # 3. Run quality checks
   make check
   make format
   make test
   
   # 4. Commit changes
   git add .
   git commit -m "feat: add semantic mutation strategy"
   
   # 5. Push to remote
   git push -u origin feature/new-mutation-strategy
   
   # 6. Create PR
   gh pr create --title "Add semantic mutation strategy" \
                --body "Implements semantic mutations that preserve meaning"
   
   # 7. After PR approval, merge to main
   gh pr merge --squash
   
   # 8. Clean up
   git checkout main
   git pull
   git branch -d feature/new-mutation-strategy
   ```

### Commit Message Format

Follow conventional commits specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Test additions or changes
- `chore:` - Build process or auxiliary tool changes

Examples:
```
feat: add base64 encoding mutator
fix: handle connection timeout in ollama client
docs: update installation instructions
perf: implement request batching for 10x speedup
```

### Pull Request Guidelines

1. **PR Title**: Use conventional commit format
2. **PR Description**: Include:
   - What changed and why
   - How to test the changes
   - Any breaking changes
   - Related issues

3. **PR Template**:
   ```markdown
   ## Summary
   Brief description of changes
   
   ## Changes
   - Added X feature
   - Fixed Y bug
   - Improved Z performance
   
   ## Testing
   - [ ] Ran `make test`
   - [ ] Ran `make check`
   - [ ] Tested manually with: `make fuzz-test`
   
   ## Checklist
   - [ ] Code follows project style
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] No security vulnerabilities
   ```

### Feature Development Flow

1. **Plan the Feature**
   - Review TASKS.md for feature details
   - Use Claude agents for design help:
     ```
     /agent mutator-developer design a new mutation strategy
     ```

2. **Implement**
   - Create feature branch
   - Write code following existing patterns
   - Add tests for new functionality
   - Update documentation

3. **Test Thoroughly**
   ```bash
   make test          # Run all tests
   make fuzz-test     # Test fuzzing functionality
   make benchmark     # Check performance impact
   ```

4. **Quality Checks**
   ```bash
   make check         # Lint, type check, security scan
   make format        # Auto-format code
   ```

5. **Create PR**
   - Push branch to remote
   - Create PR with clear description
   - Request review if working with team

6. **Merge and Deploy**
   - Squash merge to keep history clean
   - Delete feature branch
   - Pull latest main

### Quick Commands

```bash
# Start new feature
make feature NAME=async-requests

# Finish feature (creates PR)
make finish-feature

# Update from main
git checkout main
git pull
git checkout -
git rebase main
```

### Working with Claude Agents

Use sub-agents to help with development:

```bash
# Get implementation help
/agent performance-optimizer how to implement async request batching

# Review code quality
/agent security-auditor review my changes for security issues

# Optimize performance
/agent inference-optimizer optimize this classifier code
```

### Code Standards

1. **Python Style**
   - Follow PEP 8
   - Use type hints for function signatures
   - Add docstrings to all public functions
   - Keep functions small and focused

2. **Testing**
   - Write tests for all new features
   - Maintain >80% code coverage
   - Use pytest fixtures for common setups
   - Mark slow tests with `@pytest.mark.slow`

3. **Documentation**
   - Update README for user-facing changes
   - Add docstrings for new modules/functions
   - Update CLAUDE.md for architectural changes
   - Include examples in documentation

### Release Process

1. **Version Bump**
   ```bash
   make bump-minor  # For new features
   make bump-patch  # For bug fixes
   ```

2. **Create Release**
   ```bash
   make dist
   git tag v$(make version)
   git push --tags
   ```

3. **Release Notes**
   - List all changes since last release
   - Highlight breaking changes
   - Thank contributors

## Getting Help

- Check existing issues and PRs
- Use Claude agents for implementation help
- Ask questions in PR comments
- Review TASKS.md for feature priorities