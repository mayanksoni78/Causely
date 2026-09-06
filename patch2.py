import re

with open("frontend/src/pages/ConnectSources.tsx", "r", encoding="utf-8") as f:
    code = f.read()

# Replace handleConnect
handle_connect_old = """  const handleConnect = async (type: string) => {
    setSubmitError('');
    setSubmitLoading(true);
    try {
      if (type === 'static_log' && !formData.file) {
        throw new Error('Please select a file');
      }
      
      let payload: Record<string, unknown> = { ...formData } as Record<string, unknown>;
      
      if (type === 'generic_rest') {
        payload.endpoints = payload.endpoints ? (payload.endpoints as string).split(',').map((s: string) => s.trim()) : [];
      }
      
      if (type === 'static_log') {
        payload.onUploadProgress = (progressEvent: { loaded: number, total?: number }) => {
          const percentCompleted = progressEvent.total ? Math.round((progressEvent.loaded * 100) / progressEvent.total) : 0;
          setUploadProgress(percentCompleted);
        };
      }
      
      await createSource(type, payload);
      setShowModal(null);
      setAddIntegrationModal(false);
      setFormData({});
      setUploadProgress(0);
      refreshData();
    } catch (error: unknown) {
      setSubmitError(getErrorMsg(error));
    }
    setSubmitLoading(false);
  };"""

handle_connect_new = """  const handleConnect = async (type: string) => {
    setSubmitError('');
    setSubmitLoading(true);
    try {
      if (type === 'static_log' && !formData.file) {
        throw new Error('Please select a file');
      }
      
      let payload: Record<string, unknown> = { ...formData } as Record<string, unknown>;
      
      if (type === 'generic_rest') {
        payload.endpoints = payload.endpoints ? (payload.endpoints as string).split(',').map((s: string) => s.trim()) : [];
      }
      
      if (type === 'static_log') {
        payload.onUploadProgress = (progressEvent: { loaded: number, total?: number }) => {
          const percentCompleted = progressEvent.total ? Math.round((progressEvent.loaded * 100) / progressEvent.total) : 0;
          setUploadProgress(percentCompleted);
        };
      }
      
      await createSource(type, payload);
      await refreshData();
      setShowModal(null);
      setAddIntegrationModal(false);
      setFormData({});
      setUploadProgress(0);
    } catch (error: unknown) {
      setSubmitError(getErrorMsg(error));
    } finally {
      setSubmitLoading(false);
    }
  };"""

code = code.replace(handle_connect_old, handle_connect_new)


# Replace handleDisconnect
handle_disconnect_old = """  const handleDisconnect = async (id: string) => {
    setDeletingId(id);
    try {
      await deleteSource(id);
      refreshData();
    } catch (error: unknown) {
      setActionFeedback({ message: getErrorMsg(error), type: "error" });
    }
    setDeletingId(null);
  };"""

handle_disconnect_new = """  const handleDisconnect = async (id: string) => {
    setDeletingId(id);
    try {
      await deleteSource(id);
      setSources(prev => prev.filter(s => s.id !== id));
      getReadiness().then(setReadiness).catch(console.error);
    } catch (error: unknown) {
      setActionFeedback({ message: getErrorMsg(error), type: "error" });
    } finally {
      setDeletingId(null);
    }
  };"""

code = code.replace(handle_disconnect_old, handle_disconnect_new)


# Replace handleTestConnection
handle_test_old = """  const handleTestConnection = async (id: string) => {
    setTestingId(id);
    try {
      await testConnection(id);
      alert('✅ Connection successful!');
      refreshData();
    } catch (error: unknown) {
      const e = error as any;
      alert('❌ Connection failed: ' + (e?.response?.data?.detail || e.message));
    }
    setTestingId(null);
  };"""

handle_test_new = """  const handleTestConnection = async (id: string) => {
    setTestingId(id);
    try {
      await testConnection(id);
      alert('✅ Connection successful!');
      await refreshData();
    } catch (error: unknown) {
      const e = error as any;
      alert('❌ Connection failed: ' + (e?.response?.data?.detail || e.message));
    } finally {
      setTestingId(null);
    }
  };"""

code = code.replace(handle_test_old, handle_test_new)


with open("frontend/src/pages/ConnectSources.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("Done patching frontend!")
