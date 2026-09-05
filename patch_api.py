import re

with open("frontend/src/lib/api.ts", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("export const signupUser = async (data: any) => {", "export const signupUser = async (data: Record<string, unknown>) => {")
content = content.replace("export const updateSettings = async (data: any) => {", "export const updateSettings = async (data: Record<string, unknown>) => {")
content = content.replace("export const createSource = async (type: string, data: any) => {", "export const createSource = async (type: string, data: Record<string, unknown> | FormData | {file?: File, onUploadProgress?: any}) => {")
content = content.replace("export const createProject = async (data: any) => {", "export const createProject = async (data: Record<string, unknown>) => {")
content = content.replace("export const updateProject = async (id: string, data: any) => {", "export const updateProject = async (id: string, data: Record<string, unknown>) => {")
content = content.replace("onUploadProgress?: any", "onUploadProgress?: (progressEvent: unknown) => void")

with open("frontend/src/lib/api.ts", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated api.ts")
