interface HelpProps {
  text: string;
}

/** Ícone de ajuda "?" com tooltip explicativo exibido em hover/foco. */
export function Help({ text }: HelpProps) {
  return (
    <span className="help" tabIndex={0} aria-label="Ajuda">
      <span className="help-icon" aria-hidden="true">
        ?
      </span>
      <span className="help-tip" role="tooltip">
        {text}
      </span>
    </span>
  );
}
