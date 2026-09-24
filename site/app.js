/* Qanun Atlas as a mountable module.

     import { mount } from "./app.js";
     mount(el, { lang: "fa", theme: "atlas", embedded: true });

   Options:
     lang      "fa" | "en"            first language (default "en" standalone, "fa" embedded)
     dataUrl   base URL of the JSON data (default: data/ next to this file)
     embedded  true inside another site: no brand bar, no theme button, follows the
               host's dark mode (.dark on <html>), keeps its hands off <html>/<body>
     theme     "atlas" adds .qa-atlas (see atlas-theme.css)
     hash      keep the view in location.hash for deep links (default true)

   Deep links: #corpus, #map, #search=<text>, #compare=<uid>,<uid>[,<topic>]
   Only documents in the same comparison group can be compared (rule: like with like). */

const T={
 en:{corpus:"Corpus",map:"Similarity",compare:"Compare",search:"Search",
   title:"Qanun Atlas",
   lede:"Every known draft constitution for Iran, from the 1906 Fundamental Law to the transitional charters of 2020 — <em>extracted, split into articles, and made comparable</em>. Texts appear exactly as their authors wrote them; nothing here is ranked or endorsed.",
   sub:"Iranian constitutional drafts",
   enacted:"Enacted or historical",proposed:"Proposed constitutions",trans:"Transitional & programmatic",
   tl:"The constitutional century",tlsub:"Each mark is one document, placed by year and sized by article count.",
   gr:"How the drafts relate",grsub:"Documents joined where their vocabulary overlaps. Thicker lines mean closer texts.",
   tbl:"All documents",tblsub:"Sorted by year. Article counts are machine-extracted and approximate.",
   cmp:"Side by side",cmpsub:"Pick two documents of the same kind to see how much each devotes to a given subject. Click a subject to read the articles.",
   srch:"Search every article",srchsub:"Full-text search across the corpus. Type in Persian.",
   year:"Year",doc:"Document",author:"Author",arts:"Articles",pages:"Pages",kind:"Type",
   ph:"e.g. آزادی بیان، حقوق زنان، فدرال",nores:"No articles matched.",
   typein:"Type a word or phrase in Persian to search the corpus.",
   arcount:n=>n+" articles",ocr:"OCR",dup:"duplicate",partial:"partial",results:n=>n+" results",
   more:"Show more",less:"Show less",loadfail:"Could not load corpus data.",
   group:"Compared only with",alone:"No other document of this kind in the corpus yet.",
   groups:{A:"constitutions and draft constitutions",B:"bylaws",C:"charters, programmes and ideological statements",D:"treatises"},
   note:"Article counts come from automated parsing of the source PDFs and may miss or over-split articles in poorly typeset documents. Every article links back to its page in the original. Topic labels are keyword-based and shown for navigation, not as legal classification."},
 fa:{corpus:"پیکره",map:"شباهت",compare:"مقایسه",search:"جست‌وجو",
   title:"اسناد بنیادین",
   lede:"همه‌ی پیش‌نویس‌های شناخته‌شده‌ی قانون اساسی برای ایران، از قانون اساسی مشروطه تا منشورهای دوران گذار — <em>استخراج‌شده، تفکیک‌شده به اصول، و قابل مقایسه</em>. متن‌ها همان‌گونه‌اند که نویسندگانشان نوشته‌اند؛ هیچ‌چیز در اینجا رتبه‌بندی یا تأیید نشده است.",
   sub:"پیش‌نویس‌های قانون اساسی ایران",
   enacted:"مصوب یا تاریخی",proposed:"پیش‌نویس‌های پیشنهادی",trans:"دوران گذار و برنامه‌ها",
   tl:"یک سده قانون‌نویسی",tlsub:"هر نشانه یک سند است؛ جای آن بر پایه‌ی سال و اندازه‌اش بر پایه‌ی شمار اصول.",
   gr:"نسبت پیش‌نویس‌ها با یکدیگر",grsub:"اسناد آن‌جا که واژگانشان هم‌پوشانی دارد به هم پیوسته‌اند. خط ضخیم‌تر یعنی نزدیکی بیشتر.",
   tbl:"همه‌ی اسناد",tblsub:"مرتب بر پایه‌ی سال. شمار اصول به‌صورت ماشینی استخراج شده و تقریبی است.",
   cmp:"رویارو",cmpsub:"دو سند از یک گونه را برگزینید تا ببینید هر یک چقدر به یک موضوع پرداخته است. برای خواندن اصول روی موضوع کلیک کنید.",
   srch:"جست‌وجو در همه‌ی اصول",srchsub:"جست‌وجوی تمام‌متن در سراسر پیکره.",
   year:"سال",doc:"سند",author:"نویسنده",arts:"اصول",pages:"صفحه",kind:"گونه",
   ph:"برای نمونه: آزادی بیان، حقوق زنان، فدرال",nores:"اصلی یافت نشد.",
   typein:"برای جست‌وجو واژه‌ای به فارسی بنویسید.",
   arcount:n=>n+" اصل",ocr:"نویسه‌خوانی",dup:"تکراری",partial:"ناقص",results:n=>n+" نتیجه",
   more:"بیشتر",less:"کمتر",loadfail:"بارگذاری داده‌های پیکره ممکن نشد.",
   group:"تنها قابل مقایسه با",alone:"هنوز سند دیگری از این گونه در پیکره نیست.",
   groups:{A:"قانون‌های اساسی و پیش‌نویس‌ها",B:"اساسنامه‌ها",C:"منشورها، برنامه‌ها و مرامنامه‌ها",D:"رساله‌ها"},
   note:"شمار اصول از تجزیه‌ی خودکار فایل‌های اصلی به‌دست آمده و ممکن است در اسنادِ بدحروف‌چینی‌شده کم یا زیاد باشد. هر اصل به صفحه‌ی اصلی خود پیوند دارد. برچسب‌های موضوعی بر پایه‌ی کلیدواژه‌اند و برای گشت‌وگذار آمده‌اند، نه طبقه‌بندی حقوقی."}};

const BUCKET={in_force:0,historical:0,draft:1,transitional:2,program:2,treatise:2};
const BCOL=["var(--s1)","var(--s2)","var(--s3)"];
// Comparison groups (plan §6): bylaws are never compared with constitutions.
export const GROUP={constitution:"A",constitution_proposal:"A",bylaws:"B",
  charter:"C",program:"C",ideology:"C",treatise:"D"};
const VIEWS=["corpus","map","compare","search"];

const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e};

export function mount(root, opts={}){
  const embedded=!!opts.embedded, useHash=opts.hash!==false;
  const dataUrl=new URL(opts.dataUrl||"data/", new URL(".", import.meta.url));
  let L=opts.lang||(embedded?"fa":"en"), CAT=[], AN=null, ARTS=[], view="corpus";
  let cmpA=null,cmpB=null,cmpT=null,q="";
  const t=k=>T[L][k];
  const title=d=>L==="fa"?d.fa:d.en;
  const author=d=>L==="fa"?(d.author_fa||""):(d.author_en||"");
  const group=d=>GROUP[d.kind]||"A";
  const width=()=>root.clientWidth||innerWidth;

  root.classList.add("qa-root");
  if(embedded)root.classList.add("qa-embedded");
  if(opts.theme==="atlas")root.classList.add("qa-atlas");
  root.innerHTML=`
    <div class="hdr"><div class="hdr-in">
      <div class="brand"><b data-k="brand"></b><span data-k="brandsub"></span></div>
      <div class="tabs" role="tablist"></div>
      <button class="ghost" data-k="lang"></button>
      ${embedded?"":`<button class="ghost" data-k="theme" title="Toggle theme">◐</button>`}
    </div></div>
    <div class="qa-main">
      <p class="lede"></p>
      ${VIEWS.map(v=>`<section class="view" data-v="${v}" hidden></section>`).join("")}
    </div>
    <div class="qa-tip"></div>`;
  const $=s=>root.querySelector(s), V=v=>$(`[data-v="${v}"]`);

  /* ---------- theme: own toggle standalone, host's .dark embedded ---------- */
  let observer=null;
  if(embedded){
    const sync=()=>root.setAttribute("data-theme",document.documentElement.classList.contains("dark")?"dark":"light");
    sync();observer=new MutationObserver(sync);
    observer.observe(document.documentElement,{attributes:true,attributeFilter:["class"]});
  }else{
    $('[data-k="theme"]').onclick=()=>{
      const d=root.getAttribute("data-theme")==="dark"||(!root.getAttribute("data-theme")&&matchMedia("(prefers-color-scheme:dark)").matches);
      root.setAttribute("data-theme",d?"light":"dark");render();};
  }
  $('[data-k="lang"]').onclick=()=>{L=L==="en"?"fa":"en";render();};

  /* ---------- tooltip ---------- */
  const tip=$(".qa-tip");
  function showTip(e,html){tip.innerHTML=html;tip.style.opacity=1;
    const r=tip.getBoundingClientRect();
    tip.style.left=Math.min(e.clientX+14,innerWidth-r.width-10)+"px";
    tip.style.top=Math.min(e.clientY+14,innerHeight-r.height-10)+"px";}
  function hideTip(){tip.style.opacity=0}

  /* ---------- deep links ---------- */
  function readHash(){
    const h=decodeURIComponent(location.hash.slice(1)), [k,v=""]=h.split(/=(.*)/s);
    if(!VIEWS.includes(k))return;
    view=k;
    if(k==="search")q=v;
    if(k==="compare"){const [a,b,tp]=v.split(",");cmpA=a||null;cmpB=b||null;cmpT=tp||null;}
  }
  function writeHash(){
    if(!useHash)return;
    let h=view;
    if(view==="search"&&q)h+="="+q;
    if(view==="compare"&&cmpA)h+="="+[cmpA,cmpB,cmpT].filter(Boolean).join(",");
    if(decodeURIComponent(location.hash.slice(1))!==h)
      history.replaceState(history.state,"","#"+encodeURIComponent(h).replace(/%2C/g,",").replace(/%3D/g,"="));
  }
  const onHash=()=>{readHash();render();};
  if(useHash){readHash();addEventListener("hashchange",onHash);}

  /* ---------- boot ---------- */
  const get=n=>fetch(new URL(n,dataUrl)).then(r=>{if(!r.ok)throw new Error(n+": "+r.status);return r.json()});
  Promise.all([get("catalog.json"),get("analysis.json"),get("articles.json")])
    .then(([c,a,ar])=>{CAT=c;AN=a;ARTS=ar;render()})
    .catch(e=>{root.setAttribute("lang",L);V("corpus").hidden=false;
      V("corpus").innerHTML=`<div class="empty">${esc(t("loadfail"))}</div>`;console.error(e)});

  function render(){
    root.setAttribute("lang",L);root.setAttribute("dir",L==="fa"?"rtl":"ltr");
    $('[data-k="brand"]').textContent=t("title");
    $('[data-k="brandsub"]').textContent=t("sub");
    $('[data-k="lang"]').textContent=L==="en"?"فارسی":"English";
    $(".lede").innerHTML=t("lede");
    const tb=$(".tabs");tb.innerHTML="";
    VIEWS.forEach(k=>{
      const b=el("button",null,esc(t(k)));b.setAttribute("role","tab");
      b.setAttribute("aria-selected",view===k);
      b.onclick=()=>{view=k;render()};tb.append(b);});
    VIEWS.forEach(k=>V(k).hidden=view!==k);
    if(!CAT.length)return;
    ({corpus:corpusView,map:mapView,compare:compareView,search:searchView})[view]();
    writeHash();
  }

  /* ================= CORPUS ================= */
  function corpusView(){
    const v=V("corpus");v.innerHTML="";
    const p1=el("div","panel");
    p1.append(el("h2",null,esc(t("tl"))),el("div","sub",esc(t("tlsub"))),legend());
    p1.append(timeline());
    v.append(p1);
    const p2=el("div","panel");
    p2.append(el("h2",null,esc(t("tbl"))),el("div","sub",esc(t("tblsub"))));
    const w=el("div","tbl-wrap");w.append(table());p2.append(w);
    p2.append(el("div","note",esc(t("note"))));
    v.append(p2);
  }
  function legend(){
    const g=el("div","legend");
    [t("enacted"),t("proposed"),t("trans")].forEach((n,i)=>
      g.append(el("span",null,`<i style="background:${BCOL[i]}"></i>${esc(n)}`)));
    return g;
  }
  function timeline(){
    const W=Math.max(620,Math.min(1200,width()-44)),LH=104,H=LH*3+46,PL=L==="fa"?16:132,PR=L==="fa"?132:16;
    const y0=1900,y1=2025;
    const x=y=>{const f=(Math.max(y0,y)-y0)/(y1-y0);return L==="fa"?W-PR-f*(W-PL-PR):PL+f*(W-PL-PR)};
    const s=[`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("tl"))}">`];
    for(let y=1900;y<=2020;y+=20){s.push(`<line class="gridline" x1="${x(y)}" y1="26" x2="${x(y)}" y2="${LH*3+22}"/>`,
      `<text class="axis-t" x="${x(y)}" y="18" text-anchor="middle">${y}</text>`);}
    [t("enacted"),t("proposed"),t("trans")].forEach((n,i)=>{
      const ty=26+i*LH+15;
      s.push(`<text class="lane-t" x="${L==="fa"?W-8:8}" y="${ty}" text-anchor="${L==="fa"?"end":"start"}">${esc(n)}</text>`);});
    const placed=[];
    CAT.forEach((d,i)=>{
      const b=BUCKET[d.type]??2, cx=x(d.year||1900), r=Math.max(4.5,Math.min(17,Math.sqrt(d.n_articles||1)*1.25));
      let cy=26+b*LH+LH/2+8, dir=1, k=0;
      while(placed.some(p=>p.b===b&&Math.hypot(p.cx-cx,p.cy-cy)<p.r+r+3)&&k<28){k++;cy=26+b*LH+LH/2+8+dir*Math.ceil(k/2)*(r+5);dir*=-1;}
      cy=Math.max(26+b*LH+r+6,Math.min(26+(b+1)*LH-r-2,cy));
      placed.push({cx,cy,r,b,d,i});});
    placed.forEach(p=>s.push(`<circle class="node" data-i="${p.i}" cx="${p.cx}" cy="${p.cy}" r="${p.r}" fill="${BCOL[p.b]}" fill-opacity=".82"/>`));
    s.push("</svg>");
    const w=el("div","chart",s.join(""));
    w.querySelectorAll(".node").forEach(n=>{
      const d=CAT[+n.dataset.i];
      n.onmousemove=e=>showTip(e,`<b>${esc(title(d))}</b><span>${esc(author(d))}${d.era?" · "+esc(d.era):""}<br>${esc(t("arcount")(d.n_articles))}</span>`);
      n.onmouseleave=hideTip;});
    return w;
  }
  function table(){
    const tb=el("table");
    tb.innerHTML=`<thead><tr><th>${t("year")}</th><th>${t("doc")}</th><th>${t("author")}</th>
      <th style="text-align:end">${t("arts")}</th><th style="text-align:end">${t("pages")}</th></tr></thead>`;
    const body=el("tbody");
    CAT.forEach(d=>{
      const b=BUCKET[d.type]??2;
      const tr=el("tr");
      tr.innerHTML=`<td class="num">${d.year||"—"}</td>
        <td class="ttl"><span class="dot" style="background:${BCOL[b]}"></span>${esc(title(d))}
          ${d.ocr?`<span class="flag">${t("ocr")}</span>`:""}${d.duplicate_of?`<span class="flag">${t("dup")}</span>`:""}${(d.confidence<0.8&&["draft","in_force","historical","transitional"].includes(d.type))?`<span class="flag quiet">${t("partial")}</span>`:""}
          <small>${esc(d.source_pdf)}</small></td>
        <td>${esc(author(d))}</td><td class="num">${d.n_articles}</td><td class="num">${d.n_pages}</td>`;
      body.append(tr);});
    tb.append(body);return tb;
  }

  /* ================= MAP ================= */
  function mapView(){
    const v=V("map");v.innerHTML="";
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("gr"))),el("div","sub",esc(t("grsub"))),legend());
    p.append(graph());
    p.append(el("div","note",esc(t("note"))));
    v.append(p);
  }
  function graph(){
    const W=Math.max(620,Math.min(1100,width()-44)),H=520;
    const ids=CAT.map(c=>c.uid), idx={};ids.forEach((d,i)=>idx[d]=i);
    const nodes=ids.map((id,i)=>{const d=CAT.find(c=>c.uid===id)||{n_articles:1,type:"draft"};
      return{id,d,b:BUCKET[d.type]??2,r:Math.max(5,Math.min(16,Math.sqrt(d.n_articles||1)*1.15)),
        x:W/2+Math.cos(i*2.4)*180,y:H/2+Math.sin(i*2.4)*150,vx:0,vy:0};});
    // edges reference documents by uid; any pointing at a removed document just drop out
    const edges=AN.edges.filter(e=>e.s>0.42&&idx[e.a]!=null&&idx[e.b]!=null)
                        .map(e=>({a:idx[e.a],b:idx[e.b],s:e.s}));
    for(let it=0;it<420;it++){
      for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
        const a=nodes[i],b=nodes[j];let dx=b.x-a.x,dy=b.y-a.y,dd=Math.hypot(dx,dy)||.1;
        const f=1400/(dd*dd);a.vx-=dx/dd*f;a.vy-=dy/dd*f;b.vx+=dx/dd*f;b.vy+=dy/dd*f;
        const mn=a.r+b.r+7; if(dd<mn){const p=(mn-dd)*.5;a.vx-=dx/dd*p;a.vy-=dy/dd*p;b.vx+=dx/dd*p;b.vy+=dy/dd*p;}}
      edges.forEach(e=>{const a=nodes[e.a],b=nodes[e.b];
        let dx=b.x-a.x,dy=b.y-a.y,dd=Math.hypot(dx,dy)||.1;
        const f=(dd-110)*.012*e.s;a.vx+=dx/dd*f;a.vy+=dy/dd*f;b.vx-=dx/dd*f;b.vy-=dy/dd*f;});
      nodes.forEach(n=>{n.vx+=(W/2-n.x)*.0016;n.vy+=(H/2-n.y)*.0016;
        n.x+=n.vx*.62;n.y+=n.vy*.62;n.vx*=.82;n.vy*=.82;
        n.x=Math.max(n.r+4,Math.min(W-n.r-4,n.x));n.y=Math.max(n.r+4,Math.min(H-n.r-4,n.y));});}
    const s=[`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("gr"))}">`];
    edges.forEach(e=>s.push(`<line class="edge" x1="${nodes[e.a].x.toFixed(1)}" y1="${nodes[e.a].y.toFixed(1)}" x2="${nodes[e.b].x.toFixed(1)}" y2="${nodes[e.b].y.toFixed(1)}" stroke-width="${(e.s*3.4).toFixed(2)}" stroke-opacity="${(e.s*.9).toFixed(2)}"/>`));
    nodes.forEach((n,i)=>s.push(`<circle class="node" data-i="${i}" cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="${n.r}" fill="${BCOL[n.b]}" fill-opacity=".85"/>`));
    s.push("</svg>");
    const w=el("div","chart",s.join(""));
    w.querySelectorAll(".node").forEach(c=>{const n=nodes[+c.dataset.i];
      c.onmousemove=e=>{const near=edges.filter(x=>x.a===+c.dataset.i||x.b===+c.dataset.i)
        .sort((p,q)=>q.s-p.s).slice(0,2)
        .map(x=>{const o=nodes[x.a===+c.dataset.i?x.b:x.a];return esc(title(o.d))+" ("+x.s.toFixed(2)+")"}).join("<br>");
        showTip(e,`<b>${esc(title(n.d))}</b><span>${esc(t("arcount")(n.d.n_articles))}${near?"<br><br>"+near:""}</span>`)};
      c.onmouseleave=hideTip;});
    return w;
  }

  /* ================= COMPARE ================= */
  function compareView(){
    const v=V("compare");v.innerHTML="";
    const withArts=CAT.filter(d=>d.n_articles>5);
    const byId=id=>withArts.find(d=>d.uid===id);
    if(!byId(cmpA))cmpA=(withArts.find(d=>d.type==="draft")||withArts[0]).uid;
    const A0=byId(cmpA), peers=withArts.filter(d=>d.uid!==cmpA&&group(d)===group(A0));
    if(!peers.some(d=>d.uid===cmpB))cmpB=(peers.find(d=>d.type==="draft")||peers[0]||{}).uid||null;
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("cmp"))),el("div","sub",esc(t("cmpsub"))));
    const row=el("div","row");
    [["A",cmpA,withArts,i=>{cmpA=i}],["B",cmpB,peers,i=>{cmpB=i}]].forEach(([k,cur,list,set],n)=>{
      const s=el("select");
      list.forEach(d=>{const o=el("option",null,esc(title(d))+" ("+d.n_articles+")");o.value=d.uid;
        if(d.uid===cur)o.selected=true;s.append(o)});
      s.disabled=!list.length;
      s.onchange=()=>{set(s.value);cmpT=null;compareView();writeHash()};
      const wrap=el("div");wrap.style.flex="1";wrap.style.minWidth="220px";
      wrap.append(el("div",null,`<span class="dot" style="background:${n?"var(--s2)":"var(--s1)"}"></span><small style="color:var(--ink-3)">${k}</small>`),s);
      row.append(wrap);});
    p.append(row);
    p.append(el("div","group-note",esc(peers.length?`${t("group")} ${t("groups")[group(A0)]}`:t("alone"))));
    if(!cmpB){p.append(el("div","note",esc(t("note"))));v.append(p);return;}

    const A=ARTS.filter(a=>a.doc===cmpA),B=ARTS.filter(a=>a.doc===cmpB);
    const cnt=o=>{const m={};o.forEach(a=>a.topics.forEach(x=>m[x]=(m[x]||0)+1));return m};
    const ca=cnt(A),cb=cnt(B),max=Math.max(1,...Object.values(ca),...Object.values(cb));
    const list=el("div");list.style.marginBlockStart="16px";
    Object.keys(AN.topics).forEach(k=>{
      const a=ca[k]||0,b=cb[k]||0; if(!a&&!b)return;
      const r=el("div","topic-row"+(cmpT===k?" on":""));
      r.innerHTML=`<div class="tname"><b>${esc(AN.topics[k][L])}</b></div>
        <div class="bars">
          <div style="display:flex;align-items:center"><div class="bar" style="width:${a/max*100}%;background:var(--s1)"></div><span class="barlbl">${a}</span></div>
          <div style="display:flex;align-items:center"><div class="bar" style="width:${b/max*100}%;background:var(--s2)"></div><span class="barlbl">${b}</span></div>
        </div>`;
      r.onclick=()=>{cmpT=cmpT===k?null:k;compareView();writeHash()};
      list.append(r);});
    p.append(list);
    if(cmpT){
      const g=el("div","arts");
      [[cmpA,A,"var(--s1)"],[cmpB,B,"var(--s2)"]].forEach(([id,arr,col])=>{
        const c=el("div","artcol"),d=CAT.find(x=>x.uid===id);
        c.append(el("h3",null,`<span class="dot" style="background:${col}"></span>`+esc(title(d))));
        const hits=arr.filter(a=>a.topics.includes(cmpT));
        if(!hits.length)c.append(el("div","empty",esc(t("nores"))));
        hits.slice(0,14).forEach(a=>c.append(artCard(a)));
        g.append(c);});
      p.append(g);}
    p.append(el("div","note",esc(t("note"))));
    v.append(p);
  }
  function artCard(a){
    const c=el("div","art");
    c.innerHTML=`<div class="art-h"><span class="art-n">${esc(a.unit)} ${a.n}</span>
      <span class="art-p">p.${a.page}</span></div><div class="fa" dir="rtl" lang="fa">${esc(a.text)}</div>`;
    if(a.text.length>320){const b=el("button","more");
      b.textContent=t("more");
      b.onclick=()=>{c.classList.toggle("open");b.textContent=c.classList.contains("open")?t("less"):t("more")};
      c.append(b);}
    return c;
  }

  /* ================= SEARCH ================= */
  function searchView(){
    const v=V("search");v.innerHTML="";
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("srch"))),el("div","sub",esc(t("srchsub"))));
    const bar=el("div","searchbar");
    const inp=el("input");inp.placeholder=t("ph");inp.value=q;
    inp.dir="rtl";inp.setAttribute("lang","fa");inp.setAttribute("aria-label",t("srch"));
    bar.append(inp);p.append(bar);
    const res=el("div");p.append(res);
    const run=()=>{q=inp.value.trim();res.innerHTML="";writeHash();
      if(q.length<2){res.append(el("div","empty",esc(t("typein"))));return}
      const hits=ARTS.filter(a=>a.text.includes(q)).slice(0,60);
      if(!hits.length){res.append(el("div","empty",esc(t("nores"))));return}
      res.append(el("div","sub",esc(t("results")(hits.length))));
      hits.forEach(a=>{const d=CAT.find(c=>c.uid===a.doc)||{};
        const i=a.text.indexOf(q),s=Math.max(0,i-110);
        const snip=(s?"…":"")+esc(a.text.slice(s,i))+"<mark>"+esc(q)+"</mark>"+esc(a.text.slice(i+q.length,i+q.length+180))+"…";
        const h=el("div","hit");
        h.innerHTML=`<div class="hit-src"><b>${esc(title(d))}</b> · ${esc(a.unit)} ${a.n} · p.${a.page}</div>
          <div class="fa" dir="rtl" lang="fa">${snip}</div>`;
        res.append(h);});};
    inp.oninput=run;run();
    setTimeout(()=>inp.focus({preventScroll:true}),0);
    p.append(el("div","note",esc(t("note"))));
    v.append(p);
  }

  return {
    destroy(){ if(useHash)removeEventListener("hashchange",onHash); observer?.disconnect(); root.innerHTML=""; },
    show(k){ if(VIEWS.includes(k)){view=k;render();} },
  };
}
