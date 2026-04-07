export const tableTemplate = (paciente) => {
    return `
        <tr>
            <td class="td-clicavel action-trigger" 
                data-action="abrir_dashboard" 
                data-paciente-id="${paciente.id}">
                ${paciente.nome}
            </td>
            <td>${paciente.cpf}</td>
            <td>${paciente.data_internacao}</td>
            <td>${paciente.convenio}</td>
            <td>
                <button class="btn-acao action-trigger" data-action="dar_baixa" data-paciente-id="${paciente.id}">Baixa</button>
            </td>
        </tr>
    `;
};