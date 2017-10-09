import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote
import requests

mapping = {}

blnk_form = """
<!DOCTYPE html>
<html>
<head>
	<title>JPs BookMark App</title>
</head>
<body>
<h2>J-P's BookMark site</h2>
<hr>
<p>Sure, its pretty useless in that it doesn't have a backend, so there is no persistent data storage... yet.</p>
	<form method = "POST">
		<table>
			<tr>
				<th>
					<h3>Original URL</h3>
				</th>
				<th>
					<h3>Shortened URL</h3>
				</th>									
			</tr>
			<tr>
				<td>
					<input type="text" name="url_lng" placeholder="URL">
				</td>
				<td>
					<input type="text" name="url_shrt" placeholder="Short URL">
				</td>
			</tr>
			<tr>
				<td>&nbsp;</td>
				<td></td>
			</tr>
			<tr>
				<td></td>
				<td><button type = "submit">Make Shortcut</button></td>
			</tr>
			<tr>
				<td>&nbsp;</td>
				<td></td>
			</tr>
		</table>
	</form>
	<hr>
	<div>
		<div style="width: 33%;"></div>
		<div style="width: 33%;">
			<pre>{}</pre>
		</div>
		<div style="width: 33%;"></div>
	</div>
</body>
</html>

"""

def checkURI(uri2chk, timeout = 5):
	try:
		r = requests.get(uri2chk, timeout = timeout)
		return r.status_code == 200
	except requests.RequestException:
		return False

class BookMark(BaseHTTPRequestHandler):
	def do_GET(self):
		name = unquote(self.path[1:])
		if name:
			if name in mapping:
				self.send_response(303)
				self.send_header("Location", mapping[name])
				self.end_headers()
			else:
				self.send_response(404)
				self.send_header("Content-type","text/html; charset = utf-8")
				self.end_headers()
				self.wfile.write(("Unfortunately, the shortcut {}, is not in your bookmarks").format(name).encode())
		else:
			self.send_response(200)
			self.send_header("Content-type","text/html; charset=utf-8")
			self.end_headers()

			li = "\n".join("Full URL: {} | TinyURL: {}".format(mapping[key], key) for key in mapping.keys())
			self.wfile.write(blnk_form.format(li).encode())

	def do_POST(self):
		length = int(self.headers.get("Content-Length", 0))
		data = self.rfile.read(length).decode()
		msg = parse_qs(data)

		# Check that the user submitted the form fields.
		if "url_lng" not in msg or "url_shrt" not in msg:
			self.send_response(400)
			self.send_header('Content-type', 'text/plain; charset=utf-8')
			self.end_headers()
			self.wfile.write("Missing form fields!".encode())
			return

		shrt_uri = msg["url_shrt"][0]
		lng_uri = msg["url_lng"][0]


		if checkURI(lng_uri) == True:
			mapping[shrt_uri] = lng_uri
			self.send_response(303)
			self.send_header("Location", "/")
			self.end_headers()
		else:
			self.send_response(404)
			self.send_header("Content-type","text/html; charset = utf-8")
			self.end_headers()
			self.wfile.write("Unfortunately, the url \" {} \", is not a valid uri".format(lng_uri).encode())

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	server_address = ('', port)
	httpd = HTTPServer(server_address, BookMark)
	httpd.serve_forever()
