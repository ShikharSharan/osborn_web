document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const menuToggle = document.querySelector(".menu-toggle");

  if (menuToggle) {
    menuToggle.addEventListener("click", () => {
      const isOpen = body.classList.toggle("menu-open");
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    });

    document.querySelectorAll(".primary-nav a").forEach((link) => {
      link.addEventListener("click", () => {
        body.classList.remove("menu-open");
        menuToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  document.querySelectorAll(".toast").forEach((toast) => {
    window.setTimeout(() => toast.remove(), 6800);
  });

  const toggleGroup = (field, shouldShow) => {
    if (!field) return;
    const group = field.closest(".form-group");
    if (!group) return;
    group.hidden = !shouldShow;
  };

  const pharmacyMode = document.querySelector("#id_delivery_mode");
  const pharmacyAddress = document.querySelector('[data-conditional-field="pharmacy-address"]');
  const syncPharmacyAddress = () => {
    toggleGroup(pharmacyAddress, pharmacyMode && pharmacyMode.value === "home_delivery");
  };

  if (pharmacyMode) {
    pharmacyMode.addEventListener("change", syncPharmacyAddress);
    syncPharmacyAddress();
  }

  const collectionMode = document.querySelector("#id_collection_mode");
  const collectionAddress = document.querySelector('[data-conditional-field="pathology-address"]');
  const syncCollectionAddress = () => {
    toggleGroup(collectionAddress, collectionMode && collectionMode.value === "home_collection");
  };

  if (collectionMode) {
    collectionMode.addEventListener("change", syncCollectionAddress);
    syncCollectionAddress();
  }

  const dateInputs = document.querySelectorAll('input[type="date"], input[name*="date"]');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const minDate = today.toISOString().slice(0, 10);

  dateInputs.forEach((input) => {
    input.min = input.min || minDate;
    input.addEventListener("input", () => {
      if (!input.value) return;
      const selected = new Date(`${input.value}T00:00:00`);
      const isPast = selected < today;
      const isThursday = selected.getDay() === 4;

      if (isPast || isThursday) {
        input.setCustomValidity(isThursday ? "The clinic is closed on Thursdays." : "Please choose today or a future date.");
      } else {
        input.setCustomValidity("");
      }
    });
  });
});
