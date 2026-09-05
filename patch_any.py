import glob, re

def replace_in_file(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

replace_in_file("frontend/src/pages/InvestigationView.tsx", [
    ("(query: any)", "(query: unknown)"),
    ("query?.state?.data?.status", "(query as {state?: {data?: {status?: string}}})?.state?.data?.status"),
    ("(step: any, idx: number)", "(step: Record<string, unknown>, idx: number)"),
])

replace_in_file("frontend/src/pages/AcceptInvitation.tsx", [
    ("useState<any>(null)", "useState<Record<string, unknown> | null>(null)"),
    ("catch (err: any)", "catch (err: unknown)"),
    ("err?.response", "(err as {response?: {data?: {detail?: string}}})?.response"),
])

replace_in_file("frontend/src/components/ProjectSettings.tsx", [
    ("useState<any[]>([])", "useState<Record<string, unknown>[]>([])"),
    ("(e: any)", "(e: React.FormEvent)"),
])

replace_in_file("frontend/src/pages/Login.tsx", [
    ("catch (err: any)", "catch (err: unknown)"),
    ("err.response", "(err as {response?: {data?: {detail?: string}}}).response"),
    ("err.message", "(err as {message?: string}).message")
])

print("Swept remaining any types")
