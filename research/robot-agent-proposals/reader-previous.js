"use strict";
(() => {
  const files = {
    icl: { title: "上下文学习", file: "01_in_context_learning.pdf", count: 6 },
    control: { title: "底层控制", file: "02_low_level_control.pdf", count: 6 },
    response: { title: "即时响应", file: "03_realtime_response.pdf", count: 6 },
    combined: { title: "完整合订版", file: "Robot_Agent_Three_Proposals_Combined.pdf", count: 18 }
  };
  const groups = ["icl", "control", "response"];
  const image = document.getElementById("page-image");
  const surface = document.querySelector(".page-surface");
  const select = document.getElementById("page-select");
  const previous = document.getElementById("previous");
  const next = document.getElementById("next");
  const error = document.getElementById("image-error");
  let current = "icl";
  let page = 1;

  function render() {
    const match = /^#(icl|control|response|combined)(?:\/page-(\d+))?$/.exec(location.hash);
    current = match ? match[1] : "icl";
    const info = files[current];
    page = Math.min(info.count, Math.max(1, Number(match && match[2]) || 1));
    document.getElementById("document-title").textContent = info.title;
    document.title = `${info.title} · Robot Agent Proposals | Zimo Wen`;
    document.querySelectorAll("[data-doc]").forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.doc === current));
    });
    select.replaceChildren(...Array.from({length: info.count}, (_, i) => {
      const option = new Option(`${i + 1} / ${info.count}`, String(i + 1));
      option.selected = i + 1 === page;
      return option;
    }));
    previous.disabled = page === 1;
    next.disabled = page === info.count;
    const status = `${info.title}，第 ${page} 页，共 ${info.count} 页`;
    image.alt = status;
    document.getElementById("page-status").textContent = status;
    const pdf = `pdf/${info.file}`;
    document.getElementById("open-pdf").href = pdf;
    document.getElementById("download-current").href = pdf;
    const group = current === "combined" ? groups[Math.floor((page - 1) / 6)] : current;
    const leaf = (page - 1) % 6 + 1;
    const src = `pages/${group}-${String(leaf).padStart(2, "0")}.webp`;
    if (image.getAttribute("src") !== src) {
      error.hidden = true;
      surface.setAttribute("aria-busy", "true");
      image.src = src;
    }
  }

  function navigate(doc, number) {
    location.hash = `${doc}/page-${number}`;
    render();
  }
  document.querySelectorAll("[data-doc]").forEach(button => {
    button.addEventListener("click", () => navigate(button.dataset.doc, 1));
  });
  previous.addEventListener("click", () => { if (page > 1) navigate(current, page - 1); });
  next.addEventListener("click", () => { if (page < files[current].count) navigate(current, page + 1); });
  select.addEventListener("change", () => navigate(current, Number(select.value)));
  image.addEventListener("load", () => surface.setAttribute("aria-busy", "false"));
  image.addEventListener("error", () => {
    surface.setAttribute("aria-busy", "false");
    error.hidden = false;
  });
  document.addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey || /INPUT|SELECT|TEXTAREA|BUTTON/.test(event.target.tagName)) return;
    if (event.key === "ArrowLeft" && page > 1) { event.preventDefault(); navigate(current, page - 1); }
    if (event.key === "ArrowRight" && page < files[current].count) { event.preventDefault(); navigate(current, page + 1); }
  });
  window.addEventListener("hashchange", render);
  render();
})();
