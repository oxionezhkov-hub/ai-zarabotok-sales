import json,re,difflib
TEXT="""Твой вопрос: как заработать на нейросетях, с чего вообще начать? Супер просто сейчас, потому что вот так делаю я и мои знакомые. Просто нужно для начала выбрать какое-то одно направление, например, сайты сделаешь ты, или картинки, или тексты, какие-то статьи, что угодно. И на этом сфокусироваться. И дальше нужно зарегистрироваться в Клоде, в ChatGPT, где угодно, где тебе удобнее, и попросить сделать какой-то первый сайт, например: сделай сайт для стоматологии. И через минут 10, может быть 20, нейросеть отдаст какой-то первый результат, и будет у тебя первая наработка. И потом можно пойти, например, по знакомым. Либо сейчас вот хорошая стратегия: зайти просто в карты, найти какой-то бизнес, у которого нет сайта. И, кстати, вот бизнесу можно будет предложить купить этот сайт, либо доработать и потом оплатить. Даже несколько знакомых так делают, зарабатывают по 20, 30, 40 тысяч рублей с одного сайта. При том, что на сайт тратят час, два часа от силы, точно не больше. И дальше можно уже уверенно находить заказы в Telegram-чатах, на фриланс-биржах, среди знакомых. Я тут тебе, конечно, помогу."""
W=json.load(open("words.json"))
cw=TEXT.split()
def norm(x): return re.sub(r"[^а-яa-z0-9]","",x.lower().replace("ё","е"))
a=[norm(x) for x in cw]; b=[norm(x["w"]) for x in W]
n,m=len(a),len(b)
def sc(i,j):
    r=difflib.SequenceMatcher(None,a[i],b[j]).ratio()
    return 2*r if r>=0.5 else -1.5
G=-0.6
S=[[0]*(m+1) for _ in range(n+1)];T=[[0]*(m+1) for _ in range(n+1)]
for i in range(1,n+1): S[i][0]=i*G;T[i][0]=1
for j in range(1,m+1): S[0][j]=j*G;T[0][j]=2
for i in range(1,n+1):
    for j in range(1,m+1):
        d=S[i-1][j-1]+sc(i-1,j-1);u=S[i-1][j]+G;l=S[i][j-1]+G
        S[i][j]=max(d,u,l);T[i][j]=0 if S[i][j]==d else (1 if S[i][j]==u else 2)
i,j=n,m;mp={}
while i>0 or j>0:
    t=T[i][j]
    if i>0 and j>0 and t==0:
        if sc(i-1,j-1)>0: mp[i-1]=j-1
        i-=1;j-=1
    elif i>0 and (j==0 or t==1): i-=1
    else: j-=1
times=[None]*n
for i,j in mp.items(): times[i]=(W[j]["s"],W[j]["e"])
# interpolate gaps
i=0
while i<n:
    if times[i] is None:
        k=i
        while k<n and times[k] is None: k+=1
        t0=times[i-1][1] if i>0 else 0.0
        t1=times[k][0] if k<n else W[-1]["e"]
        if t1<t0: t1=t0+0.1*(k-i)
        ch=[len(norm(cw[x]))+1 for x in range(i,k)];tot=sum(ch);cur=t0
        for x in range(i,k):
            d=(t1-t0)*ch[x-i]/tot;times[x]=(cur,cur+d);cur+=d
        i=k
    else: i+=1
# make monotonic
for i in range(1,n):
    if times[i][0]<times[i-1][0]: times[i]=(times[i-1][0]+0.01,max(times[i][1],times[i-1][0]+0.05))
out=[{"w":cw[i],"s":round(times[i][0],3),"e":round(times[i][1],3)} for i in range(n)]
json.dump(out,open("aligned.json","w"),ensure_ascii=False)
print(n,"words;",len(mp),"matched")
