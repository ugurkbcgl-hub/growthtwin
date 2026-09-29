(() => {
  const briefInput = document.getElementById("campaign-brief");
  const dailyLimitInput = document.getElementById("daily-limit");
  const daysInput = document.getElementById("campaign-days");
  const briefCount = document.getElementById("brief-count");
  const budgetTotal = document.getElementById("budget-total");
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
  let planEditTarget = "campaign-brief";

  const formatNumber = (value) =>
    new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 }).format(value);

  const formatLira = (value) => `₺${formatNumber(value)}`;

  const updateBudget = () => {
    const amount = Number(dailyLimitInput.value);
    const days = Number(daysInput.value);
    budgetTotal.textContent =
      Number.isFinite(amount) && amount > 0 ? formatLira(amount * days) : "—";
  };

  const showStep = (step, shouldScroll = false) => {
    panels.forEach((panel, index) => {
      panel.hidden = index !== step - 1;
    });
    if (shouldScroll) {
      panels[step - 1].scrollIntoView({ block: "start", behavior: "instant" });
    }
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
    pauseButton.setAttribute("aria-label", "Örnek akışı durdur");
  };

  const showSavedPreview = (campaign) => {
    const brief = campaign.dataset.brief;
    const brandContext = campaign.dataset.brandContext;
    const targetAudience = campaign.dataset.targetAudience;
    const objective = campaign.dataset.objective;
    const amount = Number(campaign.dataset.dailyLimit);
    const days = Number(campaign.dataset.durationDays);
    const total = amount * days;
    document.getElementById("preview-brief").textContent = brief;
    const brandContextPreview = document.getElementById("preview-brand-context");
    brandContextPreview.textContent = brandContext;
    brandContextPreview.hidden = !brandContext;
    const targetAudiencePreview = document.getElementById("preview-target-audience");
    targetAudiencePreview.textContent = targetAudience ? `Kitle: ${targetAudience}` : "";
    targetAudiencePreview.hidden = !targetAudience;
    const objectivePreview = document.getElementById("preview-objective");
    objectivePreview.textContent = objective ? `Hedef: ${objective}` : "";
    objectivePreview.hidden = !objective;
    document.getElementById("preview-limit").textContent = formatLira(amount);
    document.getElementById("preview-duration").textContent = `${days} gün`;
    document.getElementById("preview-total").textContent = formatLira(total);
    document.getElementById("plan-budget").textContent =
      `${formatLira(total)} toplam · ${formatLira(amount)} / gün · ${days} gün`;
    const needsReview = campaign.dataset.needsReview === "true";
    planEditTarget = campaign.dataset.firstMissingField || "campaign-brief";
    document.getElementById("edit-brief").textContent = needsReview
      ? "← Bilgileri gözden geçir"
      : "← Planı düzenle";
    document.getElementById("report-brief").textContent = brief;
    document.getElementById("report-period").textContent = `${days} günlük örnek görünüm`;
    resetDemoAutomation();
    showStep(2);
  };

  briefInput.addEventListener("input", () => {
    briefCount.textContent = `${briefInput.value.length} / 280`;
  });
  dailyLimitInput.addEventListener("input", updateBudget);
  daysInput.addEventListener("change", updateBudget);
  document.getElementById("edit-brief").addEventListener("click", () => {
    showStep(1, true);
    if (planEditTarget === "target-audience" || planEditTarget === "brand-context") {
      document.querySelector(".optional-context").open = true;
    }
    document.getElementById(planEditTarget).focus();
  });
  document
    .getElementById("show-report")
    .addEventListener("click", () => showStep(3, true));
  pauseButton.addEventListener("click", () => {
    demoPaused = !demoPaused;
    document.getElementById("automation-state").textContent =
      demoPaused ? "Örnek akış duraklatıldı" : "Örnek akış etkin";
    document.querySelector(".automation-row").classList.toggle("is-paused", demoPaused);
    pauseButton.textContent = demoPaused ? "Devam ettir" : "Durdur";
    pauseButton.setAttribute(
      "aria-label",
      demoPaused ? "Örnek akışı devam ettir" : "Örnek akışı durdur",
    );
    flowStatus.textContent = demoPaused
      ? "Örnek akış duraklatıldı. Gerçek kampanya yok."
      : "Örnek akış yeniden etkin. Gerçek kampanya yok.";
  });
  briefCount.textContent = `${briefInput.value.length} / 280`;
  updateBudget();
  const savedCampaign = document.getElementById("saved-campaign");
  if (savedCampaign) {
    showSavedPreview(savedCampaign);
    document
      .getElementById("kampanya-denemesi")
      .scrollIntoView({ block: "start", behavior: "instant" });
  } else {
    showStep(1);
  }
  const firstInvalidField = document.querySelector(
    '[aria-invalid="true"][autofocus]',
  );
  if (firstInvalidField) {
    const focusFirstInvalidField = () => firstInvalidField.focus();
    window.addEventListener("load", focusFirstInvalidField, { once: true });
    focusFirstInvalidField();
  }
})();
