// ממסר קול: מקבל שמע מהמשדר (בשרת) ומעביר לדף /screen/ באתר.
// מאזין רק ל-127.0.0.1; nginx מעביר אליו את /kol/ws.
const http = require('http');
const { WebSocketServer } = require('ws');

const PORT = +(process.env.PORT || 8097);
const HOST = process.env.HOST || '127.0.0.1';
const ACCESS_KEY = process.env.ACCESS_KEY || '';

const server = http.createServer((req, res) => {
  res.writeHead(req.url === '/health' ? 200 : 404, { 'Content-Type': 'text/plain' });
  res.end(req.url === '/health' ? 'ok' : '');
});

// rooms: name -> { sender, config, listeners:Set }
const rooms = new Map();
function getRoom(name) {
  if (!rooms.has(name)) rooms.set(name, { sender: null, config: null, listeners: new Set() });
  return rooms.get(name);
}
function cleanup(name) {
  const r = rooms.get(name);
  if (r && !r.sender && r.listeners.size === 0) rooms.delete(name);
}
function sendJson(ws, obj) {
  if (ws.readyState === ws.OPEN) ws.send(JSON.stringify(obj));
}
function notifySender(room) {
  if (room.sender) sendJson(room.sender, { type: 'listeners', count: room.listeners.size });
}

const wss = new WebSocketServer({ server, path: '/ws', maxPayload: 1 << 20 });

wss.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://x');
  const role = url.searchParams.get('role');
  const roomName = (url.searchParams.get('room') || 'main').slice(0, 64);
  const key = url.searchParams.get('key') || '';

  if (ACCESS_KEY && key !== ACCESS_KEY) {
    sendJson(ws, { type: 'error', message: 'קוד גישה שגוי' });
    return ws.close(4001, 'bad key');
  }
  if (role !== 'sender' && role !== 'listener') return ws.close(4000, 'bad role');

  ws.isAlive = true;
  ws.on('pong', () => (ws.isAlive = true));

  const room = getRoom(roomName);

  if (role === 'sender') {
    if (room.sender) {
      sendJson(room.sender, { type: 'error', message: 'משדר אחר התחבר לחדר הזה' });
      room.sender.close(4002, 'replaced');
    }
    room.sender = ws;
    room.config = null;
    notifySender(room);

    ws.on('message', (data, isBinary) => {
      if (room.sender !== ws) return;
      if (!isBinary) {
        try {
          const msg = JSON.parse(data.toString());
          if (msg.type === 'config') {
            room.config = { type: 'config', sampleRate: msg.sampleRate | 0, channels: msg.channels | 0 };
            for (const l of room.listeners) sendJson(l, room.config);
          }
        } catch {}
        return;
      }
      for (const l of room.listeners) {
        // מאזין איטי מדי מדלג על חבילות במקום לצבור עיכוב
        if (l.readyState === l.OPEN && l.bufferedAmount < 256 * 1024) l.send(data, { binary: true });
      }
    });
    ws.on('close', () => {
      if (room.sender === ws) {
        room.sender = null;
        room.config = null;
        for (const l of room.listeners) sendJson(l, { type: 'sender-gone' });
      }
      cleanup(roomName);
    });
  } else {
    room.listeners.add(ws);
    if (room.config) sendJson(ws, room.config);
    else sendJson(ws, { type: 'sender-gone' });
    notifySender(room);
    ws.on('close', () => {
      room.listeners.delete(ws);
      notifySender(room);
      cleanup(roomName);
    });
  }
});

// פינג קבוע שומר על החיבור פתוח וסוגר חיבורים מתים
setInterval(() => {
  for (const ws of wss.clients) {
    if (!ws.isAlive) {
      ws.terminate();
      continue;
    }
    ws.isAlive = false;
    ws.ping();
  }
}, 20000);

server.listen(PORT, HOST, () => console.log(`kol relay on ${HOST}:${PORT}`));
