const db = require("./db");

setInterval(() => {
  const now = Date.now();

  db.leads.forEach(lead => {
    const rules = db.automations.filter(a => a.userId === lead.userId);

    rules.forEach(rule => {
      const timePassed = now - lead.createdAt;

      const threshold = rule.delayHours * 1000; // test (sekunder istället för timmar)

      if (lead.status === "NY" && timePassed > threshold && !lead.notified) {
        console.log("AUTOMATION TRIGGERED:");
        console.log("Lead:", lead.message);
        console.log("Message:", rule.message);

        lead.notified = true;
      }
    });
  });
}, 2000);