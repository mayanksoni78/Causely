import re

with open("frontend/src/pages/AcceptInvitation.tsx", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("catch (err: unknown)", "catch (err: any)")
c = c.replace("invitation?.inviter_name", "(invitation as any)?.inviter_name")

with open("frontend/src/pages/AcceptInvitation.tsx", "w", encoding="utf-8") as f:
    f.write(c)

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("(sourceInfo.config as any)?.url?.replace", "(sourceInfo.config as any)?.url?.replace") # wait that doesn't fix it.
c = c.replace("sourceInfo.config.url", "(sourceInfo.config as any)?.url")
c = c.replace("sourceInfo.config.size", "(sourceInfo.config as any)?.size")
c = c.replace("(sourceInfo.config as any)?.size as number", "(sourceInfo.config as any)?.size")

with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f:
    f.write(c)

with open("frontend/src/pages/Login.tsx", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("catch (err: unknown)", "catch (err: any)")
c = c.replace("const ax = err as {response?: {data?: {detail?: string}}};", "")
c = c.replace("const msg = ax.response?.data?.detail || (err instanceof Error ? err.message : 'Sign up failed');", "const msg = err.response?.data?.detail || err.message || 'Sign up failed';")
c = c.replace("setError(ax.response?.data?.detail || 'Invalid credentials');", "setError(err.response?.data?.detail || 'Invalid credentials');")
with open("frontend/src/pages/Login.tsx", "w", encoding="utf-8") as f:
    f.write(c)

with open("frontend/src/pages/InvestigationView.tsx", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("JSON.stringify(incident.final_report || {})", "(incident.final_report as any) || ''")
with open("frontend/src/pages/InvestigationView.tsx", "w", encoding="utf-8") as f:
    f.write(c)

print("Reverted overly strict TS constraints in error blocks.")
