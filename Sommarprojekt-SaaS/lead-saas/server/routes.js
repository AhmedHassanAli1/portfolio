const express = require("express");
const router = express.Router();

const db = require("./db");
const auth = require("./auth");
const protect = require("./middleware");

// =====================
// LOGIN
// =====================
router.post("/login", (req, res) => {
  const user = db.findUser(req.body.email);

  if (!user) {
    return res.status(400).json({ error: "No user found" });
  }

  if (!auth.comparePassword(req.body.password, user.password)) {
    return res.status(400).json({ error: "Wrong password" });
  }

  const token = auth.generateToken(user);

  res.json({
    token,
    user: {
      id: user.id,
      name: user.name,
      email: user.email
    }
  });
});

// =====================
// REGISTER
// =====================
router.post("/register", (req, res) => {
  const user = db.createUser(req.body);
  res.json(user);
});

// =====================
// LEADS
// =====================
function createLead(req, res) {
  const lead = db.addLead({
    userId: req.user.id,
    name: req.body.name,
    email: req.body.email,
    phone: req.body.phone,
    message: req.body.message
  });

  res.json(lead);
}

// ny tydlig route
router.post("/leads", protect, createLead);

// gammal route kvar för bakåtkompatibilitet
router.post("/sms", protect, createLead);

router.get("/leads", protect, (req, res) => {
  res.json(db.getLeadsByUser(req.user.id));
});

router.post("/leads/:id", protect, (req, res) => {
  db.updateLeadStatus(req.params.id, req.body.status);
  res.json({ ok: true });
});

// =====================
// AUTOMATIONS
// =====================
router.post("/automations", protect, (req, res) => {
  const rule = db.addAutomation({
    userId: req.user.id,
    channel: req.body.channel,
    delaySeconds: req.body.delaySeconds,
    subject: req.body.subject,
    message: req.body.message
  });

  res.json(rule);
});

router.get("/automations", protect, (req, res) => {
  res.json(db.getAutomationsByUser(req.user.id));
});

router.delete("/automations/:id", protect, (req, res) => {
  db.deleteAutomation(req.params.id);
  res.json({ ok: true });
});

// =====================
// EMAIL LOG
// =====================
router.get("/email-log", protect, (req, res) => {
  res.json(db.getEmailsByUser(req.user.id));
});

// =====================
// SMS LOG
// =====================
router.get("/sms-log", protect, (req, res) => {
  res.json(db.getSMSByUser(req.user.id));
});

// =====================
// ACTIVITY FEED
// =====================
router.get("/activity", protect, (req, res) => {
  res.json(db.getActivityByUser(req.user.id) || []);
});

module.exports = router;