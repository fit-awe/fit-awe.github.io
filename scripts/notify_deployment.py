#!/usr/bin/env python3
"""Optional HTTPS deployment hook, only after a validated commit was pushed."""
import os
import requests
hook=os.environ.get('KIMI_DEPLOY_HOOK_URL','')
if not hook:
 print('No deploy hook configured. The hosting platform must redeploy when the GitHub branch changes.')
else:
 if not hook.startswith('https://'):raise SystemExit('Deployment hook must use HTTPS')
 try:
  response=requests.post(hook,timeout=60,allow_redirects=False)
  if not 200<=response.status_code<300:raise SystemExit(f'Deployment hook returned HTTP {response.status_code}')
 except requests.RequestException:raise SystemExit('Deployment hook request failed; check deployment settings.')
 print('Deployment hook accepted. Check the hosting platform for deployment completion.')
