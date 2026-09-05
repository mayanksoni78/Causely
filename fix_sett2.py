import re

with open('frontend/src/pages/Settings.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

helper = '''
const getErrorMsg = (err: unknown) => {
  if (err && typeof err === 'object' && 'response' in err) {
    const ax = err as { response?: { data?: { detail?: string } } };
    if (ax.response?.data?.detail) return ax.response.data.detail;
  }
  return err instanceof Error ? err.message : "An error occurred";
};

const Settings = () => {'''

content = content.replace('const Settings = () => {', helper)

content = content.replace(
    '''    } catch (error: unknown) {
      const e = error as any;
      setSaveMessage({type: 'error', text: `Failed to save settings: ${e?.response?.data?.detail || e.message}`});
    }''',
    '''    } catch (error: unknown) {
      setSaveMessage({type: 'error', text: `Failed to save settings: ${getErrorMsg(error)}`});
    }'''
)

content = content.replace(
    '''    } catch (error: unknown) {
      const e = error as any;
      setTestResult({ status: 'error', message: e?.response?.data?.detail || e.message });
    }''',
    '''    } catch (error: unknown) {
      setTestResult({ status: 'error', message: getErrorMsg(error) });
    }'''
)

content = content.replace(
    '''      alert("All tenant data deleted securely.");
      window.location.reload();
    } catch (error: unknown) {
      const e = error as any;
      setSaveMessage({type: 'error', text: `Failed to clear data: ${e?.response?.data?.detail || e?.message}`});
    }''',
    '''      setSaveMessage({type: 'success', text: "All tenant data deleted securely."});
      setTimeout(() => window.location.reload(), 1000);
    } catch (error: unknown) {
      setSaveMessage({type: 'error', text: `Failed to clear data: ${getErrorMsg(error)}`});
    }'''
)


with open('frontend/src/pages/Settings.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
