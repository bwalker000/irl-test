IRL_031_data_fields = ["Name", "Venture", "Project", "ASSESSOR", "Assess_date",
                       "Modified_time", "REVIEWER", "Review_date", "Support Organization"]  

for i in range(1, 16):
    for j in range(1, 10):
        string = f"QA_{i:02}_{j}"
        IRL_031_data_fields.append(string)
        string = f"QR_{i:02}_{j}"
        IRL_031_data_fields.append(string)

for i in range(1, 16):
    string = f"TA_{i:02}"
    IRL_031_data_fields.append(string)
    string = f"TR_{i:02}"
    IRL_031_data_fields.append(string)


#---------------------------------------------------------------------------------

