document.addEventListener("DOMContentLoaded", () => {
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
});
