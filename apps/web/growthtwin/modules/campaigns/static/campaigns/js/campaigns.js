"use strict";

document.querySelectorAll("[data-character-counter-for]").forEach((counter) => {
  const field = document.getElementById(counter.dataset.characterCounterFor);
  if (!field || field.maxLength < 0) return;

  const describedBy = new Set(
    (field.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean),
  );
  describedBy.add(counter.id);
  field.setAttribute("aria-describedby", [...describedBy].join(" "));

  const updateCount = () => {
    counter.textContent = `${field.value.length}/${field.maxLength} karakter`;
  };

  field.addEventListener("input", updateCount);
  updateCount();
});
