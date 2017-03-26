
const express = require('express');
const mysql = require('mysql');
const router = express.Router();

const connection = mysql.createConnection(require('../configs/database'));
connection.connect();

// GET home page.
router.get('/', (request, response, next) => {
  response.send('Home');
});

// GET SQL query results
router.get('/sql', (request, response, next) => {
  console.log('query: ', request.query);
  // Find rows by SQL query in GENE DB.
  connection.query(request.query.query, (err, rows) => {
    if (err) {
      response.send('Invalid SQL statement');
      return;
    }

    console.log('The solution is: ', rows);
    response.send(rows);
  });
});

module.exports = router;