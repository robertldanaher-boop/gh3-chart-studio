"""Create the original, copyright-free timing fixture used for M3 acceptance."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
root=Path(__file__).resolve().parents[1]/'examples'/'audio';root.mkdir(parents=True,exist_ok=True)
sr=22050;onsets=np.arange(.5,8,.5);samples=np.zeros(sr*9,dtype=np.float32)
for i,start in enumerate(onsets):
    times=np.arange(round(sr*.12))/sr
    burst=.7*np.sin(2*np.pi*(220+i%4*110)*times)*np.exp(-times*30)
    pos=round(start*sr);samples[pos:pos+len(burst)]+=burst
sf.write(root/'onset-study.wav',samples,sr,subtype='PCM_16')
(root/'truth.json').write_text(json.dumps({'description':'Original synthesized tone-burst fixture; no commercial recording','sample_rate':sr,'duration':9,'bpm':120,'onset_seconds':onsets.tolist()},indent=2))
print(root/'onset-study.wav')
