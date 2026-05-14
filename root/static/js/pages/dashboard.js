// ------------------- CONTROLADOR DA PÁGINA: DASHBOARD (MODAL) ------------------- //

import { maskCPF, maskRG, maskSUS, maskData, formatarTexto } from '../utils/formatters.js';

export class DashboardController {

    /**
     * Inicializa o controlador do Dashboard mapeando as ferramentas e o DOM.
     * * @param {Object} apiService - Instância injetada para comunicação HTTP.
     * @param {Object} notificationService - Instância injetada para alertas de UI.
     * @param {Object} configIds - Dicionário contendo os IDs dos elementos HTML estruturais.
     * @param {string} configIds.modalId - ID do container principal do modal.
     * @param {string} configIds.nomeId - ID do elemento que exibe o nome do paciente.
     * @param {string} configIds.badgeAtivoId - ID do crachá principal de status (Ativo/Inativo).
     * @param {string} configIds.boxInativoId - ID da caixa que contém os detalhes da alta/baixa.
     * @param {string} configIds.dataSaidaId - ID do elemento de texto da data de saída.
     * @param {string} configIds.motivoId - ID do elemento de texto do motivo da saída.
     * @param {string} configIds.btnEditId - ID do botão de redirecionamento para edição.
     * @param {string} configIds.btnInactivateId - ID do botão de redirecionamento para baixa.
     */

    constructor(apiService, notificationService, configIds) {
            this.api = apiService;
            this.notificacao = notificationService;

            // Mapeamento dos elementos estruturais DOM salvos na memória da Classe
            this.modal = document.getElementById(configIds.modalId);
            this.nomeEl = document.getElementById(configIds.nomeId);

            // Elementos de Status
            this.badgeAtivo = document.getElementById(configIds.badgeAtivoId);
            this.boxInativo = document.getElementById(configIds.boxInativoId);
            this.elDataSaida = document.getElementById(configIds.dataSaidaId);
            this.elMotivo = document.getElementById(configIds.motivoId);

            // Botões de Ação
            this.btnEdit = document.getElementById(configIds.btnEditId);
            this.btnInactivate = document.getElementById(configIds.btnInactivateId);
    }

    /**
     * Ponto de entrada do Controlador. Abre o modal, exibe estado de carregamento,
     * busca os dados do paciente e orquestra a renderização.
     * @param {number|string} id - O identificador único do paciente.
     */
    async abrir(id) {

        // 1. Lógica Visual de Entrada: Mostra o modal e o estado de "Loading"
        if (this.modal) {
            this.modal.style.display = 'flex';
            setTimeout(() => this.modal.classList.add('show'), 10);
        }
        if (this.nomeEl) this.nomeEl.innerText = "Buscando dados...";

        // 2. Lógica de Dados: Busca na API e orquestra
        try {
            const data = await this.api.request(`/api/paciente/${id}`);
            this.#preencherTextos(data);
            this.#configurarStatus(data);
            this.#convenioBadge(data.convenio);
            this.#configBotoes(id)
        } catch (error) {
            console.error("[Dashboard] Erro:", error);
            this.notificacao.erro("Paciente não encontrado ou erro de servidor.");
            this.fechar();
        }
    }

    /**
     * Lida com a transição CSS e oculta o modal da tela.
     */
    fechar() {
        if (this.modal) {
            this.modal.classList.remove('show');
            setTimeout(() => this.modal.style.display = 'none', 300);
        }
    }

    // -----------------------------------------
    // MÉTODOS PRIVADOS
    // -----------------------------------------

    /**
     * Mapeia os dados do banco para os respectivos IDs no HTML e aplica as máscaras.
     * @param {Object} data - O objeto com os dados do paciente retornados da API.
     */
    #preencherTextos(data) {

        // Dicionário de Mapeamento (Data-Driven UI)
        const mapa = {
            'd-nome': data.nome,
            'd-convenio': data.convenio,
            'd-idade': data.idade ? `${data.idade} anos` : '-',
            'd-internacao': maskData(data.data_internacao),

            'd-cpf': maskCPF(data.cpf),
            'd-rg': maskRG(data.rg),
            'd-nascimento': maskData(data.data_nascimento),
            'd-sus': maskSUS(data.cartao_sus),
            'd-mae': formatarTexto(data.mae),

            'd-escolaridade': formatarTexto(data.escolaridade),
            'd-profissao': formatarTexto(data.profissao),
            'd-religiao': formatarTexto(data.religiao),
            'd-civil': formatarTexto(data.estado_civil),
            'd-conjuge': formatarTexto(data.conjuge),

            'd-endereco': data.endereco_completo,
            'd-bairro': data.bairro,
            'd-cidade': data.cidade,
            'd-estado': data.estado,
            'd-contato': data.contato,
            'd-contato2': data.contato_dois,

            'd-resp-nome': formatarTexto(data.responsavel),
            'd-resp-relacao': formatarTexto(data.relacao),
            'd-contrib': 'R$' + data.contrib,
            'd-resp-cpf': maskCPF(data.cpf_resp),
            'd-resp-rg': maskRG(data.rg_resp),
        };

        // Motor de injeção automática no DOM
        for (const [idDOM, valorFormatado] of Object.entries(mapa)) {
            const elemento = document.getElementById(idDOM);

            if (elemento) {
                elemento.innerText = valorFormatado || '-';
            } else {
                console.warn(`[Dashboard] O ID '${idDOM}' não foi encontrado no HTML.`);
            }
        }
    }

    /**
     * Aplica as cores corretas nas badges de acordo com o tipo de convênio.
     * @param {string} convenioStr - A string bruta do convênio vinda do banco.
     */
    #convenioBadge(convenioStr) {
        const elBadge = document.getElementById('d-badge-status')
        if (!elBadge) return;

        const convenioMinusculo = (convenioStr || '').toLowerCase();

        let classeBadge = 'badge-padrao';
        let textoBadge = convenioStr || 'Não Informado';

        if (convenioMinusculo.includes('social')) {
            classeBadge = 'badge-social';
            textoBadge = 'Social';
        } else if (convenioMinusculo.includes('particular')) {
            classeBadge = 'badge-particular';
            textoBadge = 'Particular';
        } else if (convenioMinusculo.includes('capsad')) {
            classeBadge = 'badge-caps';
            textoBadge = 'Caps AD';
        } else if (convenioMinusculo.includes('taruma')) {
            classeBadge = 'badge-taruma';
            textoBadge = 'Convênio Tarumã';
        }

        elBadge.className = `badge ${classeBadge}`;
        elBadge.innerText = textoBadge
    }

    /**
     * Gerencia a exibição da caixa de desligamento e da badge principal de status.
     * @param {Object} data - Objeto do paciente para checar a propriedade booleana 'ativo'.
     */
    #configurarStatus(data) {
        if (this.badgeAtivo) {
            if (data.ativo) {
                this.badgeAtivo.className = "badge badge-padrao";
                this.badgeAtivo.innerText = 'Ativo';
            } else {
                this.badgeAtivo.className = "badge";
                this.badgeAtivo.innerText = 'Inativo';
            }
        }

        if (this.boxInativo) {
            if (data.ativo) {
                this.boxInativo.style.display = 'none';
            } else {
                this.boxInativo.style.display = 'block';

                if (this.elDataSaida) this.elDataSaida.innerText = maskData(data.data_saida);
                if (this.elMotivo) this.elMotivo.innerText = data.motivo_saida || 'Motivo não informado';
            }
        }
    }

    /**
     * Injeta dinamicamente as rotas corretas (com o ID do paciente) nos botões de ação do modal.
     * @param {number|string} id - O identificador do paciente para a rota HTTP.
     */
    #configBotoes(id) {
        if (this.btnEdit) {
            this.btnEdit.href = `/paciente/${id}/editar`;
        }

        if (this.btnInactivate) {
            this.btnInactivate.href = `/paciente/${id}/baixa`
        }

    }
}
