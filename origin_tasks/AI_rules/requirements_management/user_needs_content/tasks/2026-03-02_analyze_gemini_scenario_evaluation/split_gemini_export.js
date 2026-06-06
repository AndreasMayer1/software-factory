#!/usr/bin/env node
// Splits a Gemini AI Studio export JSON into one file per conversation turn.
// Each output file contains: runSettings + systemInstruction + initial context chunk + 1 turn (3 chunks).
// Output: ./split/ folder, files named turn_01.json ... turn_NN.json

const fs = require('fs');
const path = require('path');

const INPUT_FILE = path.join(__dirname, 'Index von Lücken Füllen Für Alle Personas.json');
const OUTPUT_DIR = path.join(__dirname, 'split');

const data = JSON.parse(fs.readFileSync(INPUT_FILE, 'utf8'));
const allChunks = data.chunkedPrompt.chunks;

// chunk[0] is the initial driveDocument context; everything after is in triplets.
const contextChunk = allChunks[0];
const turnChunks = allChunks.slice(1);

if (turnChunks.length % 3 !== 0) {
  console.warn(`Warning: ${turnChunks.length} turn chunks not divisible by 3. Last ${turnChunks.length % 3} chunk(s) will be included in a partial file.`);
}

fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const numTurns = Math.ceil(turnChunks.length / 3);
const pad = String(numTurns).length;

for (let i = 0; i < turnChunks.length; i += 3) {
  const turnIndex = Math.floor(i / 3) + 1;
  const turnNumber = String(turnIndex).padStart(pad, '0');
  const chunks = turnChunks.slice(i, i + 3);

  const output = {
    runSettings: data.runSettings,
    systemInstruction: data.systemInstruction,
    chunkedPrompt: {
      chunks: [contextChunk, ...chunks],
    },
  };

  const outPath = path.join(OUTPUT_DIR, `turn_${turnNumber}.json`);
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf8');
  console.log(`Written: turn_${turnNumber}.json  (${chunks.length} chunks, roles: ${chunks.map(c => c.role).join(', ')})`);
}

console.log(`\nDone. ${numTurns} files written to: ${OUTPUT_DIR}`);
