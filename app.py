const fs = require('fs');
const express = require('express');
const wiegine = require('fca-mafiya');
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 21731;

// Configuration and session storage
const sessions = new Map();
let wss;

// HTML Control Panel with session management
const htmlControlPanel = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYCO AHSAN Message Sender Bot</title>
    <style>
        :root {
            --color1: #FF9EC5; /* BLACK */
            --color2: #9ED2FF; /* RED */
            --color3: #FFFFFF; /* BLUE */
            --color4: #FFB6D9; /* BLACK HURT */
            --text-dark: #333333;
            --text-light: #FFFFFF;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, var(--color1) 0%, var(--color2) 100%);
            color: var(--text-dark);
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            margin-bottom: 25px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .status {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 10px;
            font-weight: bold;
            text-align: center;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }
        
        .online { background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%); color: white; }
        .offline { background: linear-gradient(135deg, #f44336 0%, #E91E63 100%); color: white; }
        .connecting { background: linear-gradient(135deg, #ff9800 0%, #FFC107 100%); color: white; }
        .server-connected { background: linear-gradient(135deg, var(--color2) 0%, var(--color1) 100%); color: var(--text-dark); }
        
        .panel {
            background: rgba(255, 255, 255, 0.9);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
            backdrop-filter: blur(5px);
        }
        
        button {
            padding: 12px 20px;
            margin: 8px;
            cursor: pointer;
            background: linear-gradient(135deg, var(--color2) 0%, var(--color1) 100%);
            color: var(--text-dark);
            border: none;
            border-radius: 8px;
            transition: all 0.3s;
            font-weight: bold;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        button:disabled {
            background: #cccccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        input, select, textarea {
            padding: 12px 15px;
            margin: 8px 0;
            width: 100%;
            border: 2px solid var(--color2);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.8);
            color: var(--text-dark);
            font-size: 16px;
            transition: all 0.3s;
            box-sizing: border-box;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--color1);
            box-shadow: 0 0 0 3px rgba(158, 210, 255, 0.3);
        }
        
        .log {
            height: 300px;
            overflow-y: auto;
            border: 2px solid var(--color2);
            padding: 15px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
            background: rgba(0, 0, 0, 0.8);
            color: #00ff00;
            border-radius: 10px;
            box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        
        small {
            color: #666;
            font-size: 13px;
        }
        
        h1, h2, h3 {
            color: var(--text-dark);
            margin-top: 0;
        }
        
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--color1) 0%, var(--color2) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }
        
        .session-info {
            background: linear-gradient(135deg, var(--color2) 0%, var(--color1) 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            color: var(--text-dark);
        }
        
        .tab {
            overflow: hidden;
            border: 2px solid var(--color2);
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .tab button {
            background: transparent;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 20px;
            transition: 0.3s;
            margin: 0;
            border-radius: 0;
            width: 50%;
        }
        
        .tab button:hover {
            background: rgba(158, 210, 255, 0.2);
        }
        
        .tab button.active {
            background: linear-gradient(135deg, var(--color2) 0%, var(--color1) 100%);
            color: var(--text-dark);
        }
        
        .tabcontent {
            display: none;
            padding: 15px;
            border: 2px solid var(--color2);
            border-top: none;
            border-radius: 0 0 10px 10px;
            background: rgba(255, 255, 255, 0.8);
        }
        
        .active-tab {
            display: block;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            background: linear-gradient(135deg, var(--color2) 0%, var(--color1) 100%);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            color: var(--text-dark);
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }
        
        .cookie-status {
            margin-top: 15px;
            padding: 12px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.8);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .cookie-active {
            border-left: 5px solid #4CAF50;
        }
        
        .cookie-inactive {
            border-left: 5px solid #f44336;
        }
        
        .heart {
            color: var(--color4);
            margin: 0 5px;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: var(--text-dark);
            font-size: 14px;
        }
        
        .session-manager {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, var(--color1) 0%, var(--color2) 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, var(--color4) 0%, var(--color1) 100%);
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .tab button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span class="heart">SYCO AHSAN</span> Message Sender Bot <span class="heart">SYCO AHSAN</span></h1>
        <p>Send messages automatically using multiple Facebook accounts - Sessions continue even if you close this page!</p>
    </div>
    
    <div class="status server-connected" id="status">
        Status: Connecting to server...
    </div>
    
    <div class="panel">
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'cookie-file-tab')">Cookie File</button>
            <button class="tablinks" onclick="openTab(event, 'cookie-text-tab')">Paste Cookies</button>
        </div>
        
        <div id="cookie-file-tab" class="tabcontent active-tab">
            <input type="file" id="cookie-file" accept=".txt">
            <small>Select your cookies file (each line should contain one cookie)</small>
        </div>
        
        <div id="cookie-text-tab" class="tabcontent">
            <textarea id="cookie-text" placeholder="Paste your cookies here (one cookie per line)" rows="5"></textarea>
            <small>Paste your cookies directly (one cookie per line)</small>
        </div>
        
        <div>
            <input type="text" id="thread-id" placeholder="Thread/Group ID">
            <small>Enter the Facebook Group/Thread ID where messages will be sent</small>
        </div>
        
        <div>
            <input type="number" id="delay" value="5" min="1" placeholder="Delay in seconds">
            <small>Delay between messages (in seconds)</small>
        </div>
        
        <div>
            <input type="text" id="prefix" placeholder="Message Prefix (Optional)">
            <small>Optional prefix to add before each message</small>
        </div>
        
        <div>
            <label for="message-file">Messages File</label>
            <input type="file" id="message-file" accept=".txt">
            <small>Upload messages.txt file with messages (one per line)</small>
        </div>
        
        <div style="text-align: center;">
            <button id="start-btn">Start Sending <span class="heart">SYCO AHSAN</span></button>
            <button id="stop-btn" disabled>Stop Sending <span class="heart">SYCO AHSAN</span></button>
        </div>
        
        <div id="session-info" style="display: none;" class="session-info">
            <h3>Your Session ID: <span id="session-id-display"></span></h3>
            <p>Save this ID to stop your session later or view its details</p>
        </div>
    </div>
    
    <div class="panel session-manager">
        <h3><span class="heart">SYCO AHSAN</span> Session Manager</h3>
        <p>Enter your Session ID to manage your running session</p>
        
        <input type="text" id="manage-session-id" placeholder="Enter your Session ID">
        
        <div style="text-align: center; margin-top: 15px;">
            <button id="view-session-btn">View Session Details</button>
            <button id="stop-session-btn">Stop Session</button>
        </div>
        
        <div id="session-details" style="display: none; margin-top: 20px;">
            <h4>Session Details</h4>
            <div class="stats">
                <div class="stat-box">
                    <div>Status</div>
                    <div id="detail-status">-</div>
                </div>
                <div class="stat-box">
                    <div>Total Messages Sent</div>
                    <div id="detail-total-sent">-</div>
                </div>
                <div class="stat-box">
                    <div>Current Loop Count</div>
                    <div id="detail-loop-count">-</div>
                </div>
                <div class="stat-box">
                    <div>Started At</div>
                    <div id="detail-started">-</div>
                </div>
            </div>
            
            <h4>Cookies Status</h4>
            <div id="detail-cookies-status"></div>
            
            <h4>Session Logs</h4>
            <div class="log" id="detail-log-container"></div>
        </div>
    </div>
    
    <div class="panel">
        <h3><span class="heart">SYCO AHSAN</span> Active Session Statistics</h3>
        <div class="stats" id="stats-container">
            <div class="stat-box">
                <div>Status</div>
                <div id="stat-status">Not Started</div>
            </div>
            <div class="stat-box">
                <div>Total Messages Sent</div>
                <div id="stat-total-sent">0</div>
            </div>
            <div class="stat-box">
                <div>Current Loop Count</div>
                <div id="stat-loop-count">0</div>
            </div>
            <div class="stat-box">
                <div>Current Message</div>
                <div id="stat-current">-</div>
            </div>
            <div class="stat-box">
                <div>Current Cookie</div>
                <div id="stat-cookie">-</div>
            </div>
            <div class="stat-box">
                <div>Started At</div>
                <div id="stat-started">-</div>
            </div>
        </div>
        
        <h3><span class="heart">SYCO AHSAN</span> Cookies Status</h3>
        <div id="cookies-status-container"></div>
        
        <h3><span class="heart">SYCO AHSAN</span> Logs</h3>
        <div class="log" id="log-container"></div>
    </div>

    <div class="footer">
        <p>Made with <span class="heart">SYCO AHSAN</span> | Sessions continue running even if you close this page!</p>
    </div>

    <script>
        const logContainer = document.getElementById('log-container');
        const statusDiv = document.getElementById('status');
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const cookieFileInput = document.getElementById('cookie-file');
        const cookieTextInput = document.getElementById('cookie-text');
        const threadIdInput = document.getElementById('thread-id');
        const delayInput = document.getElementById('delay');
        const prefixInput = document.getElementById('prefix');
        const messageFileInput = document.getElementById('message-file');
        const sessionInfoDiv = document.getElementById('session-info');
        const sessionIdDisplay = document.getElementById('session-id-display');
        const cookiesStatusContainer = document.getElementById('cookies-status-container');
        
        // Session manager elements
        const manageSessionIdInput = document.getElementById('manage-session-id');
        const viewSessionBtn = document.getElementById('view-session-btn');
        const stopSessionBtn = document.getElementById('stop-session-btn');
        const sessionDetailsDiv = document.getElementById('session-details');
        const detailStatus = document.getElementById('detail-status');
        const detailTotalSent = document.getElementById('detail-total-sent');
        const detailLoopCount = document.getElementById('detail-loop-count');
        const detailStarted = document.getElementById('detail-started');
        const detailCookiesStatus = document.getElementById('detail-cookies-status');
        const detailLogContainer = document.getElementById('detail-log-container');
        
        // Stats elements
        const statStatus = document.getElementById('stat-status');
        const statTotalSent = document.getElementById('stat-total-sent');
        const statLoopCount = document.getElementById('stat-loop-count');
        const statCurrent = document.getElementById('stat-current');
        const statCookie = document.getElementById('stat-cookie');
        const statStarted = document.getElementById('stat-started');
        
        let currentSessionId = null;
        let reconnectAttempts = 0;
        let maxReconnectAttempts = 10;
        let socket = null;
        let sessionLogs = new Map();

        function openTab(evt, tabName) {
            const tabcontent = document.getElementsByClassName("tabcontent");
            for (let i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            
            const tablinks = document.getElementsByClassName("tablinks");
            for (let i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }

        function addLog(message, type = 'info', sessionId = null) {
            const logEntry = document.createElement('div');
            const timestamp = new Date().toLocaleTimeString();
            let prefix = '';
            
            switch(type) {
                case 'success':
                    prefix = 'SYCO';
                    break;
                case 'error':
                    prefix = 'SYCO';
                    break;
                case 'warning':
                    prefix = 'SYCO';
                    break;
                default:
                    prefix = 'SYCO';
            }
            
            logEntry.innerHTML = \`<span style="color: #FF9EC5">[\${timestamp}]</span> \${prefix} \${message}\`;
            
            if (sessionId) {
                // Store log for specific session
                if (!sessionLogs.has(sessionId)) {
                    sessionLogs.set(sessionId, []);
                }
                sessionLogs.get(sessionId).push(logEntry.innerHTML);
                
                // If we're currently viewing this session, add to detail log
                if (manageSessionIdInput.value === sessionId) {
                    detailLogContainer.appendChild(logEntry.cloneNode(true));
                    detailLogContainer.scrollTop = detailLogContainer.scrollHeight;
                }
            } else {
                // Add to main log
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        }
        
        function updateStats(data, sessionId = null) {
            if (sessionId && manageSessionIdInput.value === sessionId) {
                // Update session details
                if (data.status) detailStatus.textContent = data.status;
                if (data.totalSent !== undefined) detailTotalSent.textContent = data.totalSent;
                if (data.loopCount !== undefined) detailLoopCount.textContent = data.loopCount;
                if (data.started) detailStarted.textContent = data.started;
            }
            
            if (!sessionId || sessionId === currentSessionId) {
                // Update main stats
                if (data.status) statStatus.textContent = data.status;
                if (data.totalSent !== undefined) statTotalSent.textContent = data.totalSent;
                if (data.loopCount !== undefined) statLoopCount.textContent = data.loopCount;
                if (data.current) statCurrent.textContent = data.current;
                if (data.cookie) statCookie.textContent = \`Cookie \${data.cookie}\`;
                if (data.started) statStarted.textContent = data.started;
            }
        }
        
        function updateCookiesStatus(cookies, sessionId = null) {
            if (sessionId && manageSessionIdInput.value === sessionId) {
                // Update session details cookies status
                detailCookiesS
