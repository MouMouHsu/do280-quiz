#!/usr/bin/env python3
"""Build the DO280 V4.22 quiz static site (GitHub Pages ready)."""
import json, glob, os, random, html

SRC = os.path.join(os.path.dirname(__file__), "data")
OUT = os.path.join(os.path.dirname(__file__), "site")
os.makedirs(OUT, exist_ok=True)

CSS = r"""
:root{--bg:#f6f7f9;--card:#fff;--ink:#1d2430;--mute:#5b6676;--line:#dde2ea;--accent:#c00;--accent2:#8a0000;
--ok:#1a7f37;--okbg:#e9f6ec;--bad:#c62828;--badbg:#fdecec;--sel:#eef3ff}
@media (prefers-color-scheme:dark){:root{--bg:#14171c;--card:#1d2128;--ink:#e6e9ee;--mute:#9aa4b2;--line:#323844;
--sel:#24304a;--okbg:#16301f;--badbg:#3a1c1c;--ok:#5cc97a;--bad:#ff7b7b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif}
a{color:var(--accent)}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.wrap{max-width:860px;margin:0 auto;padding:0 18px}
.bar{display:flex;align-items:center;gap:14px;padding:12px 0;flex-wrap:wrap}
.bar h1{font-size:18px;margin:0;flex:1;min-width:220px;line-height:1.35}
.bar h1 small{display:block;font-weight:400;color:var(--mute);font-size:13px}
.stat{font-size:14px;color:var(--mute);white-space:nowrap}
.stat b{color:var(--ink)}
.prog{height:4px;background:var(--line)}
.prog i{display:block;height:100%;width:0;background:var(--accent);transition:width .2s}
.btn{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:7px 12px;font:inherit;font-size:14px;cursor:pointer}
.btn:hover{border-color:var(--mute)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.primary:hover{background:var(--accent2)}
.tools{display:flex;gap:8px;flex-wrap:wrap;padding:14px 0 4px}
main{padding:8px 0 60px}
.q{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}
.q h2{font-size:16px;font-weight:600;margin:0 0 12px;display:flex;gap:10px}
.q h2 .n{color:var(--accent);flex:none;min-width:2.2em}
.opts{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.opts label{display:flex;gap:10px;align-items:flex-start;border:1px solid var(--line);border-radius:8px;padding:9px 12px;cursor:pointer}
.opts label:hover{background:var(--sel)}
.opts input{margin-top:5px;accent-color:var(--accent)}
.opts .k{font-weight:700;flex:none;width:1.3em}
.opts label.chosen{background:var(--sel);border-color:#7b93c9}
.opts label.right{background:var(--okbg);border-color:var(--ok)}
.opts label.wrong{background:var(--badbg);border-color:var(--bad)}
.act{margin-top:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.ans{display:none;margin-top:12px;border-left:4px solid var(--ok);background:var(--okbg);padding:10px 14px;border-radius:0 8px 8px 0}
.ans.show{display:block}
.ans.x{border-color:var(--bad);background:var(--badbg)}
.ans .v{font-weight:700;margin-bottom:4px}
.ans p{margin:4px 0 0}
.badge{font-size:13px;font-weight:600}
.badge.ok{color:var(--ok)}.badge.bad{color:var(--bad)}
.summary{display:none;background:var(--card);border:2px solid var(--accent);border-radius:12px;padding:16px 20px;margin:14px 0}
.summary.show{display:block}
.hide{display:none!important}
footer{color:var(--mute);font-size:13px;text-align:center;padding:24px 0 40px}
/* index */
.hero{padding:34px 0 10px}.hero h1{margin:0 0 6px;font-size:26px}.hero p{color:var(--mute);margin:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;padding:20px 0 40px}
.card{display:block;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;transition:border-color .15s,transform .15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card .c{color:var(--accent);font-weight:700;font-size:13px;letter-spacing:.05em}
.card h2{font-size:17px;margin:4px 0 2px;line-height:1.35}
.card p{margin:0;color:var(--mute);font-size:14px}
.card .best{margin-top:8px;font-size:13px;color:var(--mute)}
"""

JS = r"""
const D=window.QUIZ, L='ABCD', KEY='do280-v422-'+D.id;
let st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){st={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
const M=document.getElementById('qs');
D.q.forEach((q,i)=>{
  const s=document.createElement('section');s.className='q';s.id='q'+(i+1);
  s.innerHTML=`<h2><span class="n">Q${i+1}.</span><span lang="en">${q.q}</span></h2>
  <ul class="opts">${q.o.map((o,j)=>`<li><label><input type="radio" name="r${i}" value="${j}"><span class="k">${L[j]}.</span><span lang="en">${o}</span></label></li>`).join('')}</ul>
  <div class="act"><button class="btn primary show-ans">查看答案與說明</button><span class="badge"></span></div>
  <div class="ans"><div class="v"></div><p>${q.e}</p></div>`;
  M.appendChild(s);
  s.querySelectorAll('input').forEach(r=>r.addEventListener('change',()=>{st[i]={c:+r.value,r:st[i]&&st[i].r};save();paint(i,false)}));
  s.querySelector('.show-ans').addEventListener('click',()=>{st[i]=st[i]||{};st[i].r=1;save();paint(i,true)});
});
function paint(i,scroll){
  const q=D.q[i],s=document.getElementById('q'+(i+1)),x=st[i]||{};
  const labels=s.querySelectorAll('label');
  labels.forEach((lb,j)=>{lb.classList.remove('chosen','right','wrong');lb.querySelector('input').checked=(x.c===j);if(x.c===j)lb.classList.add('chosen')});
  const a=s.querySelector('.ans'),b=s.querySelector('.badge'),btn=s.querySelector('.show-ans');
  if(x.r){
    labels[q.a].classList.add('right');
    if(x.c!==undefined&&x.c!==q.a)labels[x.c].classList.add('wrong');
    a.classList.add('show');a.classList.toggle('x',x.c!==undefined&&x.c!==q.a);
    a.querySelector('.v').textContent=(x.c===undefined?'正確答案：':x.c===q.a?'答對了！正確答案：':'答錯了。正確答案：')+L[q.a]+'. '+strip(q.o[q.a]);
    b.textContent=x.c===undefined?'未作答':x.c===q.a?'✔ 正確':'✘ 錯誤';b.className='badge '+(x.c===q.a?'ok':x.c===undefined?'':'bad');
    btn.textContent='隱藏答案';btn.onclick=()=>{st[i].r=0;save();paint(i)};
  }else{
    a.classList.remove('show');b.textContent='';btn.textContent='查看答案與說明';
    btn.onclick=()=>{st[i]=st[i]||{};st[i].r=1;save();paint(i)};
  }
  stats();
}
function strip(h){const t=document.createElement('div');t.innerHTML=h;return t.textContent}
function stats(){
  let done=0,rev=0,ok=0;D.q.forEach((q,i)=>{const x=st[i]||{};if(x.c!==undefined)done++;if(x.r&&x.c!==undefined){rev++;if(x.c===q.a)ok++}});
  document.getElementById('done').textContent=done;document.getElementById('ok').textContent=ok;document.getElementById('rev').textContent=rev;
  document.querySelector('.prog i').style.width=(done/D.q.length*100)+'%';
}
document.getElementById('checkAll').onclick=()=>{
  D.q.forEach((q,i)=>{st[i]=st[i]||{};st[i].r=1});save();D.q.forEach((q,i)=>paint(i));
  let ok=0,un=0;D.q.forEach((q,i)=>{if(st[i].c===undefined)un++;else if(st[i].c===q.a)ok++});
  const s=document.getElementById('sum');s.classList.add('show');
  s.innerHTML=`<b>成績：${ok} / ${D.q.length} (${Math.round(ok/D.q.length*100)}%)</b><br>答錯 ${D.q.length-ok-un} 題，未作答 ${un} 題。可按「只看答錯」複習。`;
  try{const b=JSON.parse(localStorage.getItem('do280-v422-best')||'{}');if(!b[D.id]||ok>b[D.id]){b[D.id]=ok;localStorage.setItem('do280-v422-best',JSON.stringify(b))}}catch(e){}
  s.scrollIntoView({behavior:'smooth',block:'center'});
};
document.getElementById('reset').onclick=()=>{if(!confirmReset())return;st={};save();document.getElementById('sum').classList.remove('show');filt=0;applyFilter();D.q.forEach((q,i)=>paint(i));window.scrollTo(0,0)};
let armed=0;function confirmReset(){const b=document.getElementById('reset');if(armed){armed=0;b.textContent='重新作答';return true}armed=1;b.textContent='再按一次確認清除';setTimeout(()=>{armed=0;b.textContent='重新作答'},3000);return false}
let filt=0;document.getElementById('wrongOnly').onclick=()=>{filt=!filt;applyFilter()};
function applyFilter(){const b=document.getElementById('wrongOnly');b.textContent=filt?'顯示全部題目':'只看答錯';
  D.q.forEach((q,i)=>{const x=st[i]||{};const w=x.r&&x.c!==undefined&&x.c!==q.a;document.getElementById('q'+(i+1)).classList.toggle('hide',!!filt&&!w)})}
D.q.forEach((q,i)=>paint(i));
"""

def page(title, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>{extra_head}
<style>{CSS}</style></head><body>
{body}
</body></html>"""

chapters = []
for f in sorted(glob.glob(os.path.join(SRC, "ch*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    assert len(d["q"]) == 50, f
    rng = random.Random("do280-" + d["id"])
    # balanced answer positions: 12-13 per letter, then shuffle the rest
    pos = [i % 4 for i in range(50)]
    rng.shuffle(pos)
    qs = []
    for q, p in zip(d["q"], pos):
        correct, wrong = q["o"][0], q["o"][1:]
        rng.shuffle(wrong)
        opts = wrong[:p] + [correct] + wrong[p:]
        qs.append({"q": html.escape(q["q"]), "o": [html.escape(o) for o in opts],
                   "a": p, "e": html.escape(q["e"])})
    data = {"id": d["id"], "q": qs}
    name = f"{d['id']}.html"
    t = f"DO280 V4.22 · {d['num']} {d['title']}"
    body = f"""<header class="top"><div class="wrap"><div class="bar">
<h1><span lang="en">{d['num']} · {html.escape(d['title'])}</span><small>{html.escape(d['zh'])} · 50 題單選題 · DO280 V4.22</small></h1>
<span class="stat">已作答 <b id="done">0</b>/50 · 已對答 <b id="rev">0</b> · 答對 <b id="ok">0</b></span>
</div></div><div class="prog"><i></i></div></header>
<main><div class="wrap">
<div class="tools"><a class="btn" href="index.html">← 回章節列表</a>
<button class="btn primary" id="checkAll">全部對答案並計分</button>
<button class="btn" id="wrongOnly">只看答錯</button>
<button class="btn" id="reset">重新作答</button></div>
<div class="summary" id="sum"></div>
<div id="qs"></div>
<div class="tools"><button class="btn primary" onclick="document.getElementById('checkAll').click()">全部對答案並計分</button><a class="btn" href="index.html">← 回章節列表</a></div>
</div></main>
<footer>題目依 DO280 V4.22 {d['num']} 簡報內容撰寫 · 作答進度只存在你的瀏覽器</footer>
<script>window.QUIZ={json.dumps(data, ensure_ascii=False)};</script>
<script>{JS}</script>"""
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(page(t, body))
    chapters.append((d, name, [q["a"] for q in qs]))
    print(name, "answer distribution", [sum(1 for q in qs if q["a"] == k) for k in range(4)])

cards = "\n".join(
    f"""<a class="card" href="{n}"><div class="c">{d['num']}</div><h2 lang="en">{html.escape(d['title'])}</h2><p>{html.escape(d['zh'])} · 50 題</p><div class="best" data-id="{d['id']}"></div></a>"""
    for d, n, _ in chapters)
idx = f"""<main><div class="wrap">
<div class="hero"><h1>DO280 V4.22 練習題庫</h1>
<p>Red Hat OpenShift Administration II · 每章 50 題英文單選題，答案與說明為中文。</p></div>
<div class="grid">{cards}</div></div></main>
<footer>作答進度與最佳成績只存在你的瀏覽器</footer>
<script>try{{const b=JSON.parse(localStorage.getItem('do280-v422-best')||'{{}}');document.querySelectorAll('.best').forEach(e=>{{const v=b[e.dataset.id];if(v!==undefined)e.textContent='最佳成績：'+v+' / 50'}})}}catch(e){{}}</script>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page("DO280 V4.22 練習題庫", idx))
open(os.path.join(OUT, ".nojekyll"), "w").write("")
open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(
"""# DO280 V4.22 練習題庫

Red Hat OpenShift Administration II (DO280) V4.22 各章練習題：每章 50 題英文單選題，提供「查看答案與說明」(中文)、全部計分、只看答錯與重新作答。

- `index.html`：章節列表
- `ch01.html` – `ch09.html`：各章測驗頁 (題庫內嵌於頁面，不需後端)

## 發布到 GitHub Pages

1. 把本資料夾所有檔案 (含 `.nojekyll`) Push 到 Repository 的 `main` Branch 根目錄。
2. Repository → Settings → Pages → Build and deployment：Source 選 **Deploy from a branch**，Branch 選 `main`、資料夾 `/ (root)`，按 Save。
3. 約一分鐘後，網址為 `https://<帳號>.github.io/<Repository 名稱>/`。
""")
print("built", len(chapters), "chapters")
