const express = require('express')
require('dotenv').config()

console.log(process.env.URL_FRONTEND)

const app = express()
app.get('/', (req, res) => {
    res.status(200).json({
        msg: "Hello ABA TECH IAC",
        env: process.env.URL_FRONTEND
    })
})
app.listen(3000, () => {
    console.log('Server is up on 3000')
})