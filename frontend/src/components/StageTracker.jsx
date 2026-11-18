const STAGES = ["Awareness", "Client problem", "Solve client problem", "Discussion", "Negotiation", "Conversion"];

export default function StageTracker({ enquiry, onChange }) {
  const start = { new_client: 1, referral: 4, rebuy: 5, new_product: 3 }[enquiry.enquiry_type];
  return (
    <section className="panel stage-panel">
      <h2>Sales funnel</h2>
      <div className="stage-track">
        {STAGES.map((label, index) => {
          const stage = index + 1;
          const skipped = stage < start;
          const current = stage === enquiry.current_stage;
          return (
            <div className={`stage-step ${skipped ? "skipped" : ""} ${current ? "current" : ""}`} key={label}>
              <span>{stage}</span><strong>{label}</strong>
              {skipped && <small>Skipped by fast-track</small>}
            </div>
          );
        })}
      </div>
      <div className="stage-actions">
        <button disabled={enquiry.current_stage <= 1} onClick={() => onChange(enquiry.current_stage - 1)}>Move back</button>
        <button disabled={enquiry.current_stage >= 6} onClick={() => onChange(enquiry.current_stage + 1)}>Move forward</button>
      </div>
    </section>
  );
}
