import { useMemo } from "react";
import { validarFormulario, type FormularioState } from "../domain/formularioSimulacao";

interface ChecklistValidacaoProps {
  estado: FormularioState;
}

export function ChecklistValidacao({ estado }: ChecklistValidacaoProps) {
  const { itens } = useMemo(() => validarFormulario(estado), [estado]);

  return (
    <ul className="checklist" aria-label="checklist-validacao">
      {itens.map((item) => (
        <li key={item.chave} data-valido={item.valido}>
          <span className="check-dot" /> {item.descricao}
        </li>
      ))}
    </ul>
  );
}

