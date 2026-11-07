const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const [mode, base] = process.argv.slice(2);
const output = path.resolve(__dirname, '../../test-artifacts/s016');
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
    const page = await browser.newPage({viewport:mode==='mobile375'?{width:375,height:844}:mode==='mobile'?{width:390,height:844}:{width:1280,height:960},reducedMotion:'reduce'});
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
    if (mode==='success'||mode==='mobile') {
      await page.screenshot({path:path.join(output,'setup-'+mode+'.png'),fullPage:true});
      await fill('S$1,200','12');
      const responsePromise=page.waitForResponse(r=>r.url().endsWith('/api/scenarios/S016/preview'));
      await preview();
      const response=await responsePromise, body=await response.json();
      assert.equal(response.status(),200);
      assert.equal(body.may_post_to_household_projection,false);
      assert.equal(body.status,'LIMITED_RECURRING_COST_PREVIEW_ONLY');
      assert.deepEqual(response.request().postDataJSON().params,{additional_care_cost_monthly:'1200',months:12});
      await focused('#care-result h3');
      const text=await page.locator('#care-result').innerText();
      for (const expected of ['Limited preview','Your parent-care cost estimate','S$1,200.00','S$14,400.00',
        "This doesn't change your main retirement plan.",'no inflation','no assumed entitlement',
        'CareShield LIFE','lost pay or unpaid leave','Illustrative recurring care costs only; leave, insurance and subsidies omitted']) assert.ok(text.includes(expected),expected);
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
      for (const invalid of ['1.500','0.0001','1e-3','1.005']) {
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
      for(const [amount,monthly,total] of [['1.50','S$1.50','S$18.00'],['1,200.5','S$1,200.50','S$14,406.00'],['1e2','S$100.00','S$1,200.00']]) {
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
      for (const pair of [['253646','fff8eb'],['146d5b','ffffff'],['40585e','ffffff'],['922818','ffffff'],['253646','ffefca']]) assert.ok(contrast(...pair)>=4.5,pair.join('/'));
      assert.ok(await cost.evaluate(el=>Boolean(document.querySelector('label[for="'+el.id+'"]'))));
      assert.equal(await cost.getAttribute('inputmode'),'decimal');
      assert.equal(await months.getAttribute('inputmode'),'numeric');
      await cost.focus();await page.keyboard.type('1200');await page.keyboard.press('Tab');await focused('#care-months');
      await page.keyboard.type('12');await page.keyboard.press('Tab');
      assert.equal(await primary.evaluate(el=>el===document.activeElement),true);
      await page.keyboard.press('Enter');await page.locator('#care-result:not([hidden])').waitFor();await focused('#care-result h3');
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
