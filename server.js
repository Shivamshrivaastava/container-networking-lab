const express = require('express');
const app = express();

const PORT = 8080;
const HOST = '127.0.0.1';

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.listen(PORT, HOST, () => {
  console.log(`Server running on http://${HOST}:${PORT}`);
});
