import re

with open('frontend/src/pages/ConnectSources.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Interfaces
content = content.replace(
    'import type { Source } from \'../lib/types\';',
    '''import type { Source } from '../lib/types';

interface Readiness {
  score: number;
  code: boolean;
  logs: boolean;
  database: boolean;
  external_services: boolean;
  history: boolean;
}

interface SourceFormData {
  name?: string;
  repo_url?: string;
  github_token?: string;
  connection_string?: string;
  [key: string]: unknown;
}

const getErrorMsg = (err: unknown) => {
  if (err && typeof err === 'object' && 'response' in err) {
    const ax = err as { response?: { data?: { detail?: string } } };
    if (ax.response?.data?.detail) return ax.response.data.detail;
  }
  return err instanceof Error ? err.message : "An error occurred";
};'''
)

# 2. State Types
content = content.replace(
    'const [readiness, setReadiness] = useState<Record<string, any> | null>(null);',
    'const [readiness, setReadiness] = useState<Readiness | null>(null);'
)
content = content.replace(
    'const [formData, setFormData] = useState<Record<string, any>>({});',
    'const [formData, setFormData] = useState<SourceFormData>({});'
)
content = content.replace('icon: any;', 'icon: React.ElementType;')

# 3. Error handling
content = content.replace('.catch(e => {', '.catch(() => {')

content = content.replace(
    '''    } catch (error: unknown) {
      const e = error as any;
      setSubmitError(e?.response?.data?.detail || e.message);
    }''',
    '''    } catch (error: unknown) {
      setSubmitError(getErrorMsg(error));
    }'''
)

content = content.replace(
    '''    } catch (error: unknown) {
      const e = error as any;
      setActionFeedback({ message: e?.response?.data?.detail || e?.message || "Action failed", type: "error" });
    }''',
    '''    } catch (error: unknown) {
      setActionFeedback({ message: getErrorMsg(error), type: "error" });
    }'''
)

content = content.replace(
    '''    } catch (error: unknown) {
      const e = error as any;
      alert('❌ Connection failed: ' + (e?.response?.data?.detail || e.message));
    }''',
    '''    } catch (error: unknown) {
      setActionFeedback({ message: 'Connection failed: ' + getErrorMsg(error), type: "error" });
    }'''
)

content = content.replace(
    '''      await testConnection(id);
      alert('✅ Connection successful!');
      refreshData();''',
    '''      await testConnection(id);
      setActionFeedback({ message: 'Connection successful!', type: "success" });
      refreshData();'''
)

with open('frontend/src/pages/ConnectSources.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
