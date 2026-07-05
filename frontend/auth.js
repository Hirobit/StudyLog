const API = (location.hostname === "127.0.0.1" || location.hostname === "localhost")
  ? "http://127.0.0.1:8000"
  : window.location.origin;

// 未ログインならlogin.htmlへ飛ばす（各画面の一番最初に呼ぶ）
function requireAuth() {
  const token = localStorage.getItem("studylog_token");
  if (!token) {
    location.href = "login.html";
  }
}

// Authorizationヘッダーを自動で付けるfetchラッパー
// 既存コードの fetch(...) を authFetch(...) に置き換えるだけで使える
async function authFetch(url, options = {}) {
  const token = localStorage.getItem("studylog_token");
  const headers = {
    ...(options.headers || {}),
    "Authorization": `Bearer ${token}`
  };
  const res = await fetch(url, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("studylog_token");
    location.href = "login.html";
    throw new Error("Unauthorized");
  }
  return res;
}

// ログアウト処理（ヘッダーのログアウトボタンから呼ぶ）
function logout() {
  localStorage.removeItem("studylog_token");
  location.href = "login.html";
}