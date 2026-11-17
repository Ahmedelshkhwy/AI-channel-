import wave, subprocess, numpy as np
SR=44100; rng=np.random.default_rng(3)
D=[11.15,13.24,13.4,17.0,12.04,16.43,15.96,11.39,4.44]; S=[]; a=1.0
for d in D: S.append(a); a+=d+0.35
TOTAL=121.4; N=int(SR*(TOTAL+1))
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
add(fx,.15,riser(.9),.5); add(fx,1.0,impact(1.8),.7); add(fx,S[0]+1.6,whoosh(.8),.35); add(fx,S[0]+2.9,ding(880),.35); add(fx,S[0]+4.7,whoosh(.7),.4,-.5); add(fx,S[0]+5.6,whoosh(.7),.4,.5); add(fx,S[0]+8.0,impact(2.0),.9); add(fx,S[0]+9.0,shimmer(1.6),.45); add(fx,S[0]+9.5,ding(1175),.35)
add(fx,S[1]-.5,whoosh(1.0),.45); add(fx,S[1]+.2,pop(520),.4); add(fx,S[1]+3.5,whoosh(1.0,300,4000),.35); add(fx,S[1]+4.7,pop(400),.5); add(fx,S[1]+5.9,hit(),.5); add(fx,S[1]+9.4,liquid(1.0,False),.45); add(fx,S[1]+9.7,shimmer(1.4),.45); add(fx,S[1]+11.9,pop(560),.4); add(fx,S[1]+12.3,pop(640),.4)
add(fx,S[2]-.5,whoosh(1.0),.45); add(fx,S[2]+1.3,ding(740),.3); add(fx,S[2]+3.8,pop(480),.4); add(fx,S[2]+5.4,whoosh(1.3,300,4000),.4); add(fx,S[2]+5.8,shimmer(1.4),.4); add(fx,S[2]+7.0,ding(880),.4)
for i in range(18): add(fx,S[2]+7.1+i*.13,pop(1400+rng.uniform(-200,200)),.06)
add(fx,S[2]+10.5,impact(1.8),.9); add(fx,S[2]+12.2,ding(1320),.45)
add(fx,S[3]-.5,whoosh(1.0),.45); add(fx,S[3]+.9,ding(740),.35); add(fx,S[3]+3.4,ding(880),.35); add(fx,S[3]+5.5,impact(1.8),.85); add(fx,S[3]+5.8,whoosh(1.3,300,4000),.4); add(fx,S[3]+7.4,ding(1175),.45); add(fx,S[3]+8.0,whoosh(.8,300,3000),.4); add(fx,S[3]+8.8,hit(),.8); add(fx,S[3]+9.6,ding(330),.4)
add(fx,S[3]+10.4,whoosh(1.0),.45); add(fx,S[3]+11.2,whoosh(1.0),.35); add(fx,S[3]+12.4,impact(2.0),.8); add(fx,S[3]+12.6,shimmer(1.6),.45); add(fx,S[3]+14.4,hit(),.6)
add(fx,S[4]-.5,whoosh(1.0),.45); add(fx,S[4]+2.4,hit(),.85); add(fx,S[4]+3.9,hit(),.7); add(fx,S[4]+5.4,whoosh(.9),.4); add(fx,S[4]+6.6,ding(880),.35); add(fx,S[4]+8.2,whoosh(1.3,300,4000),.4); add(fx,S[4]+8.6,whoosh(.9),.4,.5); add(fx,S[4]+9.6,ding(1320),.5); add(fx,S[4]+9.7,pop(700),.4)
add(fx,S[5]-.5,whoosh(1.0),.45); add(fx,S[5]+.2,whoosh(1.0,300,4000),.35); add(fx,S[5]+1.4,whoosh(1.0,300,4000),.35); add(fx,S[5]+2.1,impact(1.8),.85); add(fx,S[5]+3.1,ding(988),.45); add(fx,S[5]+4.4,ding(330),.45); add(fx,S[5]+5.1,whoosh(.8),.35)
add(fx,S[5]+10.7,hit(),.9); add(fx,S[5]+10.9,liquid(1.0,True),.45); add(fx,S[5]+11.3,whoosh(.9),.4); add(fx,S[5]+11.8,ding(740),.35); add(fx,S[5]+13.0,pop(520),.4); add(fx,S[5]+13.6,whoosh(1.4,300,4000),.35); add(fx,S[5]+14.3,ding(1320),.45)
add(fx,S[6]-.5,whoosh(1.0),.45); add(fx,S[6]+.4,whoosh(.9),.4); add(fx,S[6]+3.9,ding(880),.35); add(fx,S[6]+4.4,shimmer(1.4),.4); add(fx,S[6]+8.2,whoosh(.9),.4); add(fx,S[6]+8.6,impact(1.8),.85)
for i,x in enumerate([12.5,13.3,14.1,14.7]): add(fx,S[6]+x,hit(),.45); add(fx,S[6]+x,ding(660*2**(i/4)),.35)
add(fx,S[7]-.5,whoosh(1.0),.45); add(fx,S[7]+2.0,ding(880),.4); add(fx,S[7]+4.5,ding(988),.4); add(fx,S[7]+6.6,impact(2.0),.9)
for i in range(9): add(fx,S[7]+6.9+i*.1,pop(500*2**(i/9)),.3)
add(fx,S[7]+9.9,liquid(1.0,False),.45)
for i in range(5): add(fx,S[7]+10.0+i*.08,pop(440*2**(i/6)),.3)
add(fx,S[8]-.8,riser(.8),.6); add(fx,S[8],impact(2.6),1.0); add(fx,S[8]+.3,pop(600),.4); add(fx,S[8]+.2,shimmer(2.2),.5)
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
LOGO=S[8]
b=0
while b*bar<TOTAL:
    st=b*bar; ch=chords[b%4]
    if st>=LOGO-bar*.5:
        add(mus,LOGO,pad([50,57,62,66,69],TOTAL-LOGO+1),.9); t=T(4); add(mus,LOGO,np.sin(2*np.pi*note(38)*t)*env(4,.02,2.5),.5); break
    add(mus,st,pad(ch,bar*1.2),.6)
    t=T(bar*.95); sub=np.sin(2*np.pi*note(ch[0]-12)*t)
    if st<S[1]: add(mus,st,sub*env(bar*.95,.3,1.5),.35)
    else:
        for k in range(8): add(mus,st+k*beat/2,np.sin(2*np.pi*note(ch[0]-12)*T(beat*.45))*env(beat*.45,.01,.15),.3)
    if st>=S[1]-bar*.5:
        arp=[ch[1]+12,ch[2]+12,ch[3]+12,ch[2]+12,ch[1]+24,ch[3]+12,ch[2]+12,ch[3]+12]
        for k,m in enumerate(arp): add(mus,st+k*beat/2,pluck(note(m)),.2,.4 if k%2 else -.4)
    if S[1]-.2<=st<S[8]-bar*.6:
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
for i in range(9):
    subprocess.run(['ffmpeg','-v','error','-y','-i','vo2/'+['ep3-1-hook','ep3-2-analogy','ep3-3-gemini','ep3-4-key','ep3-5-telegram','ep3-6-response','ep3-7-claude','ep3-8-next','ep3-9-cta'][i]+'.mp3','-af','highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-2:LRA=7','-ar','44100','-ac','2',f'vo{i}.wav'],check=True)
    ins+=['-i',f'vo{i}.wav']; ms=int(S[i]*1000); f.append(f'[{i+2}:a]adelay={ms}|{ms}[v{i}]'); labs.append(f'[v{i}]')
f.append(''.join(labs)+f'amix=inputs=9:normalize=0,apad=whole_dur={TOTAL},asplit=2[vo][sc]')
f.append('[0:a]volume=-13dB[m0];[m0][sc]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=450[m]')
f.append(f'[1:a]volume=-9dB[fx];[vo][m][fx]amix=inputs=3:normalize=0,atrim=0:{TOTAL},afade=t=out:st={TOTAL-1.8}:d=1.8,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[out]')
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(f),'-map','[out]','-ac','2','mix.wav'],check=True)
print('ok')
