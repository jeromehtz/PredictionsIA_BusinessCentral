pageextension 50457 "EcrituresComptables.PageExt.al" extends "General Ledger Entries"
{
    
    layout
    {
        addafter("Source No.")
        {
            field("Source Name"; SourceName)
            {
                ApplicationArea = All;
                Caption = 'Source Name';
                Editable = false;
            }
        }
    }
    trigger OnAfterGetCurrRecord()
    begin
        SourceName := GetSourceName();
    end;

    local procedure GetSourceName(): Text[100]
    var
        Customer: Record Customer;
        Vendor: Record Vendor;
        BankAccount: Record "Bank Account";
        FixedAsset: Record "Fixed Asset";
        Employee: Record Employee;
    begin
        case Rec."Source Type" of
            Rec."Source Type"::Customer:
                if Customer.Get(Rec."Source No.") then
                    exit(Customer.Name);
            
            Rec."Source Type"::Vendor:
                if Vendor.Get(Rec."Source No.") then
                    exit(Vendor.Name);
            
            Rec."Source Type"::"Bank Account":
                if BankAccount.Get(Rec."Source No.") then
                    exit(BankAccount.Name);
            
            Rec."Source Type"::"Fixed Asset":
                if FixedAsset.Get(Rec."Source No.") then
                    exit(FixedAsset.Description);
            
            Rec."Source Type"::Employee:
                if Employee.Get(Rec."Source No.") then
                    exit(Employee.FullName());
        end;
        
        exit('');
    end;
    var
        SourceName: Text[50];
}
