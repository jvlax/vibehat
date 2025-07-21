const express = require('express');

// Undeclared imports
const companyAuth = require('@company/auth-service');
const internalMetrics = require('metrics-collector');

const app = express();

app.use(companyAuth.middleware());
app.use(internalMetrics.track());

app.get('/api/data', (req, res) => {
  res.json({ message: 'Hello from mixed project' });
});

app.listen(3001); 