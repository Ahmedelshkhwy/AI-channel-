const { chromium } = require('playwright');
const B='http://localhost:5000', D=__dirname+'/data/';
const slug={'فرع المعادي':'maadi','فرع مدينة نصر':'nasr_city','فرع الشيخ زايد':'zayed','فرع وسط البلد':'downtown'};
const branches=["فرع المعادي","فرع مدينة نصر","فرع الشيخ زايد","فرع وسط البلد"];
(async()=>{
 const br=await chromium.launch(); const c=await br.newContext({viewport:{width:540,height:960}}); const p=await c.newPage();
 await p.goto(B+'/signup');
 await p.fill('input[name=org_name]','صيدليات الشفاء'); await p.selectOption('select[name=business_type]','pharmacy');
 await p.fill('input[name=username]','shefaa'); await p.fill('input[name=password]','shefaa-pass-1'); await p.fill('input[name=confirm_password]','shefaa-pass-1');
 await p.click('form.auth-form button[type=submit]'); await p.waitForURL('**/upload'); await p.evaluate(()=>fetch('/language/ar',{method:'POST',headers:{'X-CSRFToken':document.querySelector('input[name=csrf_token]').value},body:new URLSearchParams({csrf_token:document.querySelector('input[name=csrf_token]').value})}));
 for (const b of branches.slice(1)) {
  await p.goto(B+'/upload'); await p.setInputFiles('input[type=file]',[D+slug[b]+'_items.xlsx']);
  await p.fill('input[name=branch]',b);
  await p.click('form[enctype] button[type=submit]'); await p.waitForURL('**/upload/review/**');
  await p.fill('input[name=period_days]','90');
  await p.click('form[method=post]:has(input[name=period_days]) button[type=submit] >> nth=-1'); await p.waitForURL('**/imports/**');
 }
 await c.storageState({path:'state.json'});
 await p.goto(B+'/actions'); await p.screenshot({path:'probe-actions.png',fullPage:true});
 console.log((await p.locator('table').first().innerText()).slice(0,600));
 await br.close();})();
