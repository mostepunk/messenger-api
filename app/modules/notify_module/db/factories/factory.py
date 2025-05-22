from uuid import uuid4

notification_templates = {
    "target_class": "app.modules.notify_module.db.models:TemplateModel",
    "data": [
        {
            "id": uuid4(),
            "type": "email",
            "code": "confirm_email",
            "body": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Подтверждение электронной почты</title>
</head>
<body style="font-family: 'Roboto', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #333333; line-height: 1.6;">
    <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05); overflow: hidden;">
        <div style="background: linear-gradient(135deg, #6E7CFB 0%, #5F54EA 100%); color: white; padding: 30px 40px; text-align: center;">
            <div style="margin-bottom: 20px;">
                <img src="cid:logo" alt="Windi.com" style="display:block; width:150px; height:auto; margin: 0 auto;" />
            </div>
            <h1 style="margin: 0; font-size: 24px; font-weight: 700;">Подтверждение электронной почты</h1>
        </div>

        <div style="padding: 30px 40px;">
            <p style="font-size: 18px; margin-bottom: 20px; font-weight: 500;">Здравствуйте!</p>

            <div style="margin-bottom: 30px; color: #555555;">
                <p style="margin-bottom: 15px;">Благодарим вас за регистрацию в мессенджере Windi. Чтобы завершить процесс регистрации и активировать ваш аккаунт, пожалуйста, подтвердите вашу электронную почту.</p>
                <p style="margin-bottom: 15px;">Нажмите на кнопку ниже для подтверждения:</p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{{url}}" style="display: inline-block; background: linear-gradient(135deg, #6E7CFB 0%, #5F54EA 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 4px; font-weight: 500; font-size: 16px;">Подтвердить электронную почту</a>
            </div>

            <div style="margin-bottom: 30px; color: #555555;">
                <p style="margin-bottom: 15px;">Срок действия ссылки истекает через 24 часа. Если вы не регистрировались в нашем сервисе, просто проигнорируйте это письмо.</p>
            </div>
        </div>

        <div style="background-color: #f9f9f9; padding: 20px 40px; text-align: center; color: #999999; font-size: 12px;">
            <div style="margin: 15px 0;">
                <a href="#" style="display: inline-block; margin: 0 10px; color: #5F54EA; text-decoration: none; font-weight: 500;">Помощь</a>
                <a href="#" style="display: inline-block; margin: 0 10px; color: #5F54EA; text-decoration: none; font-weight: 500;">Контакты</a>
                <a href="#" style="display: inline-block; margin: 0 10px; color: #5F54EA; text-decoration: none; font-weight: 500;">Наш сайт</a>
            </div>

            <p style="margin: 10px 0;">© 2025 Windi Messenger. Все права защищены.</p>

            <div style="margin-top: 15px;">
                <p style="margin: 0;">Если у вас возникли вопросы, пожалуйста, свяжитесь с нашей службой поддержки: <a href="mailto:support@windi.com" style="color: #5F54EA; text-decoration: none;">support@windi.com</a></p>
            </div>
        </div>
    </div>
</body>
</html>""",
            "subject": "Подтверждение эл. почты",
        },
        {
            "id": uuid4(),
            "type": "email",
            "code": "reset_password",
            "body": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сброс пароля</title>
</head>
<body style="font-family: 'Roboto', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #333333; line-height: 1.6;">
    <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05); overflow: hidden;">
        <div style="background: linear-gradient(135deg, #6E7CFB 0%, #5F54EA 100%); color: white; padding: 30px 40px; text-align: center;">
            <div style="margin-bottom: 20px;">
                <img src="cid:logo" alt="Windi.com" style="display:block; width:150px; height:auto; margin: 0 auto;" />
            </div>
            <h1 style="margin: 0; font-size: 24px; font-weight: 700;">Сброс пароля</h1>
        </div>

        <div style="padding: 30px 40px;">
            <p style="font-size: 18px; margin-bottom: 20px; font-weight: 500;">Здравствуйте!</p>

            <div style="margin-bottom: 30px; color: #555555;">
                <p style="margin-bottom: 15px;">Мы получили запрос на сброс пароля для вашей учетной записи в мессенджере Windi. Чтобы создать новый пароль, пожалуйста, нажмите на кнопку ниже.</p>
                <p style="margin-bottom: 15px;">Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо — никаких изменений в вашей учетной записи не произойдет.</p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{{url}}" style="display: inline-block; background: linear-gradient(135deg, #6E7CFB 0%, #5F54EA 100%); color: white; text-decoration: none; padding: 14px 40px; border-radius: 4px; font-weight: 500; font-size: 16px;">Сбросить пароль</a>
            </div>

            <div style="margin-bottom: 30px; color: #555555;">
                <p style="margin-bottom: 15px;">Срок действия ссылки истекает через 30 минут. После этого вам потребуется сделать новый запрос на сброс пароля.</p>
                <p style="margin-bottom: 15px;">Если вы не запрашивали сброс пароля, рекомендуем немедленно изменить пароль вашей учетной записи, чтобы обеспечить её безопасность.</p>
            </div>
        </div>

        <div style="background-color: #f9f9f9; padding: 20px 40px; text-align: center; color: #999999; font-size: 12px;">
            <div style="margin: 15px 0;">
                <a href="#" style="display: inline-block; margin: 0 10px; color: #5F54EA; text-decoration: none; font-weight: 500;">Помощь</a>
                <a href="#" style="display: inline-block; margin: 0 10px; color: #5F54EA; text-decoration: none; font-weight: 500;">Контакты</a>
                <a href="#" style="display: inline-block; margin: 0 10px; color: #5F54EA; text-decoration: none; font-weight: 500;">Наш сайт</a>
            </div>

            <p style="margin: 10px 0;">© 2025 Windi Messenger. Все права защищены.</p>

            <div style="margin-top: 15px;">
                <p style="margin: 0;">Если у вас возникли вопросы, пожалуйста, свяжитесь с нашей службой поддержки: <a href="mailto:support@windi.com" style="color: #5F54EA; text-decoration: none;">support@windi.com</a></p>
            </div>
        </div>
    </div>
</body>
</html>""",
            "subject": "Запрос на изменение пароля",
        },
    ],
}

notification_attachments = {
    "target_class": "app.modules.notify_module.db.models:AttachmentModel",
    "data": [
        {
            "id": uuid4(),
            "filename": "logo.svg",
            "cid": "logo",
            "base64": "PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjU2IiB2aWV3Qm94PSIwIDAgMjAwIDU2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTI2Ljk5NTggNTAuMTA5TDMyLjc3MTQgMjguNDA5MUwzOC42NTQ3IDUzLjMxMzZDMzguOTk3NCA1NC43NjQgNDAuMzI0NCA1NS43OTE5IDQxLjg1NDMgNTUuNzkxOUg1Mi4xNjY2QzUzLjY5OTcgNTUuNzkxOSA1NS4wMjg3IDU0Ljc1OTcgNTUuMzY4MSA1My4zMDU0TDY2Ljg0OTcgNC4xMDg2OEM2Ny4zMTYgMi4xMTA0NSA2NS43NTQ2IDAuMjA4MDc2IDYzLjY0ODIgMC4yMDgwNzZINTQuNzUxMkM1My4yMDE0IDAuMjA4MDc2IDUxLjg2MjcgMS4yNjIzNCA1MS41NDAxIDIuNzM2ODhMNDUuMTEyMiAzMi4xMTgxTDM5Ljc1OTQgOC42MjE5OUMzOS40MjYzIDcuMTU5OTUgMzguMDkzNiA2LjExOTQxIDM2LjU1NDIgNi4xMTk0MUgyOS45Nzk4QzI4LjQ3OTcgNi4xMTk0MSAyNy4xNzA0IDcuMTA4NDggMjYuNzk5IDguNTIyMjdMMjAuNDc0OSAzMi41OTU5TDE1LjQwMDEgMTQuMjkwMUMxNS4wMTM3IDEyLjg5NjMgMTMuNzE0MyAxMS45MjggMTIuMjMwNCAxMS45MjhIMy41MTcyNUMxLjI5Mzg5IDExLjkyOCAtMC4yODY0NiAxNC4wMzI3IDAuMzg5ODggMTYuMDkzMUwxMS42MTI0IDUwLjI4QzEyLjA0NjkgNTEuNjAzNiAxMy4zMTE0IDUyLjUwMjEgMTQuNzM5OCA1Mi41MDIxSDIzLjgxNzdDMjUuMzEzOSA1Mi41MDIxIDI2LjYyMDggNTEuNTE4IDI2Ljk5NTggNTAuMTA5WiIgZmlsbD0idXJsKCNwYWludDBfbGluZWFyXzUzN184NzIpIi8+CjxwYXRoIGQ9Ik0xMTguNTg3IDE0LjExNjZMMTExLjIxIDQ0LjA3NkgxMDEuNjRMOTguNzcxMyAzMS4wMjI2Qzk4LjcxNjcgMzAuNzc2NyA5OC42Mjc5IDMwLjM2IDk4LjUwNDkgMjkuNzcyNkM5OC4zOTU2IDI5LjE4NTEgOTguMjY1OCAyOC41MTU3IDk4LjExNTYgMjcuNzY0M0M5Ny45Nzg5IDI3LjAxMyA5Ny44NDkyIDI2LjI3NTMgOTcuNzI2MiAyNS41NTEyQzk3LjYxNjkgMjQuODEzNSA5Ny41MzQ5IDI0LjE5MTkgOTcuNDgwMyAyMy42ODY0Qzk3LjQyNTcgMjQuMTkxOSA5Ny4zMzY5IDI0LjgxMzUgOTcuMjEzOSAyNS41NTEyQzk3LjA5MSAyNi4yNzUzIDk2Ljk1NDMgMjcuMDEzIDk2LjgwNDEgMjcuNzY0M0M5Ni42Njc0IDI4LjUxNTcgOTYuNTMwOCAyOS4xODUxIDk2LjM5NDIgMjkuNzcyNkM5Ni4yNzEzIDMwLjM2IDk2LjE4MjUgMzAuNzc2NyA5Ni4xMjc4IDMxLjAyMjZMOTMuMjM4NCA0NC4wNzZIODMuNjY4Nkw3Ni4yNTA1IDE0LjExNjZIODQuMDU4TDg3LjMxNjIgMjkuMTM3M0M4Ny4zOTgyIDI5LjUwNjIgODcuNTA3NSAzMC4wMzIxIDg3LjY0NDEgMzAuNzE1MkM4Ny43OTQ0IDMxLjM4NDYgODcuOTQ0NiAzMi4xMjIzIDg4LjA5NDkgMzIuOTI4NEM4OC4yNTg5IDMzLjcyMDcgODguNDA5MSAzNC40ODU4IDg4LjU0NTcgMzUuMjIzNUM4OC42ODI0IDM1Ljk2MTIgODguNzc4IDM2LjU3NTkgODguODMyNiAzNy4wNjc4Qzg4Ljk0MTkgMzYuMjIwNyA4OS4wODU0IDM1LjI1NzYgODkuMjYzIDM0LjE3ODRDODkuNDU0MiAzMy4wOTkxIDg5LjY1OTIgMzIuMDA2MiA4OS44Nzc3IDMwLjg5OTZDOTAuMTEgMjkuNzc5NCA5MC4zMjg2IDI4Ljc0MTEgOTAuNTMzNSAyNy43ODQ4QzkwLjczODQgMjYuODI4NSA5MC45MTYgMjYuMDQ5OCA5MS4wNjYzIDI1LjQ0ODdMOTMuNzA5OCAxNC4xMTY2SDEwMS4yMUwxMDMuNzcxIDI1LjQ0ODdDMTAzLjkwOCAyNi4wMzYyIDEwNC4wNzkgMjYuODE0OSAxMDQuMjg0IDI3Ljc4NDhDMTA0LjUwMiAyOC43NDExIDEwNC43MjEgMjkuNzc5NCAxMDQuOTM5IDMwLjg5OTZDMTA1LjE3MiAzMi4wMTk5IDEwNS4zODMgMzMuMTI2NCAxMDUuNTc1IDM0LjIxOTRDMTA1Ljc2NiAzNS4yOTg2IDEwNS45MDkgMzYuMjQ4MSAxMDYuMDA1IDM3LjA2NzhDMTA2LjA4NyAzNi4zODQ3IDEwNi4yMjQgMzUuNTI0IDEwNi40MTUgMzQuNDg1OEMxMDYuNjA2IDMzLjQzMzggMTA2Ljc5NyAzMi40MTYgMTA2Ljk4OSAzMS40MzI0QzEwNy4xOTQgMzAuNDM1MSAxMDcuMzUxIDI5LjY4MzggMTA3LjQ2IDI5LjE3ODNMMTEwLjc4IDE0LjExNjZIMTE4LjU4N1oiIGZpbGw9ImJsYWNrIi8+CjxwYXRoIGQ9Ik0xMzAuMDQyIDIwLjg1ODVWNDQuMDc2SDEyMi4wM1YyMC44NTg1SDEzMC4wNDJaTTEyNi4wNjcgMTEuNTE0MUMxMjcuMjE0IDExLjUxNDEgMTI4LjIxMiAxMS43NTMyIDEyOS4wNTkgMTIuMjMxM0MxMjkuOTE5IDEyLjcwOTUgMTMwLjM1IDEzLjY1OSAxMzAuMzUgMTUuMDc5N0MxMzAuMzUgMTYuNDU5NSAxMjkuOTE5IDE3LjM5NTMgMTI5LjA1OSAxNy44ODcyQzEyOC4yMTIgMTguMzY1MyAxMjcuMjE0IDE4LjYwNDQgMTI2LjA2NyAxOC42MDQ0QzEyNC44OTIgMTguNjA0NCAxMjMuODg4IDE4LjM2NTMgMTIzLjA1NCAxNy44ODcyQzEyMi4yMzUgMTcuMzk1MyAxMjEuODI1IDE2LjQ1OTUgMTIxLjgyNSAxNS4wNzk3QzEyMS44MjUgMTMuNjU5IDEyMi4yMzUgMTIuNzA5NSAxMjMuMDU0IDEyLjIzMTNDMTIzLjg4OCAxMS43NTMyIDEyNC44OTIgMTEuNTE0MSAxMjYuMDY3IDExLjUxNDFaIiBmaWxsPSJibGFjayIvPgo8cGF0aCBkPSJNMTUwLjE2NSAyMC40NDg3QzE1Mi41NTYgMjAuNDQ4NyAxNTQuNTEgMjEuMTI0OSAxNTYuMDI2IDIyLjQ3NzRDMTU3LjU0MyAyMy44Mjk5IDE1OC4zMDEgMjUuOTk1MiAxNTguMzAxIDI4Ljk3MzRWNDQuMDc2SDE1MC4yODhWMzEuNDExOUMxNTAuMjg4IDI5Ljg2ODIgMTUwLjA2MyAyOC43MDcgMTQ5LjYxMiAyNy45MjgzQzE0OS4xNzUgMjcuMTM1OSAxNDguNDY1IDI2LjczOTcgMTQ3LjQ4MSAyNi43Mzk3QzE0NS45NjUgMjYuNzM5NyAxNDQuOTQ3IDI3LjM2MTMgMTQ0LjQyOCAyOC42MDQ1QzE0My45MDkgMjkuODM0IDE0My42NDkgMzEuNjAzMiAxNDMuNjQ5IDMzLjkxMlY0NC4wNzZIMTM1LjYzN1YyMC44NTg1SDE0MS42ODJMMTQyLjc2OCAyMy45MzIzSDE0My4wNzVDMTQzLjU2NyAyMy4xOTQ2IDE0NC4xNTQgMjIuNTY2MiAxNDQuODM4IDIyLjA0NzFDMTQ1LjUyMSAyMS41Mjc5IDE0Ni4zMDYgMjEuMTMxNyAxNDcuMTk0IDIwLjg1ODVDMTQ4LjA4MiAyMC41ODUzIDE0OS4wNzMgMjAuNDQ4NyAxNTAuMTY1IDIwLjQ0ODdaIiBmaWxsPSJibGFjayIvPgo8cGF0aCBkPSJNMTcwLjk2NSA0NC40ODU5QzE2OC41NzQgNDQuNDg1OSAxNjYuNjA3IDQzLjQ2ODEgMTY1LjA2MyA0MS40MzI2QzE2My41MTkgMzkuMzk3IDE2Mi43NDggMzYuNDE4OCAxNjIuNzQ4IDMyLjQ5OEMxNjIuNzQ4IDI4LjUzNjIgMTYzLjU0IDI1LjUzNzUgMTY1LjEyNSAyMy41MDJDMTY2LjcwOSAyMS40NjY0IDE2OC43NTkgMjAuNDQ4NyAxNzEuMjcyIDIwLjQ0ODdDMTcyLjMxMSAyMC40NDg3IDE3My4yMDUgMjAuNTk4OSAxNzMuOTU3IDIwLjg5OTVDMTc0LjcwOCAyMS4yIDE3NS4zNTcgMjEuNjA5OSAxNzUuOTA0IDIyLjEyOUMxNzYuNDY0IDIyLjYzNDUgMTc2Ljk0OSAyMy4yMDgzIDE3Ny4zNTggMjMuODUwNEgxNzcuNTIyQzE3Ny40MjcgMjMuMjYyOSAxNzcuMzM4IDIyLjQ1NjkgMTc3LjI1NiAyMS40MzIzQzE3Ny4xNzQgMjAuMzk0IDE3Ny4xMzMgMTkuMzgzMSAxNzcuMTMzIDE4LjM5OTVWMTIuMTkwNEgxODUuMjA3VjQ0LjA3NkgxNzkuMTYyTDE3Ny40NCA0MS4xNDU3SDE3Ny4xMzNDMTc2Ljc2NCA0MS43NjA0IDE3Ni4zIDQyLjMyMDYgMTc1Ljc0IDQyLjgyNkMxNzUuMTkzIDQzLjMzMTUgMTc0LjUyNCA0My43MzQ1IDE3My43MzEgNDQuMDM1MUMxNzIuOTUzIDQ0LjMzNTYgMTcyLjAzMSA0NC40ODU5IDE3MC45NjUgNDQuNDg1OVpNMTc0LjI0NCAzOC4xNTM4QzE3NS41MjggMzguMTUzOCAxNzYuNDMgMzcuNzUwOCAxNzYuOTQ5IDM2Ljk0NDhDMTc3LjQ4MSAzNi4xMjUxIDE3Ny43NjggMzQuODgxOSAxNzcuODA5IDMzLjIxNTJWMzIuNThDMTc3LjgwOSAzMC43NDk0IDE3Ny41NSAyOS4zNDkxIDE3Ny4wMzEgMjguMzc5MUMxNzYuNTI1IDI3LjM5NTUgMTc1LjU2OSAyNi45MDM3IDE3NC4xNjIgMjYuOTAzN0MxNzMuMjA1IDI2LjkwMzcgMTcyLjQxMyAyNy4zNjgyIDE3MS43ODUgMjguMjk3MUMxNzEuMTU2IDI5LjIyNjEgMTcwLjg0MiAzMC42Njc0IDE3MC44NDIgMzIuNjIxQzE3MC44NDIgMzQuNTQ3MiAxNzEuMTU2IDM1Ljk1NDQgMTcxLjc4NSAzNi44NDIzQzE3Mi40MjcgMzcuNzE2NyAxNzMuMjQ2IDM4LjE1MzggMTc0LjI0NCAzOC4xNTM4WiIgZmlsbD0iYmxhY2siLz4KPHBhdGggZD0iTTE5OC44MTQgMjAuODU4NVY0NC4wNzZIMTkwLjgwMVYyMC44NTg1SDE5OC44MTRaTTE5NC44MzggMTEuNTE0MUMxOTUuOTg2IDExLjUxNDEgMTk2Ljk4MyAxMS43NTMyIDE5Ny44MyAxMi4yMzEzQzE5OC42OTEgMTIuNzA5NSAxOTkuMTIxIDEzLjY1OSAxOTkuMTIxIDE1LjA3OTdDMTk5LjEyMSAxNi40NTk1IDE5OC42OTEgMTcuMzk1MyAxOTcuODMgMTcuODg3MkMxOTYuOTgzIDE4LjM2NTMgMTk1Ljk4NiAxOC42MDQ0IDE5NC44MzggMTguNjA0NEMxOTMuNjYzIDE4LjYwNDQgMTkyLjY1OSAxOC4zNjUzIDE5MS44MjYgMTcuODg3MkMxOTEuMDA2IDE3LjM5NTMgMTkwLjU5NiAxNi40NTk1IDE5MC41OTYgMTUuMDc5N0MxOTAuNTk2IDEzLjY1OSAxOTEuMDA2IDEyLjcwOTUgMTkxLjgyNiAxMi4yMzEzQzE5Mi42NTkgMTEuNzUzMiAxOTMuNjYzIDExLjUxNDEgMTk0LjgzOCAxMS41MTQxWiIgZmlsbD0iYmxhY2siLz4KPGRlZnM+CjxsaW5lYXJHcmFkaWVudCBpZD0icGFpbnQwX2xpbmVhcl81MzdfODcyIiB4MT0iNjQuNzA5MiIgeTE9IjQ5LjMwNzEiIHgyPSItMTAuNDg0MSIgeTI9Ii0xNi42MzE2IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMC4wMDc3NDEzNSIgc3RvcC1jb2xvcj0iIzQ0OUFGRiIvPgo8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM3MDAwRkYiLz4KPC9saW5lYXJHcmFkaWVudD4KPC9kZWZzPgo8L3N2Zz4K",
            "!refs": {
                "template_id": {
                    "target_class": "app.modules.notify_module.db.models:TemplateModel",
                    "criteria": {"code": "confirm_email"},
                    "field": "id",
                },
            },
        },
        {
            "id": uuid4(),
            "filename": "logo.svg",
            "cid": "logo",
            "base64": "PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjU2IiB2aWV3Qm94PSIwIDAgMjAwIDU2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTI2Ljk5NTggNTAuMTA5TDMyLjc3MTQgMjguNDA5MUwzOC42NTQ3IDUzLjMxMzZDMzguOTk3NCA1NC43NjQgNDAuMzI0NCA1NS43OTE5IDQxLjg1NDMgNTUuNzkxOUg1Mi4xNjY2QzUzLjY5OTcgNTUuNzkxOSA1NS4wMjg3IDU0Ljc1OTcgNTUuMzY4MSA1My4zMDU0TDY2Ljg0OTcgNC4xMDg2OEM2Ny4zMTYgMi4xMTA0NSA2NS43NTQ2IDAuMjA4MDc2IDYzLjY0ODIgMC4yMDgwNzZINTQuNzUxMkM1My4yMDE0IDAuMjA4MDc2IDUxLjg2MjcgMS4yNjIzNCA1MS41NDAxIDIuNzM2ODhMNDUuMTEyMiAzMi4xMTgxTDM5Ljc1OTQgOC42MjE5OUMzOS40MjYzIDcuMTU5OTUgMzguMDkzNiA2LjExOTQxIDM2LjU1NDIgNi4xMTk0MUgyOS45Nzk4QzI4LjQ3OTcgNi4xMTk0MSAyNy4xNzA0IDcuMTA4NDggMjYuNzk5IDguNTIyMjdMMjAuNDc0OSAzMi41OTU5TDE1LjQwMDEgMTQuMjkwMUMxNS4wMTM3IDEyLjg5NjMgMTMuNzE0MyAxMS45MjggMTIuMjMwNCAxMS45MjhIMy41MTcyNUMxLjI5Mzg5IDExLjkyOCAtMC4yODY0NiAxNC4wMzI3IDAuMzg5ODggMTYuMDkzMUwxMS42MTI0IDUwLjI4QzEyLjA0NjkgNTEuNjAzNiAxMy4zMTE0IDUyLjUwMjEgMTQuNzM5OCA1Mi41MDIxSDIzLjgxNzdDMjUuMzEzOSA1Mi41MDIxIDI2LjYyMDggNTEuNTE4IDI2Ljk5NTggNTAuMTA5WiIgZmlsbD0idXJsKCNwYWludDBfbGluZWFyXzUzN184NzIpIi8+CjxwYXRoIGQ9Ik0xMTguNTg3IDE0LjExNjZMMTExLjIxIDQ0LjA3NkgxMDEuNjRMOTguNzcxMyAzMS4wMjI2Qzk4LjcxNjcgMzAuNzc2NyA5OC42Mjc5IDMwLjM2IDk4LjUwNDkgMjkuNzcyNkM5OC4zOTU2IDI5LjE4NTEgOTguMjY1OCAyOC41MTU3IDk4LjExNTYgMjcuNzY0M0M5Ny45Nzg5IDI3LjAxMyA5Ny44NDkyIDI2LjI3NTMgOTcuNzI2MiAyNS41NTEyQzk3LjYxNjkgMjQuODEzNSA5Ny41MzQ5IDI0LjE5MTkgOTcuNDgwMyAyMy42ODY0Qzk3LjQyNTcgMjQuMTkxOSA5Ny4zMzY5IDI0LjgxMzUgOTcuMjEzOSAyNS41NTEyQzk3LjA5MSAyNi4yNzUzIDk2Ljk1NDMgMjcuMDEzIDk2LjgwNDEgMjcuNzY0M0M5Ni42Njc0IDI4LjUxNTcgOTYuNTMwOCAyOS4xODUxIDk2LjM5NDIgMjkuNzcyNkM5Ni4yNzEzIDMwLjM2IDk2LjE4MjUgMzAuNzc2NyA5Ni4xMjc4IDMxLjAyMjZMOTMuMjM4NCA0NC4wNzZIODMuNjY4Nkw3Ni4yNTA1IDE0LjExNjZIODQuMDU4TDg3LjMxNjIgMjkuMTM3M0M4Ny4zOTgyIDI5LjUwNjIgODcuNTA3NSAzMC4wMzIxIDg3LjY0NDEgMzAuNzE1MkM4Ny43OTQ0IDMxLjM4NDYgODcuOTQ0NiAzMi4xMjIzIDg4LjA5NDkgMzIuOTI4NEM4OC4yNTg5IDMzLjcyMDcgODguNDA5MSAzNC40ODU4IDg4LjU0NTcgMzUuMjIzNUM4OC42ODI0IDM1Ljk2MTIgODguNzc4IDM2LjU3NTkgODguODMyNiAzNy4wNjc4Qzg4Ljk0MTkgMzYuMjIwNyA4OS4wODU0IDM1LjI1NzYgODkuMjYzIDM0LjE3ODRDODkuNDU0MiAzMy4wOTkxIDg5LjY1OTIgMzIuMDA2MiA4OS44Nzc3IDMwLjg5OTZDOTAuMTEgMjkuNzc5NCA5MC4zMjg2IDI4Ljc0MTEgOTAuNTMzNSAyNy43ODQ4QzkwLjczODQgMjYuODI4NSA5MC45MTYgMjYuMDQ5OCA5MS4wNjYzIDI1LjQ0ODdMOTMuNzA5OCAxNC4xMTY2SDEwMS4yMUwxMDMuNzcxIDI1LjQ0ODdDMTAzLjkwOCAyNi4wMzYyIDEwNC4wNzkgMjYuODE0OSAxMDQuMjg0IDI3Ljc4NDhDMTA0LjUwMiAyOC43NDExIDEwNC43MjEgMjkuNzc5NCAxMDQuOTM5IDMwLjg5OTZDMTA1LjE3MiAzMi4wMTk5IDEwNS4zODMgMzMuMTI2NCAxMDUuNTc1IDM0LjIxOTRDMTA1Ljc2NiAzNS4yOTg2IDEwNS45MDkgMzYuMjQ4MSAxMDYuMDA1IDM3LjA2NzhDMTA2LjA4NyAzNi4zODQ3IDEwNi4yMjQgMzUuNTI0IDEwNi40MTUgMzQuNDg1OEMxMDYuNjA2IDMzLjQzMzggMTA2Ljc5NyAzMi40MTYgMTA2Ljk4OSAzMS40MzI0QzEwNy4xOTQgMzAuNDM1MSAxMDcuMzUxIDI5LjY4MzggMTA3LjQ2IDI5LjE3ODNMMTEwLjc4IDE0LjExNjZIMTE4LjU4N1oiIGZpbGw9ImJsYWNrIi8+CjxwYXRoIGQ9Ik0xMzAuMDQyIDIwLjg1ODVWNDQuMDc2SDEyMi4wM1YyMC44NTg1SDEzMC4wNDJaTTEyNi4wNjcgMTEuNTE0MUMxMjcuMjE0IDExLjUxNDEgMTI4LjIxMiAxMS43NTMyIDEyOS4wNTkgMTIuMjMxM0MxMjkuOTE5IDEyLjcwOTUgMTMwLjM1IDEzLjY1OSAxMzAuMzUgMTUuMDc5N0MxMzAuMzUgMTYuNDU5NSAxMjkuOTE5IDE3LjM5NTMgMTI5LjA1OSAxNy44ODcyQzEyOC4yMTIgMTguMzY1MyAxMjcuMjE0IDE4LjYwNDQgMTI2LjA2NyAxOC42MDQ0QzEyNC44OTIgMTguNjA0NCAxMjMuODg4IDE4LjM2NTMgMTIzLjA1NCAxNy44ODcyQzEyMi4yMzUgMTcuMzk1MyAxMjEuODI1IDE2LjQ1OTUgMTIxLjgyNSAxNS4wNzk3QzEyMS44MjUgMTMuNjU5IDEyMi4yMzUgMTIuNzA5NSAxMjMuMDU0IDEyLjIzMTNDMTIzLjg4OCAxMS43NTMyIDEyNC44OTIgMTEuNTE0MSAxMjYuMDY3IDExLjUxNDFaIiBmaWxsPSJibGFjayIvPgo8cGF0aCBkPSJNMTUwLjE2NSAyMC40NDg3QzE1Mi41NTYgMjAuNDQ4NyAxNTQuNTEgMjEuMTI0OSAxNTYuMDI2IDIyLjQ3NzRDMTU3LjU0MyAyMy44Mjk5IDE1OC4zMDEgMjUuOTk1MiAxNTguMzAxIDI4Ljk3MzRWNDQuMDc2SDE1MC4yODhWMzEuNDExOUMxNTAuMjg4IDI5Ljg2ODIgMTUwLjA2MyAyOC43MDcgMTQ5LjYxMiAyNy45MjgzQzE0OS4xNzUgMjcuMTM1OSAxNDguNDY1IDI2LjczOTcgMTQ3LjQ4MSAyNi43Mzk3QzE0NS45NjUgMjYuNzM5NyAxNDQuOTQ3IDI3LjM2MTMgMTQ0LjQyOCAyOC42MDQ1QzE0My45MDkgMjkuODM0IDE0My42NDkgMzEuNjAzMiAxNDMuNjQ5IDMzLjkxMlY0NC4wNzZIMTM1LjYzN1YyMC44NTg1SDE0MS42ODJMMTQyLjc2OCAyMy45MzIzSDE0My4wNzVDMTQzLjU2NyAyMy4xOTQ2IDE0NC4xNTQgMjIuNTY2MiAxNDQuODM4IDIyLjA0NzFDMTQ1LjUyMSAyMS41Mjc5IDE0Ni4zMDYgMjEuMTMxNyAxNDcuMTk0IDIwLjg1ODVDMTQ4LjA4MiAyMC41ODUzIDE0OS4wNzMgMjAuNDQ4NyAxNTAuMTY1IDIwLjQ0ODdaIiBmaWxsPSJibGFjayIvPgo8cGF0aCBkPSJNMTcwLjk2NSA0NC40ODU5QzE2OC41NzQgNDQuNDg1OSAxNjYuNjA3IDQzLjQ2ODEgMTY1LjA2MyA0MS40MzI2QzE2My41MTkgMzkuMzk3IDE2Mi43NDggMzYuNDE4OCAxNjIuNzQ4IDMyLjQ5OEMxNjIuNzQ4IDI4LjUzNjIgMTYzLjU0IDI1LjUzNzUgMTY1LjEyNSAyMy41MDJDMTY2LjcwOSAyMS40NjY0IDE2OC43NTkgMjAuNDQ4NyAxNzEuMjcyIDIwLjQ0ODdDMTcyLjMxMSAyMC40NDg3IDE3My4yMDUgMjAuNTk4OSAxNzMuOTU3IDIwLjg5OTVDMTc0LjcwOCAyMS4yIDE3NS4zNTcgMjEuNjA5OSAxNzUuOTA0IDIyLjEyOUMxNzYuNDY0IDIyLjYzNDUgMTc2Ljk0OSAyMy4yMDgzIDE3Ny4zNTggMjMuODUwNEgxNzcuNTIyQzE3Ny40MjcgMjMuMjYyOSAxNzcuMzM4IDIyLjQ1NjkgMTc3LjI1NiAyMS40MzIzQzE3Ny4xNzQgMjAuMzk0IDE3Ny4xMzMgMTkuMzgzMSAxNzcuMTMzIDE4LjM5OTVWMTIuMTkwNEgxODUuMjA3VjQ0LjA3NkgxNzkuMTYyTDE3Ny40NCA0MS4xNDU3SDE3Ny4xMzNDMTc2Ljc2NCA0MS43NjA0IDE3Ni4zIDQyLjMyMDYgMTc1Ljc0IDQyLjgyNkMxNzUuMTkzIDQzLjMzMTUgMTc0LjUyNCA0My43MzQ1IDE3My43MzEgNDQuMDM1MUMxNzIuOTUzIDQ0LjMzNTYgMTcyLjAzMSA0NC40ODU5IDE3MC45NjUgNDQuNDg1OVpNMTc0LjI0NCAzOC4xNTM4QzE3NS41MjggMzguMTUzOCAxNzYuNDMgMzcuNzUwOCAxNzYuOTQ5IDM2Ljk0NDhDMTc3LjQ4MSAzNi4xMjUxIDE3Ny43NjggMzQuODgxOSAxNzcuODA5IDMzLjIxNTJWMzIuNThDMTc3LjgwOSAzMC43NDk0IDE3Ny41NSAyOS4zNDkxIDE3Ny4wMzEgMjguMzc5MUMxNzYuNTI1IDI3LjM5NTUgMTc1LjU2OSAyNi45MDM3IDE3NC4xNjIgMjYuOTAzN0MxNzMuMjA1IDI2LjkwMzcgMTcyLjQxMyAyNy4zNjgyIDE3MS43ODUgMjguMjk3MUMxNzEuMTU2IDI5LjIyNjEgMTcwLjg0MiAzMC42Njc0IDE3MC44NDIgMzIuNjIxQzE3MC44NDIgMzQuNTQ3MiAxNzEuMTU2IDM1Ljk1NDQgMTcxLjc4NSAzNi44NDIzQzE3Mi40MjcgMzcuNzE2NyAxNzMuMjQ2IDM4LjE1MzggMTc0LjI0NCAzOC4xNTM4WiIgZmlsbD0iYmxhY2siLz4KPHBhdGggZD0iTTE5OC44MTQgMjAuODU4NVY0NC4wNzZIMTkwLjgwMVYyMC44NTg1SDE5OC44MTRaTTE5NC44MzggMTEuNTE0MUMxOTUuOTg2IDExLjUxNDEgMTk2Ljk4MyAxMS43NTMyIDE5Ny44MyAxMi4yMzEzQzE5OC42OTEgMTIuNzA5NSAxOTkuMTIxIDEzLjY1OSAxOTkuMTIxIDE1LjA3OTdDMTk5LjEyMSAxNi40NTk1IDE5OC42OTEgMTcuMzk1MyAxOTcuODMgMTcuODg3MkMxOTYuOTgzIDE4LjM2NTMgMTk1Ljk4NiAxOC42MDQ0IDE5NC44MzggMTguNjA0NEMxOTMuNjYzIDE4LjYwNDQgMTkyLjY1OSAxOC4zNjUzIDE5MS44MjYgMTcuODg3MkMxOTEuMDA2IDE3LjM5NTMgMTkwLjU5NiAxNi40NTk1IDE5MC41OTYgMTUuMDc5N0MxOTAuNTk2IDEzLjY1OSAxOTEuMDA2IDEyLjcwOTUgMTkxLjgyNiAxMi4yMzEzQzE5Mi42NTkgMTEuNzUzMiAxOTMuNjYzIDExLjUxNDEgMTk0LjgzOCAxMS41MTQxWiIgZmlsbD0iYmxhY2siLz4KPGRlZnM+CjxsaW5lYXJHcmFkaWVudCBpZD0icGFpbnQwX2xpbmVhcl81MzdfODcyIiB4MT0iNjQuNzA5MiIgeTE9IjQ5LjMwNzEiIHgyPSItMTAuNDg0MSIgeTI9Ii0xNi42MzE2IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMC4wMDc3NDEzNSIgc3RvcC1jb2xvcj0iIzQ0OUFGRiIvPgo8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM3MDAwRkYiLz4KPC9saW5lYXJHcmFkaWVudD4KPC9kZWZzPgo8L3N2Zz4K",
            "!refs": {
                "template_id": {
                    "target_class": "app.modules.notify_module.db.models:TemplateModel",
                    "criteria": {"code": "reset_password"},
                    "field": "id",
                },
            },
        },
    ],
}
