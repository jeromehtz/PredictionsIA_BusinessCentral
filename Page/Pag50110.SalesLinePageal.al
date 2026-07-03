page 50110 "SalesLine.Page.al"
{
    ApplicationArea = All;
    Caption = 'Lignes de vente';
    PageType = ListPart;
    SourceTable = "Sales Line";
    
    layout
    {
        area(Content)
        {
            field(SalesLineCount; Rec."SalesLineCount")
            {
                ApplicationArea = All;
                Caption = 'Nombre de lignes de vente';
                Editable = false;
            }
            repeater(General)
            {
                field("Document Type"; Rec."Document Type")
                {
                    ApplicationArea = All;
                }
                field("Document No."; Rec."Document No.")
                {
                    ApplicationArea = All;
                }
                field("Line No."; Rec."Line No.")
                {
                    ApplicationArea = All;
                }
                field("No."; Rec."No.")
                {
                    ApplicationArea = All;
                }
                field(Quantity; Rec.Quantity)
                {
                    ApplicationArea = All;
                }
            }
        }
    }
}
