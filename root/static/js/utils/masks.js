export class MaskController {
    initMasks() {
        const masks = {
            '.mask-cpf': '000.000.000-00',
            '.mask-rg': '00.000.000-0',
            '.mask-cep': '00000-000',
            '.mask-phone': '(00) 00000-0000',
            '.mask-sus': '000.0000.0000.0000'
    }

    for (const [selector, maskPattern] of Object.entries(masks)) {
            document.querySelectorAll(selector).forEach(input => {
                if (input.tagName === 'INPUT' && !input.dataset.masked) {
                    try {
                        IMask(input, { mask: maskPattern });
                        input.dataset.masked = "true";
                    } catch (e) {
                        console.warn(`Erro na máscara ${selector}:`, e);
                    }
                }
            });
        }
    }
}