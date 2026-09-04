import { useMemo } from "react";
import { validarFormulario, type FormularioState } from "../domain/formularioSimulacao";

interface ChecklistValidacaoProps {
  estado: FormularioState;
}

export function ChecklistValidacao({ estado }: ChecklistValidacaoProps) {
  const { itens } = useMemo(() => validarFormulario(estado), [estado]);

  return (
    <ul aria-label="checklist-validacao">
      {itens.map((item) => (
        <li key={item.chave} data-valido={item.valido}>
          {item.valido ? "✅" : "❌"} {item.descricao}
        </li>
      ))}
    </ul>
  );
}

