import re

with open("backend/src/main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_cors = """FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

new_cors = """FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Allow common local development origins
origins = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]
# Remove duplicates
origins = list(set(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

content = content.replace(old_cors, new_cors)

with open("backend/src/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py CORS settings")
