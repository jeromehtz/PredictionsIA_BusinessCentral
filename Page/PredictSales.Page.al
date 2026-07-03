page 50455 PredictSales
{
    ApplicationArea = All;
    Caption = 'Prévision des ventes';
    PageType = Document;
    UsageCategory = Tasks;

    layout
    {
        area(Content)
        {
            field(TargetYear; TargetYear)
            {
                ApplicationArea = All;
                Caption = 'Année cible';
            }
            field(TargetMonth; TargetMonth)
            {
                ApplicationArea = All;
                Caption = 'Mois cible';
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(PredictSales)
            {
                ApplicationArea = All;
                Caption = 'Prévoir les ventes';
                trigger OnAction()
                var
                    Pred: Decimal;
                    YearInt: Integer;
                    MonthInt: Integer;
                begin
                    YearInt := 2026 + TargetYear.AsInteger();
                    MonthInt := TargetMonth.AsInteger(); // 0 = toute l'année
                    Pred := ML_PredictSales.PredictSales(YearInt, MonthInt);
                    if MonthInt = 0 then
                        Message('Profit cumulé prévu jusqu''au 31/12/%1 : %2 €', YearInt, Pred)
                    else
                        Message('Profit cumulé prévu jusqu''au %1/%2 : %3 €', MonthInt, YearInt, Pred);
                end;
            }
        }
    }

    var
        TargetYear: Enum "Target Year";
        TargetMonth: Enum "Target Month";
        ML_PredictSales: Codeunit "ML Predict Sales";
}