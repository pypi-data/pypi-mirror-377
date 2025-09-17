#!/usr/bin/env node

/**
 * Svelte 5 Migration Utilities
 * Helper functions for migrating MultiBrain to Svelte 5
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Convert event handlers from on:event to onevent format
 * @param {string} content - File content
 * @returns {string} - Updated content
 */
function convertEventHandlers(content) {
  // Pattern to match on:eventname={handler}
  const eventPattern = /on:(\w+)(\s*)=(\s*){/g;
  
  // Replace on:click={handler} with onclick={handler}
  let updated = content.replace(eventPattern, (match, eventName, space1, space2) => {
    return `on${eventName}${space1}=${space2}{`;
  });
  
  // Pattern to match on:eventname|modifier={handler}
  const modifierPattern = /on:(\w+)\|(\w+)(\s*)=(\s*){/g;
  
  // Handle event modifiers (these need manual review)
  updated = updated.replace(modifierPattern, (match, eventName, modifier, space1, space2) => {
    console.warn(`⚠️  Event modifier found: on:${eventName}|${modifier} - needs manual review`);
    return `on${eventName}${space1}=${space2}{ /* TODO: Handle |${modifier} modifier */`;
  });
  
  return updated;
}

/**
 * Convert export let props to $props() rune
 * @param {string} content - File content
 * @returns {string} - Updated content
 */
function convertPropsToRune(content) {
  // Find all export let declarations
  const exportLetPattern = /export\s+let\s+(\w+)(\s*=\s*([^;]+))?;/g;
  const props = [];
  
  // Collect all props
  let match;
  while ((match = exportLetPattern.exec(content)) !== null) {
    const propName = match[1];
    const defaultValue = match[3];
    props.push({ name: propName, default: defaultValue });
  }
  
  if (props.length === 0) return content;
  
  // Build the new $props() declaration
  let propsDeclaration = 'let { ';
  propsDeclaration += props.map(prop => {
    if (prop.default) {
      return `${prop.name} = ${prop.default}`;
    }
    return prop.name;
  }).join(', ');
  propsDeclaration += ' } = $props();';
  
  // Replace all export let declarations with the single $props() declaration
  let updated = content;
  let firstExportLetIndex = content.search(/export\s+let\s+\w+/);
  
  // Remove all export let declarations
  updated = updated.replace(/export\s+let\s+\w+(\s*=\s*[^;]+)?;\s*/g, '');
  
  // Insert the new $props() declaration where the first export let was
  if (firstExportLetIndex !== -1) {
    updated = updated.slice(0, firstExportLetIndex) + propsDeclaration + '\n  ' + updated.slice(firstExportLetIndex);
  }
  
  return updated;
}

/**
 * Convert reactive declarations ($:) to $derived rune
 * @param {string} content - File content
 * @returns {string} - Updated content
 */
function convertReactiveDeclarations(content) {
  // Pattern to match $: variableName = expression
  const derivedPattern = /\$:\s*(\w+)\s*=\s*([^;]+);/g;
  
  let updated = content.replace(derivedPattern, (match, varName, expression) => {
    return `let ${varName} = $derived(${expression.trim()});`;
  });
  
  return updated;
}

/**
 * Convert reactive statements ($:) to $effect rune
 * @param {string} content - File content
 * @returns {string} - Updated content
 */
function convertReactiveStatements(content) {
  // Pattern to match $: { ... } or $: if (...) { ... }
  const effectPattern = /\$:\s*{([^}]+)}/g;
  const conditionalPattern = /\$:\s*if\s*\([^)]+\)\s*{([^}]+)}/g;
  
  // Convert block statements
  let updated = content.replace(effectPattern, (match, block) => {
    return `$effect(() => {${block}});`;
  });
  
  // Convert conditional statements
  updated = updated.replace(conditionalPattern, (match) => {
    // Remove the $: prefix
    const statement = match.substring(2).trim();
    return `$effect(() => {\n    ${statement}\n  });`;
  });
  
  return updated;
}

/**
 * Convert createEventDispatcher to callback props
 * @param {string} content - File content
 * @returns {string} - Updated content
 */
function convertEventDispatcher(content) {
  // Check if file uses createEventDispatcher
  if (!content.includes('createEventDispatcher')) {
    return content;
  }
  
  // Find dispatch calls
  const dispatchPattern = /dispatch\(['"](\w+)['"](,\s*([^)]+))?\)/g;
  const events = new Set();
  
  let match;
  while ((match = dispatchPattern.exec(content)) !== null) {
    events.add(match[1]);
  }
  
  if (events.size === 0) return content;
  
  // Add event callbacks to props
  const eventProps = Array.from(events).map(event => `on${event}`).join(', ');
  
  // Update props declaration
  if (content.includes('$props()')) {
    content = content.replace(/let\s*{\s*([^}]+)\s*}\s*=\s*\$props\(\)/, (match, props) => {
      return `let { ${props}, ${eventProps} } = $props()`;
    });
  } else if (content.includes('export let')) {
    // Add after last export let
    const lastExportLet = content.lastIndexOf('export let');
    const endOfLine = content.indexOf(';', lastExportLet) + 1;
    content = content.slice(0, endOfLine) + `\n  export let ${eventProps};` + content.slice(endOfLine);
  }
  
  // Replace dispatch calls with callback invocations
  content = content.replace(dispatchPattern, (match, eventName, comma, detail) => {
    const callbackName = `on${eventName}`;
    if (detail) {
      return `${callbackName}?.(${detail})`;
    }
    return `${callbackName}?.()`;
  });
  
  // Remove createEventDispatcher import and usage
  content = content.replace(/import\s*{\s*createEventDispatcher\s*}\s*from\s*['"]svelte['"];?\s*/g, '');
  content = content.replace(/const\s+dispatch\s*=\s*createEventDispatcher\(\);?\s*/g, '');
  
  return content;
}

/**
 * Add migration comments to help track changes
 * @param {string} content - File content
 * @param {string} fileName - Name of the file
 * @returns {string} - Content with migration comments
 */
function addMigrationComments(content, fileName) {
  const timestamp = new Date().toISOString().split('T')[0];
  const header = `<!-- Svelte 5 Migration: ${fileName} - ${timestamp} -->\n`;
  
  // Add header comment if it's a .svelte file
  if (fileName.endsWith('.svelte') && !content.includes('Svelte 5 Migration:')) {
    content = header + content;
  }
  
  return content;
}

/**
 * Analyze a file and suggest migrations
 * @param {string} filePath - Path to the file
 * @returns {object} - Analysis results
 */
async function analyzeFile(filePath) {
  const content = await fs.readFile(filePath, 'utf-8');
  const results = {
    filePath,
    suggestions: [],
    hasEventHandlers: false,
    hasExportLet: false,
    hasReactiveDeclarations: false,
    hasReactiveStatements: false,
    hasEventDispatcher: false,
    hasSlots: false,
  };
  
  // Check for patterns
  if (/on:\w+\s*=/.test(content)) {
    results.hasEventHandlers = true;
    results.suggestions.push('Convert on:event to onevent syntax');
  }
  
  if (/export\s+let\s+\w+/.test(content)) {
    results.hasExportLet = true;
    results.suggestions.push('Convert export let to $props() rune');
  }
  
  if (/\$:\s*\w+\s*=/.test(content)) {
    results.hasReactiveDeclarations = true;
    results.suggestions.push('Convert reactive declarations to $derived()');
  }
  
  if (/\$:\s*(if|{)/.test(content)) {
    results.hasReactiveStatements = true;
    results.suggestions.push('Convert reactive statements to $effect()');
  }
  
  if (/createEventDispatcher/.test(content)) {
    results.hasEventDispatcher = true;
    results.suggestions.push('Convert event dispatcher to callback props');
  }
  
  if (/<slot/.test(content)) {
    results.hasSlots = true;
    results.suggestions.push('Convert slots to snippets (manual review needed)');
  }
  
  return results;
}

/**
 * Process a single file with all migrations
 * @param {string} filePath - Path to the file
 * @param {object} options - Migration options
 * @returns {object} - Migration results
 */
async function migrateFile(filePath, options = {}) {
  try {
    let content = await fs.readFile(filePath, 'utf-8');
    const originalContent = content;
    
    // Apply migrations in order
    if (options.eventHandlers !== false) {
      content = convertEventHandlers(content);
    }
    
    if (options.props !== false) {
      content = convertPropsToRune(content);
    }
    
    if (options.reactive !== false) {
      content = convertReactiveDeclarations(content);
      content = convertReactiveStatements(content);
    }
    
    if (options.eventDispatcher !== false) {
      content = convertEventDispatcher(content);
    }
    
    if (options.addComments !== false) {
      content = addMigrationComments(content, path.basename(filePath));
    }
    
    // Check if content changed
    const hasChanges = content !== originalContent;
    
    if (hasChanges && !options.dryRun) {
      await fs.writeFile(filePath, content, 'utf-8');
    }
    
    return {
      filePath,
      hasChanges,
      success: true,
    };
  } catch (error) {
    return {
      filePath,
      hasChanges: false,
      success: false,
      error: error.message,
    };
  }
}

/**
 * Process multiple files
 * @param {string[]} filePaths - Array of file paths
 * @param {object} options - Migration options
 * @returns {object[]} - Array of results
 */
async function migrateFiles(filePaths, options = {}) {
  const results = [];
  
  for (const filePath of filePaths) {
    const result = await migrateFile(filePath, options);
    results.push(result);
    
    if (result.success && result.hasChanges) {
      console.log(`✅ Migrated: ${filePath}`);
    } else if (!result.success) {
      console.error(`❌ Failed: ${filePath} - ${result.error}`);
    }
  }
  
  return results;
}

/**
 * Find all Svelte files in a directory
 * @param {string} dir - Directory path
 * @returns {string[]} - Array of file paths
 */
async function findSvelteFiles(dir) {
  const files = [];
  
  async function walk(currentDir) {
    const entries = await fs.readdir(currentDir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      
      if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
        await walk(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.svelte')) {
        files.push(fullPath);
      }
    }
  }
  
  await walk(dir);
  return files;
}

// Export all utilities
module.exports = {
  convertEventHandlers,
  convertPropsToRune,
  convertReactiveDeclarations,
  convertReactiveStatements,
  convertEventDispatcher,
  addMigrationComments,
  analyzeFile,
  migrateFile,
  migrateFiles,
  findSvelteFiles,
};

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
Svelte 5 Migration Utilities

Usage:
  node migration-utils.js analyze <file-or-directory>
  node migration-utils.js migrate <file-or-directory> [options]

Options:
  --dry-run              Show what would be changed without modifying files
  --no-event-handlers    Skip event handler conversion
  --no-props            Skip props conversion
  --no-reactive         Skip reactive declaration/statement conversion
  --no-event-dispatcher Skip event dispatcher conversion
  --no-comments         Don't add migration comments

Examples:
  node migration-utils.js analyze src/components
  node migration-utils.js migrate src/components/Button.svelte --dry-run
  node migration-utils.js migrate src/components --no-event-dispatcher
    `);
    process.exit(0);
  }
  
  const command = args[0];
  const target = args[1];
  
  if (!target) {
    console.error('Error: Please specify a file or directory');
    process.exit(1);
  }
  
  // Parse options
  const options = {
    dryRun: args.includes('--dry-run'),
    eventHandlers: !args.includes('--no-event-handlers'),
    props: !args.includes('--no-props'),
    reactive: !args.includes('--no-reactive'),
    eventDispatcher: !args.includes('--no-event-dispatcher'),
    addComments: !args.includes('--no-comments'),
  };
  
  (async () => {
    try {
      const stat = await fs.stat(target);
      let files = [];
      
      if (stat.isDirectory()) {
        files = await findSvelteFiles(target);
      } else if (stat.isFile() && target.endsWith('.svelte')) {
        files = [target];
      } else {
        console.error('Error: Target must be a .svelte file or directory');
        process.exit(1);
      }
      
      if (command === 'analyze') {
        console.log(`\nAnalyzing ${files.length} Svelte files...\n`);
        
        for (const file of files) {
          const analysis = await analyzeFile(file);
          if (analysis.suggestions.length > 0) {
            console.log(`📄 ${analysis.filePath}`);
            analysis.suggestions.forEach(suggestion => {
              console.log(`   - ${suggestion}`);
            });
            console.log('');
          }
        }
      } else if (command === 'migrate') {
        console.log(`\nMigrating ${files.length} Svelte files...`);
        if (options.dryRun) {
          console.log('(Dry run - no files will be modified)\n');
        }
        
        const results = await migrateFiles(files, options);
        
        const changed = results.filter(r => r.hasChanges).length;
        const failed = results.filter(r => !r.success).length;
        
        console.log(`\nSummary:`);
        console.log(`  Total files: ${files.length}`);
        console.log(`  Changed: ${changed}`);
        console.log(`  Failed: ${failed}`);
      } else {
        console.error(`Error: Unknown command '${command}'`);
        process.exit(1);
      }
    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  })();
}