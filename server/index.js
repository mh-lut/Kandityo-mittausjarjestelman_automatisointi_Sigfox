// ------------------------------
// Program name: index.ino
// Description: Server routes
// Date: 10.8.2023
// Notes: This is part of the automated measurement system (sigfox)
// ------------------------------

var express = require('express');
var router = express.Router();
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./database2.db');
const fs = require('fs');

/* Home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Sigfox message reception server' });
});

// Use json
router.use(express.json());

// Create the table if it doesn't exist
db.run('CREATE TABLE IF NOT EXISTS serverInfo (device TEXT, time TEXT, seqNumber TEXT, data TEXT, deviceTypeId TEXT, serverTime TEXT)', (err) => {
  if (err) {
    console.error(err);
  }
});

// Create the extra table if it doesn't exist
db.run('CREATE TABLE IF NOT EXISTS serverInfo2 (device TEXT, time TEXT, seqNumber TEXT, data TEXT, deviceTypeId TEXT, lqi TEXT, linkQuality TEXT, fixedLat TEXT, fixedLng TEXT, operatorName TEXT, countryCode TEXT, serverTime TEXT)', (err) => {
  if (err) {
    console.error(err);
  }
});


router.post('/api/post', (req, res, next) => {  // Receives messages from the sigfox backend
  console.log(req.body);
  const { device, time, seqNumber, data, deviceTypeId } = req.body; // collect info
  const serverTime = Date.now(); // Reception time

  // Save data
  db.run('INSERT INTO serverInfo (device, time, seqNumber, data, deviceTypeId, serverTime) VALUES (?, ?, ?, ?, ?, ?)', [device, time, seqNumber, data, deviceTypeId, serverTime], (err) => {
    if (err) {
      // If any error
      console.error(err);
      res.status(500).send('Internal Server Error In Inserting Data');
    } else {
      // Send ok
      res.send("OK");
    }
  });
});

router.post('/api/post2', (req, res, next) => {  // Receives extra info from the sigfox backend
  console.log(req.body);
  const { device, time, seqNumber, data, deviceTypeId, lqi, linkQuality, fixedLat, fixedLng, operatorName, countryCode } = req.body; // collect info
  const serverTime = Date.now(); // Reception time

  // Save data
  db.run('INSERT INTO serverInfo2 (device, time, seqNumber, data, deviceTypeId, lqi, linkQuality, fixedLat, fixedLng, operatorName, countryCode, serverTime) VALUES (?, ?, ?, ?, ?, ? ,? ,? ,? ,? ,? ,?)', [device, time, seqNumber, data, deviceTypeId, lqi, linkQuality, fixedLat, fixedLng, operatorName, countryCode, serverTime], (err) => {
    if (err) {
      // If any error
      console.error(err);
      res.status(500).send('Internal Server Error In Inserting Data');
    } else {
      // Send ok
      res.send("OK");
    }
  });
});

router.get('/api/get', (req, res) => { // Send json
  db.all('SELECT * FROM serverInfo', (err, rows) => {
    if (err) {
      // Id any error
      console.error(err);
      res.status(500).send('Internal Server Error');
    } else {
      //Send data
      res.json(rows);
    }
  });
});

router.get('/download', (req, res) => { // Send database file
  res.download('./database2.db', (err) => {
    if (err) {
      // Error messages
      console.error('Error while downloading file:', err);
      res.status(500).send('Error downloading file');
    }
  });;
});

// Close the connection to the database 
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Database connection succesfully closed.');
    process.exit(0);
  });
});

module.exports = router;
