#!/usr/bin/env python3
"""
חידון מיקומים - כוכב מיכאל
Static file server + shared leaderboard API
Scores are stored in scores.json so all players share the same leaderboard.
"""

import http.server
import json
import os

PORT        = 3000
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
SCORES_FILE = os.path.join(BASE_DIR, 'scores.json')


def load_scores():
    try:
        with open(SCORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_scores(scores):
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


class Handler(http.server.SimpleHTTPRequestHandler):

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/leaderboard':
            self._json(200, load_scores())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/leaderboard':
            try:
                length = int(self.headers.get('Content-Length', 0))
                entry  = json.loads(self.rfile.read(length).decode('utf-8'))
                scores = load_scores()
                scores.append(entry)
                scores.sort(key=lambda x: x.get('score', 0), reverse=True)
                save_scores(scores)
                self._json(200, {'ok': True})
            except Exception as e:
                self._json(500, {'error': str(e)})
        else:
            self._json(404, {'error': 'Not found'})

    def do_DELETE(self):
        if self.path == '/api/leaderboard':
            save_scores([])
            self._json(200, {'ok': True})
        else:
            self._json(404, {'error': 'Not found'})

    def log_message(self, fmt, *args):
        # Only print non-200/304 requests to keep console clean
        if args and str(args[1]) not in ('200', '304', '204'):
            super().log_message(fmt, *args)


if __name__ == '__main__':
    os.chdir(BASE_DIR)
    print(f'  Server running at http://localhost:{PORT}')
    print(f'  Leaderboard stored in: {SCORES_FILE}')
    print(f'  Press Ctrl+C to stop\n')
    try:
        with http.server.HTTPServer(('', PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
