#!/usr/bin/env python3
import json, os, time, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", 8104
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
MISTRAL_KEYS = [x.strip() for x in os.environ.get("MISTRAL_API_KEYS", "").split(",") if x.strip()]
MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")
COOLDOWN = {}

def call(url, headers, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, dict(r.headers), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: data=json.loads(e.read().decode())
        except Exception: data={}
        return e.code, dict(e.headers), data
    except Exception:
        return 599, {}, {}

def safe_message(provider, status, data):
    if status == 400: return f"{provider} rejected the request (400)."
    if status in (401,403): return f"{provider} authorization failed ({status})."
    if status == 429: return f"{provider} is rate-limited (429); another key/provider was tried."
    if status >= 500: return f"{provider} is temporarily unavailable ({status})."
    return f"{provider} returned HTTP {status}."

def generate(prompt):
    failures=[]
    if GEMINI_KEY:
        status, headers, data = call(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}", {"Content-Type":"application/json"}, {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.2,"maxOutputTokens":1024}})
        if status == 200:
            parts=data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text=next((p.get("text","").strip() for p in parts if p.get("text") and not p.get("thought")), "")
            if text: return 200, {"text":text,"provider":"gemini"}
        failures.append(("Gemini",status,headers,data))
    now=time.time()
    for i,key in enumerate(MISTRAL_KEYS):
        if COOLDOWN.get(i,0) > now:
            failures.append((f"Mistral key {i+1}",429,{},{}))
            continue
        status, headers, data = call("https://api.mistral.ai/v1/chat/completions", {"Content-Type":"application/json","Authorization":"Bearer "+key}, {"model":MODEL,"messages":[{"role":"user","content":prompt}],"max_tokens":1024,"temperature":0.2})
        if status == 200:
            text=data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if text: return 200, {"text":text,"provider":"mistral"}
        if status == 429:
            try: retry=float(headers.get("Retry-After", "30"))
            except Exception: retry=30
            COOLDOWN[i]=now+min(max(retry,1),300)
        failures.append((f"Mistral key {i+1}",status,headers,data))
    if any(s == 429 for _,s,_,_ in failures): return 429, {"message":"All configured AI routes are rate-limited. Retry after the provider window."}
    if failures:
        name,status,_,_=failures[-1]
        return status if status in (400,401,403) or status >= 500 else 503, {"message":safe_message(name,status,{})}
    return 503, {"message":"No AI provider is configured on the server."}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): return
    def send_json(self,status,payload):
        raw=json.dumps(payload).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path == "/health": self.send_json(200,{"ok":True,"providers":{"gemini":bool(GEMINI_KEY),"mistral_keys":len(MISTRAL_KEYS)}})
        else: self.send_json(404,{"message":"Not found"})
    def do_POST(self):
        if self.path != "/api/ai": self.send_json(404,{"message":"Not found"}); return
        try: body=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
        except Exception: self.send_json(400,{"message":"Invalid request body."}); return
        prompt=body.get("prompt","")
        if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>30000: self.send_json(400,{"message":"Invalid prompt."}); return
        status,payload=generate(prompt); self.send_json(status,payload)

ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
