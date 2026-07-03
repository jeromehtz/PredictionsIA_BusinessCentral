pageextension 50455 ItemList extends "Item List"
{
    local procedure getDocumentDate(ItemNo: Code[20]): Text
    var
        SalesLine: Record "Sales Line";
        SalesHeader: Record "Sales Header";
        DocumentDate: Text;
    begin
        SalesLine.SetRange("No.", ItemNo);

        // Parcourir toutes les lignes pour trouver la plus récente
        if SalesLine.FindSet() then
            repeat
                if SalesHeader.Get(SalesLine."Document Type", SalesLine."Document No.") then begin
                    DocumentDate := Format(SalesHeader."Document Date")
                end;
            until SalesLine.Next() = 0;

        exit(DocumentDate);
    end;

    local procedure GetLastSaleQuantity(ItemNo: Code[20]): Decimal
    var
        SalesLine: Record "Sales Line";
        SalesHeader: Record "Sales Header";
        LastQty: Decimal;
    begin
        LastQty := 0;

        // Filtrer sur l'article et les lignes de vente
        SalesLine.SetRange("No.", ItemNo);

        // Parcourir toutes les lignes pour trouver la plus récente
        if SalesLine.FindSet() then
            repeat
                if SalesHeader.Get(SalesLine."Document Type", SalesLine."Document No.") then begin
                    if LastQty = 0 then
                        LastQty := SalesLine.Quantity
                    else if SalesHeader."Document Date" >= SalesHeader."Document Date" then
                        LastQty := SalesLine.Quantity;
                end;
            until SalesLine.Next() = 0;

        exit(LastQty);
    end;

    local procedure GetQuantity(ItemNo: Code[20]): Decimal
    var
        SalesLine: Record "Sales Line";
        SalesHeader: Record "Sales Header";
        Qty: Decimal;
    begin
        Qty := 0;

        // Filtrer sur l'article et les lignes de vente
        SalesLine.SetRange("No.", ItemNo);

        // Parcourir toutes les lignes pour trouver la plus récente
        if SalesLine.FindSet() then
            repeat
                if SalesHeader.Get(SalesLine."Document Type", SalesLine."Document No.") then begin
                    Qty := Qty + SalesLine.Quantity;
                end;
            until SalesLine.Next() = 0;

        exit(Qty);
    end;

    local procedure GetLineAmount(ItemNo: Code[20]): Decimal
    var
        SalesLine: Record "Sales Line";
        Amount: Decimal;
    begin
        SalesLine.SetRange("No.", ItemNo);

        if SalesLine.FindFirst() then
            Amount := SalesLine."Line Amount";
        exit(Amount);
    end;

    local procedure toCSV()
    var
        TempBlobOut: Codeunit "Temp Blob";
        TempBlobIn: Codeunit "Temp Blob";
        InS: InStream;
        OutS: OutStream;
        FileName: Text;
        CRLF: Text;
        CR: Char;
        LF: Char;
        Line: Text;
    begin
        CR := 13;
        LF := 10;
        CRLF := Format(CR) + Format(LF);

        FileName := 'items_sales_data.csv';

        // 1. Ecriture dans TempBlobOut
        TempBlobOut.CreateOutStream(OutS, TextEncoding::UTF8);

        Line := 'Item No.;Nom;unitPrice;Line amount;last quantity;global quantity;document date' + CRLF;
        OutS.WriteText(Line);

        Rec.Reset();
        Rec.SetRange("No.");

        if Rec.FindSet() then
            repeat
                if Rec."Unit price" <> 0 then begin
                    Line :=
                        AddDoubleQuotes(Format(Rec."No.")) + ';' +
                        AddDoubleQuotes(Rec.Description) + ';' +
                        Format(Rec."Unit Price", 0, '<Precision,2:2><Standard Format,9>') + ';' +
                        Format(GetLineAmount(Rec."No."), 0, '<Precision,2:2><Standard Format,9>') + ';' +
                        Format(GetLastSaleQuantity(Rec."No.")) + ';' +
                        Format(GetQuantity(Rec."No.")) + ';' +
                        AddDoubleQuotes(GetDocumentDate(Rec."No.")) + CRLF;
                    OutS.WriteText(Line);
                end;
            until Rec.Next() = 0;

        // 2. Copie vers TempBlobIn pour la lecture
        TempBlobOut.CreateInStream(InS, TextEncoding::UTF8);
        DownloadFromStream(InS, '', '', 'CSV Files (*.csv)|*.csv', FileName);
    end;


    local procedure AddDoubleQuotes(FieldValue: Text): Text
    begin
        exit('"' + FieldValue + '"');
    end;

    var
        ML_PredictSales: Codeunit "ML Predict Sales";
}
