tableextension 50000 SalesLine extends "Sales Line"
{
    fields
    {
        field(50000; "SalesLineCount"; Integer)
        {
            Caption = '';
            FieldClass = FlowField;
            Editable = false;
            CalcFormula = count("Sales Line" where ("Line No." = field("Line No.")));
        }
    }
}
