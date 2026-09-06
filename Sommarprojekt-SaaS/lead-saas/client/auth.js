const API = "http://localhost:3000";

async function login() {
  const res = await fetch(API + "/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      email: email.value,
      password: password.value
    })
  });

  const data = await res.json();
  localStorage.setItem("token", data.token);

  window.location = "/dashboard.html";
}