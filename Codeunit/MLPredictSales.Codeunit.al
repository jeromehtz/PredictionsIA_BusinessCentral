codeunit 50110 "ML Predict Sales"
{
    procedure PredictSales(TargetYear: Integer; TargetMonth: Integer): Decimal
    var
        Client: HttpClient;
        Response: HttpResponseMessage;
        Content: HttpContent;
        Headers: HttpHeaders;
        JsonResponse: JsonObject;
        JsonRequest: JsonObject;
        Token: JsonToken;
        RespText: Text;
        RequestText: Text;
        PredictedQty: Decimal;
    begin
        // Construire le JSON
        JsonRequest.Add('target_year', TargetYear);
        if TargetMonth > 0 then
            JsonRequest.Add('target_month', TargetMonth);
        JsonRequest.WriteTo(RequestText);

        // DEBUG
        MESSAGE('JSON envoyé : %1', RequestText);

        // Configurer le contenu
        Content.WriteFrom(RequestText);
        Content.GetHeaders(Headers);
        Headers.Clear();
        Headers.Add('Content-Type', 'application/json');

        // Appeler l'API Python
        if Client.Post('https://uninstinctively-incompliant-kellee.ngrok-free.dev/predict', Content, Response) then begin
            if Response.IsSuccessStatusCode() then begin
                Response.Content.ReadAs(RespText);

                // DEBUG
                MESSAGE('JSON reçu : %1', RespText);

                if JsonResponse.ReadFrom(RespText) then
                    if JsonResponse.Get('profit_total', Token) then begin
                        PredictedQty := Token.AsValue().AsDecimal();
                        exit(PredictedQty);
                    end;
                Error('Format de réponse invalide');
            end else begin
                Response.Content.ReadAs(RespText);
                Error('Erreur API : %1 - Détails : %2', Response.HttpStatusCode(), RespText);
            end;
        end else
            Error('Impossible de contacter le service ML.');
    end;
}
