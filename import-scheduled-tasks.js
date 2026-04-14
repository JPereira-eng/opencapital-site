#!/usr/bin/env node

/**
 * Import scheduled tasks from an export JSON file
 * Usage: node import-scheduled-tasks.js <path-to-export.json>
 *
 * This recreates all tasks in the new computer's .claude/scheduled-tasks/
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const exportFile = process.argv[2];

if (!exportFile) {
  console.error('❌ Usage: node import-scheduled-tasks.js <path-to-export.json>');
  process.exit(1);
}

if (!fs.existsSync(exportFile)) {
  console.error(`❌ File not found: ${exportFile}`);
  process.exit(1);
}

console.log(`📂 Reading tasks from: ${exportFile}`);

let tasks;
try {
  const content = fs.readFileSync(exportFile, 'utf-8');
  tasks = JSON.parse(content);
} catch (e) {
  console.error(`❌ Failed to parse JSON: ${e.message}`);
  process.exit(1);
}

console.log(`Found ${tasks.length} tasks to import`);

const tasksDir = path.join(os.homedir(), '.claude', 'scheduled-tasks');

// Ensure directory exists
if (!fs.existsSync(tasksDir)) {
  fs.mkdirSync(tasksDir, { recursive: true });
  console.log(`📁 Created directory: ${tasksDir}`);
}

// Create each task
tasks.forEach(task => {
  const taskDir = path.join(tasksDir, task.taskId);

  // Create task directory
  if (!fs.existsSync(taskDir)) {
    fs.mkdirSync(taskDir, { recursive: true });
  }

  // Create SKILL.md with proper frontmatter
  const skillContent = `---
name: ${task.taskId}
description: ${task.description}
cronExpression: ${task.cronExpression}
enabled: ${task.enabled}
---

# ${task.taskId}

**Schedule:** ${task.cronExpression}
**Description:** ${task.description}
**Status:** ${task.enabled ? '✅ Enabled' : '⏸️ Disabled'}

This task was imported from another computer.
`;

  const skillPath = path.join(taskDir, 'SKILL.md');
  fs.writeFileSync(skillPath, skillContent, 'utf-8');

  console.log(`✅ Created: ${task.taskId}`);
});

console.log(`\n✅ Imported ${tasks.length} tasks successfully!`);
console.log('\n📋 Next steps:');
console.log('1. Restart Claude Code');
console.log('2. Run: /schedule');
console.log('3. Verify all tasks appear in the list');
