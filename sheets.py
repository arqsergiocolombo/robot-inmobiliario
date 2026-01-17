def export_to_sheets(data):
    if not data:
        print("⚠️ No hay datos para exportar.")
        return

    # IMPORTANTE: Verificá que este ID sea el de tu Excel real
    SPREADSHEET_ID = 'TU_ID_DE_GOOGLE_SHEETS_AQUÍ' 
    RANGE_NAME = 'Sheet1!A2'

    try:
        # Leemos la variable directamente
        env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        
        if not env_json:
            print("❌ ERROR: La variable GOOGLE_SERVICE_ACCOUNT_JSON no existe en Railway.")
            return

        info = json.loads(env_json)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)

        values = [[d['precio_usd'], d['zona'], d['link']] for d in data]
        body = {'values': values}

        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print("📊 ¡DATOS EXPORTADOS! Revisá tu Google Sheets ahora.")
    except Exception as e:
        print(f"❌ Error al exportar a Sheets: {e}")
