from datetime import datetime

def bigamy(individuals, families, tag_positions):
    """ 
    User Story 11
    Marriage should not occur during marriage to another spouse.
    
    returns: a list of warning strings.
    """
    warnings = []
    # Find of someone is married once
    # Then check if they dont have any other active marriage(married before today).
    # Ignore active marriages with dead(death before today) spouses.
    
    for indi_id in individuals:
        individual = individuals[indi_id]
        count = 0

        if individual.spouse:
            for fam_id in individual.spouse:
                if is_married(individuals, families, fam_id):
                    count += 1

        if count > 1:
            num = tag_positions[indi_id]['FAMS']
            warnings.append(f'ANOMALY: INDIVIDUAL: US11, line {num}, {individual.name} has more than 1 active marriages!')
    
    return warnings

def is_married(individuals, families, family_id):
    """
    Checks if the spouses of a given family are presently married.

    They are not married if divorce date is present and is before today
    and if one of the spouses is not alive.

    returns: a boolean
    """
    family = families[family_id]
    divorce_date = family.divorced
    if divorce_date and divorce_date < datetime.now():
        return False
    
    if not family.hid or not family.wid:
        return False
    
    # if one of the partners has passed away, they are not married.
    if not is_alive(individuals, family.hid) or not is_alive(individuals, family.wid):
        return False

    return True

def is_alive(individuals, individual_id):
    """
    Checks if the individual with the given id is alive.
    """
    return individuals[individual_id].alive

def first_cousins_married(individuals, families, tag_positions):
    """
    User Story 19

    Searches and warns if first cousins are married
    in the given families and individuals.

    returns: a list of warning strings
    """
    warnings = []

    for fam_id in families:
        family = families[fam_id]
        parents_child_at = set()

        if not family.hid or not family.wid:
            continue

        husband = individuals[family.hid]
        wife = individuals[family.wid]

        h_parents = get_parents(individuals, families, family.hid)
        w_parents = get_parents(individuals, families, family.wid)

        # add parents family where they are child to the variable
        h_parents_famc = get_parents_famc(individuals, families, family.hid)
        w_parents_famc = get_parents_famc(individuals, families, family.wid)

        if h_parents_famc.intersection(w_parents_famc) and not h_parents.intersection(w_parents):
            num = tag_positions[fam_id]['HUSB'] | tag_positions[fam_id]['WIFE'] | tag_positions[family.hid]['FAMS'] | tag_positions[family.wid]['FAMS']
            warnings.append(f'ANOMALY: FAMILY: US19, line {num} {husband.name} is married to his first cousin {wife.name}!')
    
    return warnings
        

def get_parents_famc(individuals, families, indi_id):
    """
    Find family id of both the parents of the given person.
    """
    if not indi_id:
        return set()
        
    individual = individuals[indi_id]
    parents_famc = set()

    
    if not individual.child:
        return set()
    
    for famc in individual.child:
        family = families[famc]

        if family.hid and individuals[family.hid].child:
            father = individuals[family.hid]
            parents_famc.update(father.child)

        if family.wid and individuals[family.wid].child:
            mother = individuals[family.wid]
            parents_famc.update(mother.child)
    
    return parents_famc

def get_parents(individuals, families, indi_id):
    """
    Find parents of the given person.
    """
    if not indi_id:
        return set()
        
    individual = individuals[indi_id]
    parents = set()
    
    if not individual.child:
        return set()
    
    for famc in individual.child:
        family = families[famc]

        if family.hid:
            parents.add(family.hid)
        if family.wid:
            parents.add(family.wid)
    
    return parents

def check_sibling_counts(individuals, families, tag_positions):
    """
    User Story 15

    There should be fewer than 15 siblings in a family.

    returns: a list of warning strings.
    """
    warnings = []
    for fam_id in families:
        family = families[fam_id]

        if family.children and len(family.children) >= 15:
            num = tag_positions[fam_id]['CHIL']
            for child_id in family.children:
                num.update(tag_positions[child_id]['FAMC'])
            warnings.append(f'ANOMALY: FAMILY: US15, line {sorted(num)} Family {fam_id} has more than 14 siblings!')
    
    return warnings


def check_marriage_aunts_uncles(individuals, families, tag_positions):
    """
    User Story 20

    Aunts and uncles should not marry their nieces or nephews.

    returns: a list of warning strings.
    """
    warnings = []
    
    for indi_id in individuals:
        individual = individuals[indi_id]

        if not individual.spouse:
            continue
            
        parents = get_parents(individuals, families, indi_id)
        aunts_uncles = set()

        for fam_id in get_parents_famc(individuals, families, indi_id):
            aunts_uncles.update(families[fam_id].children)
        aunts_uncles = aunts_uncles - parents

        for person_id in aunts_uncles:
            if (individuals[person_id].spouse).intersection(individual.spouse):
                num = tag_positions[indi_id]['FAMS']
                warnings.append(f'ANOMALY: FAMILY: US20, line{num} {individual.name} married to their uncle or aunt.')
    
    return warnings

def marriage_before_divorce(individuals, families, tag_positions):
    """
    User Story 04

    Marriage should be before divorce.
    """

    warnings = []
    for fam_id in families:
        family = families[fam_id]
    
        if family.married and family.divorced:
            if family.married > family.divorced:
                num = tag_positions[fam_id]['MARR'] | tag_positions[fam_id]['DIV']
                warnings.append(f'ANOMALY: FAMILY: US04, line{num}, Divorced before marriage in family {fam_id}.')
    
    return warnings

def marriage_before_death(individuals, families, tag_positions):
    """
    User Story 05

    Marriage should be before death.
    """

    warnings = []
    for indi_id in individuals:
        individual = individuals[indi_id]

        if not individual.spouse or not individual.death:
            continue
        
        for fam_spouse_id in individual.spouse:
            if families[fam_spouse_id].married and families[fam_spouse_id].married > individual.death:
                num = tag_positions[indi_id]['DEAT'] | tag_positions[fam_spouse_id]['MARR']
                warnings.append(f'ANOMALY: INDIVIDUAL: US05, line {num}, {individual.name} was married after their death.')
    
    return warnings

def divorce_before_death(individuals, families, tag_positions):
    """
    User Story 06

    Divorce should be before death.
    """

    warnings = []
    for indi_id in individuals:
        individual = individuals[indi_id]

        if not individual.spouse or not individual.death:
            continue
        
        for fam_spouse_id in individual.spouse:
            if families[fam_spouse_id].divorced and families[fam_spouse_id].divorced > individual.death:
                num = tag_positions[indi_id]['DEAT'] | tag_positions[fam_spouse_id]['DIV']
                warnings.append(f'ANOMALY: INDIVIDUAL: US06, line {num}, {individual.name} was divorced after their death.')
    
    return warnings

def marriages_to_children(individuals, families, tag_positions):
    """
    User Story 17

    No marriages to children.

    Returns a list of string warnings.
    """

    warnings = []
    for indi_id in individuals:
        individual = individuals[indi_id]
        spouses = set()
        children = set()

        if individual.spouse:
            for spouse in individual.spouse:
                family = families[spouse]
                children |= family.children
                if individual.id == family.hid:
                    spouses.add(family.wid)
                else:
                    spouses.add(family.hid)
            
            child_spouse = spouses.intersection(children)
            if child_spouse:
                child_spouse = ' '.join(child_spouse)
                num = tag_positions[indi_id]['FAMS']
                warnings.append(f'ANOMALY: FAMILY: US17, line {num}, {individual.name} is married to their child(ren) {child_spouse}!')
    
    return warnings

def marriages_to_siblings(individuals, families, tag_positions):
    """
    User Story 18

    No marriages to children.

    Returns a list of string warnings.
    """

    warnings = []
    
    for fam_id in families:
        family = families[fam_id]

        if not family.hid or not family.wid:
            continue

        husband = individuals[family.hid]
        wife = individuals[family.wid]

        for famc in husband.child:
            if famc in wife.child:
                num = tag_positions[family.hid]['FAMS'] | tag_positions[family.wid]['FAMS']
                warnings.append(f'ANOMALY: FAMILY: US18, line {num}, {husband.name} and {wife.name} are siblings and married to each other!')
    
    return warnings