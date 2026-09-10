export default function Card({ title, subtitle, actions, children, className="" }) {
  return (
    <section className={`card ${className}`}>
      {(title || subtitle || actions) && (
        <div className="card-head">
          <div>{title && <h3>{title}</h3>}{subtitle && <p>{subtitle}</p>}</div>
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}