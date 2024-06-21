from functools import cmp_to_key
from datetime import datetime as dt
from dateutil import relativedelta

NEW_FIELD_RECORD = 'NEW'

ADMINISTRATIVELY_CLOSE = 'CLOSE'

def total_months(rdelta):
    return (rdelta.years * 12) + rdelta.months

def getTiter(resultValue):
    try:
        value = resultValue.split(':')[1]
        return int(value)
    except:
        return 0

def compare(x,y):
    return int(x.get('SpecimenDate', '999999')) - int(y.get('SpecimenDate', '999999'))

def membership(val, codeset):
    if val in codeset:
        return True
    if val.lower() in codeset:
        return True
    return False 

def getSorted(input_json):
    return sorted(input_json['Investigations'], key=cmp_to_key(compare), reverse=True)

def getReactiveNonTreponemalTests(sorted_tests, code_config):
    most_recent_specimen = None
    returnList = []
    for inv in sorted_tests:
        if most_recent_specimen is not None and inv['SpecimenDate'] < most_recent_specimen:
            break
        if inv['Test'] in code_config['Table1']:
            if inv['Result'] in code_config['Table4']:
                returnList.append(inv)
                most_recent_specimen = inv['SpecimenDate']
                continue
            if inv['ResultValue'] in code_config['Table6']:
                returnList.append(inv)
                most_recent_specimen = inv['SpecimenDate']
                continue
            if membership(inv['ResultValue'] , code_config['Table8']):
                returnList.append(inv)
                most_recent_specimen = inv['SpecimenDate']
                continue
    return returnList


def seroconversion(sorted_tests, reactive_date, code_config):
    for inv in sorted_tests:
        monthDiff = total_months(relativedelta.relativedelta(dt.strptime(reactive_date, "%Y%m%d") , dt.strptime(inv['SpecimenDate'], "%Y%m%d")))
        if inv['SpecimenDate'] < reactive_date and monthDiff <=18:
            if inv['Test'] in code_config['Table1'] and inv['Result'] in code_config['Table4'] or membership(inv['ResultValue'], code_config['Table8']):
                return False
    return True

def fourFoldTiterIncrease(reactive_non_treponemal_tests, sorted_tests,reactive_date, code_config):
    rnttTiter = []
    ptTiter = []
    for inv in reactive_non_treponemal_tests:
        try:
            rnttTiter.append(int(getTiter(inv['ResultValue'])))
        except:
            pass
    for inv in sorted_tests:
        monthDiff = total_months(relativedelta.relativedelta(dt.strptime(reactive_date, "%Y%m%d") , dt.strptime(inv['SpecimenDate'], "%Y%m%d")))
        if inv['SpecimenDate'] < reactive_date and monthDiff <=18:
            if inv['Test'] in code_config['Table1'] and inv['ResultValue'] in code_config['Table6']:
                try:
                    ptTiter.append(int(getTiter(inv['ResultValue'])))
                except:
                    pass
    return int(max(rnttTiter) / min(ptTiter) ) >= 4

def femaleUnder50Titer8Previous6Months(input_json,reactive_non_treponemal_tests, sorted_tests, reactive_date, code_config):
    if input_json['Gender'] == 'Female' and input_json['Age']!='' and int(input_json['Age']) < 50:
        titer8=False
        previousTiter=False
        for inv in reactive_non_treponemal_tests:
            if getTiter(inv['ResultValue']) > 8:
                titer8=True
        for inv in sorted_tests:
            monthDiff =  total_months(relativedelta.relativedelta(dt.strptime(reactive_date, "%Y%m%d") , dt.strptime(inv['SpecimenDate'], "%Y%m%d")))
            if inv['SpecimenDate'] < reactive_date and monthDiff >= 6:
                if inv['Test'] in code_config['Table1'] and inv['ResultValue'] in code_config['Table6']:
                    previousTiter = True
        return titer8 and previousTiter
    return False

def currentTiter32Previous1Year(reactive_non_treponemal_tests,sorted_tests,reactive_date,code_config):
    lessthan32 = False
    previousTiter1year = False
    for inv in reactive_non_treponemal_tests:
        if getTiter(inv['ResultValue']) > 32:
            lessthan32=True
    for inv in sorted_tests:
        monthDiff = total_months(relativedelta.relativedelta(dt.strptime(reactive_date, "%Y%m%d") , dt.strptime(inv['SpecimenDate'], "%Y%m%d")))
        if inv['SpecimenDate'] < reactive_date and monthDiff >= 12 and monthDiff <=18:
            if inv['Test'] in code_config['Table1'] and inv['ResultValue'] in code_config['Table6']:
                previousTiter1year = True
    return lessthan32 and previousTiter1year

def quantitativeTiterOnPrevious(sorted_tests, reactive_date, code_config):
    for inv in sorted_tests:
        monthDiff = total_months(relativedelta.relativedelta(dt.strptime(reactive_date, "%Y%m%d") , dt.strptime(inv['SpecimenDate'], "%Y%m%d")))
        if inv['SpecimenDate'] < reactive_date and monthDiff <=18:
            if inv['Test'] in code_config['Table1'] and inv['ResultValue'] in code_config['Table6']:
                return True
    return False

def quantitativeTiterReported(reactive_non_treponemal_tests, code_config):
    for inv in reactive_non_treponemal_tests:
        if inv['Test'] in code_config['Table1'] and inv['ResultValue'] in code_config['Table6']:
            return True
    return False

def previouslyUnableToLocate(input_json):
    return "UNABLE_TO_LOCATE" in input_json['Dispositions'] or "REFUSED_EXAMINATION_TREATMENT" in input_json['Dispositions'] 

def priorSyphilisNTTest(sorted_tests, reactive_date, code_config):
    for inv in sorted_tests:
        monthDiff = total_months(relativedelta.relativedelta(dt.strptime(reactive_date, "%Y%m%d") , dt.strptime(inv['SpecimenDate'], "%Y%m%d")))
        if inv['SpecimenDate'] < reactive_date and monthDiff <=18:
            if inv['Test'] in code_config['Table1']:
                return True
    return False

def penultimateNegativeTreponemal(sorted_tests, reactive_date, code_config):
    penultimateDate = None
    for inv in sorted_tests:
        if inv['SpecimenDate'] < reactive_date and (dt.strptime(reactive_date, "%Y%m%d") - dt.strptime(inv['SpecimenDate'], "%Y%m%d")).days <=14 :
            if penultimateDate is not None and penultimateDate > inv['SpecimenDate']:
                break
            penultimateDate = inv['SpecimenDate']
            if inv['Test'] in code_config['Table2'] and inv['Result'] in code_config['Table5'] or membership(inv['ResultValue'], code_config['Table9']):
                return True
    return False

def ntWithin14Days(input_json, reactive_date, code_config):
    testFound = False
    for inv in input_json['Investigations']:
        daysDiff = (dt.strptime(reactive_date, "%Y%m%d") - dt.strptime(inv['SpecimenDate'], "%Y%m%d")).days
        if daysDiff <=14:
            if inv['Test'] in code_config['Table2'] and inv['Result'] in code_config['Table5'] or membership(inv['ResultValue'], code_config['Table9']):
                testFound = True
                continue
            if inv['Test'] in code_config['Table2'] and inv['Result'] in code_config['Table4']:
                return False
    return testFound

def lessThanOne(input_json):
    return input_json['Age']!='' and int(input_json['Age']) <= 1

def ntSampledCSFOrChord(reactive_non_treponemal_tests,code_config):
    for inv in reactive_non_treponemal_tests:
        if inv['Test'] in code_config['Table3'] or inv['SpecimenSource'] in code_config['Table7']:
            return True
    return False

def process(input_json, code_config):

    sorted_tests = getSorted(input_json)
    
    reactive_non_treponemal_tests = getReactiveNonTreponemalTests(sorted_tests, code_config)

    if len(reactive_non_treponemal_tests)==0:
        return ('NO_ACTION',' 1. No Reactive Non-Treponemal Tests')

    reactive_date = reactive_non_treponemal_tests[0]['SpecimenDate']

    
    if ntSampledCSFOrChord(reactive_non_treponemal_tests, code_config):
        return (NEW_FIELD_RECORD, ' 2. Current non-treponemal test sampled from CSF or cord blood (NEW)')

    if lessThanOne(input_json):
        return (NEW_FIELD_RECORD, ' 2. <= 1 year (NEW)')
 
    if ntWithin14Days(input_json, reactive_date, code_config):
        return (ADMINISTRATIVELY_CLOSE,' 3. Non-reactive treponemal test <= 14 days with no reactive treponemal test in this duration (CLOSE)')

    if penultimateNegativeTreponemal(sorted_tests, reactive_date, code_config):
        return (NEW_FIELD_RECORD, ' 4. Penultimate test has a negative treponemal test (NEW)')

    if not priorSyphilisNTTest(sorted_tests, reactive_date, code_config):
        return (NEW_FIELD_RECORD, ' 5. No Prior syphilis non-treponemal test (NEW)')
        
    if previouslyUnableToLocate(input_json):
        return (NEW_FIELD_RECORD, ' 6. Previously unable to locate or treat patient (NEW)')

    if not quantitativeTiterReported(reactive_non_treponemal_tests, code_config):
        return (NEW_FIELD_RECORD, ' 7a. Quantitative titer reported on current lab result (NEW)')
  
    if not quantitativeTiterOnPrevious(sorted_tests,reactive_date,code_config):
        return (NEW_FIELD_RECORD, ' 7b. Quantitative titer reported on previous lab result (NEW)')

    if currentTiter32Previous1Year(reactive_non_treponemal_tests,sorted_tests,reactive_date,code_config):
        return (NEW_FIELD_RECORD, ' 8. Current titer > 1:32 AND previous titer > 1 year (NEW)')

    if femaleUnder50Titer8Previous6Months(input_json,reactive_non_treponemal_tests, sorted_tests, reactive_date, code_config):
        return (NEW_FIELD_RECORD, ' 8. Females < 50 years old AND titer > 1:8 AND previous titer >6 months (NEW)')

    if fourFoldTiterIncrease(reactive_non_treponemal_tests, sorted_tests,reactive_date, code_config):
        return (NEW_FIELD_RECORD, ' 9. >= 4-fold titer increase (NEW)')

    if seroconversion(sorted_tests, reactive_date, code_config):
        return (NEW_FIELD_RECORD, ' 10. Seroconversion (NEW)')

    return (ADMINISTRATIVELY_CLOSE, ' All steps through algorithm (CLOSE)')
