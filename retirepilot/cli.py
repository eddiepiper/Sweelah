"""Run `python -m retirepilot.cli demo` or `... assess /path/to/profile.json`."""
import json,sys
from pathlib import Path
from .service import evaluate
from .assistant import answer

def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else 'demo'
    root=Path(__file__).resolve().parent.parent
    if cmd=='demo':
        profile=json.loads((root/'data/mixed_income_household.json').read_text())
        scenarios=json.loads((root/'data/scenarios.json').read_text())
        result=evaluate(profile,scenarios,projection_years=15)
    elif cmd=='assess':
        if len(sys.argv)<3:raise SystemExit('Usage: python -m retirepilot.cli assess profile.json [scenarios.json]')
        profile=json.loads(Path(sys.argv[2]).read_text())
        scenarios=json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv)>3 else []
        result=evaluate(profile,scenarios,projection_years=15)
    elif cmd=='ask':
        profile=json.loads((root/'data/mixed_income_household.json').read_text())
        result=answer(profile,' '.join(sys.argv[2:]))
    else:raise SystemExit('Unknown command')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
