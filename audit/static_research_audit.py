import json,re
from pathlib import Path
r=Path(__file__).resolve().parents[1]
html=(r/'retirepilot/ui.html').read_text()
q={
'html_lang_english': bool(re.search(r'<html lang="en"',html)),
'explicit_labels_for_core_inputs':all(f'for="{x}"' in html for x in ('profile','inflation','returns','years','stress','query')),
'visible_keyboard_focus_style':':focus-visible' in html,
'aria_live_reply':'aria-live="polite"' in html,
'responsive_media_styles':'@media(max-width:550px)' in html,
'raw_json_editor_present':'<textarea id="profile"' in html,
'guided_user_onboarding_implemented':False,
'supported_multilingual_experience':False,
'screen_reader_table_for_chart':False,
'persistent_action_completion':False,
'accessible_full_browser_QA':'blocked_by_administrator'
}
(r/'audit/phase8_static_ux_audit.json').write_text(json.dumps(q,indent=2))
print(json.dumps(q,indent=2))
