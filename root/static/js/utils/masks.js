// ==========================================
// CONTROLADOR DE MÁSCARAS DE INPUT (UI)
// ==========================================

/**
 * Classe utilitária responsável por aplicar a biblioteca IMask aos campos do formulário.
 * Utiliza o padrão Data-Driven (Mapeamento) para facilitar a manutenção.
 */
export class MaskController {
    /**
     * Varre o HTML da página atual buscando seletores de classes específicas
     * e aplica o padrão de máscara correspondente.
     */
    initMasks() {
        // Dicionário de Máscaras: A chave é a classe CSS no HTML e o valor é o padrão visual
        const masks = {
            '.mask-cpf': '000.000.000-00',
            '.mask-rg': '00.000.000-0',
            '.mask-cep': '00000-000',
            '.mask-phone': '(00) 00000-0000',
            '.mask-sus': '000.0000.0000.0000'
    }

    // Object.entries transforma o objeto acima em uma lista interável de [seletor, padrao]
    for (const [selector, maskPattern] of Object.entries(masks)) {
            document.querySelectorAll(selector).forEach(input => {
                if (input.tagName === 'INPUT' && !input.dataset.masked) {
                    try {
                        IMask(input, { mask: maskPattern });
                        // Marca o input com um data-attribute para não processá-lo novamente
                        input.dataset.masked = "true";
                    } catch (e) {
                        console.warn(`Erro na máscara ${selector}:`, e);
                    }
                }
            });
        }
    }
}