from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.units import mm
import json

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'audit/Phase2to5_Remediation_Evidence_v2.2.json').read_text())
OUT=Path('/mnt/data/RetirePilot_Phases1to8_Reaudit_v2.2.pdf')
PAGE=landscape(A4)
navy=colors.HexColor('#18354A');teal=colors.HexColor('#2C686B');muted=colors.HexColor('#516171');red=colors.HexColor('#8B3333');gold=colors.HexColor('#835D32')
white=colors.white; pale=colors.HexColor('#EEF3F5')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='RPTitle',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=19,leading=23,spaceAfter=10,textColor=navy,alignment=TA_LEFT))
styles.add(ParagraphStyle(name='RPSection',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=11,leading=14,spaceBefore=15,spaceAfter=7,textColor=teal))
styles.add(ParagraphStyle(name='RPBody',fontName='Helvetica',fontSize=9,leading=13,spaceAfter=7,textColor=navy))
styles.add(ParagraphStyle(name='RPCell',fontName='Helvetica',fontSize=7.5,leading=10,textColor=navy))
styles.add(ParagraphStyle(name='RPCellBold',fontName='Helvetica-Bold',fontSize=7.5,leading=10,textColor=navy))
styles.add(ParagraphStyle(name='RPAlert',fontName='Helvetica-Bold',fontSize=10,leading=13,spaceAfter=10,textColor=red))
styles.add(ParagraphStyle(name='RPHeader',fontName='Helvetica-Bold',fontSize=7.5,leading=10,textColor=white))

def p(x,style='RPCell'):
    return Paragraph(escape(str(x)),styles[style])

def table(headers,records,widths):
    rows=[[p(h,'RPHeader') for h in headers]] + [[p(v) for v in r] for r in records]
    t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),navy),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,pale]),
        ('LINEBELOW',(0,0),(-1,0),0.8,teal),('LINEBELOW',(0,1),(-1,-1),0.25,colors.HexColor('#D6E0E5')),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)
    ]))
    return t

def foot(c,doc):
    c.saveState();c.setStrokeColor(colors.HexColor('#D9E1E6'));c.line(38,32,PAGE[0]-38,32)
    c.setFont('Helvetica',8);c.setFillColor(muted)
    c.drawString(38,20,'RetirePilot v2.2 | Internal synthetic engineering evidence only')
    c.drawRightString(PAGE[0]-38,20,f'{doc.page}')
    c.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=PAGE,rightMargin=38,leftMargin=38,topMargin=36,bottomMargin=43,
                      title='RetirePilot Phase 2-5 Remediation and 1-8 Re-audit v2.2',author='RetirePilot engineering audit')
story=[Paragraph('RetirePilot | Remediation and Re-audit',styles['RPTitle']),
       Paragraph('3 November 2026   |   Phases 2-5 fixed where technically possible   |   Reassessment of Phases 1-8',styles['RPBody']),
       Paragraph('RELEASE DECISION: PHASE 9 NO-GO',styles['RPAlert']),
       Paragraph('The identified retirement-timing, missing-deduction, zero-score, cash-yield and first-year-date failures are now corrected in the synthetic technical prototype. Mortgage amortisation is implemented, but its full CPF, refinancing and maturity handling is not. No independent financial or regulatory sign-off has been obtained.',styles['RPBody']),
       Paragraph('Executed tests: 378 / 378 pytest checks, 498 / 498 classifier rule-contract checks and 10 / 10 localhost API smoke checks. All are self-run with synthetic inputs, not external verification.',styles['RPBody']),
       Paragraph('Phase-by-phase release assessment',styles['RPSection'])]
story.append(table(['Phase','Verdict','Evidence','Outstanding blocker'],
                   [(v['phase'],v['verdict'],v['observed_evidence'],v['open_gap']) for v in DATA['phases']],[43,156,276,288]))
story.append(Paragraph('Reproduced fixes',styles['RPSection']))
repros=DATA['reproductions']
story.append(table(['Defect','Measured outcome'],[
    ('Retirement age',f"Age 55 target yields S${repros['retirement_income_2030_age55']} earned income in 2030; age 65 target yields S${repros['retirement_income_2030_age65']}."),
    ('Missing deductions',f"Projection status: {repros['missing_deductions_projection_status']}. Unknown amounts are not treated as zero."),
    ('Zero-score persona','0/100 and all scores under provisional 60-point threshold cannot enter top three.'),
    ('Cash return',f"Cash-only investment gain: S${repros['cash_only_investment_gain']}; cash yield separately parameterised."),
    ('Partial first year','The 2026 projection covers Nov 3 through Dec 31, including prorated income, expenses and mortgage payments.'),
    ('Mortgage amortisation','Tracks interest, principal, remaining balance and CPF-funded debt payments; does not reduce CPF OA balances.')
],[138,625]))
story.append(Paragraph('Remaining blockers (18-item tracking register)',styles['RPSection']))
story.append(table(['ID','Area','Status','What the evidence actually establishes'],[(k['id'],k['name'],k['state'],k['evidence']) for k in DATA['blockers']],[63,162,137,401]))
story.append(Paragraph('What still prevents Phase 9',styles['RPSection']))
for ix,txt in enumerate([
'Approve and calibrate the 96 persona weights, 60-point threshold and financial relevance using independently labelled cases.',
'Complete authenticated data persistence, household consent controls, privacy/security and legal review. Never use the synthetic API guard for real records.',
'Implement official-source reconciled CPF, SEP/platform contributions, CPF LIFE inputs, tax and housing calculations. Explicitly address all 46 scenarios or limit scope.',
'Complete the real financial-assistant safety layer, guided onboarding, personal memory controls and accessible interface.',
'Obtain independent QA, financial-domain assurance, Singapore financial-advice legal opinion and 30-50 genuine moderated research interviews.'
],1):story.append(Paragraph(f'<b>{ix}.</b> {escape(txt)}',styles['RPBody']))
story.append(Paragraph('Technical evidence package',styles['RPSection']))
story.append(Paragraph('Source and reproducible test scripts are included in RetirePilot_Remediated_v2_2.zip. See README_REMEDIATION_v2.2.md, audit/test_run_v22.txt, audit/classifier_rule_contracts_v2_2.json, audit/api_evidence.json, and audit/Phase2to5_Remediation_Evidence_v2.2.json. Earlier PSD/TSD v2.0 are superseded for financial timing and formulas.',styles['RPBody']))
doc.build(story,onFirstPage=foot,onLaterPages=foot)
print(str(OUT), OUT.stat().st_size)
