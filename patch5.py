with open("frontend/src/pages/AcceptInvitation.tsx", "r", encoding="utf-8") as f: c = f.read()
c = c.replace("invitation?.tenant_name", "(invitation as any)?.tenant_name")
c = c.replace("invitation?.project_name", "(invitation as any)?.project_name")
c = c.replace("invitation?.invited_email", "(invitation as any)?.invited_email")
c = c.replace("invitation?.role", "(invitation as any)?.role")
with open("frontend/src/pages/AcceptInvitation.tsx", "w", encoding="utf-8") as f: f.write(c)

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f: c = f.read()
c = c.replace("(sourceInfo.config as any)?.url?.replace", "((sourceInfo.config as any)?.url || '').replace")
c = c.replace("sourceInfo.config?.url as string)?.replace", "((sourceInfo.config as any)?.url || '').replace")
c = c.replace("(sourceInfo.config as any)?.size", "String((sourceInfo.config as any)?.size)")
with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f: f.write(c)

with open("frontend/src/pages/InvestigationView.tsx", "r", encoding="utf-8") as f: c = f.read()
c = c.replace("(incident.final_report as any) || ''", "String((incident.final_report as any) || '')")
with open("frontend/src/pages/InvestigationView.tsx", "w", encoding="utf-8") as f: f.write(c)

print("Patched 5")
