document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const menuToggle = document.querySelector(".menu-toggle");

  if (menuToggle) {
    menuToggle.addEventListener("click", () => {
      const isOpen = body.classList.toggle("menu-open");
      menuToggle.setAttribute("aria-expanded", String(isOpen));
      menuToggle.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
    });

    document.querySelectorAll(".primary-nav a").forEach((link) => {
      link.addEventListener("click", () => {
        body.classList.remove("menu-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Open navigation menu");
      });
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && body.classList.contains("menu-open")) {
        body.classList.remove("menu-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Open navigation menu");
        menuToggle.focus();
      }
    });
  }

  const siteSearch = document.querySelector("[data-site-search]");
  if (siteSearch) {
    const pages = [
      { terms: ["home", "osborn", "healthcare"], url: "/" },
      { terms: ["about", "story", "mission"], url: "/about" },
      { terms: ["service", "services", "kidney", "diabetes", "blood pressure", "hypertension"], url: "/#services" },
      { terms: ["pathology", "lab", "test", "tests", "blood test"], url: "/pathology" },
      { terms: ["pharmacy", "medicine", "medicines", "prescription"], url: "/pharmacy" },
      { terms: ["doctor", "doctors", "deepak", "provider"], url: "/providers" },
      { terms: ["resource", "resources", "blog", "health guide"], url: "/resources" },
      { terms: ["location", "locations", "address", "branch", "branches", "map"], url: "/#locations" },
      { terms: ["appointment", "book", "booking", "consultation"], url: "/appointment" },
    ];

    siteSearch.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = siteSearch.querySelector("input");
      const query = input.value.trim().toLowerCase();
      if (!query) {
        input.focus();
        return;
      }
      const match = pages.find((page) => page.terms.some((term) => query.includes(term) || term.includes(query)));
      if (match) {
        window.location.assign(match.url);
        return;
      }
      input.setCustomValidity("No matching page found. Try services, pathology, pharmacy, doctors, resources, or locations.");
      input.reportValidity();
    });

    siteSearch.querySelector("input").addEventListener("input", (event) => event.target.setCustomValidity(""));
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

  const appointmentForm = document.querySelector("[data-availability-url]");
  if (appointmentForm) {
    const clinicInput = appointmentForm.querySelector("#id_clinic");
    const dateInput = appointmentForm.querySelector("#id_preferred_date");
    const serviceInput = appointmentForm.querySelector("#id_service");
    const timeInput = appointmentForm.querySelector("#id_preferred_time");
    const slotInput = appointmentForm.querySelector("#id_slot_id");
    const slotStatus = appointmentForm.querySelector("[data-slot-status]");

    const loadSlots = async () => {
      if (!clinicInput.value || !dateInput.value || !serviceInput.value) {
        slotStatus.textContent = "Choose a clinic, date, and service to check live availability.";
        return;
      }
      slotStatus.textContent = "Checking live availability...";
      slotInput.value = "";
      try {
        const params = new URLSearchParams({
          clinic: clinicInput.value,
          date: dateInput.value,
          service: serviceInput.value,
        });
        const response = await fetch(`${appointmentForm.dataset.availabilityUrl}?${params}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Scheduling is unavailable.");
        if (!data.configured) {
          slotStatus.textContent = "Online availability is not configured yet. You can still submit a request.";
          return;
        }
        if (!data.slots.length) {
          slotStatus.textContent = "No live slots are available for this selection.";
          return;
        }
        const firstSlot = data.slots[0];
        timeInput.value = firstSlot.time || firstSlot.start || firstSlot;
        slotInput.value = firstSlot.id || firstSlot.slot_id || "";
        slotStatus.textContent = `${data.slots.length} live slot${data.slots.length === 1 ? "" : "s"} available. The first available time is selected.`;
      } catch (error) {
        slotStatus.textContent = `${error.message} You can still submit a request.`;
      }
    };

    [clinicInput, dateInput, serviceInput].forEach((input) => input.addEventListener("change", loadSlots));
  }
});
