#!/usr/bin/env node

/**
 * Export scheduled tasks using the data we got from /schedule command
 * This is a manual export based on the list provided
 */

const fs = require('fs');

// This is the complete list from the /schedule command output
const tasks = [
  { taskId: "r01-scanner-c1", description: "19:15 Scanner C1 (Janela C)", cronExpression: "15 19 * * *", enabled: true },
  { taskId: "r02-monitor", description: "19:45 Monitor (Janela C)", cronExpression: "45 19 * * *", enabled: true },
  { taskId: "r03-downloader-c1", description: "20:20 Downloader C1 (Janela C)", cronExpression: "20 20 * * *", enabled: true },
  { taskId: "r04-downloader-c2", description: "20:40 Downloader C2 (Janela C)", cronExpression: "40 20 * * *", enabled: true },
  { taskId: "r05-downloader-c3", description: "21:00 Downloader C3 (Janela C)", cronExpression: "0 21 * * *", enabled: true },
  { taskId: "r06-writer-c1", description: "21:20 Writer C1 (Janela C)", cronExpression: "20 21 * * *", enabled: true },
  { taskId: "r08-scanner-d1", description: "00:15 Scanner D1 (Janela D)", cronExpression: "15 0 * * *", enabled: true },
  { taskId: "r09-scanner-d2", description: "00:45 Scanner D2 (Janela D)", cronExpression: "45 0 * * *", enabled: true },
  { taskId: "r10-downloader-d1", description: "01:15 Downloader D1 (Janela D)", cronExpression: "15 1 * * *", enabled: true },
  { taskId: "r11-downloader-d2", description: "01:35 Downloader D2 (Janela D)", cronExpression: "35 1 * * *", enabled: true },
  { taskId: "r12-downloader-d3", description: "01:55 Downloader D3 (Janela D)", cronExpression: "55 1 * * *", enabled: true },
  { taskId: "r13-downloader-d4", description: "02:15 Downloader D4 (Janela D)", cronExpression: "15 2 * * *", enabled: true },
  { taskId: "r14-writer-d1", description: "02:45 Writer D1 (Janela D)", cronExpression: "45 2 * * *", enabled: true },
  { taskId: "r15-downloader-d5", description: "04:30 Downloader D5 (Janela D)", cronExpression: "30 4 * * *", enabled: true },
  { taskId: "r16-downloader-e1", description: "05:15 Downloader E1 (Janela E)", cronExpression: "15 5 * * *", enabled: true },
  { taskId: "r17-downloader-e2", description: "05:35 Downloader E2 (Janela E)", cronExpression: "35 5 * * *", enabled: true },
  { taskId: "r18-writer-e1", description: "06:00 Writer E1 (Janela E)", cronExpression: "0 6 * * *", enabled: true },
  { taskId: "r19-writer-emergencia", description: "15:30 Writer Emergencia (Janela B)", cronExpression: "30 15 * * *", enabled: true },
  { taskId: "r20-writer-c2", description: "21:40 Writer C2 (Janela C)", cronExpression: "40 21 * * *", enabled: true },
  { taskId: "r21-writer-c3", description: "22:00 Writer C3 (Janela C)", cronExpression: "0 22 * * *", enabled: true },
  { taskId: "r22-writer-c4", description: "22:20 Writer C4 (Janela C)", cronExpression: "20 22 * * *", enabled: true },
  { taskId: "r23-writer-c5", description: "22:40 Writer C5 (Janela C)", cronExpression: "40 22 * * *", enabled: true },
  { taskId: "r24-writer-c6", description: "23:00 Writer C6 (Janela C)", cronExpression: "0 23 * * *", enabled: true },
  { taskId: "r25-writer-c7", description: "23:20 Writer C7 (Janela C)", cronExpression: "20 23 * * *", enabled: true },
  { taskId: "r26-writer-c8", description: "23:40 Writer C8 (Janela C)", cronExpression: "40 23 * * *", enabled: true },
  { taskId: "r27-writer-d2", description: "03:05 Writer D2 (Janela D)", cronExpression: "5 3 * * *", enabled: true },
  { taskId: "r28-writer-d3", description: "03:25 Writer D3 (Janela D)", cronExpression: "25 3 * * *", enabled: true },
  { taskId: "r29-writer-d4", description: "03:45 Writer D4 (Janela D)", cronExpression: "45 3 * * *", enabled: true },
  { taskId: "r30-writer-e2", description: "06:20 Writer E2 (Janela E)", cronExpression: "20 6 * * *", enabled: true },
  { taskId: "r31-writer-e3", description: "06:40 Writer E3 (Janela E)", cronExpression: "40 6 * * *", enabled: true },
  { taskId: "r32-writer-e4", description: "07:00 Writer E4 (Janela E)", cronExpression: "0 7 * * *", enabled: true },
  { taskId: "r33-downloader-c1b", description: "07:20 Downloader C1b (manha)", cronExpression: "20 7 * * *", enabled: true },
  { taskId: "r34-downloader-c2b", description: "07:40 Downloader C2b (manha)", cronExpression: "40 7 * * *", enabled: true },
  { taskId: "r35-downloader-c3b", description: "08:00 Downloader C3b (manha)", cronExpression: "0 8 * * *", enabled: true },
  { taskId: "r36-downloader-d1b", description: "08:20 Downloader D1b (manha)", cronExpression: "20 8 * * *", enabled: true },
  { taskId: "r37-downloader-d2b", description: "08:40 Downloader D2b (manha)", cronExpression: "40 8 * * *", enabled: true },
  { taskId: "r38-downloader-d3b", description: "09:00 Downloader D3b (manha)", cronExpression: "0 9 * * *", enabled: true },
  { taskId: "r39-downloader-d4b", description: "09:20 Downloader D4b (manha)", cronExpression: "20 9 * * *", enabled: true },
  { taskId: "r40-downloader-d5b", description: "04:50 Downloader D5b (noite)", cronExpression: "50 4 * * *", enabled: true },
  { taskId: "r41-downloader-e1b", description: "09:40 Downloader E1b (manha)", cronExpression: "40 9 * * *", enabled: true },
  { taskId: "r42-downloader-e2b", description: "10:00 Downloader E2b (manha)", cronExpression: "0 10 * * *", enabled: true }
];

const exportPath = 'scheduled-tasks-export.json';
fs.writeFileSync(exportPath, JSON.stringify(tasks, null, 2), 'utf-8');

console.log(`✅ Exported ${tasks.length} tasks to: ${exportPath}`);
console.log('\n📋 Next steps on the new computer:');
console.log('1. Copy this file to: C:\\Users\\jmcpe\\Desktop\\opencapital-website\\');
console.log('2. Run: node import-scheduled-tasks.js scheduled-tasks-export.json');
