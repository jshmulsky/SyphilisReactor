import logging
import json
import azure.functions as func
from Workflow import Reactor
import csv

code_config = None




def configureCodes():
    table_dict = {
    "Table1":"T1_Non_Treponemal_Tests.csv",
    "Table2":"T2_Treponemal_Tests.csv",
    "Table3":"T3_Non_Treponemal_Test_From_CSF_Cord_Blood.csv",
    "Table4":"T4_Reactive_SNOMEDs.csv",
    "Table5":"T5_Non_Reactive_SNOMEDs.csv",
    "Table6":"T6_Non_Treponemal_Titers.csv",
    "Table7":"T7_CSF_Cord_Blood_Specimens.csv",
    "Table8":"T8_Reactive_Free_Text.csv",
    "Table9":"T9_Non_Reactive_Free_Text.csv"    
    }
    code_configuration = {}
    for key,filename in table_dict.items():
        f_in  = csv.reader(open("Workflow/"+filename))
        next(f_in) 
        for line in f_in:
            try:
                inputVal=line[0]
                if inputVal is None or inputVal=='':
                    continue
                codeset = code_configuration.get(key, [])
                codeset.append(inputVal)
                if inputVal != inputVal.lower():
                    codeset.append(inputVal.lower()) 
                code_configuration[key]=codeset
            except:
                pass
    return code_configuration


def main(req: func.HttpRequest):
    json_in = req.get_json()
    global code_config
    if code_config is None:
        code_config = configureCodes()    
    disposition,dispositionText = Reactor.process(json_in, code_config)      
    response = json.dumps({"Disposition":disposition,"DispositionText":dispositionText})
    return func.HttpResponse(response,mimetype="application/json")
