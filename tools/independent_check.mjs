// Optional independent QA. Install parsehero@0.0.2 separately; it is not an app dependency.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const parser=process.argv[2];
if (!parser) throw Error('Usage: node tools/independent_check.mjs /absolute/path/to/parsehero/dist/index.js');
const {parseChart}=await import(pathToFileURL(parser));
let baseline;
for (const name of ['notes.chart','notes.mid']) {
 const buffer=fs.readFileSync(new URL('../examples/converted/'+name,import.meta.url));
 const input=name.endsWith('.chart') ? buffer.toString('utf8') : buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength);
 const {chart,warnings}=parseChart(input);
 const notes=chart.MediumSingle.filter(n=>n.type==='note');
 const phrases=chart.MediumSingle.filter(n=>n.type==='starpower');
 assert.equal(notes.length,37);
 assert(notes.every(n=>n.note>=0 && n.note<4));
 assert.equal(phrases.length,2);
 assert.deepEqual(chart.SyncTrack.bpms.map(b=>[b.tick,b.bpm]),[[0,120],[1536,150],[3072,100]]);
 const onsets=notes.map(n=>[n.tick,n.note,n.assignedTime]);
 if (baseline) assert.deepEqual(onsets,baseline); else baseline=onsets;
 console.log(JSON.stringify({file:name,mediumGems:notes.length,orange:0,starPowerPhrases:phrases.length,warnings}));
}
