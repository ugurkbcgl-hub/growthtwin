(() => {
  const briefInput = document.getElementById("campaign-brief");
  const dailyLimitInput = document.getElementById("daily-limit");
  const daysInput = document.getElementById("campaign-days");
  const briefCount = document.getElementById("brief-count");
  const budgetTotal = document.getElementById("budget-total");
  const briefError = document.getElementById("brief-error");
  const flowStatus = document.getElementById("flow-status");

  if (!briefInput || !dailyLimitInput || !daysInput) return;

  const panels = [
    document.getElementById("brief-panel"),
    document.getElementById("preview-panel"),
    document.getElementById("report-panel"),
  ];
  const stepLabel = document.getElementById("step-label");
  const stepCount = document.getElementById("step-count");
  const stepProgress = document.getElementById("step-progress");
  const pauseButton = document.getElementById("toggle-pause");
  const stepNames = ["Brief", "Önizleme", "Örnek rapor"];
  let demoPaused = false;

  const formatNumber = (value) =>
    new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 }).format(value);

  const formatLira = (value) => `₺${formatNumber(value)}`;

  const updateBudget = () => {
    const amount = Number(dailyLimitInput.value);
    const days = Number(daysInput.value);
    budgetTotal.textContent =
      Number.isFinite(amount) && amount > 0 ? formatLira(amount * days) : "—";
  };

  const showStep = (step) => {
    panels.forEach((panel, index) => {
      panel.hidden = index !== step - 1;
    });
    const stepName = document.createElement("span");
    stepName.textContent = stepNames[step - 1];
    stepLabel.replaceChildren(document.createTextNode(`0${step} `), stepName);
    stepCount.textContent = `${step} / 3`;
    stepProgress.style.width = `${(step / 3) * 100}%`;
    flowStatus.textContent = `Örnek akış: ${stepNames[step - 1]} adımı.`;
  };

  const resetDemoAutomation = () => {
    demoPaused = false;
    document.getElementById("automation-state").textContent = "Örnek akış etkin";
    document.querySelector(".automation-row").classList.remove("is-paused");
    pauseButton.textContent = "Durdur";
    pauseButton.setAttribute("aria-pressed", "false");
  };

  const createPreview = () => {
    const brief = briefInput.value.trim();
    briefError.hidden = true;

    if (!brief) {
      briefError.hidden = false;
      briefInput.focus();
      return;
    }
    if (!dailyLimitInput.reportValidity()) return;

    const amount = Number(dailyLimitInput.value);
    const days = Number(daysInput.value);
    const total = amount * days;
    document.getElementById("preview-brief").textContent = brief;
    document.getElementById("preview-limit").textContent = formatLira(amount);
    document.getElementById("preview-duration").textContent = `${days} gün`;
    document.getElementById("preview-total").textContent = formatLira(total);
    document.getElementById("report-brief").textContent = brief;
    document.getElementById("report-period").textContent = `${days} günlük örnek görünüm`;
    resetDemoAutomation();
    showStep(2);
  };

  briefInput.addEventListener("input", () => {
    briefCount.textContent = `${briefInput.value.length} / 280`;
    briefError.hidden = true;
  });
  dailyLimitInput.addEventListener("input", updateBudget);
  daysInput.addEventListener("change", updateBudget);
  document.getElementById("create-preview").addEventListener("click", createPreview);
  document.getElementById("edit-brief").addEventListener("click", () => showStep(1));
  document.getElementById("show-report").addEventListener("click", () => showStep(3));
  pauseButton.addEventListener("click", () => {
    demoPaused = !demoPaused;
    document.getElementById("automation-state").textContent =
      demoPaused ? "Örnek akış duraklatıldı" : "Örnek akış etkin";
    document.querySelector(".automation-row").classList.toggle("is-paused", demoPaused);
    pauseButton.textContent = demoPaused ? "Devam ettir" : "Durdur";
    pauseButton.setAttribute("aria-pressed", String(demoPaused));
    flowStatus.textContent = demoPaused
      ? "Örnek akış duraklatıldı. Gerçek kampanya yok."
      : "Örnek akış yeniden etkin. Gerçek kampanya yok.";
  });
  document.getElementById("restart-flow").addEventListener("click", () => {
    briefInput.value = "";
    briefCount.textContent = "0 / 280";
    briefError.hidden = true;
    resetDemoAutomation();
    showStep(1);
    briefInput.focus();
  });

  updateBudget();
})();
