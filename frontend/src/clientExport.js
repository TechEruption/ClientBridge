const CLIENT_FIELDS = [
  "name",
  "designation",
  "phone",
  "company_email",
  "company_name",
  "country",
  "industry",
  "product_interest",
  "enquiry_type",
  "message",
  "referred_by",
  "previous_order_ref",
  "quantity",
  "current_product_used",
  "new_product_needed",
];

export function clientProvidedData(enquiry) {
  return Object.fromEntries(
    CLIENT_FIELDS
      .filter((field) => {
        const value = enquiry[field];
        return value !== undefined && value !== null && value !== "";
      })
      .map((field) => [field, enquiry[field]])
  );
}

export function downloadClientJson(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
