"use strict";
(() => {
  const files = {
    control: { title: "Better manipulation", file: "01_manipulation_system0_force_en.pdf", count: 6 },
    response: { title: "Reactive policy synthesis", file: "02_agent_generated_reactive_policies_en.pdf", count: 6 },
    review: { title: "Multi-robot interaction", file: "03_multirobot_runtime_en.pdf", count: 6 },
    combined: { title: "Complete collection", file: "Robot_Agent_Control_Response_MultiRobot_EN_20260914.pdf", count: 18 }
  };
  const groups = ["control", "response", "multihost"];
  const image = document.getElementById("page-image");
  const surface = document.querySelector(".page-surface");
  const select = document.getElementById("page-select");
  const previous = document.getElementById("previous");
  const next = document.getElementById("next");
  const error = document.getElementById("image-error");
  let current = "control";
  let page = 1;

  function render() {
    const match = /^#(control|response|review|dagger|combined)(?:\/page-(\d+))?$/.exec(location.hash);
    current = match ? (match[1] === "dagger" ? "review" : match[1]) : "control";
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
    const status = `${info.title}, page ${page} of ${info.count}`;
    image.alt = status;
    document.getElementById("page-status").textContent = status;
    const pdf = `pdf/${info.file}`;
    document.getElementById("open-pdf").href = pdf;
    document.getElementById("download-current").href = pdf;
    const group = current === "combined" ? groups[Math.floor((page - 1) / 6)] : (current === "review" ? "multihost" : current);
    const leaf = (page - 1) % 6 + 1;
    const src = `pages/en/${group}-${String(leaf).padStart(2, "0")}.webp`;
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
