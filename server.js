const express = require('express');
const app = express();

const PORT = 8080;
// A container port must listen on all container interfaces so Docker can
// forward traffic from the published host port to this process.
const HOST = '0.0.0.0';

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.listen(PORT, HOST, () => {
  console.log(`Server running on http://${HOST}:${PORT}`);
});
