"""Local-only interactive research prototype. Never expose to the public internet.
Run: uvicorn retirepilot.api:app --host 127.0.0.1 --port 8766
"""
import json
from decimal import DecimalException
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from .priority_scenarios_v27 import preview_priority_scenario
from .service import evaluate
from .assistant import answer
from .core import ValidationError
from .llm_adapter import explain_synthetic,ModelDisabledError
from .financial_references_v24 import resident_tax_reference,static_cpf_interest_reference,housing_sale_reference,employee_cpf_schedule_2026_27
from .planner_session_v24 import guided_reply

ROOT=Path(__file__).resolve().parent.parent
app=FastAPI(title='RetirePilot prototype',version='2.7.0',docs_url=None,redoc_url=None)

def require_synthetic_fixture(profile):
    if not isinstance(profile,dict) or not str(profile.get('id','')).startswith('RP-SYNTH-'):
        raise HTTPException(403,'Only synthetic fixture IDs accepted; never submit actual financial records')

async def body_json(req):
    b=await req.body()
    if len(b)>250_000:raise HTTPException(413,'Prototype payload too large')
    try:return json.loads(b)
    except (ValueError,UnicodeDecodeError):raise HTTPException(400,'Invalid JSON')

@app.get('/',response_class=HTMLResponse)
def index():return (ROOT/'retirepilot/ui.html').read_text(encoding='utf-8')

@app.get('/api/sample')
def sample():return json.loads((ROOT/'data/mixed_income_household.json').read_text())

@app.get('/api/scenarios')
def scenario_sample():return json.loads((ROOT/'data/scenarios.json').read_text())

@app.post('/api/evaluate')
async def assess(req:Request):
    data=await body_json(req)
    try:
        profile=data['profile']
        require_synthetic_fixture(profile)
        scenarios=data.get('scenarios',[])
        if not isinstance(scenarios,list) or len(scenarios)>8:raise ValidationError('scenarios must contain at most 8 entries')
        years=int(data.get('years',15))
        if years<1 or years>50:raise ValidationError('years must be 1-50')
        return evaluate(profile,scenarios,years)
    except (ValueError,KeyError,TypeError) as e:raise HTTPException(422,str(e))

@app.post('/api/ask')
async def ask(req:Request):
    data=await body_json(req)
    try:
        require_synthetic_fixture(data['profile'])
        if data.get('use_experimental_llm'):
            return explain_synthetic(data['profile'],data['question'],explicit_consent=data.get('explicit_model_consent',False))
        return answer(data['profile'],data['question'])
    except ModelDisabledError as e:raise HTTPException(403,str(e))
    except (ValueError,KeyError,TypeError) as e:raise HTTPException(422,str(e))


REFERENCE_FUNCTIONS={'resident_tax':resident_tax_reference,'cpf_interest_static':static_cpf_interest_reference,'housing_sale':housing_sale_reference,'employee_cpf_schedule':employee_cpf_schedule_2026_27}

@app.post('/api/reference')
async def reference_calculation(req:Request):
    """Synthetic-only, bounded official-source calculations. No raw records retained."""
    data=await body_json(req)
    require_synthetic_fixture({'id':data.get('synthetic_profile_id','')})
    kind=data.get('kind')
    if kind not in REFERENCE_FUNCTIONS:raise HTTPException(422,'Unsupported reference calculation')
    params=data.get('params')
    if not isinstance(params,dict):raise HTTPException(422,'params must be object')
    try:return REFERENCE_FUNCTIONS[kind](**params)
    except (ValueError,TypeError) as exc:raise HTTPException(422,str(exc))

@app.post('/api/guide')
async def guided_assistant(req:Request):
    data=await body_json(req)
    require_synthetic_fixture(data.get('profile'))
    try:return guided_reply(data['profile'],data.get('question',''))
    except (ValueError,KeyError,TypeError) as exc:raise HTTPException(422,str(exc))

@app.get('/api/release-controls')
def release_controls():
    """Non-personal, read-only public release gate statuses."""
    return {'identity_verification':'not_integrated',
            'independent_adult_consent':'not_verified',
            'household_sharing':'blocked',
            'cpf_life':'member_transcribed_official_estimate_only',
            'persona_display':'provisional_descriptions_no_scores',
            'product_advice':'not_permitted',
            'external_consumer_pilot':'NO_GO',
            'consumer_research':'assumed_pass_for_planning_only; real 48 person study remains required'}


@app.get('/sweelah', response_class=HTMLResponse)
def sweelah_care_setup():
    """Wired care-setup screen; preserved design prototypes remain untouched."""
    return (ROOT / 'retirepilot/s016.html').read_text(encoding='utf-8')


@app.post('/api/scenarios/S016/preview')
async def parent_care_preview(req: Request):
    """Synthetic, stateless cost preview. Never posts to the household forecast."""
    data = await body_json(req)
    if not isinstance(data, dict):
        raise HTTPException(422, 'request must be an object')
    require_synthetic_fixture({'id': data.get('synthetic_profile_id', '')})
    params = data.get('params')
    try:
        result = preview_priority_scenario('S016', params)
    except (ValueError, TypeError, KeyError) as exc:
        detail = str(exc)
        if detail == 'additional_care_cost_monthly: nonnegative amount required':
            detail = 'additional_care_cost_monthly must be more than 0'
        raise HTTPException(422, detail) from exc
    except DecimalException as exc:
        raise HTTPException(422, 'additional_care_cost_monthly: amount cannot be represented') from exc
    return {
        **result,
        'months': params['months'],
        'synthetic_only': True,
        'label': 'Synthetic-only illustrative parent-care cost preview; not part of the plan',
        'limitations': [
            'No assumed subsidy or grant.',
            'No assumed insurance payout, including CareShield LIFE, or MediSave payment.',
            'No assumed caregiver wage loss or care leave.',
            'No assumed entitlement or benefit eligibility.',
            'Flat monthly amount with no inflation; general information, not financial advice.',
        ],
    }
