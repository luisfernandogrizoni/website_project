// ------------------- CONTROLADOR DA PÁGINA: DASHBOARD (MODAL) ------------------- //

import { maskCPF, maskRG, maskSUS, maskData, formatarTexto } from '../utils/formatters.js';

export class DashboardController {

    /**
     * @param {Object} apiService - Instância injetada para comunicação HTTP.
     * @param {Object} notificationService - Instância injetada para alertas.
     */
    constructor(apiService, notificationService) {
        this.api = apiService;
        this.notificacao = notificationService
    }

    /**
     * Ponto de entrada do Controlador. Abre o modal, exibe estado de carregamento,
     * busca os dados do paciente e orquestra a renderização.
     * @param {number|string} id - O identificador único do paciente.
     */
    async abrir(id) {
        const modal = document.getElementById('modalDashboard');
        const nomeEl = document.getElementById('d-nome');

        // 1. Lógica Visual de Entrada: Mostra o modal e o estado de "Loading"
        if (modal) {
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('show'), 10);
        }
        if (nomeEl) nomeEl.innerText = "Buscando dados...";

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
        const modal = document.getElementById('modalDashboard');
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => modal.style.display = 'none', 300);
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
        const boxInativo = document.getElementById('d-box-inativo');
        const badgeAtivo = document.getElementById('d-badge-ativo');

        if (badgeAtivo) {
            if (data.ativo) {
                badgeAtivo.className = "badge badge-padrao";
                badgeAtivo.innerText = 'Ativo';
            } else {
                badgeAtivo.className = "badge";
                badgeAtivo.innerText = 'Inativo';
            }
        }

        if (boxInativo) {
            if (data.ativo) {
                boxInativo.style.display = 'none';
            } else {
                boxInativo.style.display = 'block';

                const elDataSaida = document.getElementById('d-data-saida');
                const elMotivo = document.getElementById('d-motivo-saida');

                if (elDataSaida) elDataSaida.innerText = maskData(data.data_saida);
                if (elMotivo) elMotivo.innerText = data.motivo_saida || 'Motivo não informado';
            }
        }
    }

    /**
     * Injeta dinamicamente as rotas corretas (com o ID do paciente) nos botões de ação do modal.
     * @param {number|string} id - O identificador do paciente para a rota HTTP.
     */
    #configBotoes(id) {
        const btnEdit = document.getElementById('btnEdit');
        if (btnEdit) {
            btnEdit.href = `/paciente/${id}/editar`;
        }

        const btnInactivate = document.getElementById('btnInactivate');
        if (btnInactivate) {
            btnInactivate.href = `/paciente/${id}/baixa`
        }

    }
}
