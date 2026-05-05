/**
 * Warning banner list.
 */
export function Warnings({ warnings }: { warnings: string[] }) {
  if (!warnings.length) {
    return null;
  }
  return (
    <section className="card warning">
      <h4>Coverage Warnings</h4>
      <ul>
        {warnings.map((warning) => (
          <li key={warning}>{warning}</li>
        ))}
      </ul>
    </section>
  );
}

