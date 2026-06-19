/**
 * Simple bilingual toggle for EasyEdu.
 * Usage: include this file in every page, then call initI18n() after DOM ready.
 */
const I18N = {
  en: {
    nav_home:      "Home",
    nav_practice:  "Practice",
    nav_knowledge: "Knowledge",
    nav_upload:    "Upload",
    nav_flash:     "Flashcards",
    lang_btn:      "中文",
    // chat page
    focus_mode:    "Focus Timer",
    q_detail:      "Question",
    related_kp:    "Related Knowledge",
    similar_q:     "Similar Questions",
    back:          "Back",
    send:          "Send",
    placeholder:   "Explain your reasoning here...",
    welcome:       "Welcome to EasyEdu! Try explaining this question in your own words.",
    thinking:      "Evaluating your answer...",
    // problems page
    select_subject:"Select a subject",
    chapter_list:  "Chapters",
  },
  zh: {
    nav_home:      "首页",
    nav_practice:  "题目练习",
    nav_knowledge: "知识点速记",
    nav_upload:    "上传题目",
    nav_flash:     "抽认卡",
    lang_btn:      "EN",
    focus_mode:    "专注模式",
    q_detail:      "题目详情",
    related_kp:    "相关知识点",
    similar_q:     "相似问题",
    back:          "返回列表",
    send:          "发送",
    placeholder:   "输入你对问题的解答...",
    welcome:       "欢迎来到 EasyEdu！请用自己的话讲解这道题目。",
    thinking:      "正在评估你的回答...",
    select_subject:"选择科目",
    chapter_list:  "章节列表",
  }
};

function getCurrentLang() {
  return localStorage.getItem("easylang") || "en";
}

function setLang(lang) {
  localStorage.setItem("easylang", lang);
  applyI18n(lang);
}

function toggleLang() {
  const next = getCurrentLang() === "en" ? "zh" : "en";
  setLang(next);
}

function applyI18n(lang) {
  const t = I18N[lang] || I18N.en;
  // update all elements with data-i18n attribute
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (t[key] !== undefined) el.textContent = t[key];
  });
  // update placeholders
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (t[key] !== undefined) el.placeholder = t[key];
  });
  // update lang toggle button text
  const btn = document.getElementById("lang-toggle-btn");
  if (btn) btn.textContent = t.lang_btn;
}

function initI18n() {
  applyI18n(getCurrentLang());
}
