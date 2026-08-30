import re

with open("frontend/src/pages/Login.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the generic catch block for signup
signup_catch = r"""\} catch \(err: any\) \{
        const msg = err\?\.response\?\.data\?\.detail \|\| err\?\.message \|\| 'Sign up failed';
        setError\(msg\);
      \}"""

new_signup_catch = """} catch (err: any) {
        if (!err.response) {
            setError("Network or CORS error: Could not reach the server.");
        } else {
            const msg = err.response.data?.detail || err.message || 'Sign up failed';
            setError(msg);
        }
      }"""

content = re.sub(signup_catch, new_signup_catch, content)

# Replace the generic catch block for login
login_catch = r"""\} catch \(err: any\) \{
        setError\(err\?\.response\?\.data\?\.detail \|\| 'Invalid credentials'\);
      \}"""

new_login_catch = """} catch (err: any) {
        if (!err.response) {
            setError("Network or CORS error: Could not reach the server.");
        } else {
            setError(err.response.data?.detail || 'Invalid credentials');
        }
      }"""

content = re.sub(login_catch, new_login_catch, content)

with open("frontend/src/pages/Login.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Login.tsx error handling")
