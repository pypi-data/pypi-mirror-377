# BotMail

BotMail é uma ferramenta Python projetada para facilitar o gerenciamento de e-mails usando os protocolos SMTP e IMAP. Ideal para integrar em fluxos de trabalho de Automação de Processos Robóticos (RPA), permite o envio, leitura e manipulação de e-mails de forma simples e eficiente.

## Funcionalidades

- **Envio de E-mails (SMTP):** Configure e envie e-mails com facilidade.
- **Recebimento de E-mails (IMAP):** Leia e processe e-mails diretamente do servidor.
- **Manipulação de Anexos:** Faça download e gerenciamento de anexos.
- **Automação:** Integração com fluxos de RPA para tarefas repetitivas e automáticas.

## Requisitos

- Python 3.10 ou superior.
- Biblioteca padrão `smtplib`, `imaplib`, e `email`.

## Instalação

1. Instale o pacote:
   ```bash
    pip install botmail
   ```

## Exemplo de Uso

```python
from botmail.webmail import Email

if __name__ == "__main__":
    mail = Email(
        "smtp.example.com.br",
        "imap.example.com.br"
    )
    mail.send_email(
        "Nem Email Class",
        "example1@gmail.com",
        ["example2@gmail.com"],
        mail.generate_simple_html_body('Hi', 'BotMail', "What's up?"),
    )
```

No exemplo acima:
- Configuramos as credenciais do servidor SMTP e IMAP.
- Enviamos um e-mail simples usando `send_email`.

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo [Licença MIT](LICENSE) para mais detalhes.

## Contribuições

Contribuições são bem-vindas! Caso tenha sugestões, melhorias ou correções, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Contato

Para dúvidas ou suporte, entre em contato com o mantenedor através do [GitHub](https://github.com/botlorien/botmail).
