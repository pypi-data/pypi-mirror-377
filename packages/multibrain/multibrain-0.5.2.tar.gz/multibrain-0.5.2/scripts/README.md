# Svelte 5 Migration Utilities

This directory contains utilities to help migrate the MultiBrain application from Svelte 4 patterns to Svelte 5 features.

## migration-utils.js

A comprehensive CLI tool and library for analyzing and migrating Svelte components to use Svelte 5 features.

### Features

- **Analyze components** for migration opportunities
- **Automated conversion** of common patterns:
  - Event handlers: `on:click` → `onclick`
  - Props: `export let` → `$props()`
  - Reactive declarations: `$:` → `$derived()`
  - Reactive statements: `$:` → `$effect()`
  - Event dispatchers → Callback props
- **Dry-run mode** to preview changes
- **Selective migration** with feature flags
- **Migration comments** for tracking

### CLI Usage

#### Analyze a component or directory:
```bash
node scripts/migration-utils.js analyze frontend/src/components/Button.svelte
node scripts/migration-utils.js analyze frontend/src/components
```

#### Migrate with dry-run (preview changes):
```bash
node scripts/migration-utils.js migrate frontend/src/components/Button.svelte --dry-run
```

#### Migrate a component:
```bash
node scripts/migration-utils.js migrate frontend/src/components/Button.svelte
```

#### Migrate with options:
```bash
# Skip event dispatcher conversion
node scripts/migration-utils.js migrate frontend/src/components --no-event-dispatcher

# Skip multiple conversions
node scripts/migration-utils.js migrate frontend/src/components --no-props --no-reactive
```

### Programmatic Usage

```javascript
const { 
  analyzeFile, 
  migrateFile, 
  findSvelteFiles 
} = require('./migration-utils.js');

// Analyze a file
const analysis = await analyzeFile('path/to/component.svelte');
console.log(analysis.suggestions);

// Migrate a file
const result = await migrateFile('path/to/component.svelte', {
  dryRun: false,
  eventHandlers: true,
  props: true,
  reactive: true,
  eventDispatcher: true,
  addComments: true
});
```

### Migration Functions

- `convertEventHandlers(content)` - Convert `on:event` to `onevent`
- `convertPropsToRune(content)` - Convert `export let` to `$props()`
- `convertReactiveDeclarations(content)` - Convert `$: var = expr` to `$derived()`
- `convertReactiveStatements(content)` - Convert `$: { ... }` to `$effect()`
- `convertEventDispatcher(content)` - Convert event dispatchers to callback props

### Important Notes

1. **Always backup your code** before running migrations
2. **Test thoroughly** after migration
3. Some patterns require **manual review**:
   - Event modifiers (`on:click|preventDefault`)
   - Complex slot patterns
   - Store subscriptions in templates
4. The tool adds migration comments to track changes

### Workflow Recommendation

1. **Analyze first**: Run analysis to understand what needs migration
2. **Create tests**: Ensure component has tests before migrating
3. **Dry-run**: Preview changes with `--dry-run`
4. **Migrate**: Run the actual migration
5. **Test**: Run component tests
6. **Manual review**: Check for TODO comments and complex patterns
7. **Update tracking**: Mark component as migrated in `docs/MIGRATION_PROGRESS.md`

## Related Resources

- [Migration Progress Tracker](../docs/MIGRATION_PROGRESS.md)
- [Migration Plan](../docs/SVELTE5_MIGRATION_PLAN.md)
- [Migration Example](../docs/examples/migration-example.svelte)
- [Test Utilities](../frontend/src/test/test-utils.js)