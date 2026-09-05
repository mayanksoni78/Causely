import re

# Helper to read/write
def patch_file(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    for old, new in replacements:
        c = c.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

# 1. ProjectSettings.tsx
patch_file("frontend/src/components/ProjectSettings.tsx", [
    ("Array<{id: string, email: string, role: string, user_id?: string}>", "Array<{id: string, email: string, role: string, user_id?: string, name?: string}>")
])

# 2. AcceptInvitation.tsx
patch_file("frontend/src/pages/AcceptInvitation.tsx", [
    ("useState<{project_name: string, tenant_name: string, role: string, invited_email: string}", "useState<{project_name: string, tenant_name: string, role: string, invited_email: string, inviter_name: string}"),
    ("invitation.inviter_name", "invitation?.inviter_name"),
    ("invitation.project_name", "invitation?.project_name"),
    ("invitation.tenant_name", "invitation?.tenant_name"),
    ("invitation.invited_email", "invitation?.invited_email"),
    ("const e = err as any", "const e = err as {response?: {data?: {detail?: string}}, message?: string}")
])

# 3. ConnectSources.tsx
patch_file("frontend/src/pages/ConnectSources.tsx", [
    ("payload.endpoints.split", "(payload.endpoints as string).split"),
    ("sourceInfo.config.url.replace", "(sourceInfo.config?.url as string)?.replace"),
    ("sourceInfo.config.size", "(sourceInfo.config?.size as number)"),
    ("sourceInfo.config.file_name", "(sourceInfo.config?.file_name as string)"),
    ("sourceInfo.config.database", "(sourceInfo.config?.database as string)")
])

# 4. InvestigationView.tsx
patch_file("frontend/src/pages/InvestigationView.tsx", [
    ("import { getIncident, getIncidentTrace", "import { Incident, InvestigationTraceStep } from '../lib/types';\nimport { getIncident, getIncidentTrace"),
    ("<div>{incident.final_report}</div>", "<div>{typeof incident.final_report === 'string' ? incident.final_report : JSON.stringify(incident.final_report)}</div>"),
])

# 5. Login.tsx
patch_file("frontend/src/pages/Login.tsx", [
    ("const e = err as {response?: {data?: {detail?: string}}, message?: string};\n        const msg = e.response?.data?.detail || e.message || 'Sign up failed';", "const ax = err as {response?: {data?: {detail?: string}}};\n        const msg = ax.response?.data?.detail || (err instanceof Error ? err.message : 'Sign up failed');"),
    ("const e = err as {response?: {data?: {detail?: string}}};\n        setError(e.response?.data?.detail || 'Invalid credentials');", "const ax = err as {response?: {data?: {detail?: string}}};\n        setError(ax.response?.data?.detail || 'Invalid credentials');")
])

print("Patched part 2")
