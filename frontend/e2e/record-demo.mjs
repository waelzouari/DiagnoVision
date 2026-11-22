import {chromium} from '@playwright/test';
import {mkdir,rename} from 'node:fs/promises';
import path from 'node:path';

const outputDir=path.resolve('demo-video');
await mkdir(outputDir,{recursive:true});
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({
  viewport:{width:1440,height:900},
  recordVideo:{dir:outputDir,size:{width:1280,height:720}},
  locale:'en-US',
  colorScheme:'light',
});
const page=await context.newPage();

const pause=ms=>page.waitForTimeout(ms);
async function caption(title,subtitle){
  await page.evaluate(({title,subtitle})=>{
    document.querySelector('#demo-caption')?.remove();
    const box=document.createElement('div');box.id='demo-caption';
    box.style.cssText='position:fixed;z-index:99999;left:50%;bottom:28px;transform:translateX(-50%);width:min(860px,82vw);padding:14px 20px;border-radius:14px;background:rgba(15,23,42,.93);color:white;box-shadow:0 18px 45px rgba(15,23,42,.28);font-family:Inter,Arial,sans-serif;text-align:center;pointer-events:none';
    box.innerHTML=`<div style="font-size:20px;font-weight:800">${title}</div><div style="margin-top:4px;font-size:13px;color:#cbd5e1">${subtitle}</div>`;
    document.body.appendChild(box);
  },{title,subtitle});
}
async function removeCaption(){await page.evaluate(()=>document.querySelector('#demo-caption')?.remove())}
async function smoothScroll(y){await page.evaluate(value=>window.scrollTo({top:value,behavior:'smooth'}),y);await pause(1200)}

await page.goto('http://127.0.0.1:5174/login');
await caption('DiagnoVision','From clinical conversation to an explainable patient review');
await pause(2500);
await removeCaption();
await page.getByLabel('Email address').fill('doctor@diagnovision.local');
await page.getByLabel('Password').fill('DemoPass123!');
await page.getByRole('button',{name:'Sign in securely'}).click();
await page.waitForURL('**/dashboard');
await caption('Clinical overview','Patient activity, approved facts and physician review queue');
await pause(4000);
await removeCaption();

await page.goto('http://127.0.0.1:5174/patients');
await page.getByText('Sami Gharbi',{exact:true}).waitFor();
await caption('Synthetic patient workspace','Every demonstration record is fictional');
await pause(3000);
await removeCaption();
const samiRow=page.locator('tr').filter({hasText:'Sami Gharbi'});
await samiRow.getByRole('link',{name:/Open record/i}).click();
await page.getByRole('heading',{name:'Sami Gharbi'}).waitFor();
const patientUrl=page.url();
const patientId=patientUrl.split('/patients/')[1].split(/[/?#]/)[0];
await caption('One longitudinal patient record','Timeline, observations, documents and AI review');
await pause(3500);
await removeCaption();

await page.goto(`http://127.0.0.1:5174/patients/${patientId}/recording-demo`);
await page.getByRole('heading',{name:'Consultation recording demo'}).waitFor();
await caption('Consent-first conversation capture','Audio remains local in this frontend demonstration');
await pause(3000);
await removeCaption();
await page.getByRole('checkbox',{name:/Patient recording consent confirmed/i}).check();
await page.getByRole('button',{name:/Use jury demo sample/i}).click();
await page.getByRole('heading',{name:/Raw transcript/i}).waitFor();
await caption('Raw transcript','The original simulated speech-to-text output is preserved');
await pause(3000);
await removeCaption();
await page.getByRole('button',{name:/Run data cleaning/i}).click();
await page.getByRole('heading',{name:/Cleaned transcript/i}).waitFor();
await caption('Data cleaning','Fillers removed, units normalized and clinical negations preserved');
await pause(4000);
await removeCaption();
await smoothScroll(760);
await pause(2500);

await page.goto(`http://127.0.0.1:5174/patients/${patientId}/documents`);
await page.getByRole('heading',{name:/Documents/i}).waitFor();
await caption('Medical documents','Synthetic OCR workspace for reports, laboratory values and source review');
await pause(3500);
await removeCaption();

await page.goto(`http://127.0.0.1:5174/patients/${patientId}/analytics`);
await page.getByRole('heading',{name:'Patient AI review'}).waitFor();
await caption('Five simulated AI agents','Voice, documents, fusion, risk hypotheses and review priority');
await pause(4000);
await removeCaption();
await smoothScroll(460);
await caption('Explainable risk hypotheses','Every result shows evidence, contradictions and missing information');
await pause(4000);
await removeCaption();
await smoothScroll(1050);
await caption('Transparent priority score','82/100 for record review — not an emergency-triage score');
await pause(4500);
await removeCaption();
await smoothScroll(0);
await caption('DiagnoVision','Synthetic data · Research prototype · Physician validation required');
await pause(3500);
await removeCaption();

const video=page.video();
await context.close();
await browser.close();
const recordedPath=await video.path();
const finalWebm=path.join(outputDir,'demo-diagnovision-60s.webm');
await rename(recordedPath,finalWebm);
console.log(finalWebm);
