// ==========================================
// CONTROLADOR DE TABELA DINÂMICA (DATA-DRIVEN)
// ==========================================

import { NotificationService } from '../core/notification.js';
import {tableTemplate} from "../pages/table-template.js";

export class TableController {
    /**
     * @param {Object} apiService - Sua classe de comunicação com o Flask
     * @param {string} tbodyId - O ID do <tbody> onde as linhas serão injetadas
     */
    constructor(apiService, tbodyId) {
        this.api = apiService;
        this.notificacao = new NotificationService;
        this.tbody = document.getElementById(tbodyId);

        // 1. FONTE DA VERDADE (Source of Truth)
        // Array imutável. Guarda o JSON original retornado pelo Flask.
        this.dadosOriginais = [];

        // 2. ESTADO DA INTERFACE (UI State)
        // Array mutável. Guarda a versão cortada/filtrada que deve ser exibida.
        this.dadosFiltrados = [];
    }

    /**
     * O "Big Bang" do componente. Disparado ao carregar a página.
     * Busca os dados no back-end e aciona a primeira renderização.
     */
    async inicializador() {
        if (!this.tbody) return;

        try {
            this.notificacao.loading('Buscando pacientes');

            // 1. Busca os dados no Flask (Requisição Assíncrona)
            this.dadosOriginais = await this.api.request('/api/pacientes');
            this.dadosFiltrados = [...this.dadosOriginais];
            this.render();
            this.notificacao.fecharAlerta();

            const inputBusca = document.getElementById('Busca');
            if (inputBusca) {
                inputBusca.addEventListener('input', (event) => {
                    this.pesquisar(event.target.value);
                });
            }

        } catch (error){
            console.error("[Table] Falha na comunicação com a API:", error);
            this.notificacao.erro('Erro de conexão com o servidor.');
        }
    }
    /**
     * Motor de Renderização (Data-to-UI).
     * Limpa o HTML atual e reconstrói as linhas baseado no array 'dadosFiltrados'.
     */
    render() {
        if (!this.tbody) return;

        this.tbody.innerHTML = '';

        if (this.dadosFiltrados.length === 0) {
            this.tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Nenhum paciente encontrado.</td></tr>';
            return;
        }

        this.dadosFiltrados.forEach(paciente => {

            const linhaHTML = tableTemplate(paciente)
            this.tbody.insertAdjacentHTML('beforeend', linhaHTML);
        })
    }

    /**
     * Motor de Busca em Tempo Real.
     * @param {string} termoDigitado - O texto vindo da barra de pesquisa.
     */
    pesquisar(termoDigitado) {
        const busca = termoDigitado.toLowerCase().trim();

        if (busca === '') {
            this.dadosFiltrados = [...this.dadosOriginais];
        } else {
            this.dadosFiltrados = this.dadosOriginais.filter(paciente => {
                return Object.values(paciente).some(valor => {
                    if (valor === null || valor === undefined) return false;
                    return String(valor).toLowerCase().includes(busca);
                });
            });
        }
        this.render();
    }
}