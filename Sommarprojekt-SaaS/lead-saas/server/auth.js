const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");

const SECRET = "secret";

module.exports = {
  SECRET,

  generateToken: (user) =>
    jwt.sign(
      {
        id: user.id,
        email: user.email,
        name: user.name 
      },
      SECRET
    ),

  comparePassword: (pw, hash) =>
    bcrypt.compareSync(pw, hash)
};