const jwt = require("jsonwebtoken");
const { SECRET } = require("./auth");

module.exports = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: "No token provided" });
  }

  try {
    const token = authHeader.replace("Bearer ", "");
    const decoded = jwt.verify(token, SECRET);

    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: "Invalid token" });
  }
};