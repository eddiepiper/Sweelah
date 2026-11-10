const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const [mode, base] = process.argv.slice(2);
const output = path.resolve(__dirname, mode.startsWith('qafu2d01l01-') ? '../../test-artifacts/qa-fu2d01-l01' : mode.startsWith('cxuifu2d01-') ? '../../test-artifacts/cxui-fu2-d01' : mode.startsWith('cxuifu2-') ? '../../test-artifacts/cxui-001-followup2' : mode.startsWith('cxuifu-') ? '../../test-artifacts/cxui-001-followup' : mode.startsWith('cxui-') ? '../../test-artifacts/cxui-001' : '../../test-artifacts/s016');
const costLabel = 'Extra care cost each month (S$)';
const monthsLabel = 'For how many months?';
(async () => {
  let browser;
  try {
    browser = await chromium.launch({headless:true,
      ...(process.env.S016_CHROMIUM ? {executablePath:process.env.S016_CHROMIUM} : {}),
      args:['--no-sandbox']});
  } catch (error) {
    if (mode === 'probe') { console.error('S016 browser unavailable offline: ' + error.message); process.exitCode=77; return; }
    throw error;
  }
  try {
    if (mode === 'probe') { console.log('Chromium ' + browser.version()); return; }
    const page = await browser.newPage({viewport:(mode==='mobile375'||mode==='cxui-mobile375'||mode.endsWith('-375'))?{width:375,height:844}:mode==='mobile'?{width:390,height:844}:{width:1280,height:960},reducedMotion:'reduce'});
    const errors=[];
    page.on('pageerror', e=>errors.push(e.message));
    await page.route('**/*', route => new URL(route.request().url()).origin===base ? route.continue() : route.abort());
    await page.goto(base+'/sweelah');
    const cost=page.getByLabel(costLabel,{exact:true}), months=page.getByLabel(monthsLabel,{exact:true});
    const submit=page.getByRole('button',{name:'Preview care cost',exact:true});
    await cost.waitFor();
    assert.equal(await cost.inputValue(),''); assert.equal(await months.inputValue(),'');
    assert.equal(await page.locator('input').count(),2);
    assert.doesNotMatch(await page.locator('main').innerText(),/Great Eastern|product library|recommended product|share with|validated by users/i);
    fs.mkdirSync(output,{recursive:true});
    const fill=async(c,m)=>{await cost.fill(c);await months.fill(m);};
    const preview=async()=>{await submit.click();await page.locator('#care-result:not([hidden])').waitFor();};
    const focused=async selector=>assert.equal(await page.locator(selector).evaluate(el=>el===document.activeElement),true);
    const limitations = async locator => {
      const text=await locator.innerText();
      for (const term of ['subsidies and grants','CareShield LIFE','MediSave','lost pay or unpaid leave','not financial advice']) assert.ok(text.includes(term),term);
    };
    const axe = async state => {
      let axePath=process.env.AXE_CORE_PATH;
      if (!axePath) {try {axePath=require.resolve('axe-core/axe.min.js');} catch {}}
      if (!axePath) {console.log('axe unavailable offline; CXUI geometry and behavior checked, no full accessibility audit');return;}
      await page.addScriptTag({path:axePath});
      const audit=await page.evaluate(()=>window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}}));
      fs.writeFileSync(path.join(output,`axe-${mode}-${state}.json`),JSON.stringify(audit,null,2));
      assert.deepEqual(audit.violations,[]);
    };
    const screenshot=async state=>page.screenshot({path:path.join(output,`${mode}-${state}.png`),fullPage:true});
    if (mode==='cxui-d01'||mode==='cxui-d04') {
      await fill('1200','12');await preview();
      const text=await page.locator('#care-result').innerText();
      if(mode==='cxui-d01') assert.doesNotMatch(text,/Preview status:|LIMITED_RECURRING_COST_PREVIEW_ONLY/);
      else assert.doesNotMatch(text,/Illustrative recurring care costs only; leave, insurance and subsidies omitted/);
    } else if (mode==='cxui-d02') {
      await limitations(page.locator('#care-setup-notice'));
      await fill('1200','12');await preview();await limitations(page.locator('section'));
      await page.getByRole('button',{name:'Change my numbers'}).click();await limitations(page.locator('#care-setup-notice'));
    } else if (mode==='cxui-d03') {
      await months.fill('0');await submit.click();
      await cost.fill('1');
      assert.equal(await cost.getAttribute('aria-invalid'),'false');
      assert.equal(await months.getAttribute('aria-invalid'),'true');
      assert.equal(await page.locator('#care-months-error').isVisible(),true);
      assert.equal(await page.locator('#care-errors a').count(),1);
      await page.locator('#care-errors a').click();await focused('#care-months');
      await months.fill('12');assert.equal(await page.locator('#care-errors').isVisible(),false);
      await fill('','');await submit.click();await months.fill('12');
      assert.equal(await cost.getAttribute('aria-invalid'),'true');
      assert.equal(await page.locator('#care-cost-error').isVisible(),true);
      assert.equal(await page.locator('#care-errors a[href="#care-cost"]').count(),1);
    } else if (mode==='cxui-d05') {
      assert.doesNotMatch(await page.locator('body').innerText(),/Illustrative scenario setup|household projection|research dashboard|Synthetic-only|Local preview|Single user/i);
      await fill('1200','12');await preview();
      assert.doesNotMatch(await page.locator('body').innerText(),/household projection|Limited preview|Illustrative scenario setup/i);
      assert.match(await page.locator('body').innerText(),/synthetic figures only/i);
    } else if (mode==='cxui-d06'||mode==='cxui-mapping') {
      await fill('1200','12');
      const cases=mode==='cxui-d06'?[500,403,'abort']:[
        {detail:'words changed completely',field:'months',code:'months'},
        {detail:'not a prefix',field:'additional_care_cost_monthly',code:'precision'},
        {detail:'additional_care_cost_monthly must be more than 0'},
        {detail:'months invalid',field:'unexpected',code:'months'},
        {detail:'anything',field:'additional_care_cost_monthly',code:'unexpected'},
      ];
      for (const item of cases) {
        await page.unroute('**/api/scenarios/S016/preview');
        await page.route('**/api/scenarios/S016/preview',route=>item==='abort'?route.abort():route.fulfill({status:typeof item==='number'?item:422,contentType:'application/json',body:JSON.stringify(typeof item==='number'?{detail:'internal detail'}:item)}));
        await submit.click();await page.locator('#care-errors:not([hidden])').waitFor();
        const heading=await page.locator('#care-error-heading').innerText();
        if(typeof item==='object'&&['months','precision'].includes(item.code)&&['months','additional_care_cost_monthly'].includes(item.field)) {
          assert.equal(heading,'Please check these answers');
          assert.equal(await (item.field==='months'?months:cost).getAttribute('aria-invalid'),'true');
        } else {
          assert.equal(heading,'Something went wrong');
          assert.equal(await cost.getAttribute('aria-invalid'),'false');assert.equal(await months.getAttribute('aria-invalid'),'false');
          assert.doesNotMatch(await page.locator('#care-errors').innerText(),/internal detail|must be more than 0|months invalid/);
        }
        assert.equal(await cost.inputValue(),'1200');assert.equal(await months.inputValue(),'12');
      }
      await screenshot('server-error');
    } else if (mode==='cxui-d07') {
      let requests=0;page.on('request',r=>{if(r.url().endsWith('/api/scenarios/S016/preview')) requests++;});
      for(const amount of ['100000.01','999999999999','100001']) {
        await fill(amount,'12');await submit.click();
        assert.equal(await page.locator('#care-cost-error').innerText(),'Error: Enter an amount no more than S$100,000.');
      }
      for(const amount of ['Infinity','NaN','-Infinity','sNaN','1e12','1e400']) {
        await fill(amount,'12');await submit.click();
        assert.equal(await page.locator('#care-cost-error').innerText(),'Error: Enter numbers only, for example 1200.');
      }
      for(const duration of ['121','1e400','Infinity','NaN']) {
        await fill('1200',duration);await submit.click();
        assert.equal(await page.locator('#care-months-error').innerText(),'Error: Enter the number of months, from 1 to 120 (10 years).');
      }
      assert.equal(requests,0);
      await fill('100000.00','120');await preview();assert.match(await page.locator('#care-result').innerText(),/S\$12,000,000.00/);
    } else if(mode==='cxui-d08'||mode==='cxui-mobile375') {
      await page.setViewportSize({width:375,height:844});
      await screenshot('setup');
      if(mode==='cxui-mobile375') await axe('setup');
      await submit.click();await screenshot('field-errors');
      const geometry=await page.locator('#care-errors li').evaluateAll(items=>items.map(li=>{
        const a=li.querySelector('a'),range=document.createRange();range.selectNodeContents(a);
        const first=range.getClientRects()[0],box=a.getBoundingClientRect(),parent=li.getBoundingClientRect();
        return {display:getComputedStyle(a).display,firstTop:first.top,top:box.top,itemTop:parent.top};
      }));
      fs.writeFileSync(path.join(output,`${mode}-bullet-geometry.json`),JSON.stringify(geometry,null,2));
      for(const item of geometry) {assert.equal(item.display,'block');assert.ok(Math.abs(item.top-item.itemTop)<1);assert.ok(item.firstTop-item.top<12);}
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await axe('field-errors');
      await fill('1200','12');await preview();await screenshot('result');await axe('result');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      if(mode==='cxui-mobile375') {
        await page.getByRole('button',{name:'Change my numbers'}).click();
        await page.route('**/api/scenarios/S016/preview',route=>route.abort());await submit.click();
        await page.getByText("We couldn't work this out just now. Your answers are kept. Please try again.",{exact:true}).waitFor();
        await screenshot('server-error');await axe('server-error');
      }
    } else if(mode==='cxuifu-rd01'||mode==='cxuifu-rd01-375') {
      const link=page.locator('header a');
      assert.equal(await link.count(),1);
      assert.equal((await link.innerText()).trim(),'Back to RetirePilot lab');
      assert.equal(await link.getAttribute('href'),'/');
      assert.doesNotMatch(await page.locator('header').innerText(),/overview/i);
      const box=await link.boundingBox();assert.ok(box.width>=44&&box.height>=44,JSON.stringify(box));
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await screenshot('header');await axe('setup');
      await link.click();await page.waitForURL(base+'/');
      assert.match(await page.title(),/RetirePilot/);
      await page.locator('#metrics').waitFor();
      await screenshot('destination');
    } else if(mode==='cxuifu-rd02'||mode==='cxuifu-rd02-375') {
      const general="We couldn't work this out just now. Your answers are kept. Please try again.";
      await fill('1200','12');
      await page.route('**/api/scenarios/S016/preview',route=>route.abort());
      await submit.click();await page.getByText(general,{exact:true}).waitFor();
      assert.equal(await page.locator('#care-error-heading').innerText(),'Something went wrong');
      await screenshot('server-error-before-edit');
      await cost.fill('1500');
      assert.equal(await page.locator('#care-errors').isVisible(),false,'server error must clear on edit');
      assert.equal(await page.getByText('Something went wrong').isVisible(),false);
      assert.equal(await cost.getAttribute('aria-invalid'),'false');assert.equal(await months.getAttribute('aria-invalid'),'false');
      assert.equal(await cost.inputValue(),'1500');assert.equal(await months.inputValue(),'12');
      await screenshot('server-error-after-edit');await axe('after-edit');
      // Editing months also clears a fresh server error.
      await submit.click();await page.getByText(general,{exact:true}).waitFor();
      await months.fill('24');assert.equal(await page.locator('#care-errors').isVisible(),false);
      // D03 still holds: a server-mapped months error survives a cost edit.
      await page.unroute('**/api/scenarios/S016/preview');
      await page.route('**/api/scenarios/S016/preview',route=>route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({detail:'x',field:'months',code:'months'})}));
      await submit.click();await page.locator('#care-errors:not([hidden])').waitFor();
      assert.equal(await page.locator('#care-error-heading').innerText(),'Please check these answers');
      await cost.fill('1600');
      assert.equal(await months.getAttribute('aria-invalid'),'true');
      assert.equal(await page.locator('#care-months-error').isVisible(),true);
      assert.equal(await page.locator('#care-errors').isVisible(),true);
      assert.equal(await page.locator('#care-errors a[href="#care-months"]').count(),1);
      // D03 still holds for client-side errors.
      await page.unroute('**/api/scenarios/S016/preview');
      await fill('','0');await submit.click();await cost.fill('5');
      assert.equal(await months.getAttribute('aria-invalid'),'true');
      assert.equal(await page.locator('#care-errors a[href="#care-months"]').count(),1);
      assert.equal(await page.locator('#care-errors a[href="#care-cost"]').count(),0);
      // Recovery: a real preview still works afterwards.
      await months.fill('12');await preview();
      assert.ok((await page.locator('#care-result').innerText()).includes('S$5.00'));
    } else if(mode==='cxuifu-rd03'||mode==='cxuifu-rd03-375') {
      await submit.click();await page.locator('#care-errors:not([hidden])').waitFor();
      const m=await page.locator('#care-error-heading').evaluate(el=>{
        const s=getComputedStyle(el),box=el.getBoundingClientRect(),parent=el.parentElement.getBoundingClientRect(),ps=getComputedStyle(el.parentElement);
        return {marginTop:s.marginTop,gap:box.top-parent.top-parseFloat(ps.borderTopWidth)-parseFloat(ps.paddingTop)};
      });
      fs.writeFileSync(path.join(output,`${mode}-heading-geometry.json`),JSON.stringify(m,null,2));
      assert.equal(m.marginTop,'0px');assert.ok(Math.abs(m.gap)<1,JSON.stringify(m));
      await screenshot('field-errors');await axe('field-errors');
      await fill('1200','12');await page.route('**/api/scenarios/S016/preview',route=>route.abort());
      await submit.click();await page.locator('#care-errors:not([hidden])').waitFor();
      assert.equal(await page.locator('#care-error-heading').evaluate(el=>getComputedStyle(el).marginTop),'0px');
      await screenshot('server-error');await axe('server-error');
    } else if(mode==='cxuifu-exponent') {
      let requests=0;page.on('request',r=>{if(r.url().endsWith('/api/scenarios/S016/preview')) requests++;});
      for(const amount of ['1e2','1E2','1e-3','1.005e2','1e400','2e+3','S$1e2']) {
        await fill(amount,'12');await submit.click();
        await page.locator('#care-errors:not([hidden])').waitFor();
        assert.equal(await page.locator('#care-cost-error').innerText(),'Error: Enter numbers only, for example 1200.',amount);
        assert.equal(await cost.inputValue(),amount);
      }
      assert.equal(requests,0);
      await screenshot('rejected');
      await fill('100','12');await preview();
      assert.ok((await page.locator('#care-result').innerText()).includes('An extra S$100.00 a month for 12 months adds up to S$1,200.00.'));
    } else if(mode==='cxuifu-wording') {
      for(const state of ['setup','result','return']) {
        if(state==='result') {await fill('1200','12');await preview();}
        if(state==='return') await page.getByRole('button',{name:'Change my numbers'}).click();
        const text=await page.locator('#care-setup-notice').innerText();
        assert.doesNotMatch(text,/entitlement/i,state);
        assert.match(text,/no inflation/,state);
        await limitations(page.locator('#care-setup-notice'));
      }
      assert.doesNotMatch(await page.locator('body').innerText(),/entitlement/i);
    } else if(mode==='cxuifu2-months'||mode==='cxuifu2-months-375') {
      // CXUI-FU-D01: "1 month" singular; 2+ plural; 0 never reaches a result.
      for(const [n,total] of [[1,'S$1,200.00'],[2,'S$2,400.00'],[12,'S$14,400.00'],[120,'S$144,000.00']]) {
        await fill('1200',String(n));await preview();
        const text=await page.locator('#care-result').innerText();
        const unit=n===1?'1 month':`${n} months`;
        assert.ok(text.includes(`Over ${unit}`),text);
        assert.ok(text.includes(`An extra S$1,200.00 a month for ${unit} adds up to ${total}.`),text);
        assert.doesNotMatch(text,/\b1 months\b/);
        if(n!==1) assert.doesNotMatch(text,new RegExp(`\\b${n} month\\b`));
        if(n===1) {await screenshot('one-month');await axe('one-month');}
        if(n===2) await screenshot('two-months');
        if(mode.endsWith('-375')) assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
        await page.getByRole('button',{name:'Change my numbers'}).click();
      }
      let requests=0;const count=r=>{if(r.url().endsWith('/api/scenarios/S016/preview')) requests++;};
      page.on('request',count);
      await fill('1200','0');await submit.click();
      assert.equal(await page.locator('#care-months-error').innerText(),'Error: Enter the number of months, from 1 to 120 (10 years).');
      assert.equal(await page.locator('#care-result').isVisible(),false);
      assert.equal(requests,0);page.off('request',count);
      // A forged response with months 0 is treated as a failure, never shown as "0 months".
      await page.route('**/api/scenarios/S016/preview',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
        status:'LIMITED_RECURRING_COST_PREVIEW_ONLY',synthetic_only:true,may_post_to_household_projection:false,
        extra_monthly_cost:'1200.00',period_cash_cost:'0.00',months:0})}));
      await fill('1200','1');await submit.click();await page.locator('#care-errors:not([hidden])').waitFor();
      assert.equal(await page.locator('#care-error-heading').innerText(),'Something went wrong');
      assert.equal(await page.locator('#care-result').isVisible(),false);
      assert.doesNotMatch(await page.locator('body').innerText(),/\b0 months?\b/);
    } else if(mode==='qafu2d01l01-guard'||mode==='qafu2d01l01-guard-375') {
      // QA-FU2D01-L01: forged 200 amounts must be canonical ^(0|[1-9]\d*)\.\d{2}$ (monthly and total),
      // monthly within 0.01..100000.00, total = monthly x months in integer cents. Otherwise "Something went wrong".
      const contract='"status":"LIMITED_RECURRING_COST_PREVIEW_ONLY","synthetic_only":true,"may_post_to_household_projection":false';
      const forged=(monthly,total,monthsJson)=>`{${contract},"extra_monthly_cost":${JSON.stringify(monthly)},"period_cash_cost":${JSON.stringify(total)},"months":${monthsJson}}`;
      let body='';
      await page.route('**/api/scenarios/S016/preview',route=>route.fulfill({status:200,contentType:'application/json',body}));
      const send=async()=>{
        await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/scenarios/S016/preview')),submit.click()]);
        await page.waitForFunction(()=>!document.getElementById('care-form').hasAttribute('aria-busy'));
      };
      const refused=async label=>{
        await page.locator('#care-errors:not([hidden])').waitFor();
        assert.equal(await page.locator('#care-error-heading').innerText(),'Something went wrong',label);
        assert.ok((await page.locator('#care-errors').innerText()).includes("We couldn't work this out just now. Your answers are kept. Please try again."),label);
        assert.equal(await page.locator('#care-result').isVisible(),false,label);
        const text=await page.locator('body').innerText();
        assert.doesNotMatch(text,/Over \d|adds up to|Your parent-care cost estimate/,label);
        assert.doesNotMatch(text,/S\$0?1,200\.00|S\$0\.00|S\$999,999\.00|S\$119,999,880\.00|S\$99,999,999,999\.99|S\$11,999,999,999,998\.80|S\$14,400\.00|NaN|Infinity|undefined|null/,label);
      };
      const bad=[
        // QA-FU2D01-L01: non-canonical or out-of-range amounts.
        ['leading-zero','1','01200.00','01200.00'],['leading-zero-total-only','1','1200.00','01200.00'],
        ['zero-monthly','1','0.00','0.00'],['zero-monthly-120','120','0.00','0.00'],
        ['over-cap-999999','120','999999.00','119999880.00'],['over-cap-huge','120','99999999999.99','11999999999998.80'],
        ['over-cap-100000.01','1','100000.01','100000.01'],
        ['one-dp','1','1200.0','1200.0'],['three-dp','1','1200.000','1200.000'],['plus-sign','1','+1200.00','+1200.00'],
        ['trailing-dot','1','1200.','1200.'],['no-int-part','1','.50','.50'],['minus','1','-1200.00','-1200.00'],
        ['space','1',' 1200.00',' 1200.00'],
        // FU2-D01 regressions (type/arithmetic refusals).
        ['months-true','true','1200.00','14400.00'],['months-"1"','"1"','1200.00','1200.00'],['months-[5]','[5]','1200.00','6000.00'],
        ['months-"1e1"','"1e1"','1200.00','12000.00'],['total-mismatch','1','1200.00','14400.00'],['total-off-by-1c','12','1200.00','14400.01'],
        ['monthly-number','12',1200,'14400.00'],['total-number','1','1200.00',1200],['total-1dp','12','1200.00','14400.0'],['monthly-exponent','2','1e2','200.00']
      ];
      await fill('1200','1');
      for(const [label,monthsJson,monthly,total] of bad) {
        body=forged(monthly,total,monthsJson);
        await send();await refused(label);
        if(label==='leading-zero') {await screenshot('forged-leading-zero');await axe('forged-leading-zero');}
        if(label==='over-cap-huge') await screenshot('forged-over-cap-huge');
      }
      for(const [n,monthly,total,line] of [
        [1,'1200.00','1200.00','An extra S$1,200.00 a month for 1 month adds up to S$1,200.00.'],
        [1,'0.01','0.01','An extra S$0.01 a month for 1 month adds up to S$0.01.'],
        [3,'0.10','0.30','An extra S$0.10 a month for 3 months adds up to S$0.30.'],
        [7,'99999.99','699999.93','An extra S$99,999.99 a month for 7 months adds up to S$699,999.93.'],
        [1,'100000.00','100000.00','An extra S$100,000.00 a month for 1 month adds up to S$100,000.00.'],
        [120,'100000.00','12000000.00','An extra S$100,000.00 a month for 120 months adds up to S$12,000,000.00.']]) {
        body=forged(monthly,total,String(n));
        await send();await page.locator('#care-result:not([hidden])').waitFor();
        const text=await page.locator('#care-result').innerText();
        assert.ok(text.includes(line),text);
        assert.ok(text.includes(n===1?'Over 1 month':`Over ${n} months`),text);
        assert.doesNotMatch(text,/\b1 months\b/);
        if(n===120) {await screenshot('forged-valid-120-cap');await axe('forged-valid-120-cap');}
        if(mode.endsWith('-375')) assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
        await page.getByRole('button',{name:'Change my numbers'}).click();
      }
      await page.unroute('**/api/scenarios/S016/preview');
      await fill('1200','1');await preview();
      assert.ok((await page.locator('#care-result').innerText()).includes('An extra S$1,200.00 a month for 1 month adds up to S$1,200.00.'));
    } else if(mode==='cxuifu2d01-guard'||mode==='cxuifu2d01-guard-375') {
      // CXUI-FU2-D01: a forged 200 must carry months as a whole JSON number 1..120 (no coercion),
      // and extra_monthly_cost x months must equal period_cash_cost exactly. Raw bodies let NaN/Infinity be forged.
      const contract='"status":"LIMITED_RECURRING_COST_PREVIEW_ONLY","synthetic_only":true,"may_post_to_household_projection":false';
      const forged=(monthly,total,monthsJson)=>`{${contract},"extra_monthly_cost":${JSON.stringify(monthly)},"period_cash_cost":${JSON.stringify(total)},"months":${monthsJson}}`;
      let body='';
      await page.route('**/api/scenarios/S016/preview',route=>route.fulfill({status:200,contentType:'application/json',body}));
      const send=async()=>{
        await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/scenarios/S016/preview')),submit.click()]);
        await page.waitForFunction(()=>!document.getElementById('care-form').hasAttribute('aria-busy'));
      };
      const refused=async label=>{
        await page.locator('#care-errors:not([hidden])').waitFor();
        assert.equal(await page.locator('#care-error-heading').innerText(),'Something went wrong',label);
        assert.ok((await page.locator('#care-errors').innerText()).includes("We couldn't work this out just now. Your answers are kept. Please try again."),label);
        assert.equal(await page.locator('#care-result').isVisible(),false,label);
        const text=await page.locator('body').innerText();
        assert.doesNotMatch(text,/Over \d|Over 1 month|adds up to|Your parent-care cost estimate/,label);
        assert.doesNotMatch(text,/S\$14,400\.00|NaN|Infinity|undefined|null/,label);
      };
      const bad=[
        ['true','true','1200.00','14400.00'],['"1"','"1"','1200.00','1200.00'],['[5]','[5]','1200.00','6000.00'],
        ['"1e1"','"1e1"','1200.00','12000.00'],['1.5','1.5','1200.00','1800.00'],
        ['NaN-token','NaN','1200.00','14400.00'],['Infinity-token','Infinity','1200.00','14400.00'],
        ['1e400-Infinity','1e400','1200.00','14400.00'],['-1e400','-1e400','1200.00','14400.00'],
        // Mismatched or malformed totals with a valid months value.
        ['total-mismatch-1','1','1200.00','14400.00'],['total-off-by-1c','12','1200.00','14400.01'],
        ['monthly-number','12',1200,'14400.00'],['total-1dp','12','1200.00','14400.0'],['monthly-exponent','2','1e2','200.00']
      ];
      await fill('1200','1');
      for(const [label,monthsJson,monthly,total] of bad) {
        body=forged(monthly,total,monthsJson);
        await send();await refused(label);
        if(label==='true') {await screenshot('forged-months-true');await axe('forged-months-true');}
      }
      // Valid forged integers (cents arithmetic, no float drift) still render with the existing grammar.
      for(const [n,monthly,total,line] of [
        [1,'1200.00','1200.00','An extra S$1,200.00 a month for 1 month adds up to S$1,200.00.'],
        [3,'0.10','0.30','An extra S$0.10 a month for 3 months adds up to S$0.30.'],
        [7,'99999.99','699999.93','An extra S$99,999.99 a month for 7 months adds up to S$699,999.93.'],
        [120,'100000.00','12000000.00','An extra S$100,000.00 a month for 120 months adds up to S$12,000,000.00.']]) {
        body=forged(monthly,total,String(n));
        await send();await page.locator('#care-result:not([hidden])').waitFor();
        const text=await page.locator('#care-result').innerText();
        assert.ok(text.includes(line),text);
        assert.ok(text.includes(n===1?'Over 1 month':`Over ${n} months`),text);
        assert.doesNotMatch(text,/\b1 months\b/);
        if(n===1) await screenshot('forged-months-1-valid');
        if(mode.endsWith('-375')) assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
        await page.getByRole('button',{name:'Change my numbers'}).click();
      }
      await page.unroute('**/api/scenarios/S016/preview');
      // Real API, unforged, still succeeds.
      await fill('1200','1');await preview();
      assert.ok((await page.locator('#care-result').innerText()).includes('An extra S$1,200.00 a month for 1 month adds up to S$1,200.00.'));
    } else if(mode==='cxuifu2-heading'||mode==='cxuifu2-heading-375') {
      // CXUI-001-F-D01: force a general failure and field error(s) to coexist, as in the Designer's repro.
      const general="We couldn't work this out just now. Your answers are kept. Please try again.";
      const force=async()=>page.locator('#care-errors').evaluate((el,text)=>{
        el.querySelector('#care-error-heading').textContent='Something went wrong';
        const p=document.createElement('p');p.textContent=text;el.querySelector('#care-error-heading').after(p);
      },general);
      const heading=()=>page.locator('#care-error-heading').innerText();
      // (a) server-mapped months error + general; edit cost.
      await fill('1200','12');
      await page.route('**/api/scenarios/S016/preview',route=>route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({detail:'x',field:'months',code:'months'})}));
      await submit.click();await page.locator('#care-errors:not([hidden])').waitFor();
      await force();
      assert.equal(await heading(),'Something went wrong');
      assert.equal(await page.getByText(general,{exact:true}).isVisible(),true);
      await screenshot('combined-before-edit');
      await cost.fill('1500');
      assert.equal(await page.locator('#care-errors').isVisible(),true);
      assert.equal(await heading(),'Please check these answers');
      assert.equal(await page.getByText(general,{exact:true}).count(),0,'R-D02: general message cleared on edit');
      assert.equal(await page.locator('#care-errors a[href="#care-months"]').count(),1,'D03: months error kept');
      assert.equal(await months.getAttribute('aria-invalid'),'true');
      assert.equal(await page.locator('#care-months-error').isVisible(),true);
      assert.equal(await cost.getAttribute('aria-invalid'),'false');
      await screenshot('combined-after-edit');await axe('combined-after-edit');
      await months.fill('12');
      assert.equal(await page.locator('#care-errors').isVisible(),false);
      // (b) both client field errors + general; edit months; cost error kept, heading corrected.
      await page.unroute('**/api/scenarios/S016/preview');
      await fill('','0');await submit.click();await page.locator('#care-errors:not([hidden])').waitFor();
      await force();
      await months.fill('6');
      assert.equal(await heading(),'Please check these answers');
      assert.equal(await page.getByText(general,{exact:true}).count(),0);
      assert.equal(await page.locator('#care-errors a[href="#care-cost"]').count(),1);
      assert.equal(await page.locator('#care-errors a[href="#care-months"]').count(),0);
      assert.equal(await cost.getAttribute('aria-invalid'),'true');
      // Clicking the remaining link still moves focus to its field.
      await page.locator('#care-errors a[href="#care-cost"]').click();await focused('#care-cost');
      // (c) pure general failure (R-D02 path): edit hides the whole summary.
      await page.route('**/api/scenarios/S016/preview',route=>route.abort());
      await fill('1200','12');await submit.click();await page.getByText(general,{exact:true}).waitFor();
      assert.equal(await heading(),'Something went wrong');
      await months.fill('24');
      assert.equal(await page.locator('#care-errors').isVisible(),false);
      // (d) field-only summary is unchanged by the fix.
      await page.unroute('**/api/scenarios/S016/preview');
      await fill('','');await submit.click();await cost.fill('5');
      assert.equal(await heading(),'Please check these answers');
      assert.equal(await page.locator('#care-errors a[href="#care-months"]').count(),1);
      await months.fill('3');await preview();
      assert.ok((await page.locator('#care-result').innerText()).includes('An extra S$5.00 a month for 3 months adds up to S$15.00.'));
    } else if(mode==='cxui-d09') {
      const tokens=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../design/sweelah/DESIGN_TOKENS.json'))).palette;
      for(const key of ['ink','cream','mint','green','coral']) assert.equal((await page.locator('html').evaluate((el,key)=>getComputedStyle(el).getPropertyValue('--'+key).trim(),key)).toLowerCase(),tokens[key].toLowerCase());
      assert.equal(await page.locator('.wordmark b').evaluate(el=>getComputedStyle(el).color),'rgb(250, 98, 73)');
      assert.equal(await page.locator('.eyebrow').evaluate(el=>getComputedStyle(el).textTransform),'uppercase');
      await screenshot('setup');await axe('setup');await submit.click();await screenshot('field-errors');await axe('field-errors');
      await fill('1200','12');await preview();await screenshot('result');await axe('result');
    } else if(mode==='cxui-d10') {
      for(const state of ['setup','errors','result']) {
        if(state==='errors') await submit.click();
        if(state==='result') {await fill('1200','12');await preview();}
        const levels=await page.locator('h1,h2,h3,h4,h5,h6').evaluateAll(els=>els.filter(el=>el.getClientRects().length).map(el=>Number(el.tagName[1])));
        let previous=0;for(const level of levels) {assert.ok(level<=previous+1,`${state}: ${previous} to ${level}`);previous=level;}
      }
    } else if(mode==='cxui-d11') {
      const box=await page.locator('header a').boundingBox();assert.ok(box.width>=44&&box.height>=44);
    } else if (mode==='success'||mode==='mobile') {
      await page.screenshot({path:path.join(output,'setup-'+mode+'.png'),fullPage:true});
      await fill('S$1,200','12');
      const responsePromise=page.waitForResponse(r=>r.url().endsWith('/api/scenarios/S016/preview'));
      await preview();
      const response=await responsePromise, body=await response.json();
      assert.equal(response.status(),200);
      assert.equal(body.may_post_to_household_projection,false);
      assert.equal(body.status,'LIMITED_RECURRING_COST_PREVIEW_ONLY');
      assert.deepEqual(response.request().postDataJSON().params,{additional_care_cost_monthly:'1200',months:12});
      await focused('#care-result h2');
      const text=await page.locator('section').innerText();
      for (const expected of ['YOUR ESTIMATE','Your parent-care cost estimate','S$1,200.00','S$14,400.00',
        "This doesn't change your main retirement plan.",'no inflation',
        'CareShield LIFE','lost pay or unpaid leave']) assert.ok(text.includes(expected),expected);
      await page.screenshot({path:path.join(output,'success-'+mode+'.png'),fullPage:true});
      await page.getByRole('button',{name:'Change my numbers',exact:true}).click();
      assert.equal(await cost.inputValue(),'S$1,200'); assert.equal(await months.inputValue(),'12');
      await focused('#care-cost');
      assert.equal(await page.locator('#care-result').isVisible(),false);
      await fill('12.50','1'); await preview();
      assert.ok((await page.locator('#care-result').innerText()).includes('S$12.50'));
      if (mode==='mobile') assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    } else if (mode==='errors') {
      for (const [c,m,costMessage,monthsMessage] of [
        ['','','Please enter how much extra you expect to spend on care each month.','Enter the number of months, from 1 to 120 (10 years).'],
        ['0','0','Enter an amount more than S$0.','Enter the number of months, from 1 to 120 (10 years).'],
        ['-1','121','Enter an amount more than S$0.','Enter the number of months, from 1 to 120 (10 years).'],
        ['abc','1.5','Enter numbers only, for example 1200.','Enter the number of months, from 1 to 120 (10 years).'],
        ['true','true','Enter numbers only, for example 1200.','Enter the number of months, from 1 to 120 (10 years).'],
      ]) {
        await fill(c,m); await submit.click(); await focused('#care-errors');
        assert.ok((await page.locator('#care-errors').innerText()).includes('Please check these answers'));
        assert.equal(await cost.inputValue(),c); assert.equal(await months.inputValue(),m);
        for (const [field,message] of [[cost,costMessage],[months,monthsMessage]]) {
          assert.equal(await field.getAttribute('aria-invalid'),'true');
          const ids=(await field.getAttribute('aria-describedby')).split(' ');
          assert.ok(ids.length>=2);
          const inline=await page.locator('#'+ids.at(-1)).innerText();
          assert.equal(inline,'Error: '+message);
        }
        assert.equal(await page.locator('#care-result').isVisible(),false);
        await page.locator('#care-errors a[href="#care-cost"]').click(); await focused('#care-cost');
        await page.locator('#care-errors a[href="#care-months"]').click(); await focused('#care-months');
      }
      await page.screenshot({path:path.join(output,'error.png'),fullPage:true});
      await fill('1200','12'); await preview();
      await page.getByRole('button',{name:'Change my numbers',exact:true}).click();
      await months.fill(''); await submit.click();
      assert.equal(await page.locator('#care-result').isVisible(),false);
    } else if (mode==='server-refusal') {
      // Change only the outgoing duration; the real local API refuses it. No fake response.
      await page.route('**/api/scenarios/S016/preview',route=>{
        const body=route.request().postDataJSON();body.params.months=true;
        return route.continue({postData:JSON.stringify(body)});
      });
      await fill('1200','12'); await submit.click();
      await page.locator('#care-errors:not([hidden])').waitFor(); await focused('#care-errors');
      assert.ok((await page.locator('#care-errors').innerText()).includes('Enter the number of months, from 1 to 120 (10 years).'));
      assert.equal(await months.inputValue(),'12');
      assert.equal(await page.locator('#care-result').isVisible(),false);
      await page.unroute('**/api/scenarios/S016/preview');
      await page.route('**/api/scenarios/S016/preview',route=>route.abort());
      await submit.click();
      await page.getByText("We couldn't work this out just now. Your answers are kept. Please try again.",{exact:true}).waitFor();
      assert.equal(await cost.inputValue(),'1200');
    } else if (mode==='precision'||mode==='mobile375') {
      const geometry=async()=>{
        const overflow=await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(el=>el.getClientRects().length&&el.clientWidth>0).filter(el=>el.scrollWidth>el.clientWidth||el.scrollWidth>innerWidth).map(el=>({tag:el.tagName,id:el.id,class:el.className,client:el.clientWidth,scroll:el.scrollWidth})));
        assert.deepEqual(overflow,[]);
        const status=page.getByText('Preview status:',{exact:false});
        if (await status.isVisible()) {
          const box=await status.boundingBox();assert.ok(box.x+box.width<=375);
        }
      };
      if(mode==='mobile375') {await fill('1200','12');await preview();await geometry();await page.getByRole('button',{name:'Change my numbers',exact:true}).click();}
      let precisionRequests=0;
      const countPreview=request=>{if(request.url().endsWith('/api/scenarios/S016/preview')) precisionRequests++;};
      page.on('request',countPreview);
      for (const invalid of ['1.500','0.0001','1.005']) {
        await fill(invalid,'12');await submit.click();
        await page.locator('#care-errors:not([hidden])').waitFor();await focused('#care-errors');
        assert.equal(await page.locator('#care-cost-error').innerText(),'Error: Enter an amount with up to 2 decimal places, for example 1200.50.');
        assert.equal(await cost.inputValue(),invalid);
        assert.equal(await page.locator('#care-result').isVisible(),false);
      }
      assert.equal(precisionRequests,0,'invalid precision must not reach the API');
      page.off('request',countPreview);
      if(mode==='mobile375') {await geometry();await page.screenshot({path:path.join(output,'375-errors.png'),fullPage:true});}
      await page.route('**/api/scenarios/S016/preview',route=>{
        const body=route.request().postDataJSON();body.params.additional_care_cost_monthly='1.005';
        return route.continue({postData:JSON.stringify(body)});
      });
      await fill('1.50','12');await submit.click();
      await page.locator('#care-errors:not([hidden])').waitFor();
      assert.equal(await page.locator('#care-cost-error').innerText(),'Error: Enter an amount with up to 2 decimal places, for example 1200.50.');
      assert.equal(await page.locator('#care-result').isVisible(),false);
      await page.unroute('**/api/scenarios/S016/preview');
      for(const [amount,monthly,total] of [['1.50','S$1.50','S$18.00'],['1,200.5','S$1,200.50','S$14,406.00'],['100','S$100.00','S$1,200.00']]) {
        await fill(amount,'12');await preview();
        assert.ok((await page.locator('#care-result').innerText()).includes(`An extra ${monthly} a month for 12 months adds up to ${total}.`));
        if(mode==='mobile375') await geometry();
        if(mode==='mobile375'&&amount==='1.50') await page.screenshot({path:path.join(output,'375-success.png'),fullPage:true});
        await page.getByRole('button',{name:'Change my numbers',exact:true}).click();
      }
    } else if (mode==='accessibility') {
      const primary=page.getByRole('button',{name:'Preview care cost',exact:true});
      for (const target of [cost,months,primary,page.getByRole('button',{name:'Talk to Swee',exact:true})]) {
        const box=await target.boundingBox(); assert.ok(box.width>=24&&box.height>=24);
        assert.ok(await target.evaluate(el=>parseFloat(getComputedStyle(el).fontSize)>=16));
      }
      const contrast=(a,b)=>{
        const luminance=hex=>{const parts=hex.match(/\w\w/g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return parts[0]*.2126+parts[1]*.7152+parts[2]*.0722;};
        const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);
      };
      for (const pair of [['253646','fff8eb'],['1c806e','ffffff'],['40585e','ffffff'],['922818','ffffff'],['253646','ffefca']]) assert.ok(contrast(...pair)>=4.5,pair.join('/'));
      assert.ok(await cost.evaluate(el=>Boolean(document.querySelector('label[for="'+el.id+'"]'))));
      assert.equal(await cost.getAttribute('inputmode'),'decimal');
      assert.equal(await months.getAttribute('inputmode'),'numeric');
      await cost.focus();await page.keyboard.type('1200');await page.keyboard.press('Tab');await focused('#care-months');
      await page.keyboard.type('12');await page.keyboard.press('Tab');
      assert.equal(await primary.evaluate(el=>el===document.activeElement),true);
      await page.keyboard.press('Enter');await page.locator('#care-result:not([hidden])').waitFor();await focused('#care-result h2');
      let axePath=process.env.AXE_CORE_PATH;
      if (!axePath) {try {axePath=require.resolve('axe-core/axe.min.js');} catch {}}
      if (axePath) {
        await page.addScriptTag({path:axePath});
        const audit=await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}}));
        assert.deepEqual(audit.violations,[]); console.log('axe WCAG checks PASS');
      } else console.log('axe unavailable offline; keyboard, ARIA, target sizes and selected color pairs checked, not a full WCAG audit');
    } else if (mode==='nonmutation') {
      const dashboard=await browser.newPage();
      await dashboard.goto(base+'/');
      await dashboard.locator('#metrics').waitFor();
      await dashboard.waitForFunction(()=>document.querySelectorAll('#metrics .metric').length===4);
      const snapshot=()=>dashboard.evaluate(()=>Object.fromEntries(['metrics','scenarioSummary','graph','raw'].map(id=>[id,document.getElementById(id).innerHTML])));
      const before=await snapshot();
      const sample=await (await page.request.get(base+'/api/sample')).json();
      const evaluation=async()=> (await page.request.post(base+'/api/evaluate',{data:{profile:sample,years:2}})).json();
      const projection=await evaluation();
      await fill('1200','12');await preview();
      assert.deepEqual(await evaluation(),projection);
      await dashboard.reload();
      await dashboard.waitForFunction(()=>document.querySelectorAll('#metrics .metric').length===4);
      assert.deepEqual(await snapshot(),before);
      await dashboard.close();
    }
    assert.deepEqual(errors,[]);
    console.log('PASS S016 browser '+mode+' (Chromium '+browser.version()+')');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
