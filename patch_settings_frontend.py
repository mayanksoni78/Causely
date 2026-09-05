import re

with open("frontend/src/pages/Settings.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove hardcoded GEMINI_MODELS and OLLAMA_MODELS arrays
content = re.sub(r'const GEMINI_MODELS = \[.*?\];', '', content, flags=re.DOTALL)
content = re.sub(r'const OLLAMA_MODELS = \[.*?\];', '', content, flags=re.DOTALL)

# 2. Add state for models inside Settings component
content = re.sub(
    r'const \[ollamaModel, setOllamaModel\] = useState\(\'llama3\'\);',
    "const [ollamaModel, setOllamaModel] = useState('llama3');\n  const [supportedGeminiModels, setSupportedGeminiModels] = useState<string[]>([]);\n  const [supportedOllamaModels, setSupportedOllamaModels] = useState<string[]>([]);",
    content
)

# 3. Update fetchSettings to set the models
fetch_settings_update = """      if (data.ollama_model) setOllamaModel(data.ollama_model);
      setHasByokKey(!!data.has_byok_key);
      if (data.supported_gemini_models) setSupportedGeminiModels(data.supported_gemini_models);
      if (data.supported_ollama_models) setSupportedOllamaModels(data.supported_ollama_models);
      setUsage(usageData);"""
content = re.sub(r'if \(data\.ollama_model\) setOllamaModel\(data\.ollama_model\);\s*setHasByokKey\(\!\!data\.has_byok_key\);\s*setUsage\(usageData\);', fetch_settings_update, content)

# 4. Fix clear data alert and error casting
old_clear = """      await clearTenantData(clearConfirm);
      alert("All tenant data deleted securely.");
      setShowClearModal(false);
      setClearConfirm('');
      window.location.reload();
    } catch (error: unknown) {
      const e = error as any;
      setSaveMessage({type: 'error', text: `Failed to clear data: ${e?.response?.data?.detail || e?.message}`});
    }"""
new_clear = """      await clearTenantData(clearConfirm);
      setSaveMessage({type: 'success', text: "All tenant data deleted securely."});
      setShowClearModal(false);
      setClearConfirm('');
      setTimeout(() => window.location.reload(), 1500);
    } catch (error: unknown) {
      setSaveMessage({type: 'error', text: `Failed to clear data: ${getErrorMsg(error)}`});
    }"""
content = content.replace(old_clear, new_clear)

# 5. Fix model dropdown to use the fetched arrays
gemini_dropdown = """<select className="input-field" value={model} onChange={e => setModel(e.target.value)}>
                    {GEMINI_MODELS.map(m => (
                      <option key={m.id} value={m.id}>{m.name}</option>
                    ))}
                  </select>"""
new_gemini_dropdown = """<select className="input-field" value={model} onChange={e => setModel(e.target.value)}>
                    {supportedGeminiModels.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>"""
content = content.replace(gemini_dropdown, new_gemini_dropdown)

ollama_dropdown = """<select className="input-field" value={ollamaModel} onChange={e => setOllamaModel(e.target.value)}>
                    {OLLAMA_MODELS.map(m => (
                      <option key={m.id} value={m.id}>{m.name}</option>
                    ))}
                  </select>"""
new_ollama_dropdown = """<select className="input-field" value={ollamaModel} onChange={e => setOllamaModel(e.target.value)}>
                    {supportedOllamaModels.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>"""
content = content.replace(ollama_dropdown, new_ollama_dropdown)

# 6. Fix API key input
api_input_old = """                      value={hasByokKey && geminiKey.startsWith('••••••••••••••••') ? geminiKey : geminiKey}"""
api_input_new = """                      value={geminiKey}"""
content = content.replace(api_input_old, api_input_new)

with open("frontend/src/pages/Settings.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Settings.tsx")
