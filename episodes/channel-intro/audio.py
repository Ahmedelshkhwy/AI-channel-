import wave, subprocess, numpy as np
SR=44100; rng=np.random.default_rng(3)
D=[9.09,9.56,12.67,9.87,9.09,8.28]; S=[]; a=0.6
for d in D: S.append(a); a+=d+0.3
TOTAL=63.6; N=int(SR*(TOTAL+1))
def T(sec): return np.arange(int(SR*sec))/SR
def lp(x,c):
    c=np.broadcast_to(c,x.shape); k=np.exp(-2*np.pi*c/SR); y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc=(1-k[i])*x[i]+k[i]*acc; y[i]=acc
    return y
def env(sec,a,r,c=2.0):
    t=T(sec); return np.clip(t/max(a,1e-4),0,1)*np.clip((sec-t)/max(r,1e-4),0,1)**c
mus=np.zeros((N,2)); fx=np.zeros((N,2))
def add(buf,at,sig,g=1.0,pan=0.0):
    i=int(at*SR)
    if i<0 or i>=N: return
    sig=sig[:N-i]; buf[i:i+len(sig),0]+=sig*g*(1-max(pan,0)); buf[i:i+len(sig),1]+=sig*g*(1+min(pan,0))
def note(m): return 440*2**((m-69)/12)
# ---- sfx ----
def whoosh(sec=.8,lo=300,hi=5000):
    t=T(sec); n=rng.standard_normal(len(t)); sw=lo+hi*np.sin(np.pi*t/sec)**2; return (lp(n,sw)-lp(n,sw*.25))*env(sec,.35,.4)
def riser(sec):
    t=T(sec); n=rng.standard_normal(len(t)); return (lp(n,200+7000*(t/sec)**2)*.8+np.sin(2*np.pi*np.cumsum(150+700*(t/sec)**2)/SR)*.3)*(t/sec)**1.7*env(sec,.05,.03,1)
def impact(sec=2.2):
    t=T(sec); return np.sin(2*np.pi*np.cumsum(85*np.exp(-t*3)+36)/SR)*np.exp(-t*2)+lp(rng.standard_normal(len(t)),2600)*np.exp(-t*12)*.7
def shatter():
    sec=1.4; t=T(sec); x=(rng.standard_normal(len(t))-lp(rng.standard_normal(len(t)),3000))*np.exp(-t*9)*.9
    for _ in range(26):
        st=rng.uniform(0,.7); f=rng.uniform(2500,9000); k=T(.25); g=np.sin(2*np.pi*f*k)*np.exp(-k*rng.uniform(18,40))*rng.uniform(.15,.5); i=int(st*SR); x[i:i+len(g)]+=g[:len(x)-i]
    return x
def ding(f,sec=1.0):
    t=T(sec); return sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*d) for m,a,d in [(1,1,4),(2.01,.4,6),(2.99,.2,9)])*env(sec,.004,.2,1)
def pop(f=520):
    t=T(.16); return np.sin(2*np.pi*np.cumsum(f*1.8*np.exp(-t*25)+f)/SR)*np.exp(-t*30)
def hit():
    t=T(.5); return np.sin(2*np.pi*np.cumsum(140*np.exp(-t*14)+50)/SR)*np.exp(-t*8)+lp(rng.standard_normal(len(t)),4000)*np.exp(-t*40)*.6
def liquid(sec=1.2,down=True):
    t=T(sec); f=(900*np.exp(-t*2.2)+120) if down else (120+900*(t/sec)**2); w=np.sin(2*np.pi*np.cumsum(f*(1+.08*np.sin(2*np.pi*9*t)))/SR); return (w*.6+lp(rng.standard_normal(len(t)),f*2)*.5)*env(sec,.08,.5)
def shimmer(sec=1.4):
    t=T(sec); return sum(np.sin(2*np.pi*f*t+rng.uniform(0,6))*np.exp(-t*2.5) for f in (1760,2217,2637,3520,4186))*env(sec,.25,.6,1)*.3
add(fx,.9,whoosh(),.35,-.5); add(fx,2.4,whoosh(1.0),.35,.5); add(fx,S[0]+4.4,riser(1.35),.5)
add(fx,S[0]+5.75,shatter(),.8); add(fx,S[0]+5.75,hit(),.6); add(fx,S[0]+7.6,riser(1.7),.6); add(fx,S[1]-.05,impact(),.9)
add(fx,S[1]+.2,pop(400),.5); add(fx,S[1]+1.8,shimmer(),.6); add(fx,S[1]+2.85,ding(880),.3); add(fx,S[1]+5.22,hit(),.9)
for i in range(6): add(fx,S[1]+5.8+i*.42,pop(330*2**(i/6)),.45,(-.4+i*.16))
add(fx,S[1]+7.45,shimmer(1.2),.35)
add(fx,S[2]-.5,liquid(1.1,False),.6); add(fx,S[2]+.8,hit(),.6)
for i,st in enumerate([2.1,3.58,5.44,6.8,8.32,10.68]):
    add(fx,S[2]+st-.7,whoosh(.7,200,3000),.22,(.4 if i%2 else -.4)); add(fx,S[2]+st,ding(note([62,65,69,72,74,77][i])*2),.42)
add(fx,S[3]-.75,riser(.75),.5); add(fx,S[3]-.02,impact(1.6),.5)
for i in range(6): add(fx,S[3]+.6+i*.38,pop(900),.12)
add(fx,S[3]+2.7,whoosh(1.0),.4,.5); add(fx,S[3]+5.25,whoosh(1.0),.4,-.5); add(fx,S[3]+3.9,pop(500),.3); add(fx,S[3]+6.5,shimmer(1.5),.4)
add(fx,S[4]-.55,liquid(1.4,True),.7); add(fx,S[4]+1.0,liquid(.9,True),.45); add(fx,S[4]+1.7,hit(),.9); add(fx,S[4]+1.95,pop(420),.4); add(fx,S[4]+3.3,whoosh(.9),.35); add(fx,S[4]+3.55,pop(520),.4)
for i in range(7): add(fx,S[4]+4.55+i*.14,pop(400*2**(i/7)),.3)
add(fx,S[4]+7.75,ding(1175),.4)
add(fx,S[5]-.1,shimmer(2.0),.5); add(fx,S[5]+1.0,hit(),.5); add(fx,S[5]+2.9,riser(1.3),.7); add(fx,S[5]+4.2,impact(2.6),1.0); add(fx,S[5]+4.25,shimmer(2.2),.6); add(fx,S[5]+4.4,pop(600),.4); add(fx,S[5]+5.65,pop(700),.4)
# ---- music: Dm Bb F C, 96 bpm ----
BPM=96; beat=60/BPM; bar=beat*4; chords=[[50,57,62,65],[46,53,58,62],[41,48,57,60],[48,55,60,64]]
def pad(ms,sec):
    t=T(sec); s=np.zeros(len(t))
    for m in ms:
        f=note(m)
        for dt in (-.15,0,.15): ph=2*np.pi*f*(1+dt/100)*t; s+=np.sin(ph)+.3*np.sin(2*ph)+.12*np.sin(3*ph)
    return lp(s,1200)*env(sec,.8,1.0,1.4)/(len(ms)*3)
def pluck(f,sec=.4):
    t=T(sec); return (np.sin(2*np.pi*f*t)+.4*np.sin(4*np.pi*f*t))*np.exp(-t*8)*env(sec,.003,.05,1)
def kick():
    t=T(.4); return np.sin(2*np.pi*np.cumsum(120*np.exp(-t*20)+42)/SR)*np.exp(-t*8)
def hat():
    t=T(.05); n=rng.standard_normal(len(t)); return (n-lp(n,7000))*np.exp(-t*80)
def clap():
    t=T(.18); n=rng.standard_normal(len(t)); return (lp(n,3500)-lp(n,800))*np.exp(-t*28)
LOGO=S[5]+4.2
b=0
while b*bar<TOTAL:
    st=b*bar; ch=chords[b%4]
    if st>=LOGO-bar*.5:
        add(mus,LOGO,pad([50,57,62,66,69],TOTAL-LOGO+1),.9); t=T(4); add(mus,LOGO,np.sin(2*np.pi*note(38)*t)*env(4,.02,2.5),.5); break
    add(mus,st,pad(ch,bar*1.2),.6)
    t=T(bar*.95); sub=np.sin(2*np.pi*note(ch[0]-12)*t)
    if st<S[1]: add(mus,st,sub*env(bar*.95,.3,1.5),.35)
    else:
        for k in range(8): add(mus,st+k*beat/2,np.sin(2*np.pi*note(ch[0]-12)*T(beat*.45))*env(beat*.45,.01,.15),.3 if st<S[5] else .15)
    if st>=S[1]-bar*.5:
        arp=[ch[1]+12,ch[2]+12,ch[3]+12,ch[2]+12,ch[1]+24,ch[3]+12,ch[2]+12,ch[3]+12]
        for k,m in enumerate(arp): add(mus,st+k*beat/2,pluck(note(m)),.2 if st<S[5] else .12,.4 if k%2 else -.4)
    if S[2]-.2<=st<S[5]-bar*.6:
        for k in range(4):
            add(mus,st+k*beat,kick(),.55); add(mus,st+k*beat+beat/2,hat(),.13)
            if k in (1,3): add(mus,st+k*beat,clap(),.22)
        if st>=S[3]:
            for k in range(8): add(mus,st+k*beat/2+beat/4,hat(),.06)
    b+=1
def save(name,x):
    x=x/ (np.max(np.abs(x)) or 1)*.89
    with wave.open(name,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x[:int(SR*TOTAL)]*32767).astype(np.int16).tobytes())
save('music.wav',mus); save('fx.wav',fx)
ins=['-i','music.wav','-i','fx.wav']; f=[]; labs=[]
for i in range(6):
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'vo/plan-{i}-'+['hook','who','journey','formats','proof','cta'][i]+'.mp3','-af','highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-2:LRA=7','-ar','44100','-ac','2',f'vo{i}.wav'],check=True)
    ins+=['-i',f'vo{i}.wav']; ms=int(S[i]*1000); f.append(f'[{i+2}:a]adelay={ms}|{ms}[v{i}]'); labs.append(f'[v{i}]')
f.append(''.join(labs)+f'amix=inputs=6:normalize=0,apad=whole_dur={TOTAL},asplit=2[vo][sc]')
f.append('[0:a]volume=-13dB[m0];[m0][sc]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=450[m]')
f.append(f'[1:a]volume=-9dB[fx];[vo][m][fx]amix=inputs=3:normalize=0,atrim=0:{TOTAL},afade=t=out:st={TOTAL-1.8}:d=1.8,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[out]')
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(f),'-map','[out]','-ac','2','mix.wav'],check=True)
print('ok')
