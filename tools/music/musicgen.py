import torch, numpy as np, soundfile as sf, sys
from transformers import AutoProcessor, MusicgenForConditionalGeneration
torch.set_num_threads(4)
proc = AutoProcessor.from_pretrained('facebook/musicgen-small')
model = MusicgenForConditionalGeneration.from_pretrained('facebook/musicgen-small')
prompt = sys.argv[1]; out = sys.argv[2]; secs = float(sys.argv[3])
inp = proc(text=[prompt], padding=True, return_tensors='pt')
toks = int(secs * 50)
torch.manual_seed(7)
audio = model.generate(**inp, max_new_tokens=toks, do_sample=True, guidance_scale=3.0)
sr = model.config.audio_encoder.sampling_rate
sf.write(out, audio[0, 0].numpy(), sr)
print('done', out, sr)
