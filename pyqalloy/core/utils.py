from pymatgen.core import Composition
from pymatgen.core.periodic_table import get_el_sp
from typing import Union, Dict, List

# Modify composition string from the template into a unified
# representation of (1) IUPAC standardized formula, (2) pymatgen dictionary
# composition object, (3) anonymized formula, (4) reduced formula, (5) chemical system,
# and (6) number of components

def percentileFormula(
        cd: dict
        ) -> str:
    order = sorted(cd.keys(), key=lambda s: get_el_sp(s).iupac_ordering)
    return ' '.join([f'{el}{round(100*cd[el], 1):g}' for el in order])

def relationalFormula(
        cd: dict
        ) -> str:
    order = sorted(cd.keys(), key=lambda s: get_el_sp(s).iupac_ordering)
    lowest = min([v for v in cd.values() if v>0.005])
    return ' '.join([f'{el}{round(cd[el]/lowest, 2):g}' for el in order])

def compStr2compList(
        s: str
        ) -> list:
    try:
        compObj = Composition(s).reduced_composition
        if not compObj.valid:
            print("Composition invalid")
        return [compObj.iupac_formula,
                dict(compObj.fractional_composition.as_dict()),
                percentileFormula(dict(compObj.fractional_composition.as_dict())),
                relationalFormula(dict(compObj.fractional_composition.as_dict())),
                compObj.anonymized_formula,
                compObj.reduced_formula,
                compObj.chemical_system,
                compObj.chemical_system.split('-'),
                compObj.__len__()]
    except Exception as e:
        print(e)
        raise ValueError("Warning! Can't parse composition!: "+s)

# Unifies phase names in the database
# If composition -> keep as is
# if all uppercase (e.g. BCC, FCC) -> keep as is
# otherwise -> make all lowercase

def phaseNameUnifier(
        s: str
        ) -> str:
    exceptionToUpper = ['b0', 'b1', 'b2', 'a0', 'a1', 'a2']
    replaceDict = {'bulkmetallic\nglass' : 'amorphous', 'bcc' : 'BCC', 'fcc' : 'FCC', 'LAVES' : 'laves'}

    try:
        isComp = Composition(s).valid
    except Exception as e:
        isComp = False

    if s in exceptionToUpper:
        return s.upper()
    elif s in replaceDict:
        return replaceDict[s]
    elif isComp:
        return s
    elif s.isupper():
        return s
    else:
        return s.lower()

# Transforms the structure string into a list of
# individual phases, interpreting (1) multiple phases
# of the same type, (2) composition-defined phases, and
# (3) named phases. Processes them in a unified way.

def structStr2list(
        s: str
        ) -> list:
    ls = []

    s = s.replace(' ','')
    tempLs = list(s.split('+'))
    for phase in tempLs:
        if phase[0].isdigit():
            for i in range(int(phase[0])):
                ls.append(phaseNameUnifier(phase[1:]))
        else:
            ls.append(phaseNameUnifier(phase))
    ls.sort()
    if ls.__len__()>0:
        return [ls, ls.__len__()]
    else:
        return []

# Process name unifier

def processNameUnifier(
        s: str
        ) -> str:
    exceptions = []

    if s in exceptions:
        return s
    elif s.isupper():
        return s
    else:
        return s.lower()

# Processes processing string into a unified-form process list

def processStr2list(
        s: str
        ) -> list:
    ls = []
    s = s.replace(' ','')
    tempLs = list(s.split('+'))
    for process in tempLs:
        if process[0].isdigit():
            for i in range(int(process[0])):
                ls.append(processNameUnifier(process[1:]))
        else:
            ls.append(processNameUnifier(process))
    if ls.__len__()>0:
        return [ls, ls.__len__()]
    else:
        return []

def compDict2Vec(
        compDict: Dict[str, Union[int, float]]
        ) -> Union[None, List[float]]:
    # A couple of constants fixes for the ULTERA database (V1 of Composition Vector)
    elementOrder = ['Ni', 'Co', 'Cr', 'Fe', 'Al', 'Ti', 'Mo', 'Zr', 'Nb', 'V', 'W', 'Ta', 'Hf', 'Cu', 'Mn', 'Si', 'B',
                'Re', 'Ru', 'Sn', 'Zn', 'Mg', 'Li', 'Y', 'Ca', 'Pd', 'Sc', 'Ir', 'Be', 'Nd', 'U', 'Er', 'Dy', 'Gd',
                'Sm', 'Pr', 'Ce', 'La', 'Ag', 'Ga', 'Bi', 'Pu', 'Th', 'Pb', 'Au', 'Pt', 'Os', 'Yb', 'Ho', 'Ba', 'In',
                'Cd', 'Sr', 'C', 'O', 'N', 'S']

    common = elementOrder[:20]
    metallic = elementOrder[:-4]
    all = elementOrder[:]

    outVec = []
    dictElements = set(compDict)

    for coverage in [common, metallic, all]:
        if dictElements.issubset(coverage):
            vecCover = coverage
            break
        else:
            vecCover = None

    if vecCover is not None:
        for el in vecCover:
            if el in dictElements:
                outVec.append(float(round(compDict[el], 4)))
            else:
                outVec.append(float(0))
    else:
        elementsNotInAll = list(dictElements.difference(set(all)))
        print(f'Composition vector could not be computed due to missing definition for {elementsNotInAll}')
        return None

    return outVec

# Convert a pair of metadata and data into ULTERA Database datapoint
def datapoint2entry(
        metaD: Dict[str, Union[str, int, float]],
        dataP: Dict[str, Union[str, int, float]],
        printOuts: bool = True
        ) -> Dict[str, Dict[str, Union[str, int, float]]]:
    # metadata
    entry = {'meta' : metaD, 'material' : {}, 'property' : {}, 'reference' : {}}

    # composition
    try:
        compList = compStr2compList(dataP['Composition'])
    except Exception as e:
        print(str(e))
        raise ValueError("Could not parse the composition! Required for upload. Aborting upload!")

    entry['material'].update({
            'rawFormula': dataP['Composition'],
            'formula': compList[0],
            'compositionDictionary' : compList[1],
            'percentileFormula': compList[2],
            'relationalFormula': compList[3],
            'compositionVector': compDict2Vec(compList[1]),
            'anonymizedFormula' : compList[4],
            'reducedFormula' : compList[5],
            'system' : compList[6],
            'elements' : compList[7],
            'nComponents' : compList[8]})

    # structure
    if 'Structure' in dataP:
        if dataP['Structure'] is not None:
            structList = structStr2list(dataP['Structure'])
            entry['material'].update({
                'structure': structList[0],
                'nPhases': structList[1]})
        else:
            if printOuts:
                print('No structure data!')

    # processing
    if 'Processing' in dataP:
        if dataP['Processing'] is not None:
            processingList = processStr2list(dataP['Processing'])
            entry['material'].update({
                    'processes' : processingList[0],
                    'nProcessSteps' : processingList[1]})
        else:
            if printOuts:
                print('No process data!')

    # comment
    if 'Material Comment' in dataP:
        if dataP['Material Comment'] is not None:
            entry['material'].update({
                    'comment' : dataP['Material Comment']})

    if 'Temperature [K]' in dataP:
        # If there is temperature reported, regardless of property report, note the temperature of material
        if dataP['Temperature [K]'] is not None:
            entry['material'].update({
                'observationTemperature': float(dataP['Temperature [K]'])})

    if 'Name' in dataP:
        # Requires: Name and Value
        if dataP['Name'] is not None:
            entry['property'].update({
                'name' : dataP['Name'],
                'value': float(dataP['Value [SI]'])})

            # If property has a name, go through all of property parameters and value
            if 'Source' in dataP:
                if dataP['Source'] is not None:
                    entry['property'].update({
                        'source': dataP['Source']})
            if 'Property Parameters' in dataP:
                if dataP['Property Parameters'] is not None:
                    entry['property'].update({
                        'parameters': dataP['Property Parameters']})
            if 'Temperature [K]' in dataP:
                if dataP['Temperature [K]'] is not None:
                    entry['property'].update({
                        'temperature': float(dataP['Temperature [K]'])})
            if 'Unit [SI]' in dataP:
                if dataP['Unit [SI]'] is not None:
                    entry['property'].update({
                        'unitName': dataP['Unit [SI]']})
        else:
            del entry['property']
            if printOuts:
                print('No property data or error occurred!')

    if 'DOI' in dataP:
        # Requires DOI
        if 'DOI' in dataP:
            if dataP['DOI'] is not None:
                entry['reference'].update({
                        'doi' : dataP['DOI']})
                if 'Pointer' in dataP:
                    if dataP['Pointer'] is not None:
                        entry['reference'].update({
                            'pointer': dataP['Pointer']})
            else:
                del entry['reference']
                if printOuts:
                    print('No reference data!')

    return entry
