import { useEffect, useState } from "react";
import { api } from "../api";
import { INDUSTRIES, PRODUCTS } from "../catalogue";

const TYPES = [
  ["new_client", "New customer", "First time contacting us"],
  ["referral", "Referral", "Referred by someone"],
  ["rebuy", "Repeat order", "I have bought from you before"],
  ["new_product", "New product", "Existing customer with a new need"],
];

const NAME_ERROR = "Only alphabets, hyphens and apostrophes";

export default function EnquiryForm({ sessionId }) {
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [thanks, setThanks] = useState("");
  const [form, setForm] = useState({
    name: "", designation: "", phone: "", company_email: "", company_name: "",
    country: "", industry: "", product_interest: [], enquiry_type: "new_client",
    message: "", referred_by: "", previous_order_ref: "", quantity: "",
    current_product_used: "", new_product_needed: "", honeypot: "", math_answer: "",
  });

  useEffect(() => {
    const savedEmail = localStorage.getItem("seallink_client_email");
    if (savedEmail) setForm((current) => ({ ...current, company_email: savedEmail }));
  }, []);

  function setField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  function validate() {
    const next = {};
    if (!/^[A-Za-z\s\-']+$/.test(form.name)) next.name = NAME_ERROR;
    if (!/^[A-Za-z\s\-']+$/.test(form.designation)) next.designation = NAME_ERROR;
    if (!/^\+[1-9]\d{7,14}$/.test(form.phone)) next.phone = "Please enter a valid phone number with country code";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.company_email)) next.company_email = "Please enter a valid email";
    if (!form.company_name) next.company_name = "Company name is required";
    if (!form.country) next.country = "Country is required";
    if (!form.industry) next.industry = "Please choose an industry";
    if (!form.product_interest.length) next.product_interest = "Please choose at least one product";
    if (!form.message.trim()) next.message = "Message cannot be blank";
    if (form.enquiry_type === "referral" && !form.referred_by) next.referred_by = "Referred by is required";
    if (form.enquiry_type === "rebuy" && (!form.previous_order_ref || !form.quantity)) next.quantity = "Order reference and quantity are required";
    if (form.enquiry_type === "new_product" && (!form.current_product_used || !form.new_product_needed)) next.new_product_needed = "Both product fields are required";
    if (form.math_answer !== "7") next.math_answer = "Please answer 4 + 3 correctly";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function submit(event) {
    event.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const result = await api("/api/enquiries", {
        method: "POST",
        body: JSON.stringify({ ...form, session_id: sessionId }),
      });
      setThanks(result.enquiry_id);
    } catch (error) {
      setErrors({ submit: error.message });
    } finally {
      setLoading(false);
    }
  }

  if (thanks) {
    return (
      <div className="thank-you">
        <span className="success-mark">✓</span>
        <h3>Thank you</h3>
        <p>Your enquiry has been received.</p>
        <strong>Enquiry ID: {thanks}</strong>
      </div>
    );
  }

  return (
    <form className="enquiry-form" onSubmit={submit} noValidate>
      <fieldset>
        <legend>Enquiry type</legend>
        <div className="type-grid">
          {TYPES.map(([value, title, text]) => (
            <label className={form.enquiry_type === value ? "type-card active" : "type-card"} key={value}>
              <input type="radio" name="enquiry_type" value={value} checked={form.enquiry_type === value} onChange={setField} />
              <strong>{title}</strong>
              <span>{text}</span>
            </label>
          ))}
        </div>
        <p className="fast-track-note">Already know us? Choose Repeat order or Referral to skip the introduction and go straight to your requirement.</p>
      </fieldset>

      <div className="form-grid">
        <Field label="Name" name="name" value={form.name} onChange={setField} error={errors.name} />
        <Field label="Designation" name="designation" value={form.designation} onChange={setField} error={errors.designation} />
        <Field label="Phone" name="phone" value={form.phone} onChange={setField} placeholder="+91..." error={errors.phone} />
        <Field label="Company email" name="company_email" value={form.company_email} onChange={setField} type="email" error={errors.company_email} />
        <Field label="Company name" name="company_name" value={form.company_name} onChange={setField} error={errors.company_name} />
        <Field label="Country" name="country" value={form.country} onChange={setField} error={errors.country} />
        <label>
          Industry
          <select name="industry" value={form.industry} onChange={setField}>
            <option value="">Select industry</option>
            {INDUSTRIES.map((value) => <option key={value}>{value}</option>)}
          </select>
          {errors.industry && <small className="error">{errors.industry}</small>}
        </label>
        <label>
          Product interest
          <select multiple name="product_interest" size="4" value={form.product_interest} onChange={(event) => setForm((current) => ({ ...current, product_interest: [...event.target.selectedOptions].map((option) => option.value) }))}>
            {PRODUCTS.map((value) => <option key={value} value={value}>{value}</option>)}
          </select>
          <small className="field-hint">Select one or more products. On a computer, use Ctrl-click to select multiple.</small>
          {errors.product_interest && <small className="error">{errors.product_interest}</small>}
        </label>
      </div>

      {form.enquiry_type === "referral" && <Field label="Referred by" name="referred_by" value={form.referred_by} onChange={setField} error={errors.referred_by} />}
      {form.enquiry_type === "rebuy" && (
        <div className="form-grid">
          <Field label="Previous order / invoice reference" name="previous_order_ref" value={form.previous_order_ref} onChange={setField} />
          <Field label="Quantity" name="quantity" value={form.quantity} onChange={setField} error={errors.quantity} />
        </div>
      )}
      {form.enquiry_type === "new_product" && (
        <div className="form-grid">
          <Field label="Product you currently use" name="current_product_used" value={form.current_product_used} onChange={setField} />
          <Field label="New product needed" name="new_product_needed" value={form.new_product_needed} onChange={setField} error={errors.new_product_needed} />
        </div>
      )}

      <label>
        Message
        <textarea name="message" value={form.message} onChange={setField} rows="5" />
        {errors.message && <small className="error">{errors.message}</small>}
      </label>
      <div className="honeypot" aria-hidden="true">
        <input name="honeypot" tabIndex="-1" autoComplete="off" value={form.honeypot} onChange={setField} />
      </div>
      <Field label="Security question: What is 4 + 3?" name="math_answer" value={form.math_answer} onChange={setField} error={errors.math_answer} />
      {errors.submit && <p className="error">{errors.submit}</p>}
      <button className="primary-button" type="submit" disabled={loading}>{loading ? "Sending..." : "Submit enquiry"}</button>
    </form>
  );
}

function Field({ label, name, value, onChange, error, type = "text", placeholder = "" }) {
  return (
    <label>
      {label}
      <input name={name} value={value} onChange={onChange} type={type} placeholder={placeholder} />
      {error && <small className="error">{error}</small>}
    </label>
  );
}
