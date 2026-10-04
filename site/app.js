/* Constitutions Atlas as a mountable module.

     import { mount } from "./app.js";
     mount(el, { lang: "fa", theme: "atlas", embedded: true });

   Options:
     lang      "fa" | "en"            first language (default "en" standalone, "fa" embedded)
     dataUrl   base URL of the JSON data (default: data/ next to this file)
     pdfUrl    base URL of the source PDFs (default: pdf/ next to this file)
     embedded  true inside another site: no brand bar, no theme button, follows the
               host's dark mode (.dark on <html>), keeps its hands off <html>/<body>
     theme     "atlas" adds .qa-atlas (see atlas-theme.css)
     hash      keep the view in location.hash for deep links (default true)

   Deep links: #corpus, #map, #search=<text>, #compare=<uid>,<uid>[,<topic>], #editions=<series>[,<uid>,<uid>],
   #rights=<uid>[,<right>], #topics=<uid>[,<topic>], #topics=method
   Only documents in the same comparison group can be compared (rule: like with like). */

// Persian digits for the strings below
const num2=n=>Number(n).toLocaleString("fa-IR",{useGrouping:false});
const T={
 en:{corpus:"Corpus",map:"Similarity",compare:"Compare",editions:"Editions",search:"Search",rights:"Human rights",
   ed:"Edition to edition",edsub:"Some drafts were revised and republished. Pick two editions of one draft: articles are matched across them, and each changed article shows what was removed (red) and added (green).",
   edpick:"Draft",edfrom:"Earlier",edto:"Later",
   edsum:(m,s,a,d)=>m+" articles in both, "+s+" of them unchanged · "+a+" added · "+d+" dropped",
   edcount:n=>n+" editions",edchanged:"Changed only",edall:"All articles",edsame:"Unchanged",edadd:"Added",eddrop:"Dropped",
   ednone:"No changes between these two editions.",
   ednote:"Articles are matched by their words, in order, so renumbered articles still line up. Differences in spelling, digits and spacing count as changes, and where a text was read from page images a difference can be a reading error: the PDF page is linked on every article.",
   rtitle:"Measured against international human-rights law",
   rsub:"Each document is read against 31 rights drawn from the Universal Declaration, the two Covenants and the core UN conventions. Every verdict cites the document's articles and the treaty provisions it rests on.",
   rnone:"No audit has been reviewed and published yet.",
   rpick:"Document",rreviewed:(who,d)=>"Reviewed"+(who?" by "+who:"")+(d?" on "+d:""),
   rpreview:"Preview: not yet reviewed. Not for publication.",
   rsrc:"Source of the text",rpdf:"The PDF",rpage:n=>"Open page "+n+" of the PDF",rscope:n=>n+" articles read; the wording in force of amended articles.",
   runrev:"Not yet reviewed: these verdicts come from the automated reading and its citation checks; no person has confirmed them yet.",
   rarts:"Articles cited",rbench:"Benchmark provisions",rquote:"Decisive words",rnoarts:"No article addresses this right.",
   ren:"English text; the Persian translation is pending.",rall:"All",
   v:{guaranteed:"Guaranteed",restricted_clawback:"Restricted",contradicted:"Contradicted",silent:"Silent"},
   vd:{guaranteed:"The document protects the right explicitly, at the level the treaties require.",
       restricted_clawback:"The document names the right, then takes it back: an open-ended condition (such as “Islamic standards” or “the law”), limiting it to some people, or restricting it beyond what the treaties allow.",
       contradicted:"The document goes against the right, e.g. by establishing discrimination, allowing a prohibited punishment, or placing an office above the right.",
       silent:"The document does not address the right. Silence is itself a finding."},
   mtitle:"How this was made",
   m:["The benchmark is international human-rights law, stored word for word with a stable ID for every paragraph (e.g. ICCPR.19.3). No national constitution is used as a standard; every document is only the object of assessment.",
      "Claude (Anthropic) reads the document article by article and gives one verdict per right, citing the articles and the treaty paragraphs it rests on and quoting the decisive words.",
      "Every citation is checked automatically: a verdict citing an article or treaty paragraph that does not exist is rejected, and a quote not found in the document is flagged.",
      "A person then reviews the verdicts. Until that is done, a document's page says it is not yet reviewed.",
      "The document's text comes from its PDF and was checked against the page images; the article list shows exactly what was read. Where an article was amended, only the wording in force is assessed.",
      "This is an analytical reading, not legal advice or a ruling."],
   mmodel:(m,b)=>"Model: "+m+" · benchmark version "+b,
   mby:"Read in a Claude Code working session rather than through the audit pipeline: same scoring guide, benchmark, articles and citation checks.",
   topics:"Topics",
   ttitle:"What the document covers, and what it leaves out",
   tsub:"Every article is tagged with the topics of Constitute's vocabulary (Comparative Constitutions Project): 334 subjects that constitutions around the world address, from the right to life to the removal of judges, and three from the project's later vocabulary: democracy, rule of law and social security. The topics no article touches are listed too. More lenses follow: the policy field each article governs (Comparative Agendas Project) and which level of government holds it; how much authority the regions would have (Regional Authority Index); the rules it lays down for sharing power; and its language policy.",
   tnone:"No document has been tagged and published yet.",
   tcount:(a,b)=>a+" of "+b+" topics addressed",tarts:(n,z,y)=>n+" articles, "+z+" of them on subjects Constitute does not code (transport, energy, agriculture …)"+(y?"; the added vocabularies place "+y+" of those":""),
   xcap:"Policy fields",xcapsub:n=>"The policy field each article governs, from the 213 topics of the Comparative Agendas Project: what the state does, not how its organs work. "+n+" articles have one. Only the fields that appear are listed; a constitution need not cover every field.",
   xps:"Power-sharing",xpssub:"Rules that share power among groups, parties and regions, from two datasets (Juon; Strøm and colleagues): vetoes, quotas, rotation of offices, supermajorities, elected regional and local government, the military's place. A rule that is absent is often a choice, not a gap.",
   xnone:"None of these items appears in this document.",vsrc:"Source",
   xlv:"Who holds each policy field",xlvsub:"For each article that assigns a policy field, the level of government that holds it, read from the article's text. A field appears under more than one level when articles divide it. Rights and aims carry no level.",
   xrai:"Regional authority",xraisub:u=>"How much authority the regions would hold, on the ten dimensions of the Regional Authority Index, scored for "+u+". Self-rule is authority over the region itself; shared rule is a say over the country as a whole. The index compares countries as they work; this is our reading of a draft's text.",
   xraitot:(a,b,c)=>a+" of 30 · self-rule "+b+" of 18 · shared rule "+c+" of 12",xraiscale:"The scale",
   xraicredit:"Scales: Regional Authority Index v.3 (Hooghe, Marks, Schakel and colleagues), paraphrased from its codebook. Scores: ours.",
   xlang:"Language",xlangsub:"Language policy, which the other vocabularies barely touch: which languages are official and who decides, and whether they can be used in courts, offices, schools, media and economic life. Our own list of 27 items, built on the European Charter for Regional or Minority Languages and the Framework Convention for the Protection of National Minorities. An item that is absent may be a choice, or left to ordinary law.",
   tnote:"Observation",tfind:"Gaps worth noting",tgroups:"By subject",tpresent:"Addressed",tabsent:"Not addressed",
   tart:"Articles",tpre:"Preamble",tdoc:"in the document as a whole",
   tunrev:"Not yet reviewed: the tags, gaps and observation come from one reading of the text by Claude in a working session; no person has checked them yet.",
   mlink:"How this works, and the full vocabulary →",mback:"← Back to the document",
   mshort:"How the text is read, how articles are tagged, what “not addressed” means, and the limits: on the method page.",
   mp:[["What this measures",["This section shows which topics a constitution or draft provides for, and which it says nothing about. It is not a score. The number of topics addressed says what a text deals with, not whether it is better."]],
     ["The vocabulary",["We did not make the yardstick. It is the topic vocabulary of Constitute, which the Comparative Constitutions Project uses to code the constitutions of the world: 334 topics, from the right to life to the removal of judges. Each topic has a definition and a coding question, the question a coder asks of every constitution.",
       "Three topics come from the project's later vocabulary and are not yet in Constitute's: democracy, rule of law and social security. They count with the 334, so the total is 337.",
       "For readability we placed every topic under one of 30 subject groups. The grouping is ours, not Constitute's.",
       "Constitute has no Persian. The Persian names and definitions are ours and still drafts; each unreviewed Persian name is marked, and the English name and definition are always beside it."]],
     ["The added vocabularies",["Constitute was built to compare national constitutions in force. Iranian drafts, the federal ones above all, also say who runs schools, roads and energy, and how power is shared among peoples and regions. Two more vocabularies cover this, and three additions of our own follow below. Each has its own panel and is not counted in the coverage figure.",
       "Policy fields: the 213 topics of the Comparative Agendas Project, which codes what governments deal with, from health to transport. An article gets a field when it governs that field, at any level of government. CAP's civil-rights topics are not used, since Constitute codes rights in more detail.",
       "Power-sharing: the 75 rules of Andreas Juon's Constitutional Power-Sharing Dataset and 18 rules from the Inclusion, Dispersion and Constraint dataset of Kaare Strøm and colleagues: vetoes and quotas for groups, rotation of offices, supermajorities, elected regional and local government, the tax and police powers of regions, and the military's place in politics. Only rules a constitution can lay down are used; those that record what a government actually did are left out.",
       "We took these vocabularies from the Sartori repository (sartori.network), which gathers coding vocabularies for political institutions. The Persian names are ours and, like Constitute's, still drafts."]],
     ["Our own additions",["Two questions every Iranian draft must answer are covered by none of these: language, and who holds which power in a federation. For them we added three things of our own.",
       "Levels of government: for each policy field an article assigns, the level that holds it: national; national law carried out by the regions; national principles with regional detail; shared; regional; local. Together they show how a draft divides the state's work.",
       "Language: 27 items on the status and use of languages. They follow the areas of life in Part III of the European Charter for Regional or Minority Languages (education, courts, administration, media, culture, economic life, contacts across borders) and the Framework Convention for the Protection of National Minorities (names, signs, schooling), plus questions of status: which languages are official, at which level, and who decides.",
       "Regional authority: the ten dimensions of the Regional Authority Index of Liesbet Hooghe, Gary Marks, Arjan Schakel and colleagues, which measures the authority of regional governments in 95 countries. We score a draft's regions on the same scales and cite the articles each score rests on. The index scores countries as they work; we score what a draft's text says.",
       "All three are ours and still drafts. Once reviewed, they can be offered to the Sartori repository with the Persian names."]],
     ["The text",["Tags are put on a text read from the source PDF and then proofread page by page against the image of the same page. The document's own misprints stay as printed; only reading errors are corrected.",
       "The text is split into articles with the numbers the document gives them. Every article links to its page in the PDF, so anyone can check it against the original."]],
     ["Tagging",["Each article is read on its own and in full, and gets the topics it actually provides for: it grants a right, sets up a body, assigns a power or forbids something. Being mentioned is not enough.",
       "An article can carry several topics and a topic can appear in several articles. Some topics belong to the document as a whole, such as having a preamble.",
       "Some articles get no Constitute topic, because they deal with subjects it does not code (transport, energy, agriculture). Most of them get a policy field instead; each document's page gives both numbers.",
       "The tags were made by Claude (Anthropic). A tag that names an article missing from the document is rejected. Each tag is stored with a fingerprint of its article's text: if the text is corrected later, the tag is known to be stale and is redone."]],
     ["What “addressed” and “not addressed” mean",["“Addressed” means at least one article provides for the topic. It says nothing about how: an article that grants a right and one that restricts it both fall under the same topic.",
       "“Not addressed” means no article provides for it. Some absences are choices: a draft that separates religion and state has no official religion, and a parliamentary system has no directly elected president. Some topics exclude each other, so no constitution has all 337.",
       "With power-sharing rules, absence is usually a design choice: a draft without ethnic quotas has chosen not to have them."]],
     ["Gaps and observations",["The list of gaps worth noting is our reading, not a verdict. From the topics not addressed we picked those that matter for a transition to democracy in Iran, such as an independent oversight body, an electoral commission or dealing with past crimes. Each gap links to its topics and, where relevant, to the articles concerned, so you can judge for yourself.",
       "An observation is a remark on the document as a whole, such as a model it follows."]],
     ["Review",["Until someone has checked a document's tags, gaps and observation, it is marked “not yet reviewed”. Review means checking the tags against the text article by article; the reviewer and the date are then recorded.",
       "This section is experimental. Documents are added one at a time: the federal drafts first, then the rest."]],
     ["Limits",["The model can miss a topic or add a wrong tag; that is what review is for.",
       "Constitute's vocabulary was built for national constitutions in force. The added vocabularies fill part of what it misses, not all of it.",
       "The Comparative Agendas Project's vocabulary was built to code what governments and parliaments deal with, not constitutions. An article that assigns a field to the federal or the state level is coded by the field; the level that holds it is recorded beside it.",
       "The regional authority score reads only the text. Where a draft is silent, as on borrowing, the score rests on little, and the note says so.",
       "The number of topics also depends on length: a longer text usually covers more topics."]],
     ["Source and licence",["Topic vocabulary: Constitute (constituteproject.org), Comparative Constitutions Project, under CC BY-NC 3.0. Constitute's texts of national constitutions are not used.",
       "The three added CCP topics and the policy fields come from the Sartori repository (CC BY-NC-SA 4.0); the policy fields are the Comparative Agendas Project's master codebook (CC BY-NC-SA 4.0). The power-sharing rules come from Juon's dataset and from Strøm and colleagues' (both CC0). Our Persian names for them are shared on the same ShareAlike terms.",
       "The language items cite the articles of the Council of Europe's European Charter for Regional or Minority Languages and Framework Convention for the Protection of National Minorities they are built on; the wording is ours. The Regional Authority Index's scales are paraphrased from its codebook, with attribution (its data are published under CC BY 4.0)."]]],
   tcredit:"Topic vocabulary: Constitute, Comparative Constitutions Project, CC BY-NC 3.0. Added vocabularies via the Sartori repository: CCP and the Comparative Agendas Project (CC BY-NC-SA 4.0); Juon; Strøm and colleagues (CC0). Regional Authority Index: Hooghe, Marks, Schakel and colleagues. Language items and levels: ours.",
   vtitle:"The vocabulary",vsub:n=>"All "+n+" topics, by vocabulary and subject: each with its definition and, for Constitute's, the question its coders ask of every constitution. Under each topic: the documents published here that provide for it.",
   vq:"Coding question",vdocs:"Provided for in",vnone:"No published document yet.",vdraft:"Persian name: draft",
   prog:(a,b)=>a+" of "+b+" constitutions and drafts done so far. The others are queued and follow one by one; the federal drafts come next.",queued:"queued",
   title:"Constitutions Atlas",
   lede:"Every known draft constitution for Iran, from the 1906 Fundamental Law to the transitional charters of 2020 — <em>extracted, split into articles, and made comparable</em>. Texts appear exactly as their authors wrote them; nothing here is ranked or endorsed. Alongside them, and kept apart: the bylaws, programmes and charters of organisations in Atlas, and two treatises, each compared only with its own kind.",
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
   date:"Date",len:"Length",rev:n=>"revision "+n,size:(a,p)=>a+" articles · "+p+" pages",
   kinds:{constitution:"Constitution",constitution_proposal:"Draft constitution",bylaws:"Bylaws",program:"Programme",
     charter:"Charter",ideology:"Statement of principles",treatise:"Treatise"},
   dstat:{adopted:"adopted",draft:"draft",in_force:"in force"},
   tags:{republic:"republic",secular:"secular",monarchy:"monarchy",constitutional:"constitutional",transitional:"transitional",
     federal:"federal",democratic:"democratic",islamic:"Islamic",socialist:"socialist","rights-based":"rights-based",
     "rule-of-law":"rule of law",foundational:"foundational",rights:"rights","clerical-rule":"clerical rule",
     "velayat-e-faqih":"velayat-e faqih","council-based":"council-based",parliamentary:"parliamentary",
     "opposition-in-exile":"opposition in exile",nationalist:"nationalist",unitary:"unitary","ethnic-federalism":"ethnic federalism",
     pluralist:"pluralist",revolutionary:"revolutionary",reformist:"reformist"},
   groups:{A:"constitutions and draft constitutions",B:"bylaws",C:"charters, programmes and ideological statements",D:"treatises"},
   gtitle:{A:"Constitutions and draft constitutions",B:"Bylaws of organisations",C:"Programmes, charters and statements of principle",D:"Treatises"},
   gnote:{B:"The internal rules of parties and organisations listed in Atlas. They govern an organisation, not a state, so they are compared only with each other.",
     C:"Political programmes, charters and statements of principle of organisations. Compared only with each other.",
     D:"Treatises on government. Compared only with each other."},
   show:"Show",kindf:"Type",
   note:"Article counts come from automated parsing of the source PDFs and may miss or over-split articles in poorly typeset documents. Every article links to its page in the original PDF. Topic labels are keyword-based and shown for navigation, not as legal classification."},
 fa:{corpus:"پیکره",map:"شباهت",compare:"مقایسه",editions:"ویرایش‌ها",search:"جست‌وجو",rights:"حقوق بشر",
   ed:"ویرایش به ویرایش",edsub:"برخی پیش‌نویس‌ها بازنگری و دوباره منتشر شده‌اند. دو ویرایش از یک پیش‌نویس را برگزینید: اصول دو متن با هم جفت می‌شوند و در هر اصل تغییرکرده، آن‌چه حذف شده سرخ و آن‌چه افزوده شده سبز است.",
   edpick:"پیش‌نویس",edfrom:"ویرایش پیشین",edto:"ویرایش پسین",
   edsum:(m,s,a,d)=>[m+" اصل در هر دو، "+s+" تا بی‌تغییر",a+" افزوده",d+" حذف‌شده"].map(x=>x.replace(/\d+/g,n=>Number(n).toLocaleString("fa-IR"))).join(" · "),
   edcount:n=>Number(n).toLocaleString("fa-IR")+" ویرایش",edchanged:"فقط تغییرها",edall:"همه‌ی اصول",edsame:"بی‌تغییر",edadd:"افزوده",eddrop:"حذف‌شده",
   ednone:"این دو ویرایش تفاوتی ندارند.",
   ednote:"اصول بر پایه‌ی واژه‌هایشان و به ترتیب جفت می‌شوند، پس اصلی که شماره‌اش عوض شده باز هم با همتایش جفت می‌شود. تفاوت در املا، رقم و فاصله هم تغییر به شمار می‌آید، و آن‌جا که متن از روی تصویر صفحه خوانده شده، یک تفاوت ممکن است خطای خوانش باشد: صفحه‌ی PDF هر اصل پیوند داده شده است.",
   rtitle:"سنجش با حقوق بین‌الملل بشر",
   rsub:"هر سند درباره‌ی ۳۱ حق برگرفته از اعلامیه‌ی جهانی حقوق بشر، دو میثاق بین‌المللی و کنوانسیون‌های اصلی سازمان ملل خوانده می‌شود. هر حکم به اصول خود سند و به بندهای معاهده‌ای که بر آن استوار است استناد می‌کند.",
   rnone:"هنوز هیچ سنجشی بازبینی و منتشر نشده است.",
   rpick:"سند",rreviewed:(who,d)=>"بازبینی‌شده"+(who?" به دست "+who:"")+(d?" در "+d:""),
   rpreview:"پیش‌نمایش: هنوز بازبینی نشده. برای انتشار نیست.",
   rsrc:"منبع متن",rpdf:"فایل PDF",rpage:n=>"صفحه‌ی "+Number(n).toLocaleString("fa-IR",{useGrouping:false})+" در فایل PDF",rscope:n=>n+" اصل خوانده شد؛ در اصول اصلاح‌شده، متن معتبر کنونی.",
   runrev:"هنوز بازبینی نشده: این حکم‌ها حاصل خوانش خودکار و وارسی خودکار استنادهاست و هنوز کسی آن‌ها را تأیید نکرده است.",
   rarts:"اصول استنادشده",rbench:"بندهای متن بالادستی",rquote:"عبارت تعیین‌کننده",rnoarts:"هیچ اصلی به این حق نپرداخته است.",
   ren:"متن انگلیسی؛ ترجمه‌ی فارسی در دست تهیه است.",rall:"همه",
   v:{guaranteed:"تضمین‌شده",restricted_clawback:"مشروط‌شده",contradicted:"نقض‌شده",silent:"مسکوت"},
   vd:{guaranteed:"سند این حق را صریحاً و در سطحی که معاهده‌ها می‌خواهند حمایت می‌کند.",
       restricted_clawback:"سند نام حق را می‌آورد و سپس آن را پس می‌گیرد: با قیدی باز (مانند «موازین اسلامی» یا «طبق قانون»)، با محدود کردن آن به گروهی از مردم، یا با محدودیتی فراتر از آنچه معاهده‌ها روا می‌دارند.",
       contradicted:"سند برخلاف این حق است؛ برای نمونه تبعیض برقرار می‌کند، مجازاتی ممنوع را روا می‌دارد یا مقامی را بالاتر از حق می‌نشاند.",
       silent:"سند به این حق نپرداخته است. سکوت خود یک یافته است."},
   mtitle:"روش کار",
   m:["متن بالادستی حقوق بین‌الملل بشر است که عین متن آن با شناسه‌ای پایدار برای هر بند نگهداری می‌شود (مانند ICCPR.19.3). هیچ قانون اساسی ملی معیار نیست؛ همه‌ی اسناد تنها موضوع سنجش‌اند.",
      "Claude (ساخت Anthropic) سند را اصل به اصل می‌خواند و برای هر حق یک حکم می‌دهد، با استناد به اصول سند و بندهای معاهده و نقل عبارت تعیین‌کننده.",
      "همه‌ی استنادها خودکار وارسی می‌شوند: حکمی که به اصل یا بندی ناموجود استناد کند رد می‌شود و نقل‌قولی که در سند یافت نشود علامت می‌خورد.",
      "سپس یک انسان حکم‌ها را بازبینی می‌کند. تا آن زمان، صفحه‌ی سند اعلام می‌کند که هنوز بازبینی نشده است.",
      "متن سند از فایل PDF آن گرفته و با تصویر صفحه‌ها مقابله شده است؛ فهرست اصول دقیقاً همان است که خوانده شده. در اصول اصلاح‌شده تنها متن معتبر کنونی سنجیده می‌شود.",
      "این یک خوانش تحلیلی است، نه مشاوره‌ی حقوقی یا حکم قضایی."],
   mmodel:(m,b)=>"مدل: "+m+" · نسخه‌ی متن بالادستی "+b,
   mby:"خوانده‌شده در یک جلسه‌ی کاری Claude Code، نه از راه خط لوله‌ی ارزیابی: با همان راهنمای امتیازدهی، همان متن بالادستی، همان اصل‌ها و همان وارسی استنادها.",
   topics:"موضوع‌ها",
   ttitle:"سند به چه می‌پردازد و چه را نمی‌گوید",
   tsub:"هر اصل با موضوع‌های واژگان Constitute (پروژه‌ی تطبیقی قانون‌های اساسی) برچسب خورده است: ۳۳۴ موضوعی که قانون‌های اساسی در سراسر جهان به آن‌ها می‌پردازند، از حق زندگی تا برکناری قاضیان، و سه موضوع از واژگان تازه‌ترِ همین پروژه: دموکراسی، حاکمیت قانون و تامین اجتماعی. موضوع‌هایی که هیچ اصلی به آن‌ها نپرداخته هم فهرست شده‌اند. پس از آن نگاه‌های دیگر می‌آید: حوزه‌ی سیاست‌گذاری‌ای که هر اصل تنظیم می‌کند (پروژه‌ی دستورکارهای تطبیقی) و این‌که کدام سطح حکومت آن را در دست دارد؛ مناطق چه اندازه اختیار خواهند داشت (شاخص اقتدار منطقه‌ای)؛ قاعده‌هایی که برای تقسیم قدرت می‌گذارد؛ و سیاست زبانی‌اش.",
   tnone:"هنوز هیچ سندی برچسب نخورده و منتشر نشده است.",
   tcount:(a,b)=>num2(a)+" از "+num2(b)+" موضوع",tarts:(n,z,y)=>num2(n)+" اصل؛ "+num2(z)+" تا درباره‌ی موضوع‌هایی که واژگان Constitute ندارد (حمل‌ونقل، انرژی، کشاورزی …)"+(y?"؛ واژگان افزوده "+num2(y)+" تا از آن‌ها را جا داده‌اند":""),
   xcap:"حوزه‌های سیاست‌گذاری",xcapsub:n=>"حوزه‌ی سیاست‌گذاری‌ای که هر اصل تنظیم می‌کند، از میان ۲۱۳ موضوع پروژه‌ی دستورکارهای تطبیقی: کاری که دولت می‌کند، نه این‌که نهادهایش چطور کار می‌کنند. "+num2(n)+" اصل حوزه‌ای دارند. تنها حوزه‌هایی که آمده‌اند فهرست شده‌اند؛ قانون اساسی لازم نیست به همه‌ی حوزه‌ها بپردازد.",
   xps:"تقسیم قدرت",xpssub:"قاعده‌هایی که قدرت را میان گروه‌ها، حزب‌ها و مناطق تقسیم می‌کنند، از دو مجموعه‌داده (یوئن؛ استروم و همکاران): حق وتو، سهمیه، گردش منصب‌ها، اکثریت ویژه، حکومت منتخب منطقه‌ای و محلی، و جای ارتش. نبودن یک قاعده اغلب انتخاب است، نه کاستی.",
   xnone:"هیچ‌یک از این‌ها در این سند نیامده است.",vsrc:"منبع",
   xlv:"هر حوزه با کیست",xlvsub:"برای هر اصلی که حوزه‌ای از سیاست‌گذاری را واگذار می‌کند، سطحی از حکومت که آن را در دست دارد، از روی متن همان اصل. حوزه‌ای که اصل‌ها میان چند سطح تقسیمش کرده‌اند زیر هر کدام می‌آید. حق‌ها و هدف‌ها سطح ندارند.",
   xrai:"اقتدار منطقه‌ای",xraisub:u=>"مناطق چه اندازه اختیار خواهند داشت، بر پایه‌ی ده بُعد شاخص اقتدار منطقه‌ای (Regional Authority Index)، برای "+u+". خودگردانی اختیار منطقه بر خود است؛ حکمرانی مشترک سهم آن در اداره‌ی کل کشور. این شاخص کشورها را آن‌طور که کار می‌کنند می‌سنجد؛ این‌جا خوانش ما از متن یک پیش‌نویس است.",
   xraitot:(a,b,c)=>num2(a)+" از ۳۰ · خودگردانی "+num2(b)+" از ۱۸ · حکمرانی مشترک "+num2(c)+" از ۱۲",xraiscale:"مقیاس",
   xraicredit:"مقیاس‌ها: شاخص اقتدار منطقه‌ای، نسخه‌ی ۳ (هوخه، مارکس، شاکل و همکاران)، بازنویسی‌شده از دفترچه‌ی کدگذاری آن. نمره‌ها: از ما.",
   xlang:"زبان",xlangsub:"سیاست زبانی، که واژگان‌های دیگر تقریبن به آن نمی‌پردازند: کدام زبان‌ها رسمی‌اند و چه کسی تصمیم می‌گیرد، و آیا می‌شود آن‌ها را در دادگاه، اداره، مدرسه، رسانه و زندگی اقتصادی به کار برد. فهرستی ۲۷ موردی از خود ما، بر پایه‌ی منشور اروپایی زبان‌های منطقه‌ای یا اقلیت و کنوانسیون چارچوب حمایت از اقلیت‌های ملی. نبودن یک مورد ممکن است انتخاب باشد، یا به قانون عادی سپرده شده باشد.",
   tnote:"مشاهده",tfind:"کاستی‌های درخور توجه",tgroups:"بر پایه‌ی موضوع",tpresent:"آمده",tabsent:"نیامده",
   tart:"اصول",tpre:"مقدمه",tdoc:"در کل سند",
   tunrev:"هنوز بازبینی نشده: برچسب‌ها، کاستی‌ها و مشاهده حاصل یک بار خواندن متن به دست Claude در یک جلسه‌ی کاری‌اند و هنوز کسی آن‌ها را وارسی نکرده است.",
   mlink:"روش کار و واژگان کامل ←",mback:"→ بازگشت به سند",
   mshort:"متن چطور خوانده می‌شود، برچسب‌ها چطور زده می‌شوند، «نیامده» یعنی چه، و محدودیت‌ها: در صفحه‌ی روش کار.",
   mp:[["این بخش چه می‌سنجد",["این بخش نشان می‌دهد هر قانون اساسی یا پیش‌نویس درباره‌ی کدام موضوع‌ها حکم می‌کند و درباره‌ی کدام‌ها چیزی نمی‌گوید. نمره نیست. شمار موضوع‌های آمده نشان می‌دهد متن به چه چیزهایی پرداخته، نه این‌که بهتر است."]],
     ["واژگان",["معیار را ما نساخته‌ایم. واژگان موضوع‌های Constitute است، که پروژه‌ی تطبیقی قانون‌های اساسی (Comparative Constitutions Project) با آن قانون‌های اساسی کشورهای جهان را کدگذاری می‌کند: ۳۳۴ موضوع، از حق زندگی تا برکناری قاضیان. هر موضوع یک تعریف دارد و یک پرسش کدگذاری، یعنی پرسشی که کدگذار از هر قانون اساسی می‌پرسد.",
       "سه موضوع از واژگان تازه‌ترِ همین پروژه آمده است که در واژگان Constitute هنوز نیست: دموکراسی، حاکمیت قانون و تامین اجتماعی. این سه با آن ۳۳۴ شمرده می‌شوند، پس جمع ۳۳۷ است.",
       "برای خواناتر شدن، هر موضوع را زیر یکی از ۳۰ گروه موضوعی گذاشته‌ایم. این گروه‌بندی از ماست، نه از Constitute.",
       "Constitute فارسی ندارد. نام‌ها و تعریف‌های فارسی را ما نوشته‌ایم و هنوز پیش‌نویس‌اند؛ هر نام فارسیِ بازبینی‌نشده علامت خورده و نام و تعریف انگلیسی همیشه کنارش هست."]],
     ["واژگان افزوده",["Constitute برای مقایسه‌ی قانون‌های اساسی جاری کشورها ساخته شده است. پیش‌نویس‌های ایرانی، به‌ویژه پیش‌نویس‌های فدرال، این را هم می‌گویند که مدرسه و راه و انرژی با کیست و قدرت میان مردمان و مناطق چطور تقسیم می‌شود. دو واژگان دیگر این‌ها را می‌پوشانند و سه افزوده‌ی خود ما در پی می‌آید. هر یک بخش خود را دارد و در شمار پوشش موضوع‌ها حساب نمی‌شود.",
       "حوزه‌های سیاست‌گذاری: ۲۱۳ موضوع پروژه‌ی دستورکارهای تطبیقی (Comparative Agendas Project)، که کار دولت‌ها را، از سلامت تا حمل‌ونقل، کدگذاری می‌کند. اصلی که حوزه‌ای را تنظیم کند، در هر سطحی از حکومت، آن حوزه را می‌گیرد. موضوع‌های حقوق مدنی این واژگان به کار نرفته‌اند، چون Constitute حقوق را دقیق‌تر کدگذاری می‌کند.",
       "تقسیم قدرت: ۷۵ قاعده‌ی مجموعه‌داده‌ی تقسیم قدرت در قانون اساسی (Constitutional Power-Sharing Dataset) از آندریاس یوئن (Andreas Juon)، و ۱۸ قاعده از مجموعه‌داده‌ی «فراگیری، پراکندگی و مهار» (Inclusion, Dispersion, and Constraint) از کوره استروم (Kaare Strøm) و همکاران: حق وتو و سهمیه برای گروه‌ها، گردش منصب‌ها، اکثریت ویژه، حکومت منتخب منطقه‌ای و محلی، اختیار مالیاتی و انتظامی مناطق، و جای ارتش در سیاست. تنها قاعده‌هایی به کار رفته‌اند که قانون اساسی می‌تواند بگذارد؛ آن‌هایی که کار واقعی یک دولت را ثبت می‌کنند کنار گذاشته شده‌اند.",
       "این واژگان‌ها را از مخزن Sartori (sartori.network) گرفته‌ایم، که واژگان‌های کدگذاری نهادهای سیاسی را گرد می‌آورد. نام‌های فارسی از ماست و، مانند نام‌های Constitute، هنوز پیش‌نویس‌اند."]],
     ["افزوده‌های خود ما",["دو پرسش که هر پیش‌نویس ایرانی باید پاسخ دهد در هیچ‌یک از این واژگان‌ها نیست: زبان، و این‌که در فدراسیون کدام اختیار با کیست. برای این دو، سه چیز از خود افزوده‌ایم.",
       "سطح‌های حکومت: برای هر حوزه‌ی سیاست‌گذاری که اصلی واگذار می‌کند، سطحی که آن را در دست دارد: ملی؛ قانون ملی با اجرای منطقه‌ای؛ اصول ملی با جزئیات منطقه‌ای؛ مشترک؛ منطقه‌ای؛ محلی. کنار هم، نشان می‌دهند یک پیش‌نویس کار دولت را چطور تقسیم می‌کند.",
       "زبان: ۲۷ مورد درباره‌ی جایگاه و کاربرد زبان‌ها. از عرصه‌های زندگی در بخش سوم منشور اروپایی زبان‌های منطقه‌ای یا اقلیت (European Charter for Regional or Minority Languages) پیروی می‌کنند (آموزش، دادگاه، اداره، رسانه، فرهنگ، زندگی اقتصادی، پیوند فرامرزی) و از کنوانسیون چارچوب حمایت از اقلیت‌های ملی (Framework Convention for the Protection of National Minorities) (نام‌ها، تابلوها، آموزش)، به‌اضافه‌ی پرسش‌های جایگاه: کدام زبان‌ها رسمی‌اند، در کدام سطح، و چه کسی تصمیم می‌گیرد.",
       "اقتدار منطقه‌ای: ده بُعد شاخص اقتدار منطقه‌ای (Regional Authority Index) از لیسبت هوخه، گری مارکس، آریان شاکل و همکاران، که اختیار حکومت‌های منطقه‌ای را در ۹۵ کشور می‌سنجد. ما مناطق یک پیش‌نویس را با همان مقیاس‌ها می‌سنجیم و اصل‌هایی را که هر نمره بر آن‌ها تکیه دارد می‌آوریم. شاخص کشورها را آن‌طور که کار می‌کنند می‌سنجد؛ ما آن‌چه متن پیش‌نویس می‌گوید.",
       "هر سه از ماست و هنوز پیش‌نویس. پس از بازبینی می‌توان آن‌ها را همراه نام‌های فارسی به مخزن Sartori پیشنهاد داد."]],
     ["متن",["برچسب‌ها روی متنی زده می‌شوند که از PDF منبع خوانده و بعد صفحه‌به‌صفحه با تصویر همان صفحه مقابله شده است. غلط‌های چاپی خود سند همان‌طور که چاپ شده‌اند می‌مانند؛ فقط خطای خواندن تصحیح می‌شود.",
       "متن به اصل‌ها یا ماده‌ها تقسیم می‌شود، با همان شماره‌ای که در سند آمده. کنار هر اصل لینک صفحه‌ی PDF هست تا هر کس بتواند آن را با اصل سند تطبیق دهد."]],
     ["برچسب‌زدن",["هر اصل جداگانه و کامل خوانده می‌شود و موضوع‌هایی را می‌گیرد که واقعن درباره‌شان حکم می‌کند: حقی می‌دهد، نهادی می‌سازد، اختیاری تعیین می‌کند یا چیزی را منع می‌کند. آمدن نام یک موضوع کافی نیست.",
       "یک اصل می‌تواند چند موضوع داشته باشد و یک موضوع در چند اصل بیاید. برخی موضوع‌ها به کل سند تعلق دارند، مثل داشتن مقدمه.",
       "برخی اصل‌ها هیچ موضوعی از Constitute نمی‌گیرند، چون درباره‌ی چیزی‌اند که آن واژگان کدگذاری نمی‌کند (حمل‌ونقل، انرژی، کشاورزی). بیش‌ترِ آن‌ها در عوض حوزه‌ی سیاست‌گذاری می‌گیرند؛ هر دو شمار در صفحه‌ی هر سند آمده است.",
       "برچسب‌ها را Claude (ساخت Anthropic) زده است. برچسبی که به اصلی ناموجود اشاره کند رد می‌شود. هر برچسب همراه با اثر انگشت متن اصلش ذخیره می‌شود: اگر متن بعدن تصحیح شود، برچسب کهنه شناخته می‌شود و دوباره زده می‌شود."]],
     ["«آمده» و «نیامده» یعنی چه",["«آمده» یعنی دست‌کم یک اصل درباره‌ی آن موضوع حکم می‌کند. درباره‌ی چگونگی آن چیزی نمی‌گوید: اصلی که حقی را می‌دهد و اصلی که همان حق را محدود می‌کند هر دو زیر یک موضوع می‌آیند.",
       "«نیامده» یعنی هیچ اصلی درباره‌ی آن حکم نمی‌کند. برخی نبودن‌ها انتخاب‌اند: پیش‌نویسی که دین و دولت را جدا می‌کند دین رسمی ندارد، و نظامی پارلمانی رئیس‌جمهورِ منتخب مستقیم مردم ندارد. برخی موضوع‌ها با هم جمع نمی‌شوند، پس هیچ قانون اساسی همه‌ی ۳۳۷ موضوع را ندارد.",
       "در تقسیم قدرت، نبودن یک قاعده معمولن انتخاب طراحی است: پیش‌نویسی که سهمیه‌ی قومی ندارد خواسته است که نداشته باشد."]],
     ["کاستی‌ها و مشاهده‌ها",["فهرست «کاستی‌های درخور توجه» خوانش ماست، نه حکم. از میان موضوع‌های نیامده آن‌هایی را برگزیده‌ایم که برای گذار به دموکراسی در ایران مهم‌اند، مثل نهاد ناظر مستقل، کمیسیون انتخابات یا رسیدگی به جنایات گذشته. هر کاستی به موضوع‌هایش و، هر جا لازم باشد، به اصل‌های مربوط لینک دارد تا خودتان بسنجید.",
       "«مشاهده» نکته‌ای درباره‌ی کل سند است، مثلن الگویی که از آن پیروی می‌کند."]],
     ["بازبینی",["تا وقتی کسی برچسب‌ها، کاستی‌ها و مشاهده‌ی یک سند را وارسی نکرده، آن سند علامت «هنوز بازبینی نشده» دارد. بازبینی یعنی تطبیق برچسب‌ها با متن، اصل به اصل؛ پس از آن نام بازبین و تاریخ ثبت می‌شود.",
       "این بخش آزمایشی است. سندها یکی‌یکی اضافه می‌شوند: اول پیش‌نویس‌های فدرال، بعد بقیه."]],
     ["محدودیت‌ها",["مدل ممکن است موضوعی را جا بیندازد یا برچسبی نادرست بزند؛ بازبینی برای همین است.",
       "واژگان Constitute برای قانون‌های اساسی جاری کشورها ساخته شده است. واژگان افزوده بخشی از آن‌چه را که در آن نیست پر می‌کنند، نه همه‌اش را.",
       "واژگان دستورکارهای تطبیقی برای کدگذاری کار دولت‌ها و مجلس‌ها ساخته شده است، نه قانون‌های اساسی. اصلی که حوزه‌ای را به دولت فدرال یا به ایالت می‌سپارد با همان حوزه کد می‌خورد؛ سطحی که آن را در دست دارد کنارش ثبت می‌شود.",
       "نمره‌ی اقتدار منطقه‌ای تنها متن را می‌خواند. جایی که پیش‌نویس ساکت است، مثلن درباره‌ی استقراض، نمره پشتوانه‌ی کمی دارد و یادداشتش این را می‌گوید.",
       "شمار موضوع‌ها به طول متن هم بستگی دارد: متن بلندتر معمولن موضوع‌های بیش‌تری را می‌پوشاند."]],
     ["منبع و پروانه",["واژگان موضوع‌ها: Constitute (constituteproject.org)، پروژه‌ی تطبیقی قانون‌های اساسی، با پروانه‌ی CC BY-NC 3.0. از متن قانون‌های اساسی کشورها در Constitute استفاده نشده است.",
       "سه موضوع افزوده‌ی CCP و حوزه‌های سیاست‌گذاری از مخزن Sartori آمده‌اند (CC BY-NC-SA 4.0)؛ حوزه‌های سیاست‌گذاری همان کدنامه‌ی اصلی پروژه‌ی دستورکارهای تطبیقی است (CC BY-NC-SA 4.0). قاعده‌های تقسیم قدرت از مجموعه‌داده‌ی یوئن و مجموعه‌داده‌ی استروم و همکاران آمده‌اند (هر دو CC0). نام‌های فارسی ما برای این‌ها با همان شرط «اشتراک یکسان» (ShareAlike) در دسترس است.",
       "موردهای زبان به ماده‌هایی از منشور اروپایی زبان‌های منطقه‌ای یا اقلیت و کنوانسیون چارچوب حمایت از اقلیت‌های ملی (هر دو از شورای اروپا) ارجاع می‌دهند که بر آن‌ها بنا شده‌اند؛ عبارت‌ها از ماست. مقیاس‌های شاخص اقتدار منطقه‌ای از دفترچه‌ی کدگذاری آن بازنویسی شده‌اند، با ذکر منبع (داده‌هایش با پروانه‌ی CC BY 4.0 منتشر شده‌اند)."]]],
   tcredit:"واژگان موضوع‌ها: Constitute، پروژه‌ی تطبیقی قانون‌های اساسی، CC BY-NC 3.0. واژگان افزوده از مخزن Sartori: CCP و پروژه‌ی دستورکارهای تطبیقی (CC BY-NC-SA 4.0)؛ یوئن؛ استروم و همکاران (CC0). شاخص اقتدار منطقه‌ای: هوخه، مارکس، شاکل و همکاران. موردهای زبان و سطح‌ها: از ما.",
   vtitle:"واژگان",vsub:n=>"همه‌ی "+num2(n)+" موضوع، بر پایه‌ی واژگان و موضوع اصلی: هر یک با تعریفش و، برای موضوع‌های Constitute، پرسشی که کدگذاران آن از هر قانون اساسی می‌پرسند. زیر هر موضوع: سندهای منتشرشده در این‌جا که درباره‌ی آن حکم می‌کنند.",
   vq:"پرسش کدگذاری",vdocs:"آمده در",vnone:"هنوز در هیچ سند منتشرشده‌ای نیامده.",vdraft:"نام فارسی: پیش‌نویس",
   prog:(a,b)=>"تاکنون "+num2(a)+" سند از "+num2(b)+" قانون اساسی و پیش‌نویس بررسی شده است. بقیه در نوبت‌اند و یکی‌یکی می‌آیند؛ نوبت بعد با پیش‌نویس‌های فدرال است.",queued:"در نوبت",
   title:"اطلس اسناد بنیادین",
   lede:"همه‌ی پیش‌نویس‌های شناخته‌شده‌ی قانون اساسی برای ایران، از قانون اساسی مشروطه تا منشورهای دوران گذار — <em>استخراج‌شده، تفکیک‌شده به اصول، و قابل مقایسه</em>. متن‌ها همان‌گونه‌اند که نویسندگانشان نوشته‌اند؛ هیچ‌چیز در اینجا رتبه‌بندی یا تأیید نشده است. در کنار آن‌ها و جدا از آن‌ها: اساس‌نامه‌ها، برنامه‌ها و منشورهای سازمان‌های اطلس و دو رساله، که هر یک تنها با هم‌گونه‌های خود سنجیده می‌شوند.",
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
   arcount:n=>Number(n).toLocaleString("fa-IR")+" اصل",ocr:"نویسه‌خوانی",dup:"تکراری",partial:"ناقص",results:n=>Number(n).toLocaleString("fa-IR")+" نتیجه",
   more:"بیشتر",less:"کمتر",loadfail:"بارگذاری داده‌های پیکره ممکن نشد.",
   group:"تنها قابل مقایسه با",alone:"هنوز سند دیگری از این گونه در پیکره نیست.",
   date:"تاریخ",len:"حجم",rev:n=>"ویرایش "+Number(n).toLocaleString("fa-IR"),
   size:(a,p,u)=>Number(a).toLocaleString("fa-IR",{useGrouping:false})+" "+u+" · "+Number(p).toLocaleString("fa-IR",{useGrouping:false})+" صفحه",
   kinds:{constitution:"قانون اساسی",constitution_proposal:"پیش‌نویس قانون اساسی",bylaws:"اساس‌نامه",program:"برنامه",
     charter:"منشور",ideology:"مرام‌نامه",treatise:"رساله"},
   dstat:{adopted:"مصوب",draft:"پیش‌نویس",in_force:"در حال اجرا"},
   tags:{republic:"جمهوری",secular:"سکولار",monarchy:"پادشاهی",constitutional:"مشروطه",transitional:"دوران گذار",
     federal:"فدرال",democratic:"دموکراتیک",islamic:"اسلامی",socialist:"سوسیالیستی","rights-based":"حق‌بنیاد",
     "rule-of-law":"حاکمیت قانون",foundational:"بنیادین",rights:"حقوق","clerical-rule":"حکومت روحانیان",
     "velayat-e-faqih":"ولایت فقیه","council-based":"شورایی",parliamentary:"پارلمانی",
     "opposition-in-exile":"اپوزیسیون در تبعید",nationalist:"ملی‌گرا",unitary:"یکپارچه","ethnic-federalism":"فدرالیسم قومی",
     pluralist:"کثرت‌گرا",revolutionary:"انقلابی",reformist:"اصلاح‌طلب"},
   groups:{A:"قانون‌های اساسی و پیش‌نویس‌ها",B:"اساس‌نامه‌ها",C:"منشورها، برنامه‌ها و مرام‌نامه‌ها",D:"رساله‌ها"},
   gtitle:{A:"قانون‌های اساسی و پیش‌نویس‌ها",B:"اساس‌نامه‌های سازمان‌ها",C:"برنامه‌ها، منشورها و مرام‌نامه‌ها",D:"رساله‌ها"},
   gnote:{B:"قواعد درونی حزب‌ها و سازمان‌هایی که در اطلس آمده‌اند. این متن‌ها یک سازمان را اداره می‌کنند، نه یک کشور را؛ پس تنها با یکدیگر سنجیده می‌شوند.",
     C:"برنامه‌های سیاسی، منشورها و مرام‌نامه‌های سازمان‌ها. تنها با یکدیگر سنجیده می‌شوند.",
     D:"رساله‌هایی درباره‌ی حکومت. تنها با یکدیگر سنجیده می‌شوند."},
   show:"نمایش",kindf:"گونه",
   note:"شمار اصول از تجزیه‌ی خودکار فایل‌های اصلی به‌دست آمده و ممکن است در اسنادِ بدحروف‌چینی‌شده کم یا زیاد باشد. هر اصل به صفحه‌ی اصلی خود پیوند دارد. برچسب‌های موضوعی بر پایه‌ی کلیدواژه‌اند و برای گشت‌وگذار آمده‌اند، نه طبقه‌بندی حقوقی."}};

const BUCKET={in_force:0,historical:0,draft:1,transitional:2,program:2,treatise:2};
const BCOL=["var(--s1)","var(--s2)","var(--s3)"];
// Comparison groups (plan §6): bylaws are never compared with constitutions.
export const GROUP={constitution:"A",constitution_proposal:"A",bylaws:"B",
  charter:"C",program:"C",ideology:"C",treatise:"D"};
const VIEWS=["corpus","map","compare","editions","search","rights","topics"];

// articles.json keeps the splitter's pattern for the unit; this is the word to show
const UNITW={"شماره":["","Art."],"اص[سص]?ل":["اصل","Art."],"ماد[هدة]":["ماده","Art."],"بند":["بند","Clause"],"تبصره":["تبصره","Note"]};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e};

export function mount(root, opts={}){
  const embedded=!!opts.embedded, useHash=opts.hash!==false;
  const dataUrl=new URL(opts.dataUrl||"data/", new URL(".", import.meta.url));
  const pdfUrl=new URL(opts.pdfUrl||"pdf/", new URL(".", import.meta.url));
  let L=opts.lang||(embedded?"fa":"en"), CAT=[], AN=null, ARTS=[], view="corpus";
  let cmpA=null,cmpB=null,cmpT=null,q="",AUD=null,audDoc=null,audRight=null,audFilter=null;
  let TOP=null,topDoc=null,topLeaf=null,topPage=null,ED=null,edS=null,edA=null,edB=null,edAll=false,mapG="A",srchG=null;
  const t=k=>T[L][k];
  const title=d=>L==="fa"?d.fa:d.en;
  const author=d=>L==="fa"?(d.author_fa||""):(d.author_en||"");
  const group=d=>GROUP[d.kind]||"A";
  const num=n=>L==="fa"?Number(n).toLocaleString("fa-IR",{useGrouping:false}):String(n);
  const pg=n=>(L==="fa"?"ص. ":"p. ")+num(n);
  const unitw=u=>(UNITW[u]||[u,u])[L==="fa"?0:1];
  // an article's printed number: «۲-۸» where the document numbers by chapter, else its unit word and number
  const artn=a=>[unitw(a.unit),a.label?a.label.split("-").map(num).join("-"):num(a.n)].filter(Boolean).join(" ");
  // a link into the document's PDF, at a page when given; plain text when the PDF is not published
  const docOf=uid=>CAT.find(x=>x.uid===uid)||{};
  const pdfLink=(d,page,label)=>d.pdf
    ?`<a href="${esc(new URL(d.pdf,pdfUrl).href+(page?"#page="+page:""))}" target="_blank" rel="noopener">${esc(label)}</a>`
    :esc(label);
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
    if(k==="map"&&"ABCD".includes(v)&&v)mapG=v;
    if(k==="compare"){const [a,b,tp]=v.split(",");cmpA=a||null;cmpB=b||null;cmpT=tp||null;}
    if(k==="rights"){const [a,r]=v.split(",");audDoc=a||null;audRight=r||null;}
    if(k==="topics"){const [a,r]=v.split(",");topPage=a==="method"?a:null;if(!topPage){topDoc=a||null;topLeaf=r||null;}}
    if(k==="editions"){const [s,a,b]=v.split(",");edS=s||null;edA=a||null;edB=b||null;}
  }
  function writeHash(){
    if(!useHash)return;
    let h=view;
    if(view==="search"&&q)h+="="+q;
    if(view==="map"&&mapG!=="A")h+="="+mapG;
    if(view==="compare"&&cmpA)h+="="+[cmpA,cmpB,cmpT].filter(Boolean).join(",");
    if(view==="rights"&&audDoc)h+="="+[audDoc,audRight].filter(Boolean).join(",");
    if(view==="topics"&&(topPage||topDoc))h+="="+(topPage||[topDoc,topLeaf].filter(Boolean).join(","));
    if(view==="editions"&&edS)h+="="+[edS,edA,edB].filter(Boolean).join(",");
    if(decodeURIComponent(location.hash.slice(1))!==h)
      history.replaceState(history.state,"","#"+encodeURIComponent(h).replace(/%2C/g,",").replace(/%3D/g,"="));
  }
  const onHash=()=>{readHash();render();};
  if(useHash){readHash();addEventListener("hashchange",onHash);}

  /* ---------- boot ---------- */
  const get=n=>fetch(new URL(n,dataUrl)).then(r=>{if(!r.ok)throw new Error(n+": "+r.status);return r.json()});
  // audits.json and editions.json are optional: a module built before they existed still loads
  Promise.all([get("catalog.json"),get("analysis.json"),get("articles.json"),get("audits.json").catch(()=>null),
               get("editions.json").catch(()=>null),get("topics.json").catch(()=>null)])
    .then(([c,a,ar,au,ed,tp])=>{CAT=c;AN=a;ARTS=ar;AUD=au;ED=ed;TOP=tp;render()})
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
      if(k==="editions"&&!(ED&&Object.keys(ED).length))return;
      if(k==="topics"&&!(TOP&&TOP.docs.length))return;
      const b=el("button",null,esc(t(k)));b.setAttribute("role","tab");
      b.setAttribute("aria-selected",view===k);
      b.onclick=()=>{view=k;render()};tb.append(b);});
    VIEWS.forEach(k=>V(k).hidden=view!==k);
    if(!CAT.length)return;
    ({corpus:corpusView,map:mapView,compare:compareView,editions:editionsView,search:searchView,rights:rightsView,topics:topicsView})[view]();
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
    "ABCD".split("").forEach(g=>{
      const docs=CAT.filter(d=>group(d)===g);if(!docs.length)return;
      const sec=el("div","grp-sec");
      sec.append(el("h3",null,esc(t("gtitle")[g])+` <small>${esc(num(docs.length))}</small>`));
      if(t("gnote")[g])sec.append(el("div","sub",esc(t("gnote")[g])));
      const w=el("div","tbl-wrap");w.append(table(docs));sec.append(w);p2.append(sec);});
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
      `<text class="axis-t" x="${x(y)}" y="18" text-anchor="middle">${num(y)}</text>`);}
    [t("enacted"),t("proposed"),t("trans")].forEach((n,i)=>{
      const ty=26+i*LH+15;
      s.push(`<text class="lane-t" x="${L==="fa"?W-8:8}" y="${ty}" text-anchor="${L==="fa"?"end":"start"}">${esc(n)}</text>`);});
    const placed=[];
    CAT.forEach((d,i)=>{
      if(group(d)!=="A")return;   // the timeline is of constitutions; the other groups are listed below it
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
  function table(docs){
    const tb=el("table");
    tb.innerHTML=`<thead><tr><th>${t("year")}</th><th>${t("doc")}</th><th>${t("author")}</th>
      <th style="text-align:end">${t("arts")}</th><th style="text-align:end">${t("pages")}</th></tr></thead>`;
    const body=el("tbody");
    docs.forEach(d=>{
      const b=BUCKET[d.type]??2;
      const tr=el("tr");
      tr.innerHTML=`<td class="num">${L==="fa"?esc(String(d.era||d.year||"—").replace(/[0-9]/g,c=>"۰۱۲۳۴۵۶۷۸۹"[c])):(d.year||"—")}</td>
        <td class="ttl"><span class="dot" style="background:${BCOL[b]}"></span>${esc(title(d))}
          ${d.ocr?`<span class="flag">${t("ocr")}</span>`:""}${d.duplicate_of?`<span class="flag">${t("dup")}</span>`:""}${(d.confidence<0.8&&["draft","in_force","historical","transitional"].includes(d.type))?`<span class="flag quiet">${t("partial")}</span>`:""}
          <small>${pdfLink(d,0,d.source_pdf)}</small></td>
        <td>${esc(author(d))}</td><td class="num">${num(d.n_articles)}</td><td class="num">${num(d.n_pages)}</td>`;
      body.append(tr);});
    tb.append(body);return tb;
  }

  /* ================= MAP ================= */
  function mapView(){
    const v=V("map");v.innerHTML="";
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("gr"))),el("div","sub",esc(t("grsub"))));
    const gs=el("div","aud-tally");
    "ABCD".split("").filter(g=>CAT.some(d=>group(d)===g)).forEach(g=>{
      const b=el("button","vchip"+(mapG===g?" on":""),`${esc(t("gtitle")[g])} <b>${esc(num(CAT.filter(d=>group(d)===g).length))}</b>`);
      b.onclick=()=>{mapG=g;mapView();writeHash()};gs.append(b)});
    p.append(gs);
    if(mapG==="A")p.append(legend());else if(t("gnote")[mapG])p.append(el("div","sub",esc(t("gnote")[mapG])));
    p.append(graph(CAT.filter(d=>group(d)===mapG)));
    p.append(el("div","note",esc(t("note"))));
    v.append(p);
  }
  function graph(docs){
    const W=Math.max(620,Math.min(1100,width()-44)),H=docs.length>20?520:380;
    const ids=docs.map(c=>c.uid), idx={};ids.forEach((d,i)=>idx[d]=i);
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
    const row=el("div","row cmp-row");
    [["A",cmpA,withArts,i=>{cmpA=i}],["B",cmpB,peers,i=>{cmpB=i}]].forEach(([k,cur,list,set],n)=>{
      const s=el("select");
      list.forEach(d=>{const o=el("option",null,esc(title(d))+" ("+num(d.n_articles)+")");o.value=d.uid;
        if(d.uid===cur)o.selected=true;s.append(o)});
      s.disabled=!list.length;
      s.onchange=()=>{set(s.value);cmpT=null;compareView();writeHash()};
      const wrap=el("div");wrap.style.flex="1";wrap.style.minWidth="220px";
      wrap.append(el("div",null,`<span class="dot" style="background:${n?"var(--s2)":"var(--s1)"}"></span><small style="color:var(--ink-3)">${k}</small>`),s);
      const d=list.find(x=>x.uid===cur);if(d)wrap.append(profile(d,n?"var(--s2)":"var(--s1)"));
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
          <div style="display:flex;align-items:center"><div class="bar" style="width:${a/max*100}%;background:var(--s1)"></div><span class="barlbl">${num(a)}</span></div>
          <div style="display:flex;align-items:center"><div class="bar" style="width:${b/max*100}%;background:var(--s2)"></div><span class="barlbl">${num(b)}</span></div>
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
  // who wrote it, when, what kind of document, how much was read, and where the text comes from
  function profile(d,col){
    const c=el("div","profile");c.style.borderInlineStartColor=col;
    const st=d.type==="in_force"?"in_force":d.kind==="constitution_proposal"&&d.doc_status==="draft"?null:d.doc_status;
    const date=L==="fa"?(d.era||(d.year?num(d.year):"")):(d.year?String(d.year):"");
    const rows=[[t("author"),author(d)],[t("date"),date],
      [t("kind"),[t("kinds")[d.kind]||d.kind,st&&t("dstat")[st],+d.version>1&&t("rev")(d.version)].filter(Boolean).join(" · ")],
      [t("len"),t("size")(d.n_articles,d.n_pages,unitw(d.unit))]];
    const dl=el("dl");
    rows.forEach(([k,v])=>{if(v)dl.append(el("dt",null,esc(k)),el("dd",null,esc(v)))});
    c.append(dl);
    const flags=[d.duplicate_of&&t("dup"),d.confidence<0.8&&["draft","in_force","historical","transitional"].includes(d.type)&&t("partial")].filter(Boolean);
    const tags=(d.tags||[]).map(x=>`<span class="tag">${esc(t("tags")[x]||x)}</span>`)
      .concat(flags.map(x=>`<span class="flag quiet">${esc(x)}</span>`));
    if(tags.length)c.append(el("div","tags",tags.join("")));
    const links=[d.pdf&&pdfLink(d,0,t("rpdf")),
      d.source_url&&`<a href="${esc(d.source_url)}" target="_blank" rel="noopener">${esc(t("rsrc"))}</a>`].filter(Boolean);
    if(links.length)c.append(el("div","links",links.join(" · ")));
    return c;
  }
  function artCard(a){
    const c=el("div","art");
    c.innerHTML=`<div class="art-h"><span class="art-n">${esc(artn(a))}</span>
      <span class="art-p">${pdfLink(docOf(a.doc),a.page,pg(a.page))}</span></div><div class="fa" dir="rtl" lang="fa">${esc(a.text)}</div>`;
    if(a.text.length>320){const b=el("button","more");
      b.textContent=t("more");
      b.onclick=()=>{c.classList.toggle("open");b.textContent=c.classList.contains("open")?t("less"):t("more")};
      c.append(b);}
    return c;
  }

  /* ================= EDITIONS ================= */
  // the articles of each document in articles.json order: editions.json indexes into these
  const docArts=uid=>ARTS.filter(a=>a.doc===uid);
  function editionsView(){
    const v=V("editions");v.innerHTML="";
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("ed"))),el("div","sub",esc(t("edsub"))));
    v.append(p);
    const S=ED||{}, names=Object.keys(S);
    if(!names.length)return;
    if(!S[edS])edS=names.find(n=>S[n].docs.length>2)||names[0];
    const docs=S[edS].docs;
    if(!docs.includes(edA)||!docs.includes(edB)||edA===edB){edA=docs[docs.length-2];edB=docs[docs.length-1]}
    // the earlier of the two always on the right-hand (start) side: pairs are stored in series order
    if(docs.indexOf(edA)>docs.indexOf(edB))[edA,edB]=[edB,edA];
    const row=el("div","row cmp-row");
    const pick=(label,cur,list,set)=>{
      const s=el("select");s.setAttribute("aria-label",label);
      list.forEach(([val,txt])=>{const o=el("option",null,esc(txt));o.value=val;o.selected=val===cur;s.append(o)});
      s.onchange=()=>{set(s.value);editionsView();writeHash()};
      const w=el("div");w.style.flex="1";w.style.minWidth="220px";
      w.append(el("div",null,`<small style="color:var(--ink-3)">${esc(label)}</small>`),s);return w;};
    const dlabel=uid=>{const d=docOf(uid);return title(d)+(d.era||d.year?" ("+(L==="fa"?(d.era||num(d.year)):d.year)+")":"")};
    row.append(pick(t("edpick"),edS,names.map(n=>{const d=docOf(S[n].docs[0]);
      return [n,author(d)+" — "+t("edcount")(S[n].docs.length)]}),x=>{edS=x;edA=edB=null}));
    row.append(pick(t("edfrom"),edA,docs.map(u=>[u,dlabel(u)]),x=>{edA=x}));
    row.append(pick(t("edto"),edB,docs.map(u=>[u,dlabel(u)]),x=>{edB=x}));
    p.append(row);
    const prof=el("div","row cmp-row");
    [[edA,"var(--v-bad)"],[edB,"var(--v-ok)"]].forEach(([u,c])=>{const w=el("div");w.style.flex="1";w.style.minWidth="220px";
      w.append(profile(docOf(u),c));prof.append(w)});
    p.append(prof);

    const rows=S[edS].pairs[edA+"|"+edB]||[], A=docArts(edA), B=docArts(edB);
    const both=rows.filter(r=>r[0]!=null&&r[1]!=null);
    const same=both.filter(r=>sameText(A[r[0]].text,B[r[1]].text)).length;
    const added=rows.filter(r=>r[0]==null).length, dropped=rows.filter(r=>r[1]==null).length;
    p.append(el("div","group-note",esc(t("edsum")(both.length,same,added,dropped))));
    const tg=el("div","aud-tally");
    [[false,t("edchanged")],[true,t("edall")]].forEach(([k,lbl])=>{const b=el("button","vchip"+(edAll===k?" on":""),esc(lbl));
      b.onclick=()=>{edAll=k;editionsView()};tg.append(b)});
    p.append(tg);
    const list=el("div","ed-list");let shown=0;
    rows.forEach(([i,j])=>{
      const a=i!=null?A[i]:null, b=j!=null?B[j]:null;
      const unchanged=a&&b&&sameText(a.text,b.text);
      if(unchanged&&!edAll)return;
      shown++;
      const c=el("div","art ed-art"+(unchanged?" ed-same":""));
      const tagc=!a?"v-ok":!b?"v-bad":unchanged?"v-none":"v-part";
      const tag=!a?t("edadd"):!b?t("eddrop"):unchanged?t("edsame"):"";
      const ref=(x,d)=>x?`${esc(artn(x))} <span class="art-p">${pdfLink(docOf(d),x.page,pg(x.page))}</span>`:"—";
      c.innerHTML=`<div class="art-h ed-h"><span class="art-n">${ref(a,edA)}</span><span class="ed-arrow">${L==="fa"?"←":"→"}</span>
        <span class="art-n">${ref(b,edB)}</span>${tag?`<span class="vchip ${tagc}">${esc(tag)}</span>`:""}</div>`;
      const body=el("div","fa ed-text");body.dir="rtl";body.lang="fa";
      body.innerHTML=!a?`<ins>${esc(b.text)}</ins>`:!b?`<del>${esc(a.text)}</del>`:unchanged?esc(b.text):wordDiff(a.text,b.text);
      c.append(body);list.append(c);});
    if(!shown)list.append(el("div","empty",esc(t("ednone"))));
    p.append(list);
    p.append(el("div","note",esc(t("ednote"))));
  }
  // compare words without the marks that vary between typesettings: kashida, ZWNJ, vowel marks, Arabic yeh and kaf, digits
  const DIG="۰۱۲۳۴۵۶۷۸۹",ADIG="٠١٢٣٤٥٦٧٨٩";
  const key=w=>w.replace(/[\u0640\u200c\u064b-\u0652]/g,"").replace(/ي|ى/g,"ی").replace(/ك/g,"ک")
    .replace(/[۰-۹]/g,d=>DIG.indexOf(d)).replace(/[٠-٩]/g,d=>ADIG.indexOf(d));
  // unchanged: the same letters and punctuation, whatever the spacing («اداره ی» = «اداره‌ی»)
  const sameText=(x,y)=>key(x).replace(/\s+/g,"")===key(y).replace(/\s+/g,"");
  // words and punctuation marks as separate tokens, each with the space that follows it
  const PUNCT="،؛:.!؟?«»\"'()\\[\\]{}\\-–—/";
  const toks=x=>[...x.matchAll(new RegExp(`([${PUNCT}]|[^\\s${PUNCT}]+)(\\s*)`,"g"))].map(m=>({w:m[1],sp:m[2],k:key(m[1])}));
  // a word-level diff (longest common subsequence): removed words in <del>, added words in <ins>
  function wordDiff(x,y){
    const a=toks(x),b=toks(y),n=a.length,m=b.length,L2=Array.from({length:n+1},()=>new Uint16Array(m+1));
    for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)L2[i][j]=a[i].k===b[j].k?L2[i+1][j+1]+1:Math.max(L2[i+1][j],L2[i][j+1]);
    const out=[];let i=0,j=0,run=null,buf="";
    const flush=()=>{if(!buf)return;const s=buf.trimEnd(),tail=buf.slice(s.length);
      out.push((run==="d"?`<del>${esc(s)}</del>`:run==="i"?`<ins>${esc(s)}</ins>`:esc(s))+tail);buf=""};
    const push=(k,t)=>{if(k!==run){flush();run=k}buf+=t.w+(t.sp?" ":"")};
    while(i<n||j<m){
      if(i<n&&j<m&&a[i].k===b[j].k){push("=",b[j]);i++;j++}
      else if(j<m&&(i===n||L2[i][j+1]>=L2[i+1][j])){push("i",b[j]);j++}
      else{push("d",a[i]);i++}}
    flush();return out.join("").replace(/(<\/(?:del|ins)>)(?=<(?:del|ins)>)/g,"$1 ");
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
    // which kinds of document to search: all, or one comparison group
    const gf=el("div","aud-tally");
    [null,..."ABCD".split("").filter(g=>CAT.some(d=>group(d)===g))].forEach(g=>{
      const b=el("button","vchip"+(srchG===g?" on":""),esc(g?t("gtitle")[g]:t("rall")));
      b.onclick=()=>{srchG=g;gf.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));run()};gf.append(b)});
    p.append(gf);
    const res=el("div");p.append(res);
    const run=()=>{q=inp.value.trim();res.innerHTML="";writeHash();
      if(q.length<2){res.append(el("div","empty",esc(t("typein"))));return}
      const hits=ARTS.filter(a=>a.text.includes(q)&&(!srchG||group(docOf(a.doc))===srchG)).slice(0,60);
      if(!hits.length){res.append(el("div","empty",esc(t("nores"))));return}
      res.append(el("div","sub",esc(t("results")(hits.length))));
      hits.forEach(a=>{const d=CAT.find(c=>c.uid===a.doc)||{};
        const i=a.text.indexOf(q),s=Math.max(0,i-110);
        const snip=(s?"…":"")+esc(a.text.slice(s,i))+"<mark>"+esc(q)+"</mark>"+esc(a.text.slice(i+q.length,i+q.length+180))+"…";
        const h=el("div","hit");
        h.innerHTML=`<div class="hit-src"><span class="kind-tag">${esc(t("kinds")[d.kind]||d.kind)}</span><b>${esc(title(d))}</b> · ${esc(artn(a))} · ${pdfLink(d,a.page,pg(a.page))}</div>
          <div class="fa" dir="rtl" lang="fa">${snip}</div>`;
        res.append(h);});};
    inp.oninput=run;run();
    setTimeout(()=>inp.focus({preventScroll:true}),0);
    p.append(el("div","note",esc(t("note"))));
    v.append(p);
  }

  /* ================= HUMAN RIGHTS AUDIT ================= */
  const VORDER=["guaranteed","restricted_clawback","contradicted","silent"];
  function rightsView(){
    const v=V("rights");v.innerHTML="";
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("rtitle"))),el("div","sub",esc(t("rsub"))));
    v.append(p);
    const list=(AUD&&AUD.audits)||[];
    if(!list.length){p.append(el("div","empty",esc(t("rnone"))));v.append(method(null));return}
    if(!list.some(a=>a.uid===audDoc))audDoc=list[0].uid;
    const A=list.find(a=>a.uid===audDoc), d=CAT.find(c=>c.uid===A.uid)||{};
    progress(p,list.map(a=>a.uid),audDoc,u=>{audDoc=u;audRight=null;audFilter=null;render()});
    const head=el("div","aud-head");
    head.append(el("h3",null,esc(title(d))));
    const rv=A.review||{};
    head.append(el("div",A.preview||A.unreviewed?"aud-flag":"aud-meta",
      esc(A.preview?t("rpreview"):A.unreviewed?t("runrev"):t("rreviewed")(rv.reviewer,rv.date))));
    const meta=el("div","aud-meta",esc(t("rscope")(num(d.n_articles||0))));
    if(d.pdf)meta.append(" · ",el("span",null,pdfLink(d,0,t("rpdf"))));
    if(d.source_url){meta.append(" · ");const ln=el("a",null,esc(t("rsrc")));ln.href=d.source_url;ln.target="_blank";ln.rel="noopener";meta.append(ln)}
    head.append(meta);
    head.append(el("p","aud-sum",esc(L==="fa"?A.summary_fa:A.summary_en)));
    p.append(head);
    // tally: one chip per verdict, click to filter
    const counts={};Object.values(A.rights).forEach(r=>counts[r.verdict]=(counts[r.verdict]||0)+1);
    const tally=el("div","aud-tally");
    const all=el("button","vchip"+(audFilter?"":" on"),`${esc(t("rall"))} <b>${num(Object.keys(A.rights).length)}</b>`);
    all.onclick=()=>{audFilter=null;render()};tally.append(all);
    VORDER.forEach(k=>{const b=el("button",`vchip v-${k}`+(audFilter===k?" on":""),`${esc(t("v")[k])} <b>${num(counts[k]||0)}</b>`);
      b.title=t("vd")[k];b.onclick=()=>{audFilter=audFilter===k?null:k;render()};tally.append(b)});
    p.append(tally);
    // one row per right, in the rubric's order
    const rows=el("div","aud-rows");
    AUD.rights.forEach(R=>{
      const r=A.rights[R.id];if(!r||(audFilter&&r.verdict!==audFilter))return;
      const det=el("details","aud-row");det.open=audRight===R.id;
      det.ontoggle=()=>{if(det.open){audRight=R.id;writeHash()}};
      const arts=r.segments.map(sid=>seg(A,sid)).filter(Boolean);
      det.append(el("summary",null,
        `<span class="aud-right">${esc(L==="fa"?R.fa:R.en)}</span>`+
        `<span class="vchip v-${r.verdict}">${esc(t("v")[r.verdict])}</span>`+
        `<span class="aud-cites">${arts.map(a=>esc(a.short)).join(L==="fa"?"، ":", ")}</span>`));
      const body=el("div","aud-body");
      body.append(el("p",null,esc(L==="fa"?r.note_fa:r.note_en)));
      if(r.quote){const bq=el("blockquote","fa",esc(r.quote));bq.dir="rtl";bq.lang="fa";bq.title=t("rquote");body.append(bq)}
      const h1=el("h4",null,esc(t("rarts")));body.append(h1);
      if(!arts.length)body.append(el("div","sub",esc(t("rnoarts"))));
      arts.forEach(a=>{const x=el("details","aud-art");
        x.append(el("summary",null,esc(a.label)),el("div","fa",esc(a.text||"")));x.lastChild.dir="rtl";
        if(a.page&&d.pdf)x.append(el("div","sub",pdfLink(d,a.page,t("rpage")(a.page))));
        body.append(x)});
      body.append(el("h4",null,esc(t("rbench"))));
      r.provisions.forEach(id=>{const P=AUD.provisions[id]||{},I=AUD.instruments[P.i]||{};
        const x=el("details","aud-prov");
        x.append(el("summary",null,`<code>${esc(id)}</code> ${esc(L==="fa"?I.fa||"":I.en||"")}${P.h?" · "+esc(P.h):""}`));
        const tx=L==="fa"&&P.fa?P.fa:P.en||"";
        x.append(el("div",null,esc(tx)));
        if(L==="fa"&&!P.fa){x.lastChild.dir="ltr";x.append(el("div","sub",esc(t("ren"))))}
        if(I.url){const ln=el("a",null,esc(I.en||P.i));ln.href=I.url;ln.target="_blank";ln.rel="noopener";x.append(ln)}
        body.append(x)});
      det.append(body);rows.append(det);});
    p.append(rows);
    v.append(method(A));
  }
  function seg(A,sid){
    const m=/^a(\d+)$/.exec(sid), label=(A.segment_labels||{})[sid]||sid;
    if(!m)return {short:label,label,text:""};
    const a=ARTS.find(x=>x.doc===A.uid&&x.n===+m[1]);
    const unit=unitw(a?a.unit:"اص[سص]?ل");
    return {short:`${unit} ${num(m[1])}`,label:`${unit} ${num(m[1])}${a?" · "+pg(a.page):""}`,text:a?a.text:"",page:a?.page};
  }
  function method(A){
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("mtitle"))));
    const dl=el("dl","aud-defs");
    VORDER.forEach(k=>{dl.append(el("dt",null,`<span class="vchip v-${k}">${esc(t("v")[k])}</span>`),el("dd",null,esc(t("vd")[k])))});
    p.append(dl);
    const ul=el("ul","aud-method");t("m").forEach(s=>ul.append(el("li",null,esc(s))));p.append(ul);
    if(A)p.append(el("div","note",esc(t("mmodel")(A.model,A.benchmark)+(A.by?" · "+t("mby"):""))));
    return p;
  }

  /* ================= TOPICS (Constitute vocabulary) ================= */
  // the whole vocabulary, browsable: definition, coding question, and the published documents that have each topic
  function vocab(){
    const LV=TOP.leaves,p=el("div","panel");
    p.append(el("h2",null,esc(t("vtitle"))),el("div","sub",esc(t("vsub")(Object.keys(LV).length))));
    const has={};TOP.docs.forEach(D=>{D.articles.forEach(a=>[...a.t,...(a.x||[])].forEach(id=>((has[id]=has[id]||{})[D.uid]=1)));
      (D.document||[]).forEach(id=>((has[id]=has[id]||{})[D.uid]=1))});
    const LY=TOP.layers||{},core=x=>!x.l||x.l==="ccp";
    [["",x=>core(x)],...Object.keys(LY).filter(k=>k!=="ccp").map(k=>[k,x=>x.l===k])].forEach(([k,pick])=>{
    if(k)p.append(el("h3","tp-mh",esc(L==="fa"?LY[k].fa:LY[k].en)+` <span class="tp-cites">${esc(LY[k].src.join(" · "))}</span>`));
    const groups={};Object.entries(LV).filter(([,x])=>pick(x)).forEach(([id,x])=>(groups[x.g]=groups[x.g]||[]).push(id));
    const rows=el("div","aud-rows");
    Object.keys(groups).sort((a,b)=>{const A=TOP.groups[a]||{},B=TOP.groups[b]||{};return (L==="fa"?A.fa||a:A.en||a).localeCompare(L==="fa"?B.fa||b:B.en||b,L)})
      .forEach(gk=>{const G=TOP.groups[gk]||{fa:gk,en:gk},det=el("details","aud-row tp-vrow");
        det.append(el("summary",null,`<span class="aud-right">${esc(L==="fa"?G.fa:G.en)}</span><span class="tp-frac">${esc(num(groups[gk].length))}</span>`));
        const body=el("div","aud-body");
        groups[gk].forEach(id=>{const x=LV[id],y=el("details","aud-art");
          y.append(el("summary",null,`${esc(L==="fa"?x.fa||x.en:x.en)} <span class="tp-cites">${esc(L==="fa"?x.en:x.fa||"")} · <code>${esc(id)}</code></span>`));
          const b=el("div");
          b.append(el("p",null,esc(L==="fa"?x.df||x.d:x.d)));
          if(x.q){const q=el("p","sub",`<b>${esc(t("vq"))}:</b> `),e=el("span",null,esc(x.q));e.dir="ltr";e.lang="en";q.append(e);b.append(q)}
          if(x.s)b.append(el("p","sub",`<b>${esc(t("vsrc"))}:</b> ${esc(x.s)}`));
          const ds=Object.keys(has[id]||{});
          b.append(el("p","sub",`<b>${esc(t("vdocs"))}:</b> `+(ds.length?ds.map(u=>`<a href="#topics=${esc(u)},${esc(id)}">${esc(title(docOf(u)))}</a>`).join(L==="fa"?"، ":", "):esc(t("vnone")))));
          if(L==="fa"&&x.fs!=="reviewed")b.append(el("div","sub",esc(t("vdraft"))));
          y.append(b);body.append(y)});
        det.append(body);rows.append(det)});
    p.append(rows)});return p;
  }
  // one document done among many: say so, and list every constitution and draft, the undone ones disabled
  function progress(p,done,cur,pick){
    const all=CAT.filter(c=>group(c)==="A").sort((x,y)=>(x.year||9999)-(y.year||9999));
    p.append(el("div","tp-prog",esc(t("prog")(done.length,all.length))));
    const row=el("div","row"),s=el("select");s.setAttribute("aria-label",t("rpick"));
    [...all.filter(c=>done.includes(c.uid)),...all.filter(c=>!done.includes(c.uid))].forEach(c=>{
      const ok=done.includes(c.uid),o=el("option",null,esc(title(c)+(ok?"":" · "+t("queued"))));
      o.value=c.uid;o.disabled=!ok;o.selected=c.uid===cur;s.append(o)});
    s.onchange=()=>pick(s.value);row.append(el("span","sub",esc(t("rpick"))),s);p.append(row);
  }
  function topicsView(){
    const v=V("topics");v.innerHTML="";
    const p=el("div","panel");
    p.append(el("h2",null,esc(t("ttitle"))),el("div","sub",esc(t("tsub"))));
    const list=(TOP&&TOP.docs)||[];
    if(topPage==="method"&&TOP)return methodPage();
    v.append(p);
    if(!list.length){p.append(el("div","empty",esc(t("tnone"))));return}
    if(!list.some(a=>a.uid===topDoc))topDoc=list[0].uid;
    const A=list.find(a=>a.uid===topDoc), d=docOf(A.uid), LV=TOP.leaves;
    progress(p,list.map(a=>a.uid),topDoc,u=>{topDoc=u;topLeaf=null;render()});
    // leaf → the articles that provide for it
    // leaf → the articles that provide for it; the CCP additions count with Constitute's topics, the other
    // added vocabularies (policy fields, power-sharing) go to xby and get panels of their own
    const isCore=id=>{const x=LV[id];return !!x&&(!x.l||x.l==="ccp")};
    const by={},xby={};A.articles.forEach(a=>[...a.t,...(a.x||[])].forEach(id=>{const m=isCore(id)?by:xby;(m[id]=m[id]||[]).push(a.n)}));
    (A.document||[]).forEach(id=>by[id]=by[id]||[]);
    const lname=id=>{const x=LV[id]||{};return L==="fa"?x.fa||x.en||id:x.en||id};
    // one topic present in the document: its articles, each with its text and PDF page
    const leafRow=(id,ns)=>{const x=el("details","aud-art");x.open=topLeaf===id;
      x.ontoggle=()=>{if(x.open){topLeaf=id;writeHash()}};
      x.append(el("summary",null,`${esc(lname(id))} <span class="tp-cites">${ns.length?ns.map(artRef).map(esc).join(L==="fa"?"، ":", "):esc(t("tpre")+" · "+t("tdoc"))}</span>`));
      const inner=el("div");inner.append(el("div","sub",esc(ldef(id))));
      ns.forEach(n=>{const a=artOf(n);if(!a)return;const y=el("details","aud-art");
        y.append(el("summary",null,esc(artn(a)+" · "+pg(a.page))),el("div","fa",esc(a.text||"")));y.lastChild.dir="rtl";
        if(d.pdf)y.append(el("div","sub",pdfLink(d,a.page,t("rpage")(a.page))));inner.append(y)});
      x.append(inner);return x};
    const ldef=id=>{const x=LV[id]||{};return L==="fa"?x.df||x.d||"":x.d||""};
    const artOf=n=>ARTS.find(x=>x.doc===A.uid&&x.n===n);
    const artRef=n=>{const a=artOf(n);return a?artn(a):num(n)};
    const total=Object.keys(LV).filter(isCore).length, got=Object.keys(by).length, bareA=A.articles.filter(a=>!a.t.length);
    const bare=bareA.length, placed=bareA.filter(a=>(a.x||[]).length).length;
    const head=el("div","aud-head");
    head.append(el("h3",null,esc(title(d))));
    if(A.unreviewed||A.preview)head.append(el("div","aud-flag",esc((A.preview?(L==="fa"?"پیش‌نمایش، برای انتشار نیست. ":"Preview, not for publication. "):"")+t("tunrev"))));
    const meta=el("div","aud-meta",esc(t("tarts")(A.articles.length,bare,placed)));
    if(d.pdf)meta.append(" · ",el("span",null,pdfLink(d,0,t("rpdf"))));
    head.append(meta);p.append(head);
    // overall bar
    const big=el("div","tp-big");
    big.append(el("div","tp-num",esc(t("tcount")(got,total))));
    const bar=el("div","tp-bar");bar.append(el("span",null));bar.firstChild.style.width=(100*got/total)+"%";big.append(bar);
    p.append(big);
    // observation
    const note=L==="fa"?A.note_fa:A.note_en;
    if(note){const n=el("div","tp-note");n.append(el("b",null,esc(t("tnote"))),el("p",null,esc(note)));p.append(n)}
    // gaps
    if(A.findings&&A.findings.length){
      const f=el("div","panel");f.append(el("h2",null,esc(t("tfind"))));
      const ul=el("ul","tp-finds");
      A.findings.forEach(x=>{const li=el("li");li.append(el("p",null,esc(L==="fa"?x.fa:x.en)));
        const tags=el("div","tp-chips");
        x.topics.forEach(id=>{const c=el("span","tp-chip off",esc(lname(id)));c.title=ldef(id);tags.append(c)});
        x.articles.forEach(n=>{const a=artOf(n);const c=el("span","tp-art",a&&d.pdf?pdfLink(d,a.page,artRef(n)):esc(artRef(n)));tags.append(c)});
        if(tags.childNodes.length)li.append(tags);ul.append(li)});
      f.append(ul);v.append(f);
    }
    // by group
    const g=el("div","panel");g.append(el("h2",null,esc(t("tgroups"))));
    const groups={};Object.entries(LV).filter(([id])=>isCore(id)).forEach(([id,x])=>(groups[x.g]=groups[x.g]||[]).push(id));
    const order=Object.keys(groups).sort((a,b)=>{
      const ra=groups[a].filter(i=>by[i]).length/groups[a].length, rb=groups[b].filter(i=>by[i]).length/groups[b].length;return rb-ra});
    const rows=el("div","aud-rows");
    order.forEach(gk=>{
      const ids=groups[gk], has=ids.filter(i=>by[i]), not=ids.filter(i=>!by[i]);
      const det=el("details","aud-row");det.open=!!(topLeaf&&ids.includes(topLeaf));
      const G=TOP.groups[gk]||{fa:gk,en:gk};
      const sb=el("div","tp-bar sm");sb.append(el("span",null));sb.firstChild.style.width=(100*has.length/ids.length)+"%";
      const sum=el("summary",null,`<span class="aud-right">${esc(L==="fa"?G.fa:G.en)}</span>`);
      sum.append(sb,el("span","tp-frac",esc(num(has.length)+" / "+num(ids.length))));det.append(sum);
      const body=el("div","aud-body");
      if(has.length){body.append(el("h4",null,esc(t("tpresent"))));has.forEach(id=>body.append(leafRow(id,by[id])))}
      if(not.length){body.append(el("h4",null,esc(t("tabsent"))));
        const c=el("div","tp-chips");not.forEach(id=>{const s=el("span","tp-chip off",esc(lname(id)));s.title=ldef(id);c.append(s)});body.append(c)}
      det.append(body);rows.append(det);});
    g.append(rows);v.append(g);
    // the added vocabularies: policy fields list only what appears; power-sharing shows the absent rules too
    const layerPanel=([k,key,absent])=>{
      const all=Object.keys(LV).filter(id=>LV[id].l===k);if(!all.length)return;
      const P=el("div","panel"),arts=new Set(all.flatMap(id=>xby[id]||[]));
      P.append(el("h2",null,esc(t(key))),el("div","sub",esc(k==="cap"?t("xcapsub")(arts.size):t(key+"sub"))));
      const gs={};all.forEach(id=>(gs[LV[id].g]=gs[LV[id].g]||[]).push(id));
      const keys=Object.keys(gs).filter(gk=>absent||gs[gk].some(id=>xby[id]))
        .sort((a,b)=>gs[b].filter(i=>xby[i]).length-gs[a].filter(i=>xby[i]).length);
      if(!all.some(id=>xby[id])&&absent)P.append(el("p","sub",esc(t("xnone"))));
      const rows=el("div","aud-rows");
      keys.forEach(gk=>{const ids=gs[gk],has=ids.filter(i=>xby[i]),not=ids.filter(i=>!xby[i]);
        const det=el("details","aud-row tp-vrow");det.open=!!(topLeaf&&ids.includes(topLeaf));
        const G=TOP.groups[gk]||{fa:gk,en:gk};
        det.append(el("summary",null,`<span class="aud-right">${esc(L==="fa"?G.fa||G.en:G.en)}</span><span class="tp-frac">${esc(absent?num(has.length)+" / "+num(ids.length):num(has.length))}</span>`));
        const body=el("div","aud-body");
        if(has.length){if(absent)body.append(el("h4",null,esc(t("tpresent"))));has.forEach(id=>body.append(leafRow(id,xby[id])))}
        if(absent&&not.length){body.append(el("h4",null,esc(t("tabsent"))));
          const c=el("div","tp-chips");not.forEach(id=>{const s=el("span","tp-chip off",esc(lname(id)));s.title=ldef(id);c.append(s)});body.append(c)}
        det.append(body);rows.append(det)});
      P.append(rows);v.append(P)};
    // who holds each policy field: one row per level, the fields it holds with their articles
    const levelsPanel=()=>{
      const LVL=TOP.levels||[],at={};
      A.articles.forEach(a=>Object.entries(a.lv||{}).forEach(([id,k])=>{((at[k]=at[k]||{})[id]=at[k][id]||[]).push(a.n)}));
      if(!Object.keys(at).length)return;
      const P=el("div","panel");P.append(el("h2",null,esc(t("xlv"))),el("div","sub",esc(t("xlvsub"))));
      const rows=el("div","aud-rows");
      LVL.forEach(l=>{const f=at[l.key];if(!f)return;
        const det=el("details","aud-row tp-vrow");det.open=!!(topLeaf&&f[topLeaf]);
        det.append(el("summary",null,`<span class="aud-right">${esc(L==="fa"?l.fa:l.en)}</span><span class="tp-frac">${esc(num(Object.keys(f).length))}</span>`));
        const body=el("div","aud-body");body.append(el("div","sub",esc(L==="fa"?l.df:l.d)));
        const c=el("div","tp-chips");
        Object.entries(f).sort((x,y)=>lname(x[0]).localeCompare(lname(y[0]),L)).forEach(([id,ns])=>{
          const s=el("span","tp-chip",esc(lname(id))+` <span class="tp-cites">${esc(ns.map(artRef).join(L==="fa"?"، ":", "))}</span>`);s.title=ldef(id);c.append(s)});
        body.append(c);det.append(body);rows.append(det)});
      P.append(rows);v.append(P)};
    // regional authority: the ten dimensions of the Regional Authority Index, scored for this draft's regions
    const raiPanel=()=>{
      const R=A.rai,D=TOP.rai;if(!R||!D)return;
      const P=el("div","panel");P.append(el("h2",null,esc(t("xrai"))),el("div","sub",esc(t("xraisub")(L==="fa"?R.unit.fa:R.unit.en))));
      const big=el("div","tp-big");big.append(el("div","tp-num",esc(t("xraitot")(R.total,R.self,R.shared))));
      const bar=el("div","tp-bar");bar.append(el("span",null));bar.firstChild.style.width=(100*R.total/30)+"%";big.append(bar);P.append(big);
      if(R.finding){const n=el("div","tp-note");n.append(el("b",null,esc(t("tnote"))),el("p",null,esc(L==="fa"?R.finding.fa:R.finding.en)));P.append(n)}
      const rows=el("div","aud-rows");
      ["self","shared"].forEach(dm=>{const DM=D.domains[dm];rows.append(el("h4",null,esc((L==="fa"?DM.fa:DM.en)+" · "+num(R[dm])+" / "+num(DM.max))));
        D.dims.filter(x=>x.domain===dm).forEach(x=>{const r=R.dims[x.key];if(!r)return;
          const det=el("details","aud-row tp-vrow"),sb=el("div","tp-bar sm");sb.append(el("span",null));sb.firstChild.style.width=(100*r.score/x.max)+"%";
          const sum=el("summary",null,`<span class="aud-right">${esc(L==="fa"?x.fa:x.en)}</span>`);sum.append(sb,el("span","tp-frac",esc(num(r.score)+" / "+num(x.max))));det.append(sum);
          const body=el("div","aud-body");body.append(el("p",null,esc(L==="fa"?r.fa:r.en)));
          if(r.articles.length)body.append(el("div","tp-chips",r.articles.map(n=>{const a=artOf(n);return `<span class="tp-art">${a&&d.pdf?pdfLink(d,a.page,artRef(n)):esc(artRef(n))}</span>`}).join("")));
          const sc=L==="fa"?x.scale_fa:x.scale,ul=el("ol","sub tp-scale");ul.start=0;if(sc.length>1)sc.forEach((s,i)=>{const li=el("li",i===r.score?"on":null,esc(s));li.value=i;ul.append(li)});else ul.append(el("li",null,esc(sc[0])));
          body.append(el("h4",null,esc(t("xraiscale"))),ul);det.append(body);rows.append(det)})});
      P.append(rows,el("div","note",esc(t("xraicredit"))));v.append(P)};
    layerPanel(["cap","xcap",false]);levelsPanel();raiPanel();layerPanel(["ps","xps",true]);layerPanel(["lang","xlang",true]);
    // method: a pointer to the method page
    const m=el("div","panel");m.append(el("h2",null,esc(t("mtitle"))),el("p","sub",esc(t("mshort"))));
    const mj=el("div","tp-jump"),mb2=el("button",null,esc(t("mlink")));mb2.type="button";mb2.onclick=openMethod;mj.append(mb2);m.append(mj);
    m.append(el("div","note",esc((A.model?t("mmodel")(A.model,TOP.version).split(" · ")[0]+" · ":"")+t("tcredit"))));
    v.append(m);
  }
  function openMethod(){topPage="method";render();V("topics").scrollIntoView({block:"start"})}
  // the method page: how the text is read and tagged, what the counts mean, the limits; then the vocabulary
  function methodPage(){
    const v=V("topics");v.innerHTML="";
    const p=el("div","panel"),bk=el("div","tp-jump"),b=el("button",null,esc(t("mback")));
    b.type="button";b.onclick=()=>{topPage=null;render()};bk.append(b);
    p.append(bk,el("h2",null,esc(t("mtitle"))));
    t("mp").forEach(([h,ps])=>{p.append(el("h3","tp-mh",esc(h)));ps.forEach(x=>p.append(el("p","tp-mp",esc(x))))});
    v.append(p,vocab());
  }

  return {
    destroy(){ if(useHash)removeEventListener("hashchange",onHash); observer?.disconnect(); root.innerHTML=""; },
    show(k){ if(VIEWS.includes(k)){view=k;render();} },
  };
}
