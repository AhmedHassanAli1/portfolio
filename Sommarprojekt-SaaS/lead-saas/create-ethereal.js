const nodemailer = require("nodemailer");

async function main() {
  const testAccount = await nodemailer.createTestAccount();

  console.log("KOPIERA DETTA TILL DIN .env:\n");

  console.log(`SMTP_HOST=smtp.ethereal.email`);
  console.log(`SMTP_PORT=587`);
  console.log(`SMTP_SECURE=false`);
  console.log(`SMTP_USER=${testAccount.user}`);
  console.log(`SMTP_PASS=${testAccount.pass}`);
  console.log(`SMTP_FROM=LeadFlow <${testAccount.user}>`);
}

main().catch(console.error);