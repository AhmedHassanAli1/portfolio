const bcrypt = require("bcryptjs");
const nodemailer = require("nodemailer");

// =====================
// USERS
// =====================
let users = [
  {
    id: 1,
    name: "Ahmed",
    email: "test@test.com",
    password: bcrypt.hashSync("123456", 8),
    plan: "free",
    subscriptionActive: true
  }
];

// =====================
// CORE DATA
// =====================
let leads = [];
let automations = [];
let smsLog = [];
let emailLog = [];
let activityLog = [];

let leadId = 1;
let automationId = 1;

// =====================
// HELPERS
// =====================
function addActivity(userId, message) {
  activityLog.unshift({
    id: Date.now() + Math.floor(Math.random() * 1000),
    userId,
    message,
    createdAt: Date.now()
  });
}

function createMailTransport() {
  const host = process.env.SMTP_HOST;
  const port = Number(process.env.SMTP_PORT || 587);
  const secure = String(process.env.SMTP_SECURE || "false") === "true";
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;

  if (!host || !user || !pass) {
    return null;
  }

  return nodemailer.createTransport({
    host,
    port,
    secure,
    auth: {
      user,
      pass
    }
  });
}

// =====================
// DB CORE
// =====================
module.exports = {
  users,
  leads,
  automations,
  smsLog,
  emailLog,
  activityLog,
  addActivity,

  // =====================
  // USERS
  // =====================
  createUser: (user) => {
    const newUser = {
      id: Date.now(),
      name: user.name || "Användare",
      email: user.email,
      password: bcrypt.hashSync(user.password, 8)
    };

    users.push(newUser);
    return newUser;
  },

  findUser: (email) => users.find(u => u.email === email),

  // =====================
  // LEADS
  // =====================
  addLead: (lead) => {
    const newLead = {
      id: leadId++,
      name: lead.name || "Okänd",
      email: lead.email || "",
      phone: lead.phone || "",
      message: lead.message || "Ingen beskrivning",
      status: "NY",
      followUpSmsStatus: "NONE",
      followUpEmailStatus: "NONE",
      createdAt: Date.now(),
      userId: lead.userId
    };

    leads.push(newLead);

    addActivity(lead.userId, `Ny lead skapad: ${newLead.name}`);

    return newLead;
  },

  getLeadsByUser: (userId) =>
    leads
      .filter(l => l.userId === userId)
      .sort((a, b) => b.createdAt - a.createdAt),

  updateLeadStatus: (id, status) => {
    const lead = leads.find(l => l.id === Number(id));
    if (!lead) return false;

    lead.status = status;
    return true;
  },

  // =====================
  // AUTOMATIONS
  // =====================
  addAutomation: (a) => {
    const rule = {
      id: automationId++,
      userId: a.userId,
      channel: a.channel === "email" ? "email" : "sms",
      delaySeconds: Number(a.delaySeconds) || 10,
      subject: a.subject || "Uppföljning från LeadFlow",
      message: a.message || "Standard uppföljning",
      createdAt: Date.now()
    };

    automations.push(rule);

    addActivity(
      a.userId,
      `Automation skapad (${rule.channel.toUpperCase()}, ${rule.delaySeconds}s delay)`
    );

    return rule;
  },

  getAutomationsByUser: (userId) =>
    automations
      .filter(a => a.userId === userId)
      .sort((a, b) => b.createdAt - a.createdAt),

  deleteAutomation: (id) => {
    const index = automations.findIndex(a => a.id === Number(id));
    if (index === -1) return false;

    automations.splice(index, 1);
    return true;
  },

  // =====================
  // SMS (SIMULERAD)
  // =====================
  sendSMS: (sms) => {
    const entry = {
      id: Date.now(),
      userId: sms.userId,
      to: sms.to || "",
      message: sms.message,
      status: sms.to ? "SENT" : "FAILED",
      createdAt: Date.now()
    };

    smsLog.unshift(entry);

    if (entry.status === "SENT") {
      addActivity(sms.userId, `SMS skickat till ${sms.to}`);
    } else {
      addActivity(sms.userId, "SMS kunde inte skickas: telefonnummer saknas");
    }

    return entry;
  },

  getSMSByUser: (userId) =>
    smsLog
      .filter(s => s.userId === userId)
      .sort((a, b) => b.createdAt - a.createdAt),

  // =====================
  // EMAIL (SMTP / ETHEREAL)
  // =====================
  sendEmail: async (email) => {
    const entry = {
      id: Date.now(),
      userId: email.userId,
      to: email.to || "",
      subject: email.subject || "Uppföljning från LeadFlow",
      message: email.message || "",
      status: "QUEUED",
      previewUrl: null,
      createdAt: Date.now()
    };

    try {
      if (!email.to) {
        throw new Error("E-postadress saknas på lead");
      }

      const transporter = createMailTransport();

      if (!transporter) {
        throw new Error("SMTP är inte konfigurerat i .env");
      }

      const info = await transporter.sendMail({
        from: process.env.SMTP_FROM || process.env.SMTP_USER,
        to: email.to,
        subject: entry.subject,
        text: entry.message,
        html: `
          <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <p>${entry.message.replace(/\n/g, "<br>")}</p>
          </div>
        `
      });

      entry.status = "SENT";
      entry.previewUrl = nodemailer.getTestMessageUrl(info) || null;

      emailLog.unshift(entry);
      addActivity(email.userId, `Mail skickat till ${email.to}`);

      if (entry.previewUrl) {
        console.log("📧 ETHEREAL PREVIEW:", entry.previewUrl);
      }

      return entry;
    } catch (error) {
      entry.status = "FAILED";
      entry.error = error.message;

      emailLog.unshift(entry);
      addActivity(
        email.userId,
        `Mail kunde inte skickas till ${email.to || "okänd adress"}`
      );

      console.error("EMAIL ERROR:", error.message);

      return entry;
    }
  },

  getEmailsByUser: (userId) =>
    emailLog
      .filter(e => e.userId === userId)
      .sort((a, b) => b.createdAt - a.createdAt),

  // =====================
  // ACTIVITY FEED
  // =====================
  getActivityByUser: (userId) =>
    activityLog
      .filter(a => a.userId === userId)
      .sort((a, b) => b.createdAt - a.createdAt)
};