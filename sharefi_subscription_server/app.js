const express = require('express');

const app = express();

app.get('/', (req, res)=>{
    res.sendFile(__dirname + '/index.html');
});

app.use((req, res)=>res.sendFile(__dirname + '/404.html'));

app.listen(8080, ()=>console.log('server started at port 8080'));