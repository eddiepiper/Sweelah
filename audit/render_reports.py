from pathlib import Path
import mistune
from weasyprint import HTML,CSS
p=Path(__file__).resolve().parents[1]/'audit'
css='''
@page {size:A4; margin:17mm 18mm 16mm 18mm; @bottom-center{content:"RetirePilot | 3 November 2026  -  Page " counter(page);font-size:8px;color:#718096}}
body{font-family:DejaVu Sans,Arial,sans-serif;font-size:9px;line-height:1.5;color:#1A2C3D}
h1{font-size:21px;color:#15394A;border-bottom:3px solid #5FA99F;padding-bottom:8px;margin:0 0 17px}h2{font-size:13.5px;color:#15394A;line-height:1.35;margin:22px 0 9px;page-break-after:avoid}h3{font-size:10.5px;color:#22545A;margin:12px 0 7px}p{margin:7px 0 10px}strong{color:#0F2C3A}table{border-collapse:collapse;width:100%;margin:10px 0 14px;table-layout:fixed;font-size:7.8px}thead{display:table-header-group}tr{page-break-inside:avoid}td,th{border:1px solid #D8E2E7;padding:6px 7px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#E9F2F1;color:#1E3F4B}tr:nth-child(even) td{background:#F8FAFB}blockquote{border-left:3px solid #5FA99F;padding:5px 10px;background:#F0F6F4}ul,ol{padding-left:19px;margin:7px 0 12px}li{margin:3px 0}code{font-family:DejaVu Sans Mono,monospace;font-size:8px;background:#F1F4F7;padding:1px 3px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#F1F4F7;border:1px solid #DDE5E9;padding:9px;font-size:8px}pre code{padding:0}a{color:#1B6F76;overflow-wrap:anywhere}hr{border:0;border-top:1px solid #DDE5E9;margin:15px 0}*{orphans:2;widows:2}
'''
md=mistune.create_markdown(plugins=['table'])
for stem,out in [('Phase7_Independent_Financial_and_Policy_Audit','RetirePilot_Phase7_Validation_Report_v2.1.pdf'),('Phase8_Consumer_Research_and_Usability_Plan','RetirePilot_Phase8_Research_Protocol_v1.0.pdf')]:
    content=(p/(stem+'.md')).read_text()
    body=md(content)
    HTML(string='<html><meta charset="utf-8"><body>'+body+'</body></html>',base_url=str(p)).write_pdf('/mnt/data/'+out,stylesheets=[CSS(string=css)])
    print('/mnt/data/'+out)
