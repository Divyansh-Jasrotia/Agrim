export function Badge({ text, className }: { text: string; className: string }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${className}`}>{text}</span>;
}
