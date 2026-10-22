import numpy as np, subprocess
SR=48000
def load(f):
    return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,dtype=np.float32).reshape(-1,2).copy()
voice=load('src/1022.mp4'); out=voice.copy()
def place(f,t,peak_db,align='start'):
    s=load('sfx/'+f); pk=np.abs(s).max()+1e-9; s*=10**(peak_db/20)/pk
    env=np.abs(s).max(1); off=int(np.argmax(env)) if align=='peak' else 0
    i=int(t*SR)-off; a=max(0,-i); i=max(0,i); n=min(len(s)-a,len(out)-i)
    out[i:i+n]+=s[a:a+n]
EV=[('swish_03_C.wav',3.08,-20,'peak'),('hit_01_A.wav',8.74,-12,'start'),
    ('whoosh-rise_03_C.wav',11.66,-16,'peak'),
    ('bass_01_A.wav',17.5,-10,'start'),('swish_03_C.wav',23.6,-20,'peak'),
    ('click-pop_05_C.wav',25.42,-16,'start'),('click-pop_05_C.wav',26.44,-16,'start'),
    ('click-pop_05_C.wav',27.42,-16,'start'),('click-pop_05_C.wav',29.26,-16,'start'),
    ('whoosh-rise_03_C.wav',33.56,-16,'peak'),('hit_01_A.wav',39.06,-14,'start')]
EV+=[('swish_01_B.wav',11.66,-18,'peak'),('whoosh-rise_04_C.wav',16.62,-17,'peak'),
     ('whoosh-rise_01_A.wav',17.5,-18,'peak'),
     ('whoosh-rise_04_C.wav',38.98,-17,'peak'),('swish_03_C.wav',8.74,-18,'peak'),('whoosh-rise_05_D.wav',39.06,-16,'peak'),('click-pop_08_D.wav',39.10,-16,'start'),
     ('click-pop_04_B.wav',17.52,-18,'start')]
import sys; sys.argv=['x']; import render
for e in EV: place(*e)
EV.append(('click-pop_04_B.wav',39.35,-18,'start')); place(*EV[-1])
# typing sound under every word that is being typed on the navy background
typ=load('sfx/typing.mp3')[int(2.45*SR):int(8.9*SR)]
vrms=np.sqrt(np.mean(voice[np.abs(voice).max(1)>0.02]**2)); typ*=0.1*vrms/np.sqrt(np.mean(typ**2))
pos=0
for c in render.CIRCLES:
    for w in render.words:
        if c[2][0]-0.01<=w['s']<c[1]:
            n=int((w['e']-w['s'])*SR); i=int(w['s']*SR)
            if pos+n>len(typ): pos=0
            seg=typ[pos:pos+n].copy(); pos+=n
            f=min(len(seg)//4,int(0.015*SR)); ramp=np.linspace(0,1,f)[:,None]
            if f>0: seg[:f]*=ramp; seg[-f:]*=ramp[::-1]
            out[i:i+len(seg)]+=seg[:len(out)-i]
out.astype(np.float32).tofile('out/mix.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','out/mix.f32','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),'out/mix.wav'])
