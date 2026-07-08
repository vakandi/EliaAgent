#!/usr/bin/env python3
"""
CAPTCHA Solver - Uses agent-browser for reCAPTCHA v2/v3, hCaptcha, Turnstile
Practical alternative to OhMyCaptcha until full deployment is possible.

Usage:
  python3 captcha_solver.py solve-recaptcha --url <url> --sitekey <key>
  python3 captcha_solver.py check-ohmycaptcha
  python3 captcha_solver.py test-target
"""

import sys
import json
import subprocess
import argparse
import time
import re

AGENT_BROWSER = "agent-browser"
BROWSER_PROFILE = "--profile ~/.agent-browser-profile"

def run_browser_cmd(cmd, timeout=60):
    """Run agent-browser command and return output."""
    result = subprocess.run(
        f"{AGENT_BROWSER} {cmd}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.stdout, result.stderr

def solve_recaptcha_v3(url, sitekey, action="verify"):
    """Solve reCAPTCHA v3 using agent-browser."""
    print(f"[*] Solving reCAPTCHA v3 for {url}")
    print(f"[*] Site key: {sitekey}")
    
    # Close any existing browser session
    run_browser_cmd("close")
    
    # Open the target page with the profile for logged-in session
    stdout, stderr = run_browser_cmd(
        f'close && {BROWSER_PROFILE} --headed open "{url}"',
        timeout=30
    )
    
    if "Error" in stdout or "Error" in stderr:
        print(f"[!] Error opening page: {stderr}")
        return None
    
    time.sleep(3)
    
    # Try to find and interact with the recaptcha iframe
    # Use JS eval to check for recaptcha
    js_check = """() => {
        const frames = document.querySelectorAll('iframe[src*="recaptcha"]');
        const grecaptcha = window.grecaptcha;
        return {
            hasIframe: frames.length > 0,
            hasGreptcha: typeof grecaptcha !== 'undefined',
            frameSrcs: Array.from(frames).map(f => f.src.substring(0, 100))
        };
    }"""
    
    stdout, stderr = run_browser_cmd(
        f'eval "{js_check}"',
        timeout=15
    )
    
    print(f"[*] reCAPTCHA detection: {stdout[:300]}")
    
    # For v3, execute grecaptcha.execute if available
    js_execute = """() => {
        return new Promise((resolve) => {
            if (typeof grecaptcha !== 'undefined' && grecaptcha.execute) {
                grecaptcha.execute('SITE_KEY', {action: 'ACTION'})
                    .then(token => resolve({success: true, token: token}))
                    .catch(err => resolve({success: false, error: err.message}));
            } else {
                resolve({success: false, error: 'grecaptcha not available'});
            }
        });
    }""".replace("SITE_KEY", sitekey).replace("ACTION", action)
    
    stdout, stderr = run_browser_cmd(
        f'eval "{js_execute}"',
        timeout=20
    )
    
    run_browser_cmd("close")
    print(f"[*] Result: {stdout[:300]}")
    return stdout

def test_ohmycaptcha_health():
    """Test if OhMyCaptcha is running locally."""
    import urllib.request
    try:
        response = urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=5)
        data = json.loads(response.read())
        print(f"[✓] OhMyCaptcha server is RUNNING")
        print(f"    {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"[✗] OhMyCaptcha server is NOT running: {e}")
        print(f"[*] To start: cd /Users/vakandi/Documents/BypassCaptcha/ohmycaptcha && source .venv/bin/activate && CLIENT_KEY=test python3 main.py")
        return None

def check_requirements():
    """Check if we can install and run OhMyCaptcha."""
    print("[*] Checking CAPTCHA bypass requirements...")
    
    # Check agent-browser
    stdout, stderr = run_browser_cmd("--help", timeout=5)
    if "Usage" in stdout or "Agent Browser" in stdout:
        print(f"[✓] agent-browser is available")
    else:
        print(f"[✗] agent-browser not found or not working")
    
    # Check playwright
    import shutil
    if shutil.which("playwright"):
        print(f"[✓] playwright CLI is available")
    else:
        print(f"[✗] playwright CLI not found")
    
    print(f"\n[*] Recommended next steps:")
    print(f"  1. Install OhMyCaptcha deps: cd ohmycaptcha && pip install -r requirements.txt")
    print(f"  2. Install playwright: playwright install chromium")
    print(f"  3. Set env vars: CLIENT_KEY, CLOUD_API_KEY (OpenRouter)")
    print(f"  4. Start server: python3 main.py")
    print(f"  5. Test: curl http://localhost:8000/api/v1/health")

def test_openrouter_access():
    """Test if we have access to OpenRouter for vision models."""
    import urllib.request
    api_key = "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"
    
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET"
        )
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        models = [m["id"] for m in data.get("data", []) if "free" in m.get("id", "")]
        print(f"[✓] OpenRouter accessible! {len(models)} free models available")
        return True
    except Exception as e:
        print(f"[✗] OpenRouter error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAPTCHA Solver Utility")
    parser.add_argument("action", choices=["check", "test-openrouter", "solve-v3", "solve-v2"])
    parser.add_argument("--url", help="Target URL")
    parser.add_argument("--sitekey", help="reCAPTCHA site key")
    parser.add_argument("--action", default="verify", help="reCAPTCHA v3 action name")
    
    args = parser.parse_args()
    
    if args.action == "check":
        print("=" * 50)
        print("CAPTCHA BYPASS SYSTEM - STATUS CHECK")
        print("=" * 50)
        test_ohmycaptcha_health()
        print()
        check_requirements()
        print()
        test_openrouter_access()
    
    elif args.action == "test-openrouter":
        test_openrouter_access()
    
    elif args.action == "solve-v3":
        if not args.url or not args.sitekey:
            print("Error: --url and --sitekey required for solve-v3")
            sys.exit(1)
        solve_recaptcha_v3(args.url, args.sitekey, args.action)
    
    else:
        parser.print_help()
