require("dotenv").config();

const express = require("express");
const cors = require("cors");
const path = require("path");

const routes = require("./routes");
require("./engine");

const app = express();

app.use(cors());
app.use(express.json());

// serve frontend
app.use(express.static(path.join(__dirname, "../client")));

// root = login
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "../client/login.html"));
});

app.use("/", routes);

app.listen(3000, () => console.log("http://localhost:3000"));