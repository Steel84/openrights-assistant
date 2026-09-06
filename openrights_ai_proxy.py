#!/usr/bin/env python3
"""Same-origin AI proxy. Secrets are loaded only from the service environment."""
import json, math, os, threading, time, urllib.error, urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = '127.0.0.1', 8104
GEMINI_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')
MISTRAL_KEYS = list(dict.fromkeys(k.strip() for k in os.environ.get('MISTRAL_API_KEYS', '').split(',') if k.strip()))
MODEL = os.environ.get('MISTRAL_MODEL', 'mistral-small-latest')
COOLDOWN = {}
LOCK = threading.Lock()

def retry_seconds(headers):
    value = next((v for k,v in headers.items() if k.lower() == 'retry-after'), None)
    try:
        number = float(value)
        if math.isfinite(number): return max(1, math.ceil(number))
    except (ValueError, TypeError): pass
    try:
        when = parsedate_to_datetime(value)
        if when.tzinfo is None: when = when.replace(tzinfo=timezone.utc)
        return max(1, math.ceil((when - datetime.now(timezone.utc)).total_seconds()))
    except (TypeError, ValueError, OverflowError): return 30

def call(url, headers, body, timeout=4):
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), json.loads(response.read(2_000_000))
    except urllib.error.HTTPError as error:
        try: data = json.loads(error.read(65536))
        except (ValueError, UnicodeError): data = {}
        return error.code, dict(error.headers), data
    except Exception:
        # Never log exception strings: URLs or headers may contain secrets.
        return 502, {}, {}

def failure(provider, status, data, retry=None):
    message = str(data.get('error', {}).get('message', '')) if isinstance(data.get('error'), dict) else ''
    if status == 400 and 'location' in message.lower(): reason = 'location_not_supported'
    elif status == 400: reason = 'invalid_request'
    elif status == 401: reason = 'invalid_credentials'
    elif status == 403: reason = 'access_denied'
    elif status == 404: reason = 'model_or_endpoint_not_found'
    elif status == 429: reason = 'rate_limited'
    elif status >= 500: reason = 'upstream_unavailable'
    else: reason = 'invalid_response'
    result = {'provider':provider, 'status':status, 'reason':reason}
    if retry is not None: result['retry_after'] = retry
    return result

def generate(prompt):
    attempts = []
    deadline = time.monotonic() + 24
    routes = []
    if GEMINI_KEY:
        routes.append(('Gemini', 'https://generativelanguage.googleapis.com/v1beta/models/'+GEMINI_MODEL+':generateContent', {'Content-Type':'application/json','x-goog-api-key':GEMINI_KEY}, {'contents':[{'parts':[{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':1024}}))
    routes += [('Mistral key '+str(i+1), 'https://api.mistral.ai/v1/chat/completions', {'Content-Type':'application/json','Authorization':'Bearer '+key}, {'model':MODEL,'messages':[{'role':'user','content':prompt}],'max_tokens':1024,'temperature':0.2}) for i,key in enumerate(MISTRAL_KEYS)]
    for name,url,headers,body in routes:
        remaining = COOLDOWN.get(name,0) - time.monotonic()
        if remaining > 0:
            attempts.append(failure(name,429,{},math.ceil(remaining))); continue
        budget = deadline-time.monotonic()
        if budget <= 0:
            attempts.append({'provider':name,'status':504,'reason':'request_deadline_exceeded'}); continue
        status, response_headers, data = call(url,headers,body,timeout=min(4,budget))
        if not isinstance(data,dict): data = {}
        if status == 200:
            try:
                if name == 'Gemini':
                    parts = data['candidates'][0]['content']['parts']
                    text = '\n'.join(p['text'] for p in parts if p.get('text') and not p.get('thought'))
                else: text = data['choices'][0]['message']['content']
                if isinstance(text,str) and text.strip(): return 200, {'text':text.strip(),'provider':name.split(' key')[0]}
            except (KeyError,IndexError,TypeError): pass
            attempts.append({'provider':name,'status':502,'reason':'empty_or_invalid_response'}); continue
        retry = retry_seconds(response_headers) if status == 429 else None
        if retry is not None: COOLDOWN[name] = time.monotonic()+retry
        attempts.append(failure(name,status,data,retry))
    if not attempts: return 503, {'message':'No AI provider is configured. Local search remains available.'}
    labels = {
        'location_not_supported':'location is not supported', 'invalid_request':'request rejected',
        'invalid_credentials':'invalid credentials', 'access_denied':'access denied',
        'model_or_endpoint_not_found':'model or endpoint not found', 'rate_limited':'rate-limited',
        'upstream_unavailable':'upstream unavailable', 'invalid_response':'invalid response',
        'empty_or_invalid_response':'empty or invalid response', 'request_deadline_exceeded':'not attempted: request deadline reached'}
    message = '; '.join(f"{a['provider']}: {labels[a['reason']]} ({a['status']})" for a in attempts)
    retries = [a['retry_after'] for a in attempts if 'retry_after' in a]
    result = {'message':message+'. Local search and legal sources remain available.', 'attempts':attempts}
    if retries: result['retry_after'] = min(retries)
    statuses = {a['status'] for a in attempts}
    status = next(iter(statuses)) if len(statuses)==1 and next(iter(statuses)) in (400,401,403,404,429) else 503
    return status,result

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def send_json(self,status,payload):
        raw = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(raw)))
        if payload.get('retry_after'): self.send_header('Retry-After',str(payload['retry_after']))
        self.end_headers()
        try: self.wfile.write(raw)
        except (BrokenPipeError,ConnectionResetError): pass
    def do_GET(self):
        if self.path == '/health': self.send_json(200,{'ok':True,'providers':{'gemini':bool(GEMINI_KEY),'mistral_keys':len(MISTRAL_KEYS)}})
        else: self.send_json(404,{'message':'Not found'})
    def do_POST(self):
        if self.path != '/api/ai': self.send_json(404,{'message':'Not found'}); return
        origin = self.headers.get('Origin')
        if origin and origin != 'https://openrights.fortravels.xyz': self.send_json(403,{'message':'Origin is not allowed.'}); return
        try: length = int(self.headers.get('Content-Length','0'))
        except ValueError: length = 0
        if not 0 < length <= 65536: self.send_json(413,{'message':'Invalid request size.'}); return
        self.connection.settimeout(10)
        try:
            body = json.loads(self.rfile.read(length))
            prompt = body.get('prompt') if isinstance(body,dict) else None
        except Exception: self.send_json(400,{'message':'Invalid JSON.'}); return
        if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>30000: self.send_json(400,{'message':'Invalid prompt.'}); return
        if not LOCK.acquire(blocking=False): self.send_json(503,{'message':'AI is processing another request. Local search remains available.','retry_after':2}); return
        try: status,payload = generate(prompt)
        except Exception: status,payload = 502,{'message':'AI response could not be processed. Local search remains available.'}
        finally: LOCK.release()
        self.send_json(status,payload)

if __name__ == '__main__':
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
