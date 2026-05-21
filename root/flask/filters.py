def mask_cpf(valor):
    """Filtro para formatar CPF (11 dígitos)"""
    if not valor:
        return "-"
    v = str(valor)
    if len(v) != 11:
        return v

    return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"


def mask_rg(valor):
    """Filtro para formatar RG (Aproximadamente 9 dígitos em SP)"""
    if not valor:
        return "-"
    v = str(valor)
    if len(v) != 9:
        return v
    return f"{v[:2]}.{v[2:5]}.{v[5:8]}-{v[8:]}"

def mask_data(valor):

    """Filtro para converter datetime do banco para DD/MM/YYYY"""
    if not valor:
        return "-"

    return valor.strftime('%d/%m/%Y')

def mask_str(valor):
    """Filtro para formatar string do banco"""
    if not valor:
        return "-"
    v = str(valor).replace('_', ' ')
    return v.title()