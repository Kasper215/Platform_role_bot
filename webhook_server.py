#!/usr/bin/env python3
import hmac, hashlib, json, subprocess, logging, os
from http.server import HTTPServer, BaseHTTPRequestHandler

WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'CHANGE_ME_SECRET_123')
DEPLOY_SCRIPT = '/root/role_bot/deploy.sh'
PORT = 9000

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(length)
        sig = self.headers.get('X-Hub-Signature-256', '')
        
        if WEBHOOK_SECRET and not self.verify(payload, sig):
            self.send_error(403); return
        
        event = self.headers.get('X-GitHub-Event', '')
        logger.info(f"📨 Event: {event}")
        
        if event == 'push':
            data = json.loads(payload)
            ref = data.get('ref', '')
            if ref == 'refs/heads/main':
                logger.info(f"🎯 Push to main by {data.get('pusher',{}).get('name')}")
                subprocess.Popen([DEPLOY_SCRIPT], start_new_session=True)
                self.send_response(200)
            else:
                logger.info(f"⏭️ Skip {ref}")
                self.send_response(200)
        elif event == 'ping':
            logger.info('🏓 Ping')
            self.send_response(200)
        else:
            self.send_response(200)
        
        self.end_headers()
        self.wfile.write(b'OK')
    
    def verify(self, payload, sig):
        expected = 'sha256=' + hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig)

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    logger.info(f'🎣 Webhook on port {PORT}')
    server.serve_forever()
