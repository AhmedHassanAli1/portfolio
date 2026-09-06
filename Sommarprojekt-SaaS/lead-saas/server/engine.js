const db = require("./db");

let isRunning = false;

// Kör ofta så att test med 3-10 sekunder känns direkt
setInterval(async () => {
  if (isRunning) return;
  isRunning = true;

  try {
    const now = Date.now();

    for (const lead of db.leads) {
      const rules = db.automations.filter(a => a.userId === lead.userId);
      if (!rules.length) continue;

      for (const rule of rules) {
        const ageSeconds = (now - lead.createdAt) / 1000;
        if (ageSeconds < Number(rule.delaySeconds)) continue;

        // =====================
        // EMAIL AUTOMATION
        // =====================
        if (rule.channel === "email") {
          if (lead.followUpEmailStatus !== "NONE") continue;

          const result = await db.sendEmail({
            userId: lead.userId,
            to: lead.email,
            subject: rule.subject || "Uppföljning från LeadFlow",
            message: rule.message
          });

          lead.followUpEmailStatus = result.status;

          if (result.status === "SENT") {
            lead.status = "FOLLOWED_UP";
            db.addActivity(lead.userId, `Automatisk mailuppföljning skickad till ${lead.name}`);
          }

          console.log("⚡ AUTOMATION TRIGGERED");
          console.log(`Channel: EMAIL`);
          console.log(`Lead: ${lead.name}`);
          console.log(`Email: ${lead.email || "(saknas)"}`);
          console.log(`Subject: ${rule.subject}`);
          console.log(`Message: ${rule.message}`);
          continue;
        }

        // =====================
        // SMS AUTOMATION
        // =====================
        if (rule.channel === "sms") {
          if (lead.followUpSmsStatus !== "NONE") continue;

          const result = db.sendSMS({
            userId: lead.userId,
            to: lead.phone,
            message: rule.message
          });

          lead.followUpSmsStatus = result.status;

          if (result.status === "SENT") {
            lead.status = "FOLLOWED_UP";
            db.addActivity(lead.userId, `Automatisk SMS-uppföljning skickad till ${lead.name}`);
          }

          console.log("⚡ AUTOMATION TRIGGERED");
          console.log(`Channel: SMS`);
          console.log(`Lead: ${lead.name}`);
          console.log(`Phone: ${lead.phone || "(saknas)"}`);
          console.log(`Message: ${rule.message}`);
        }
      }
    }
  } catch (error) {
    console.error("ENGINE ERROR:", error.message);
  } finally {
    isRunning = false;
  }
}, 1000);