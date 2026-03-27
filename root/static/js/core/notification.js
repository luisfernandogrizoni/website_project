// ------------------- SERVIÇO DE NOTIFICAÇÕES (ALERTS) ------------------- //

/**
 * Classe responsável por gerenciar o feedback visual para o usuário.
 * biblioteca SweetAlert2.
 */
export class NotificationService {
    /**
     * Exibe um modal de carregamento que não pode ser fechado pelo usuário.
     * @param {string} titulo - O texto principal do modal.
     */
    loading(titulo = 'Processando...'){
        Swal.fire({
            title: titulo,
            html: 'Por favor, aguarde.',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });
    }

    /**
     * Exibe um alerta de sucesso e opcionalmente recarrega a página.
     * @param {string} mensagem - A mensagem de sucesso.
     * @param {boolean} [reload=false] - Se true, dá refresh na página ao fechar.
     */
    sucesso(mensagem, reload = false) {
        Swal.fire({
            icon: 'success',
            title: 'Sucesso!',
            text: mensagem,
            confirmButtonColor: '#28a745'}).then(() => {
            if (reload) window.location.reload();
        });
        }

    /**
     * Exibe um alerta de erro crítico ou de validação.
     * @param {string} mensagem - O detalhe do erro.
     */
    erro(mensagem) {
        Swal.fire({
            icon: 'error',
            title: 'Parece que algo deu errado!',
            text: mensagem,
            confirmButtonColor: '#d33'
        });
    }

    /**
     * Força o fechamento de qualquer alerta ativo na tela.
     */
    fecharAlerta() { Swal.close(); }
}