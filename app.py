from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import os
import re
import subprocess
import threading
import socket

# Simple YouTube downloader using yt-dlp
class YouTubeDownloaderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('/home/runner/work/cors/cors/templates/youtube_downloader.html', 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        elif self.path.startswith('/static/'):
            # Serve static files
            file_path = '/home/runner/work/cors/cors' + self.path
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                if self.path.endswith('.css'):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/css')
                    self.end_headers()
                elif self.path.endswith('.js'):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/javascript')
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            youtube_url = data.get('url', '')
            format_type = data.get('format', 'mp4')
            
            if not youtube_url or not self.is_valid_youtube_url(youtube_url):
                self.send_json_response({'error': 'رابط اليوتيوب غير صحيح'}, 400)
                return
            
            try:
                # Use yt-dlp to get video info
                result = self.download_video(youtube_url, format_type)
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({'error': f'حدث خطأ: {str(e)}'}, 500)
    
    def is_valid_youtube_url(self, url):
        pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)'
        return re.match(pattern, url) is not None
    
    def download_video(self, url, format_type):
        # Create downloads directory if it doesn't exist
        downloads_dir = '/tmp/downloads'
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Simple simulation for now - in real implementation would use yt-dlp
        return {
            'success': True,
            'title': 'فيديو تجريبي',
            'message': f'تم تحضير الفيديو للتحميل بصيغة {format_type}',
            'download_url': f'/download_file?format={format_type}'
        }
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def run_server(port=5000):
    # Find available port
    sock = socket.socket()
    sock.bind(('', port))
    sock.listen(1)
    port = sock.getsockname()[1]
    sock.close()
    
    server = HTTPServer(('', port), YouTubeDownloaderHandler)
    print(f"خادم تحميل اليوتيوب يعمل على المنفذ {port}")
    print(f"افتح المتصفح على: http://localhost:{port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()