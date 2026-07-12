const express = require('express');
const _ = require('lodash'); // Using vulnerable lodash
const app = express();
const PORT = 3000;

app.use(express.json());

const products = [
  { id: 1, name: 'Laptop Gaming', price: 1500, stock: 10 },
  { id: 2, name: 'Wireless Mouse', price: 25, stock: 150 },
  { id: 3, name: 'Mechanical Keyboard', price: 80, stock: 45 }
];

// Health check
app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

// Get all products
app.get('/api/products', (req, res) => {
  res.json(products);
});

// Vulnerable endpoint - command execution (SAST should catch this)
// This endpoint takes user input and runs a system command
app.get('/api/products/search', (req, res) => {
  const query = req.query.q;
  const exec = require('child_process').exec;
  
  // CRITICAL SAST VULNERABILITY: Command Injection
  // Semgrep will flag child_process.exec with template literal input
  exec(`echo Search query: ${query}`, (err, stdout, stderr) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    // Simple filter using lodash
    const filtered = products.filter(p => p.name.toLowerCase().includes((query || '').toLowerCase()));
    res.json({ output: stdout, products: filtered });
  });
});

// Single product
app.get('/api/products/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const product = products.find(p => p.id === id);
  if (!product) {
    return res.status(404).json({ error: 'Product not found' });
  }
  res.json(product);
});

app.listen(PORT, () => {
  console.log(`Product service running on port ${PORT}`);
});
