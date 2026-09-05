import re

with open("frontend/src/pages/AcceptInvitation.tsx", "r", encoding="utf-8") as f: c = f.read()
c = c.replace("invitation?.role", "(invitation && (invitation as any).role)")
with open("frontend/src/pages/AcceptInvitation.tsx", "w", encoding="utf-8") as f: f.write(c)

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f: c = f.read()
c = c.replace("((sourceInfo.config as any)?.url || '').replace", "String((sourceInfo.config as any)?.url || '').replace")
c = c.replace("<div>{String((sourceInfo.config as any)?.size)} bytes</div>", "<div>{String((sourceInfo.config as any)?.size || '')} bytes</div>")
with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f: f.write(c)

with open("frontend/src/pages/InvestigationView.tsx", "r", encoding="utf-8") as f: c = f.read()
c = c.replace("String((incident.final_report as any) || '')", "JSON.stringify(incident.final_report || {}) as any")
with open("frontend/src/pages/InvestigationView.tsx", "w", encoding="utf-8") as f: f.write(c)

print("TS hacks")
