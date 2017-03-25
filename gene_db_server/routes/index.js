const express = require('express');
const router = express.Router();

// GET home page.
router.get('/', (req, res, next) => {
  res.render('index', { title: 'Express' });
});

// GET SQL query results
router.get('/sql', (request, response, next) => {
  console.log('SQL query results');
  // Find rows by SQL query in GENE DB.
  response.send('SQL query results');
});

module.exports = router;
